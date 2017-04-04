# coding: utf-8

import datetime
import jira
import settings
import collector
import reporter
import sender


def report():
    # Дата формирования отчёта - вчера
    report_date = datetime.date.today() - datetime.timedelta(days=settings.DAY_DELTA)
    date_title = report_date.strftime('%Y-%m-%d')

    jira_client = jira.JIRA(settings.JIRA_URL, basic_auth=(
        settings.JIRA_USER,
        settings.JIRA_PASS
    ))

    # Получение задач, учавствовавших в work-логах
    jira_collector = collector.Collector(jira_client)
    jira_authors = [x[1] for x in settings.TEAM]
    workon_issues = jira_collector.get_workon_issues(
        settings.JIRA_PROJECT,
        jira_authors,
        report_date,
    )

    # Получение work-логов по найденным задачам
    team_worklogs = {}
    for issue in workon_issues:
        issue_key = issue['key']

        # Получение work-логов по задаче на дату
        worklogs = jira_collector.get_issue_worklogs(
            issue_key,
            report_date
        )

        for worklog in worklogs:
            # Группировка work-логов автора
            author_mail = worklog['author']['mail']
            author_worklogs = team_worklogs.setdefault(author_mail, {})

            # Группировка work-логов автора по задаче
            issue_worklogs = author_worklogs.setdefault(issue_key, {
                'issue': issue,
                'comments': [],
            })

            # Группа коментариев к work-логам автора к задаче
            issue_worklogs['comments'].append(worklog['comment'])

    # Составление отчёта о проделанной работе
    html_reporter = reporter.Reporter()
    html_result = html_reporter.render(
        settings.TEAM,
        team_worklogs
    )

    # Отправка составленного отчета
    result_sender = sender.Sender(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        settings.SMTP_USER,
        settings.SMTP_PASS,
    )
    result_sender.send(
        settings.EMAIL_TITLE % date_title,
        settings.EMAIL_FROM,
        settings.EMAIL_TO,
        html_result,
    )
