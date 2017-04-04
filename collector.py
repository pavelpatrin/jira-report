# coding: utf-8

import dateutil.parser as parser


class Collector(object):
    def __init__(self, jira):
        self.jira = jira

    def get_workon_issues(self, project, authors, date):
        jql = (
            'project = %(project)s AND '
            'worklogDate = "%(date)s" '
            'AND timespent > 0 '
            'AND worklogAuthor IN (%(authors)s)'
        ) % {
            'project': project,
            'date': date.strftime('%Y-%m-%d'),
            'authors': ', '.join('"%s"' % x for x in authors),
        }
        issues = self.jira.search_issues(jql)

        return [
            {
                'key': issue.key,
                'url': issue.permalink(),
                'title': issue.fields.summary,
            }
            for issue in issues
        ]

    def get_issue_worklogs(self, key, date):
        worklogs = self.jira.worklogs(key)
        return [
            {
                'author': {
                    'mail': worklog.author.key
                },
                'comment': worklog.comment,
            }
            for worklog in worklogs
            if self._worklog_at(worklog, date)
        ]

    def _worklog_at(self, worklog, date):
        started = parser.parse(worklog.started)
        return started.date() == date
