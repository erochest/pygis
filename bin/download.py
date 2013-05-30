#!/usr/bin/env python


from contextlib import closing
import ftplib
import glob
import gzip
import os
import re
import tarfile


HOST     = 'ftp.ncdc.noaa.gov'
PATH     = '/pub/data/gsod/'
YEAR     = re.compile(r'\d{4}')
DOWNLOAD = 'tars'
DATADIR  = 'data'


def download(host, path, year_filter, target):
    """This downloads the files into the target directory. """
    if not os.path.exists(target):
        os.makedirs(target)

    with closing(ftplib.FTP(host)) as ftp:
        ftp.login()
        ftp.cwd(path)

        for dirname in ftp.nlst():
            if year_filter(dirname):
                src  = '%s/gsod_%s.tar' % (dirname, dirname)
                dest = os.path.join(target, 'gsod_%s.tar' % (dirname,))
                print('%s => %s' % (src, dest))

                with open(dest, 'wb') as f:
                    ftp.retrbinary('RETR ' + src, f.write)


def untar(input_file, dest):
    """This untars the file into the directory given."""
    with closing(tarfile.open(input_file, 'r')) as tf:
        tf.extractall(dest)


def ungzip(input_file):
    """This un-gzips the input file and deletes the original."""
    dest = os.path.splitext(input_file)[0]
    print('%s => %s' % (input_file, dest))

    with closing(gzip.open(input_file, 'rb')) as zf:
        with closing(open(dest, 'wb')) as fout:
            fout.write(zf.read())

    os.remove(input_file)


def main():
    download(HOST, PATH, YEAR.match, DOWNLOAD)
    for fn in glob.glob(os.path.join(DOWNLOAD, '*.tar')):
        untar(fn, DATADIR)
    for fn in glob.glob(os.path.join(DATADIR, '*.gz')):
        ungzip(fn)
    print('done.')


if __name__ == '__main__':
    main()
