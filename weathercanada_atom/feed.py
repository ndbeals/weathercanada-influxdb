import asyncio
import concurrent.futures

from feedparser import parse

from config import config, logger


def try_parse(url):
    try:
        return parse(url)
    except Exception as ex:
        logger.warning("Atom failed to parse url: {}", url)

def feed_list():
    return config['weather']['regions']

def parse_list( feeds ):
    data = []
    for feed in feeds:
        feed_data = try_parse( feed.get('url','') )
        if feed_data:
            data.append( (feed, feed_data) )
    
    return data

async def async_parse_list( feeds, wait_between=0 ):
    loop = asyncio.get_running_loop()
    data = []
    for feed in feeds:
        # feed_data = await loop.run_in_executor(None, try_parse, feed.get('url', '') )
        feed_data = try_parse( feed.get('url','') )
        if feed_data:
            data.append( (feed, feed_data))
            
        await asyncio.sleep( wait_between )

    return data
