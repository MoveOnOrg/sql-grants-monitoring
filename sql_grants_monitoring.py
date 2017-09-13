import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "vendored"))

import psycopg2
import psycopg2.extras
import slackweb

if os.path.exists(os.path.join(BASE_DIR, 'settings.py')):
    import settings
else:
    settings = {}


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

ARG_DEFINITIONS = {
    'DB_HOST': 'Database host IP or hostname',
    'DB_PORT': 'Database port number',
    'DB_USER': 'Database user',
    'DB_PWD': 'Database password',
    'DB_NAME': 'Database name',
    'NO_SELECT': 'Comma-separated list of table names that should not have select access',
    'SLACK_WEBHOOK': 'Slack webhook URL, e.g. https://hooks.slack.com/services/...',
    'SLACK_CHANNEL': 'Slack room name for alerts, e.g. #general',
    'SLACK_USERNAME': 'Slack user name for alerts, e.g. SQL Grant Monitor',
    'SLACK_ICON': 'Slack icon for alerts, e.g. :no-entry:',
    }
REQUIRED_ARGS = [
    'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PWD', 'DB_NAME',
    'NO_SELECT', 'SLACK_WEBHOOK'
    ]
DEFAULT_ARG_VALUES = {
    'SLACK_CHANNEL': '#general',
    'SLACK_USERNAME': 'SQL Grant Monitor',
    'SLACK_ICON': ':no_entry:'
    }

def main(args):

    all_required_args_set = True

    for arg in REQUIRED_ARGS:
        if not getattr(args, arg, False):
            print('%s (%s) required, missing.' % (ARG_DEFINITIONS.get(arg), arg))
            all_required_args_set = False

    for arg in DEFAULT_ARG_VALUES:
        if not getattr(args, arg, False):
            setattr(args, arg, DEFAULT_ARG_VALUES.get(arg))

    if all_required_args_set:

        redshift = psycopg2.connect(
            host=args.DB_HOST,
            port=args.DB_PORT,
            user=args.DB_USER,
            password=args.DB_PWD,
            database=args.DB_NAME
        )
        redshift_cursor = redshift.cursor(cursor_factory=psycopg2.extras.DictCursor)

        open_tables = []
        other_error_tables = []

        for table in args.NO_SELECT.split(','):
            query = 'SELECT * FROM %s LIMIT 1' % table
            try:
                redshift_cursor.execute(query)
                open_tables.append(table)
            except psycopg2.Error as e:
                redshift.rollback()
                if e.pgcode == '42501':
                    pass
                else:
                    other_error_tables.append(table)

        slack = slackweb.Slack(url=args.SLACK_WEBHOOK)

        notification_text = False

        if len(open_tables):
            if len(other_error_tables):
                notification_text = 'The following tables have SELECT grants and should not: %s. Also, these tables raised non-access errors on SELECT: %s' % (','.join(open_tables), ','.join(other_error_tables))
            else:
                notification_text = 'The following tables have SELECT grants and should not: %s' % ','.join(open_tables)
        elif len(other_error_tables):
            notification_text = 'No open tables were found, but the following tables raised non-access errors on SELECT: %s' % ','.join(other_error_tables)

        if notification_text:
            slack.notify(text=notification_text, channel=args.SLACK_CHANNEL, username=args.SLACK_USERNAME, icon_emoji=args.SLACK_ICON)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Check table grants are set.')

    for argname, helptext in ARG_DEFINITIONS.items():
        parser.add_argument('--%s' % argname, dest=argname, help=helptext, default=getattr(settings, argname, False))

    args = parser.parse_args()
    main(args)

def aws_lambda(event, context):

    for argname, helptext in ARG_DEFINITIONS.items():
        if not event.get(argname, False):
            event[argname] = getattr(settings, argname, False)

    args = Struct(**event)
    return main(args)
