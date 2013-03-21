#!/usr/bin/env python

"""
python getjasl.py [--ocean atlantic|indian|pacific] stationid
Get hourly sea level data from JASL for a particular station.
You must already know the JASL identifier
"""

import datetime
import os

import scraperwiki

class Error(Exception):
    """Some sort of error."""

def usage(out):
    out.write(__doc__.split('\n')[1] + '\n')

def main(argv=None):
    import getopt
    import sys

    if argv is None:
        argv = sys.argv
    ocean = None
    opts,arg = getopt.getopt(argv[1:], '', ['ocean='])
    for o,v in opts:
        if o == '--ocean':
          ocean = v
    if len(arg) < 1:
        usage(sys.stderr)
        sys.exit(4)

    id = arg[0]
    if ocean is None:
        ocean = oceanFromStation(id)

    url = "ftp://ilikai.soest.hawaii.edu"
    filename = "h%s.zip" % id
    url += "/rqds/%s/hourly/%s" % (ocean, filename)

    os.system("curl -O %s" % url)
    scraperwiki.sqlite.save([],
      dict(time=datetime.datetime.now().isoformat(),
        verb='GET',
        location=url), table_name='action')

def oceanFromStation(jaslid):
    """Derive the ocean from the JASL station ID by
    database lookup.
    """
    rows = scraperwiki.sqlite.select(
      "ocean from inventory where lower(jaslid) == ?",
      [jaslid])
    if not rows:
        raise Error("Can't find station %r" % jaslid)
    ocean = rows[0]['ocean']
    return ocean

if __name__ == '__main__':
    main()
