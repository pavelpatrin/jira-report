# coding: utf-8

import datetime
import argparse
import jira
import settings
import collector
import reporter
import sender


def delta_to_date(delta):
    delta = datetime.timedelta(days=int(delta))
    today = datetime.date.today()
    return today - delta


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--days-from', required=True, dest='date_from', type=delta_to_date)
    parser.add_argument('--days-to', required=True, dest='date_to', type=delta_to_date)
    return parser.parse_args()


def report():
    # Даты формирования отчёта
    arguments = parse_args()
    date_from = arguments.date_from
    date_to = arguments.date_to
    dates_title = '%s - %s' % (
        date_from.strftime('%Y-%m-%d'),
        date_to.strftime('%Y-%m-%d'),
    )

    # Инициализация работы с Jira
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
        date_from,
        date_to,
    )

    # Получение work-логов по найденным задачам
    team_worklogs = {}
    for issue in workon_issues:
        issue_key = issue['key']

        # Получение work-логов по задаче на дату
        worklogs = jira_collector.get_issue_worklogs(
            issue_key,
            date_from,
            date_to,
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
        settings.EMAIL_TITLE % dates_title,
        settings.EMAIL_FROM,
        settings.EMAIL_TO,
        html_result,
    )
