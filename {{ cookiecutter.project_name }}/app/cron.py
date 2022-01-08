import logging

import aiocron

logger = logging.getLogger('Cron')


@aiocron.crontab('*/1 * * * *', start=False)
async def test_cron_task():
    logger.info("Executing test_cron_task")


def initialize():
    logger.info("Start launching tasks")
    logger.info("Launch test_cron_task")
    test_cron_task.start()
    logger.info("Stop launching tasks")
