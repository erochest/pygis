#!/usr/bin/env python


from collections import namedtuple
import csv
import glob
import itertools
import os
import shutil


DATADIR = 'data'
HISTORY = 'ish-history.csv'

# This is from ftp://ftp.ncdc.noaa.gov/pub/data/gsod/country-list.txt
COUNTRY = 'US'
STATE   = 'VA'


IshHistory = namedtuple(
        'IshHistory',
        '''
        usaf wban station_name country fips state call lat lon elevation begin
        end
        '''
        )

WeatherRow = namedtuple(
        'WeatherRow',
        '''
        station wban year month_day temp count dewp dewp_count slp slp_count
        stp stp_count visibility vis_count wdsp wdsp_count max_wind_spd
        max_gust max_temp max_from_hourly min_temp min_from_hourly
        precipitation precip_source snow_depth rfshtt
        '''
        )


def csv_tuples(fn, tuple_class):
    """This reads the CSV file into tuple_class, skipping the front row. """
    with open(fn, 'rb') as f:
        for row in itertools.islice(csv.reader(f), 1, None):
            yield tuple_class._make(row)


def read_history(fn):
    """This reads the ish-history.csv file into a sequence of named tuples. """
    return csv_tuples(fn, IshHistory)


def read_weather_data(fn):
    """This reads data files into a sequence of WeatherRow instances. """
    return csv_tuples(fn, WeatherRow)


def get_stations(history, country, state):
    """\
    This takes a seq of IshHistory objects and returns a set of stations
    for the country and state.

    """

    stations = set()
    for h in history:
        if h.country == country and h.state == state:
            stations.add(h.usaf)
    return stations


def main():
    history  = read_history(HISTORY)
    stations = get_stations(history, COUNTRY, STATE)

    if not os.path.exists(STATE):
        os.makedirs(STATE)

    for fn in glob.glob(os.path.join(DATADIR, '*.op')):
        basename = os.path.basename(fn)
        station  = basename.split('-')[0]
        if station in stations:
            shutil.copyfile(fn, os.path.join(STATE, basename))


if __name__ == '__main__':
    main()
