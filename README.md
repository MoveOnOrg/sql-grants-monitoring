# About

SQL Grants Monitoring is a Python 3 script that checks if a given user can access a given list of tables. The idea is to monitor that tables that should not be accessible are, in fact, not accessible. If the listed tables are accessible, notifications are sent via Slack.

# Install

1) Download Git repo
2) From within Python 3 environment ...
3) $ `pip install -t vendored/ -r requirements.txt`

# Configure

1) $ `cp settings.py.template settings.py`
2) Add database and Slack connection settings to settings.py

# Deploy

1) Set AWS credentials in ~/.aws/credentials
2) From within Node 4+ environment ....
3) $ `npm install -g serverless@1.20.2` (**NOTE**: this is a specific version because newer versions currently package psychopg2 in a corrupt state)
4) $ `npm install`
5) $ `serverless deploy`

# More Options

In addition to `settings.py`, configuration can also happen via command line flags or Amazon Lambda events. All configuration options use the same name in any context. Run `python sql_grants_monitoring.py --help` for a full list of config options.

If deploying with Serverless, you may also want to change the timing of your checks in `serverless.yml`.
