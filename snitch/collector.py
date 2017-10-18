import collections
import datetime
import dateutil.parser
import jira
import lxml.etree
import requests
from . import utils


class Collector(object):
    def __init__(self, jira_url, basic_auth):
        self._jira = jira.JIRA(jira_url, basic_auth=basic_auth)
        self._session = requests.Session()
        self._session.url = jira_url
        self._session.auth = basic_auth

    def collect(self, accounts, projects, date_from, date_to):
        """Collect complete accounts history."""
        if not accounts:
            return {}, {}

        if not projects:
            return {}, {}

        history = collections.OrderedDict()
        for account in accounts:
            history[account] = {
                'active': self._query_status('active', account, projects, date_from, date_to),
                'review': self._query_status('review', account, projects, date_from, date_to),
                'stream': self._query_stream(account, projects, date_from, date_to),
                'workon': self._query_workon(account, projects, date_from, date_to),
            }

        return history

    def _query_status(self, action, account, projects, date_from, date_to):
        """Gets issues in status."""
        actions = {
            'active': 'WAS "In progress"',
            'review': 'CHANGED FROM "Code review"',
        }

        issues = self._jira.search_issues(
            (
                'project IN (%(projects)s) '
                'AND status %(action)s BY "%(account)s" '
                'DURING ("%(date_from)s", "%(date_to)s") '
            ) % {
                'projects': ', '.join('"%s"' % x for x in projects),
                'date_from': date_from.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
                'account': account,
                'action': actions[action],
            },
            maxResults=100500,
            fields='summary',
        )

        results = []
        for issue in issues:
            results.append({
                'key': issue.key,
                'title': issue.fields.summary,
            })

        return results

    def _query_stream(self, account, projects, date_from, date_to):
        """Gets accounts stream."""
        datetime_from = datetime.datetime.combine(date_from, datetime.time.min)
        datetime_to = datetime.datetime.combine(date_to, datetime.time.max)
        jira_url = self._session.url + '/plugins/servlet/streams'
        response = self._session.get(jira_url, params={
            'streams': 'user IS %s' % account,
            'relativeLinks': 'true',
            'maxResults': 100500,
            'minDate': int(datetime_from.timestamp() * 1000),
            'maxDate': int(datetime_to.timestamp() * 1000),
        })

        def query(element, xpath, first=True):
            items = element.xpath(xpath, namespaces={
                'activity': 'http://activitystrea.ms/spec/1.0/',
                'feed': 'http://www.w3.org/2005/Atom',
                'usr': 'http://streams.atlassian.com/syndication/username/1.0',
            })
            return (items[0] if items else None) if first else items

        results = []
        stream = lxml.etree.fromstring(response.content)
        for element in query(stream, '/feed:feed/feed:entry', False):
            key_target = query(element, 'activity:target/feed:title/text()')
            key_object = query(element, 'activity:object/feed:title/text()')
            project = utils.split_key(key_target or key_object)[0]
            if project in projects:
                title_target = query(element, 'activity:target/feed:summary/text()')
                title_object = query(element, 'activity:object/feed:summary/text()')
                category_term = query(element, 'feed:category/@term')
                category_actions = {'comment': 'comment'}

                if category_term in category_actions:
                    results.append({
                        'key': key_target or key_object,
                        'title': title_object or title_target,
                        'action': category_actions[category_term],
                    })

        return results

    def _query_workon(self, account, projects, date_from, date_to):
        """Gets work log issues."""
        issues = self._jira.search_issues(
            (
                'project IN (%(projects)s) '
                'AND worklogAuthor = "%(author)s" '
                'AND worklogDate >= "%(date_from)s" '
                'AND worklogDate <= "%(date_to)s" '
            ) % {
                'projects': ', '.join('"%s"' % x for x in projects),
                'date_from': date_from.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
                'author': account,
            },
            maxResults=100500,
            fields='summary',
        )

        results = []
        for issue in issues:
            for worklog in self._jira.worklogs(issue.key):
                if worklog.author.key != account:
                    continue

                started = dateutil.parser.parse(worklog.started)
                if not (date_from <= started.date() <= date_to):
                    continue

                results.append({
                    'key': issue.key,
                    'title': issue.fields.summary,
                    'comment': worklog.comment,
                })

        return results
