import argparse
import datetime


def delta_to_date(delta):
    delta = datetime.timedelta(days=int(delta))
    today = datetime.date.today()
    return today - delta


class Main(object):
    def __init__(self):
        self.arguments = self.parse_args()

        from .settings import Settings
        from .collector import Collector
        from .reporter import Reporter
        from .sender import Sender

        self.settings = Settings.load(
            self.arguments.settings_path,
        )
        self.collector = Collector(
            self.settings.JIRA_URL,
            basic_auth=(
                self.settings.JIRA_USER,
                self.settings.JIRA_PASS,
            )
        )
        self.reporter = Reporter(
            self.settings.LANGUAGE,
        )
        self.sender = Sender(
            self.settings.SMTP_HOST,
            self.settings.SMTP_PORT,
            self.settings.SMTP_USER,
            self.settings.SMTP_PASS,
        )

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--settings',
            default='settings.yaml',
            dest='settings_path',
            type=str,
        )
        parser.add_argument(
            '--days-from',
            required=True,
            dest='date_from',
            type=delta_to_date,
        )
        parser.add_argument(
            '--days-to',
            required=True,
            dest='date_to',
            type=delta_to_date,
        )
        parser.add_argument(
            '--print-report',
            default=False,
            dest='print_report',
            action='store_true',
        )
        parser.add_argument(
            '--email-report',
            default=False,
            dest='email_report',
            action='store_true',
        )
        return parser.parse_args()

    def main(self):
        history = self.collector.collect(
            self.settings.ACCOUNTS.keys(),
            self.settings.PROJECTS.keys(),
            self.arguments.date_from,
            self.arguments.date_to,
        )

        report = self.reporter.report(
            self.settings.JIRA_URL,
            self.settings.PROJECTS,
            self.settings.ACCOUNTS,
            history,
        )

        title = self.settings.EMAIL_TITLE % {
            'date_from': self.arguments.date_from.strftime('%Y-%m-%d'),
            'date_to': self.arguments.date_to.strftime('%Y-%m-%d'),
        }

        if self.arguments.print_report:
            print(title, report)

        if self.arguments.email_report:
            self.sender.send(
                self.settings.EMAIL_FROM,
                self.settings.EMAIL_TO,
                title, report,
            )


if __name__ == '__main__':
    try:
        Main().main()
    except Exception:
        import sys
        import ipdb

        etype, evalue, traceback = sys.exc_info()
        ipdb.post_mortem(traceback)
