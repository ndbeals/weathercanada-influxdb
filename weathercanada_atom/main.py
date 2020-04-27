import sys
import asyncio

from db import pgdb, tsdb
from job import RecurringJob, register_job, run_jobs
from weathercan import WeatherReport

from config import config, logger

RUN_INT = 3.37

import time
async def weather_report(conf):
    rep = WeatherReport(conf['url'],{
        "tags": {
            "region": conf.get('region','')
        },
    })
    logger.success(f'Got "{conf["name"]:18}" report. temp: {rep.temperature}')

    return True


# job_classes = {
#     'RecurringWeatherJob': {
        
#     }
# }

class JobLoader():
    def RecurringWeatherJob( conf ):
        job = RecurringJob( conf['interval'], weather_report, conf )

    @staticmethod
    def load_job_type( job_type, conf ):
        try:
            job_loader = JobLoader.__getattribute__(JobLoader, job_type )
        except AttributeError as ex:
            return False
        
        job_loader( conf )

        return True

async def load_jobs():
    for job in config['jobs']:
        job_type = list(job)[0]
        success = JobLoader.load_job_type( job_type, job[job_type] )
        if success:
            logger.success(f'Loaded job: "{job[job_type]}" of type "{job_type}"')


async def main_loop():
    loop = True

    await load_jobs()

    while loop:
        # tasks = asyncio.create_task( run_jobs() )
        await run_jobs()

        await asyncio.sleep(config['general']['update_interval'])


async def shutdown(main_task=None):
    for task in asyncio.all_tasks():  
        if task == asyncio.current_task():
            continue      
        try:
            # pass
            task.cancel()
            try:
                print("task ex: ",task.exception())
            except Exception as ex:
                pass
        except Exception as ex:
            logger.error("Task failed to cancel {}",ex)
        finally:
            logger.success(f'Finished cleanup, exiting')


def main():
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt as ex:
        print()
        logger.warning(f'Caught Ctrl-C, exiting gracefully.')
        asyncio.run(shutdown())
        sys.exit(0)


if __name__ == "__main__":
    main()
