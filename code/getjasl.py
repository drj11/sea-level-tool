#!/usr/bin/env python

"""
python getjasl.py [atlantic|pacific] stationid
Get hourly sea level data from JASL for a particular station.
You must already know the JASL identifier
"""

import datetime
import os

import scraperwiki

def usage(out):
    out.write(__doc__.split('\n')[0] + '\n')

def main(argv=None):
    import sys

    if argv is None:
        argv = sys.argv
    arg = argv[1:]
    if len(arg) < 2:
        usage(sys.stderr.write)
        sys.exit(4)

    ocean = arg[0]
    id = arg[1]

    url = "ftp://ilikai.soest.hawaii.edu"
    filename = "h%s.zip" % id
    url += "/rqds/%s/hourly/%s" % (ocean, filename)

    os.system("curl -O %s" % url)
    scraperwiki.sqlite.save([],
      dict(time=datetime.datetime.now().isoformat(),
        verb='GET',
        location=url), table_name='action')

if __name__ == '__main__':
    main()
