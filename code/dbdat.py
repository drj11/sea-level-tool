#!/usr/bin/env python

"""Convert hourly data from JASL archive into a table in a sqlite file.
dbdat.py jaslid
Looks for data in download/hXXXY/
"""

import os
import re
import sys
from collections import OrderedDict

import requests
import scraperwiki

DAT_DIR = "download/%s"

def check_input():
    if not os.path.exists(DAT_DIR):
        sys.stderr.write("Missing directory: %s\nTry running code/unpack\n" %
          DAT_DIR)

def scrape(jaslid):
    import glob
    statusok("Processing station %s" % jaslid)
    scraperwiki.sqlite.execute("DROP TABLE IF EXISTS obs")
    tosave = []
    for fn in glob.glob("%s/*.dat" % DAT_DIR):
        with open(fn) as f:
            scrape1(f, jaslid)

def scrape1(f, jaslid):
    """Scrape 1 .dat file (from the JASL)."""
    # First line is some sort of header; ignore it.
    f.readline()
    tosave = []
    for row in f:
        l = fixie('4 5 9' + (12*' 4'), row)
        date = l[2][:8]
        pm = int(l[2][8])
        for h,v in enumerate(l[3:]):
            if v == '9999':
                continue
            d = OrderedDict()
            pmadj = 12 if pm > 1 else 0
            d['jaslid'] = jaslid
            d['t'] = "%sT%02d00" % (date, h+pmadj)
            d['z'] = int(v)
            tosave.append(d)
    scraperwiki.sqlite.save(['jaslid', 't'], tosave, table_name='obs')
    statusok("Data file %s has been saved" % f.name)

def statusok(message=None):
    """Post a status message, if on a scraperwiki server. If not
    on a scraperwiki server, write the message to stdout."""
    if not os.path.exists(os.path.join(os.environ['HOME'], "box.json")):
        sys.stdout.write(message + '\n')
    d = { type: 'ok' }
    if message is not None:
        d['message'] = message
        return
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
    global DAT_DIR
    import sys
    if argv is None:
        argv = sys.argv
    arg = argv[1:]

    jaslid = "h" + arg[0]
    DAT_DIR %= jaslid
    check_input()
    scrape(jaslid)

if __name__ == '__main__':
    main()
