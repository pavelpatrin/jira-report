# coding: utf-8

import os.path
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'settings.yaml')

with open(CONFIG_PATH, 'r') as fh:
    config = yaml.load(fh)

# Jira settings
JIRA_URL = config['jira']['url']
JIRA_USER = config['jira']['user']
JIRA_PASS = config['jira']['pass']
JIRA_PROJECT = config['jira']['project']

# SMTP settings
SMTP_HOST = config['smtp']['host']
SMTP_PORT = config['smtp']['port']
SMTP_USER = config['smtp']['user']
SMTP_PASS = config['smtp']['pass']

# Mail settings
EMAIL_TITLE = config['email']['title']
EMAIL_FROM = config['email']['from']
EMAIL_TO = config['email']['to']

# Team settings
TEAM = [(x['name'], x['mail']) for x in config['team']]
