# coding: utf-8

import dateutil.parser as parser


class Collector(object):
    def __init__(self, jira):
        self.jira = jira

    def get_workon_issues(self, project, authors, date_from, date_to):
        issues = self.jira.search_issues((
            'project = %(project)s '
            'AND worklogDate >= "%(date_from)s" '
            'AND worklogDate <= "%(date_to)s" '
            'AND timespent > 0 '
            'AND worklogAuthor IN (%(authors)s)'
        ) % {
            'project': project,
            'date_from': date_from.strftime('%Y-%m-%d'),
            'date_to': date_to.strftime('%Y-%m-%d'),
            'authors': ', '.join('"%s"' % x for x in authors),
        })

        return [
            {
                'key': issue.key,
                'url': issue.permalink(),
                'title': issue.fields.summary,
            }
            for issue in issues
        ]

    def get_issue_worklogs(self, key, date_from, date_to):
        worklogs = self.jira.worklogs(key)
        return [
            {
                'author': {
                    'mail': worklog.author.key
                },
                'comment': worklog.comment,
            }
            for worklog in worklogs
            if self._worklog_at(
                worklog,
                date_from,
                date_to,
            )
        ]

    def _worklog_at(self, worklog, date_from, date_to):
        started = parser.parse(worklog.started)
        return date_from <= started.date() <= date_to
