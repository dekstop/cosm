# Power-law fitting for histograms.
#

import argparse
import csv
import os.path
import sys

from plfit import plfit
from plfit import plpva
from plfit import plvar

# ========
# = Main =
# ========

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Calculate power-law stats.')
    parser.add_argument('filename', help='TSV histogram data of (tag, count)')
    # parser.add_argument('outfilename', help='report filename')
    parser.add_argument('-n', '--no-plfit', dest='noplfit', action='store_true', 
        default=False, help='don\'t run plfit')
    parser.add_argument('-2', '--plpva', dest='plpva', action='store_true', 
        default=False, help='run plpva (this is very slow.)')
    parser.add_argument('-3', '--plvar', dest='plvar', action='store_true', 
        default=False, help='run plvar (this is very slow.)')
    parser.add_argument('-s', '--sample', dest='samples', action='store', type=int,
        default=None, help='take n samples')
    parser.add_argument('-r', '--reps', dest='reps', action='store', type=int,
        default=None, help='number of iterations')
    args = parser.parse_args()
    
    if (os.path.isfile(args.filename)==False):
        print "File doesn't exist: %s" % (args.filename)
        sys.exit(1)
    
    plfargs = []
    if args.samples > 0:
        plfargs = plfargs + ['sample', args.samples]
    if args.reps is not None:
        plfargs = plfargs + ['reps', args.reps]

    # Load
    data = []
    reader = csv.reader(open(args.filename, 'rb'), delimiter='	', quoting=csv.QUOTE_NONE)
    for rec in reader:
        val = int(rec[1])
        data.append(val)

    # Prepare data
    data.sort(reverse=True)
    maxcount = max(data)

    print "%d items, max count is %d" % (len(data), maxcount)
    
    # Power-law test
    if args.noplfit==False:
        print 'Estimating parameters for power-law distribution...'
        # This is quite slow.
        alpha, xmin, L = plfit.plfit(data, *plfargs)
        print "alpha = %f xmin = %d L = %f" % (alpha, xmin, L)

    if args.plvar:
        print 'Estimating the uncertainty in the estimated power-law parameters...'
        # This is really slow.
        alpha, xmin, ntail = plvar.plvar(data, *plfargs)
        print "alpha = %f xmin = %d ntail = %f" % (alpha, xmin, ntail)

    if args.plpva:
        # This is really slow.
        print 'Calculating p-value and goodness-of-fitpower-law...'
        p, gof = plpva.plpva(data, xmin, *plfargs)
        print "p = %f gof = %f" % (p, gof)
