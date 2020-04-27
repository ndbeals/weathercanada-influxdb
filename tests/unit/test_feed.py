import asyncio

import feed

feed_list = [
    {'url':'https://weather.gc.ca/rss/city/on-149_e.xml'},
    {'url':'https://weather.gc.ca/rss/city/on-117_e.xml'}
]

def test_parse():
    assert feed.parse('https://weather.gc.ca/rss/city/on-149_e.xml') != None

def test_feed_list():
    assert len(feed.feed_list())>-1

def test_feed_parse_list():
    data = feed.parse_list(feed_list)
    assert len(data) > 1
    assert data[0][1]['feed']['id'] and data[0][1]['entries']


async def _testasyncparse():
    return await feed.async_parse_list(feed_list,0.1)
def test_feed_async_parse_list():
    data = asyncio.run(_testasyncparse())
    assert len(data) > 1
    assert data[0][1]['feed']['id'] and data[0][1]['entries']
