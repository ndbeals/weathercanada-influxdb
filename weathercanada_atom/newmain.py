import sys
import asyncio

from db import tsdb
from job import RecurringJob, register_job, run_jobs
from weathercan import WeatherReport, WeatherReportEntry

from config import config, logger
import time
TICK_SLEEP=0.5

async def weather_report(conf):
    rep = WeatherReport(conf['url'],{
        "tags": {
            "region": conf.get('region','')
        },
    })
    logger.success(f'Got "{conf["name"]:18}" report. temp: {rep.temperature}')

    return True


import feed
async def weather_main(config):
    # print("DONE: ",4)
    feeds = feed.feed_list()
    # print("DONE: ",feeds)

    read_data = await feed.async_parse_list( feeds, config.get('time_between', 0) )

    for (conf, data) in read_data:
        # report = WeatherReport(conf['url'],{"tags":{"region": conf.get('region', '')}})
        # report.feed_url = conf['url']
        # report.feed_data = data
        # report.parse_data()

        for entry in data['entries']:
            extra_data = {
                "tags": conf
            }
            weather_entry = WeatherReportEntry( entry, extra_data)

        # logger.success(f'Got "{conf["name"]:18}" report. temp: {rep.temperature}')


tasks = []
async def main_loop():
    loop = True

    # await load_jobs()
    
    weather_task = RecurringJob(config['weather']['update_interval'], weather_main, config['weather'] )
    print("weather task : ", weather_task)

    tasks.append(weather_task)

    while loop:
        for task in tasks:
            if task.task.done():
                print("task done ",task)
                tasks.remove(task)
            
        await asyncio.sleep(TICK_SLEEP)
        # tasks = asyncio.create_task( run_jobs() )
        # await run_jobs()

        # await asyncio.sleep(config['general']['update_interval'])


# async def shutdown(main_task=None):
#     for task in asyncio.all_tasks():  
#         if task == asyncio.current_task():
#             continue      
#         try:
#             # pass
#             task.cancel()
#             try:
#                 print("shutdowN: task ex: ",task.exception())
#             except Exception as ex:
#                 pass
#         except Exception as ex:
#             logger.error("Task failed to cancel {}",ex)
#         finally:
#             logger.success(f'Finished cleanup, exiting')


def main():
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt as ex:
        print()
        logger.warning(f'Caught Ctrl-C, exiting gracefully.')
        # asyncio.run(shutdown())
        sys.exit(0)


if __name__ == "__main__":
    main()
