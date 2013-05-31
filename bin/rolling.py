#!/usr/bin/env python


from collections import defaultdict, namedtuple
import csv
import datetime
import glob
import itertools
import operator
import os

from filter_data import HISTORY, STATE, read_history


DUMP   = True
PERIOD = 30
MONTH  = 6
OUTPUT = 'climate.csv'


WeatherRow = namedtuple(
        'WeatherRow',
        '''
        station wban date temp temp_count dewp dewp_count slp slp_count stp
        stp_count visibility vis_count wdsp wdsp_count max_wind_spd max_gust
        max_temp min_temp precipitation snow_depth rfshtt
        '''
        )


AccumDict = lambda: defaultdict(list)


def log(msg):
    print('[%s] %s' % (datetime.datetime.now(), msg))


def dump(filename, fields, data):
    if DUMP:
        log('\t>>> %s' % (filename,))
        with open(filename + '.tsv', 'wb') as f:
            w = csv.writer(f, 'excel-tab')
            w.writerow(fields)
            w.writerows(data)


def read_weather(fn):
    """This reads a weather data file into a sequence of named tuples. """
    with open(fn, 'rb') as f:
        for line in itertools.islice(f, 1, None):
            row = normalize(WeatherRow._make(line.split()))
            if row is not None:
                yield row


def parse_date(year_month_day):
    """Takes a string in the format YYYYMMDD and returns a date. """
    year  = int(year_month_day[:4])
    month = int(year_month_day[4:6])
    day   = int(year_month_day[6:])
    return datetime.date(year, month, day)


def parse_temp(temp):
    """\
    This converts temperatures to floats, stripping off the trailing '*'.
    """
    temp = temp.rstrip('*')
    if temp[-1] == '*':
        temp = temp[:-1]
    return float(temp)


def normalize(row):
    """\
    This normalizes a WeatherRow instance.

    * converts the date field.

    """

    max_temp = parse_temp(row.max_temp)
    min_temp = parse_temp(row.min_temp)

    if max_temp > 9000 or min_temp > 9000:
        return None
    else:
        return row._replace(
                date=parse_date(row.date),
                max_temp=max_temp,
                min_temp=min_temp,
                )


def get_month(year_month_day):
    """Takes a string in the format YYYYMMDD and returns the int month. """
    return int(year_month_day[4:6])


def window(seq, n):
    """\
    Returns a sliding window of width n over seq.

    (Modified from old Python docs.)

    """

    it     = iter(seq)
    result = tuple(itertools.islice(it, n))
    if len(result) <= n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


get_station      = operator.attrgetter('station')
get_station_year = operator.attrgetter('station', 'wban', 'date.year')
get_date         = operator.attrgetter('date')
first            = operator.itemgetter(0)


def mean(seq):
    return sum(seq) / float(len(seq))


def read_month_data(datadir, month):
    """\
    Read in all the data, but filter out everything not in the right month.
    """
    log('read_month_data')
    weather = []

    for fn in glob.glob(os.path.join(datadir, '*.op')):
        weather += ( w for w in read_weather(fn) if w.date.month == month )

    dump('00-read-month-data', weather[0]._fields, weather)
    return weather


def get_monthly_avgs(weather):
    """\
    Sort it and index the monthly average of the max temperatures by
    station/wban.
    """
    log('get_monthly_avgs')

    month_avgs = AccumDict()

    weather.sort(key=get_station_year)
    groups = itertools.groupby(weather, get_station_year)
    for ((station, wban, year), obs_iter) in groups:
        key = (station, wban)
        avg = mean([ o.max_temp for o in obs_iter ])
        month_avgs[key].append((year, avg))

    dump('01-get-monthly-avgs', ('station', 'wban', 'year', 'avgs'),
         iter_monthly_avgs(month_avgs))
    return month_avgs


def iter_monthly_avgs(month_avgs):
    """This turns the monthly averages dict into a seq of flat tuples. """
    for ((station, wban), vals) in month_avgs.iteritems():
        for (year, avg) in vals:
            yield (station, wban, year, avg)


def get_rolling_avgs(month_avgs, period):
    """Get 30-year rolling averages by station/wban. """
    log('get_rolling_avgs')
    avgs = {}

    for (key, month_avgs) in month_avgs.iteritems():
        month_avgs.sort(key=first)
        windows = [
                (wnd[0][0], mean([ w[1] for w in wnd ]))
                for wnd in window(month_avgs, period)
                ]
        if len(windows) > 1:
            avgs[key] = windows

    dump('02-get-rolling-avgs', ('station', 'wban', 'start-year', 'rolling-avg'),
         iter_monthly_avgs(avgs))
    return avgs


def get_avg_diffs(avgs):
    """\
    Get the difference in the first and last rolling averages for each item.
    """
    log('get_avg_diffs')
    diffs = {}

    for (key, rolling_avgs) in avgs.iteritems():
        if rolling_avgs:
            diffs[key] = (
                    rolling_avgs[-1][0] - rolling_avgs[0][0],
                    rolling_avgs[-1][1] - rolling_avgs[0][1]
                    )

    dump('03-get-avg-diffs', ('station', 'wban', 'delta-year', 'delta-temp'),
         ( (s, w, d1, d2) for ((s, w), (d1, d2)) in diffs.iteritems() ))
    return diffs


def get_station_locs(history_fn):
    """Load the lat-lon data for the stations. """
    log('get_station_locs')
    history = read_history(history_fn)
    station_locs = {}

    for row in history:
        if row.lat and row.lon:
            key = (row.usaf, row.wban)
            station_locs[key] = (float(row.lat), float(row.lon))

    dump('04-get-station-locs', ('station', 'wban', 'lat', 'lon'),
         ( (s, w, lat, lon) for ((s, w), (lat, lon)) in station_locs.iteritems() ))
    return station_locs


def write_diffs(diffs, station_locs, output_fn):
    """Output new data. """
    log('write_diffs')
    with open(output_fn, 'wb') as fout:
        writer = csv.writer(fout)
        writer.writerow(('station', 'lat', 'lon', 'delta-year', 'delta-temp'))
        writer.writerows(
                output_row(d, station_locs[d[0]])
                for d in diffs.iteritems()
                if d[0] in station_locs
                )


def output_row(diff_item, lat_lon):
    """This constructs a tuple for outputting a row. """
    (key, (delta_year, delta_temp)) = diff_item
    (lat, lon) = lat_lon
    return ('%s-%s' % key, lat, lon, delta_year, delta_temp)


def main():
    start = datetime.datetime.now()

    weather      = read_month_data(STATE, MONTH)
    month_avgs   = get_monthly_avgs(weather)
    avgs         = get_rolling_avgs(month_avgs, PERIOD)
    diffs        = get_avg_diffs(avgs)
    station_locs = get_station_locs(HISTORY)
    write_diffs(diffs, station_locs, OUTPUT)

    end = datetime.datetime.now()
    log('done. elapsed time: %s' % (end-start,))


if __name__ == '__main__':
    main()
