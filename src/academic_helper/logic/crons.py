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
    schedule = Schedule(run_at_times=["04:00"])
    code = "academic_helper.BackupCron"

    def job(self):
        management.call_command("dbbackup")
        # management.call_command("mediabackup")
