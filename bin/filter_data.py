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


def read_history(fn):
    """This reads the ish-history.csv file into a sequence of named tuples. """
    with open(fn, 'rb') as f:
        for row in itertools.islice(csv.reader(f), 1, None):
            yield IshHistory._make(row)


def get_stations(history, country, state):
    """\
    This takes a seq of IshHistory objects and returns a set of stations
    for the country and state.

    """

    stations = set()
    for h in history:
        if h.country == country and h.state == state:
            stations.add((h.usaf, h.wban))
    return stations


def main():
    history  = read_history(HISTORY)
    stations = get_stations(history, COUNTRY, STATE)

    if not os.path.exists(STATE):
        os.makedirs(STATE)

    for fn in glob.glob(os.path.join(DATADIR, '*.op')):
        basename = os.path.basename(fn)
        station  = tuple(basename.split('-')[:2])
        if station in stations:
            shutil.copyfile(fn, os.path.join(STATE, basename))


if __name__ == '__main__':
    main()
