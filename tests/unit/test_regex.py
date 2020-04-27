# content of test_sysexit.py
import pytest

import weathercan




def test_imported():
    assert weathercan != None


weather_result_tmpl = '<b>Observed at:</b> Oshawa Executive Airport 10:00 AM EDT Tuesday 21 April 2020 <br/>\n<b>Condition:</b> Mainly Sunny <br/>\n<b>Temperature:</b> {}&deg;C <br/>\n<b>Pressure:</b> {} kPa <br/>\n<b>Visibility:</b> {} km<br/>\n<b>Humidity:</b> {} %<br/>\n<b>Dewpoint:</b> {}&deg;C <br/>\n<b>Wind:</b> NW {} km/h gust {} km/h<br/>\n<b>Air Quality Health Index:</b> {} <br/>'

test_vals =[
    (40.0,120.0,100.0,100,40,100,200,10),
    (-40.0,20,0,0,-40,0,0,0),
    (-40.0,20,'unlimited',0,-40,0,0,0),
]
def weather_regex( inp , num_groups ):
    match = weathercan.MATCH_CURRENT_CONDITIONS.search(inp)
    return match != None and len(match.groups())==num_groups

def test_regex():
    for test in test_vals:
        res = weather_result_tmpl.format(*test)
        assert weather_regex(res, 11)