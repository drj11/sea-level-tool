#!/usr/bin/env python

"""Convert a downloaded inventry.lst into a sqlite file."""

import os
import re
import sys
from collections import OrderedDict

import requests
import scraperwiki

INV_PATH = 'inventry.lst' # Note: 8.3 filename

def check_input():
    if not os.path.exists(INV_PATH):
        sys.stderr.write("Missing file: %s\nTry running code/getinv\n",
          INV_PATH)

def treat_lat(l):
    """Convert to decimal degrees, positive North. Typical input is
    "00-32S"."""

    assert l[2] == '-'
    assert l[5] in 'SN'

    return treat_latlon(l)

def treat_latlon(s):
    """Treat either lat or lon."""

    l = s.split('-')

    d = float(l[0])
    m = float(l[1][:-1])
    d += m/60.0
    if l[1][-1] in 'WS':
	d = -d
    return d

def treat_lon(l):
    """Convert to decimal degrees, positive East. Typical input is
    "158-14E"."""

    assert l[3] == '-'
    assert l[6] in 'EW'

    return treat_latlon(l)

def ocean_colour(ocean):
    """Pick a colour."""

    d = dict(atlantic='dd0022', pacific='0000cc', indian='ccffdd')
    return d.get(ocean, '555555')

def scrape():
    statusok("Processing station list")
    ocean = None
    jasl = None
    tosave = []
    with open(INV_PATH) as f:
      for row in f:
        # Set ocean from a matching line, if possible
        m = re.match(r'^\s+GENERAL\sINFORMATION.*\s+(\w+)\s+Ocean', row)
        if m:
            ocean = m.group(1).lower()
        # The data begins just after a line starting JASL, so detect that
        if not jasl:
            jasl = re.match(r'^JASL', row)
            if jasl: continue
        # Data ends with a blank line
        if re.match(r'^\s*$', row):
            jasl = False
        if not jasl:
            continue
        # We're between a line starting JASL and a blank line, must
        # be useful data.
        d = OrderedDict()
        # dummy assigments to set the ordering in the dict.
        d['jaslid'] = None
        d['ocean'] = None
        l = fixie('4 4 4 17 17 6 7 9 3 23', row)
        (d['jaslid'], d['toga'], d['glos'], d['station'], d['country'],
         d['lat'],  d['lon'], d['qcyears'], d['ci'], d['contributor']
        ) = l
        d['ocean'] = ocean
        d['lat'] = treat_lat(d['lat'])
        d['lon'] = treat_lon(d['lon'])
        d['colour'] = ocean_colour(ocean)
        tosave.append(d)
    scraperwiki.sqlite.save(['jaslid'], tosave, table_name='inventory')
    statusok("Station list has been saved")

def statusok(message=None):
    """Post a status message, if on a scraperwiki server."""
    if not os.path.exists(os.path.join(os.environ['HOME'], "box.json")):
        return
    d = { type: 'ok' }
    if message is not None:
        d['message'] = message
    requests.post("http://x.scraperwiki.com/api/status", d)

def fixie(fmt, row):
    """Parse columns out of a fixie format row."""
    res = []
    c = 0
    while fmt:
        m = re.match(r'^[0-9]+', fmt)
        if m:
            i = int(m.group())
            res.append(row[c:c+i])
            fmt = fmt[len(m.group()):]
            c += i
        elif fmt[0] == ' ':
            c += 1
            fmt = fmt[1:]
    return res

def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv
    check_input()
    scrape()

if __name__ == '__main__':
    main()
