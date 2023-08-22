#!/bin/bash

source /usr/lib/zabbix/alertscripts/.venv/bin/activate
python /usr/lib/zabbix/alertscripts/send_to_bot.py "$@"

