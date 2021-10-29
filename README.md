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

With a filled out copy of `zappa_settings.json` the AWS Lambda deploy command is just `zappa deploy prod` for initial deploy and `zappa update prod` for subsequent deploys.

# More Options

In addition to `settings.py`, configuration can also happen via command line flags or Amazon Lambda events. All configuration options use the same name in any context. Run `python sql_grants_monitoring.py --help` for a full list of config options.
