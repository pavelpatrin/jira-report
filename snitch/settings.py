import yaml
import collections


class Settings:
    def __init__(self, settings):
        # Jira settings.
        self.JIRA_URL = settings['jira']['url']
        self.JIRA_USER = settings['jira']['user']
        self.JIRA_PASS = settings['jira']['pass']

        # SMTP settings.
        self.SMTP_HOST = settings['smtp']['host']
        self.SMTP_PORT = settings['smtp']['port']
        self.SMTP_USER = settings['smtp']['user']
        self.SMTP_PASS = settings['smtp']['pass']

        # Mail settings.
        self.EMAIL_TITLE = settings['email']['title']
        self.EMAIL_FROM = settings['email']['from']
        self.EMAIL_TO = settings['email']['to']

        # Language settings.
        self.LANGUAGE = settings['language']

        # Collection settings.
        self.PROJECTS = collections.OrderedDict([
            (x['project'], x['title'])
            for x in settings['projects']
        ])
        self.ACCOUNTS = collections.OrderedDict([
            (x['account'], x['title'])
            for x in settings['accounts']
        ])

    @classmethod
    def load(cls, settings_path):
        with open(settings_path) as fh:
            return cls(yaml.load(fh))
