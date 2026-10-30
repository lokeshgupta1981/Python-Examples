"""Run report.py every Monday at 07:00 for the ISO week that ended on Sunday.

Usage: python schedule_report.py          # keep running
       python schedule_report.py --next   # print the next five fire times and exit
"""
import subprocess
import sys
from datetime import date, datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

TRIGGER = CronTrigger(day_of_week="mon", hour=7, minute=0)


def last_week(today=None):
    year, week, _ = ((today or date.today()) - timedelta(days=7)).isocalendar()
    return f"{year}-W{week:02d}"


def run_report():
    subprocess.run([sys.executable, "report.py", "--week", last_week()], check=False)


def next_fire_times(count=5):
    times, previous = [], None
    now = datetime.now(TRIGGER.timezone)
    for _ in range(count):
        previous = TRIGGER.get_next_fire_time(previous, previous or now)
        times.append(previous)
        previous = previous + timedelta(seconds=1)
    return times


if __name__ == "__main__":
    if "--next" in sys.argv:
        for t in next_fire_times():
            print(t.isoformat(), "->", last_week(t.date()))
    else:
        scheduler = BlockingScheduler()
        scheduler.add_job(run_report, TRIGGER)
        scheduler.start()
