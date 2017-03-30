# coding: utf-8


class Collector(object):
    def __init__(self, jira):
        self.jira = jira

    def get_workon_issues(self, date, team):
        jql = (
            'project = TRG AND '
            'worklogDate = "%(date)s" '
            'AND timespent > 0 '
            'AND worklogAuthor IN (%(authors)s)'
        ) % {
            'date': date.strftime('%Y-%m-%d'),
            'authors': ', '.join('"%s"' % x for x in team),
        }
        issues = self.jira.search_issues(jql)

        return [{
            'key': issue.key,
            'url': issue.permalink(),
            'title': issue.fields.summary,
        } for issue in issues]

    def get_issue_worklogs(self, key):
        worklogs = self.jira.worklogs(key)
        return [{
            'author': {
                'mail': worklog.author.key
            },
            'comment': worklog.comment,
        } for worklog in worklogs]
