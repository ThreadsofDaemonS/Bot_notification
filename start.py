#!/usr/bin/python3
# _*_ coding: utf-8 _*_

from bot_copy import notification, create_report
import schedule
import time

schedule.every().day.at("11:14").do(create_report)
schedule.every().day.at("11:15").do(notification)

while True:
    schedule.run_pending()
    time.sleep(1)

