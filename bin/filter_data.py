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


IshHistory = namedtuple(
    'IshHistory',
    '''
    usaf wban station_name country fips state call lat lon elevation begin
    end
    '''
    )


def read_history(fn):
    """This reads the ish-history.csv file into a sequence of named tuples. """
    with open(fn, 'rb') as f:
        for row in itertools.islice(csv.reader(f), 1, None):
            yield IshHistory._make(row)


def get_stations(history, country):
    """\
    This takes a seq of IshHistory objects and returns a set of stations
    for the country and state.

    """

    stations = set(
        (h.usaf, h.wban)
        for h in history
        if h.country == country
        )
    return stations


def main():
    history = read_history(HISTORY)
    stations = get_stations(history, COUNTRY)

    if not os.path.exists(COUNTRY):
        os.makedirs(COUNTRY)

    for fn in glob.glob(os.path.join(DATADIR, '*.op')):
        basename = os.path.basename(fn)
        station = tuple(basename.split('-')[:2])
        if station in stations:
            shutil.copyfile(fn, os.path.join(COUNTRY, basename))


if __name__ == '__main__':
    main()
