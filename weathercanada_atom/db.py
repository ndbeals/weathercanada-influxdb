from influxdb import InfluxDBClient

tsdb = InfluxDBClient('192.168.0.11', 8086, 'root', 'root', 'weather_data')
tsdb.create_database('weather_data')

import asyncio
import asyncpg

async def init_datastores():
    global pgdb
    pgdb = await asyncpg.create_pool(database='postgres',
                                            user='postgres', password='development')

loop = asyncio.get_event_loop()
loop.run_until_complete(init_datastores())
# async def run():
#     conn = await asyncpg.connect(user='user', password='password',
#                                  database='database', host='127.0.0.1')
#     values = await conn.fetch('''SELECT * FROM mytable''')
#     await conn.close()
