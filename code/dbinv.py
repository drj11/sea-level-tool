#!/usr/bin/env python

"""Convert a downloaded inventry.lst into a sqlite file."""

import os
import sys

import scraperwiki

INV_PATH = 'inventry.lst' # Note: 8.3 filename

def check_input():
    if not os.path.exists(INV_PATH):
        sys.stderr.write("Missing file: %s\nTry running code/getinv\n",
          INV_PATH)

def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv
    check_input()

if __name__ == '__main__':
    main()
