import feedparser
import time
import re
from enum import Enum
from db import tsdb#, pgdb

from config import logger

MATCH_CURRENT_CONDITIONS = re.compile(r'.*at:.....([\w\s:]*).*\n.*Condition:.....([\w\s:]*).*\n.*Temperature[^-0-9]*(-?\d+\.?\d*).*\n.*Pressure\D*(\d+\.?\d*).*\n.*Visibility.{0,6}((?:\d+\.?\d*)|(?:\w+)).*\n.*Humidity\D*(\d+\.?\d*).*\n.*Dewpoint[^-0-9]*(-?\d+\.?\d*).*\n.*Wind.*?([A-Z]+)\s(\d+).*?\s?gust\s?(\d+).*\n.*Index\D*(\d+)',re.IGNORECASE)

class ReportEntryType(Enum):
    WARNINGS_AND_WATCHES = 1
    CURRENT_CONDITIONS = 2
    WEATHER_FORECASTS = 3

class WeatherReportEntry():
    regex = {
        "observed_at": re.compile(r'at:.{0,4}?>\s?([\w*\s?]*\w+)\s\d+',re.IGNORECASE),
        "condition": re.compile(r'Condition:.....([\w*\s?]*\w+)\s?',re.IGNORECASE),
        "temperature": re.compile(r'Temperature[^-0-9]*(-?\d+\.?\d*)',re.IGNORECASE),
        "pressure": re.compile(r'Pressure\D*(\d+\.?\d*)',re.IGNORECASE),
        "visibility": re.compile(r'Visibility.{0,6}((?:\d+\.?\d*)|(?:\w+))',re.IGNORECASE),
        "humidity": re.compile(r'Humidity\D*(\d+\.?\d*)',re.IGNORECASE),
        "dewpoint": re.compile(r'Dewpoint[^-0-9]*(-?\d+\.?\d*)',re.IGNORECASE),
        "wind": re.compile(r'Wind.*?([A-Z]+)\s(\d+).*?\s?gust\s?(\d+)',re.IGNORECASE),
        "wind_direction": re.compile(r'Wind.*?([A-Z]+)\s\d+.*?\s?',re.IGNORECASE),
        "wind_speed": re.compile(r'Wind.*?[A-Z]*\s?(\d+).*?\s?',re.IGNORECASE),
        "wind_gust": re.compile(r'Wind.*?[A-Z]+\s\d+.*?\s?gust\s?(\d+)',re.IGNORECASE),
        "air_index": re.compile(r'Index\D*(\d+)',re.IGNORECASE),
    }


    def __init__(self, data, extra_data, parent = None):
        # super().__init__()
        if data:
            self.extra_data = extra_data
            self.parse_data(data)

        if parent:
            self.parent = parent

    def parse_data(self, data):
        self.raw_data = data

        self.id = data['id']
        self.updated_at = data['updated_parsed']

        self.title = data['title']
        self.summary = data['summary']

        

        term = data['tags'][0]['term']
        if term == 'Warnings and Watches':
            self.type = ReportEntryType.WARNINGS_AND_WATCHES
        elif term == 'Current Conditions':
            self.current_conditions(data)
        elif term == 'Weather Forecasts':
            self.type = ReportEntryType.WEATHER_FORECASTS

    def try_regex(self, regex_name, search_string, transform=lambda x: x ):
        try:
            match = self.regex[regex_name].search( search_string )
            return transform(match.group(1))
        except Exception as ex:
            logger.trace('Exception in regex "{}" caught: {}', regex_name, ex)
        return None

    def current_conditions(self, data):
        self.type = ReportEntryType.CURRENT_CONDITIONS
        
        self.observed_at = self.try_regex( 'observed_at', data['summary'])
        self.condition = self.try_regex( 'condition', data['summary'], lambda x: x.lower().strip())

        self.temperature = self.try_regex( 'temperature', data['summary'], float )
        # self.parent.temperature = self.temperature
        self.pressure = self.try_regex( 'pressure', data['summary'], float )

        vis = self.try_regex( 'visibility', data['summary'] )
        if vis:
            if vis == 'unlimited':
                self.visibility = -1
            else: self.visibility = float(vis)
        else: self.visibility = None

        self.humidity = self.try_regex( 'humidity', data['summary'], float )        
        self.dewpoint = self.try_regex( 'dewpoint', data['summary'], float )    
        self.wind_direction = self.try_regex( 'wind_direction', data['summary'])    
        self.wind_speed = self.try_regex( 'wind_speed', data['summary'], float )    
        self.wind_gust = self.try_regex( 'wind_gust', data['summary'], float )    
        self.air_quality_index = self.try_regex( 'air_index', data['summary'], float )    

        # print("temp at: ",self.temperature)

        self.commit_condition_data()
    
    def commit_condition_data(self):
        fields = {
            "air_quality_index": self.air_quality_index,
            "condition": self.condition, 
            "dewpoint": self.dewpoint,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "temperature": self.temperature,
            "visibility": self.visibility,
            "wind_direction": self.wind_direction,
            "wind_speed": self.wind_speed,
            "wind_gust": self.wind_gust,
        }
        # tags = {"type":"temp"}
        tags = {}
        tags.update(self.extra_data.get("tags",{}))
        # print(tags)
        json_body = [
            {
                "measurement": "weather_data",
                "tags": self.extra_data.get("tags",{}),
                "time": time.asctime(self.updated_at),
                "fields": fields
            },
            {
                "measurement": "weather_data",
                "tags": tags,
                # "tags": {
                #     "region": "oshawa"
                # },

                "time": time.asctime(time.gmtime()),
                "fields": fields
            }
        ]
        # print(json_body)
        # tsdb.write_points(json_body, database='weather_data')
        # result = tsdb.query('select value from weather_data;',database='weather_data')
        # print("Result: {0}".format(result))

        # now = datetime.datetime.now(tz=datetime.timezone.utc)
        # hour = now.replace(minute=0,second=0,microsecond=0)
        ss = (f"""delete from "weather_data" where region='{tags['region']}' and time > '{time.strftime('%Y-%m-%dT%H:%M:%SZ',self.updated_at)}' and time < '{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}' """)
        # ss = (f"""delete from "weather_data" where time > '{time.asctime(self.updated_at)}' and time < '{(str(hour))[:-6]}' """)
        # print(ss,self.updated_at)
        tsdb.query(ss)
        # print(json_body)
        tsdb.write_points(json_body, database='weather_data')

        logger.debug(f'Region: "{tags["region"]:10}". temp: {self.temperature} C')

    # async def commit_forecast(self):
import datetime

class WeatherReport():
    def __init__(self, url, extra_data):
        super().__init__()

        if url:
            self.extra_data = extra_data
            # self.parse_feed(url)


    def parse_feed(self, url):
        self.feed_url = url
        self.feed_data = feedparser.parse(url)

        self.parse_data()
        # self.updated_at = self.feed_data['updated_parsed']
    def parse_data(self):
        self.updated_at = self.feed_data['updated_parsed']

        self.entries = []
        for entry in self.feed_data['entries']:
            parsed_entry = WeatherReportEntry(self, entry, self.extra_data)
            self.entries.append( parsed_entry )

