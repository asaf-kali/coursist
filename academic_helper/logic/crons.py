from django.core import management
from django_cron import CronJobBase, Schedule

from academic_helper.utils.logger import log, wrap


class ExtendedCronJob(CronJobBase):
    code = "Default code"

    def do(self):
        log.info(f"{wrap(self.code)} cron is starting")
        self.job()
        log.info(f"{wrap(self.code)} cron is done")

    def job(self):
        raise NotImplementedError()


class BackupCron(ExtendedCronJob):
    RUN_EVERY_MINS = 720  # 12 hours
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "academic_helper.BackupCron"

    def job(self):
        management.call_command("dbbackup")
        # management.call_command("mediabackup")
