import asyncio
import sys
import time
from time import time as scalar_time
import datetime

jobs = []

def register_job(job):
    jobs.append(job)

async def run_jobs():
    for job in jobs:
        task = asyncio.create_task( job.run() )


class Job():
    def __init__(self, func, func_args=[],register=True):
        super().__init__()
        self.func_args = func_args
        self.func=func
        self._did_execute = False

        if register:
            register_job(self)

    async def run(self, *args, **kwargs):
        try:
        	results = await self.func( self.func_args )
        	return results
        except Exception as ex:
            print(f"Task ex caught: {ex}\n {self.func_args}")
        finally:
            pass


    def runSync(self):
        pass

    def did_execute(self):
        return self._did_execute


class TimedJob(Job):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_run_time = 0
        self.create_time = scalar_time()

    async def run(self, *args, **kwargs):
        if scalar_time() >= self.next_run_time:
            await super().run(*args, **kwargs)
            self._did_execute = True
        else:
            self._did_execute = False


class RecurringJob(TimedJob):
    def __init__(self, interval=1, *args, register=False, **kwargs):
        super().__init__(register=register, *args, **kwargs)
        self.next_run_time = time.time()
        self.interval = interval
        if not register:
            self.start()

    def start(self):
        try:
            self.task = asyncio.create_task( self.loop_recurring_job() )
            self._running = True
        except KeyboardInterrupt as ex:
            print(f'Caught quit on Job, odd.')
            self.task.cancel()
            try:
                task.exception()
            except Exception as ex:
                pass

    async def loop_recurring_job(self):
        while self._running:
            await self.run()

            diff = 0.96 * (self.next_run_time - scalar_time())
            await asyncio.sleep(diff)

        return True # True means it finished successfully

    async def run(self, *args, **kwargs):
        prior_time = scalar_time()
        await super().run(self, *args, **kwargs)
        if self.did_execute():
            self.next_run_time += self.interval

