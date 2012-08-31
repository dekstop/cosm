# Sparkline plots to visually show data volume in a group of time series data streams.
#
# TODO:
# - use formatNumber from plot-variance.py
#
# Martin Dittus, 2012
# 

import argparse
from collections import defaultdict
import csv
import os.path
import sys

import numpy as np

import matplotlib
matplotlib.use('PDF')
# matplotlib.use('macosx')

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

# =========
# = Tools =
# =========

# For filtering
def isValue(v):
    return (v is not None) and (np.isnan(v)==False)

# ========
# = Main =
# ========

if __name__ == "__main__":
    
    defaultWidth = 2
    defaultHeight = 0.4
    defaultDpi = 80
    defaultFontsize = 8
        
    parser = argparse.ArgumentParser(description='Create a bar chart for pre-aggregated data.')
    parser.add_argument('filename', help='TSV file of (date, val1, val2, ...)')
    parser.add_argument('validx', help='index of column to plot')
    parser.add_argument('outfilename', help='PDF filename')
    parser.add_argument('-w', '--width', dest='width', action='store', type=float, 
        default=defaultWidth, help='width (in inches)')
    parser.add_argument('-e', '--height', dest='height', action='store', type=float, 
        default=defaultHeight, help='height (in inches)')
    parser.add_argument('-d', '--dpi', dest='dpi', action='store', type=float, 
        default=defaultWidth, help='dpi')
    parser.add_argument('-f', '--font-size', dest='fontsize', action='store', type=float, 
        default=defaultFontsize, help='font size in points')
    args = parser.parse_args()
    
    if (os.path.isfile(args.filename)==False):
        print "File doesn't exist: %s" % (args.filename)
        sys.exit(1)

    # Load
    data = defaultdict(lambda: dict())
    allDates = set()
    reader = csv.reader(open(args.filename, 'rb'), delimiter='	', quoting=csv.QUOTE_NONE)
    for rec in reader:
        date = rec[0]
        str = rec[int(args.validx)]
        if (str==''):
            val = None
        else:
            try:
                val = int(str)
            except ValueError:
                val = None
        data[date] = val
        allDates.add(date)

    # Prepare data
    dates = sorted(allDates)
    maxval = max(data.values())
    series = [data[d] for d in dates]

    print "%d dates, max value is %d" % (len(allDates), maxval)

    # graph dimensions
    numpoints = len(data.values())
    width = numpoints * 1.5
    textpos = numpoints * 1.03

    # Graph
    figsize = (args.width, args.height)
    fig = plt.figure(figsize=figsize, dpi=args.dpi)
    ax1 = plt.axes(frameon=False)

    ax1.axes.get_xaxis().set_visible(False)
    ax1.axes.get_yaxis().set_visible(False)
    ax1.set_xlim(0, width)
    
    plt.bar(range(numpoints), series, 
        color='#666666', linewidth=0)

    plt.text(textpos, 0, maxval, 
        size=args.fontsize, color='#666666', 
        horizontalalignment='left', verticalalignment='bottom')

    # Done.
    plt.savefig(args.outfilename, bbox_inches='tight')
