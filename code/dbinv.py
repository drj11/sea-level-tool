#!/usr/bin/env python

"""Convert a downloaded inventry.lst into a sqlite file."""

import os
import re
import sys

import scraperwiki

INV_PATH = 'inventry.lst' # Note: 8.3 filename

def check_input():
    if not os.path.exists(INV_PATH):
        sys.stderr.write("Missing file: %s\nTry running code/getinv\n",
          INV_PATH)

def scrape():
    ocean = None
    jasl = None
    tosave = []
    with open(INV_PATH) as f:
      for row in f:
        # Set ocean from a matching line, if possible
        m = re.match(r'^\s+GENERAL\sINFORMATION.*\s+(\w+)\s+Ocean', row)
        if m:
            ocean = m.group(1)
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
        d = {}
        l = fixie('4 4 4 17 17 6 7 9 3 23', row)
        (d['jaslid'], d['toga'], d['glos'], d['station'], d['country'],
         d['lat'],  d['lon'], d['qcyears'], d['ci'], d['contributor']
        ) = l
        tosave.append(d)
    scraperwiki.sqlite.save(['jaslid'], tosave, table_name='inventory')

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
