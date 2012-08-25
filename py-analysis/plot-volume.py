# Sparkline plots to visually show data volume in a group of time series data streams.
#
# TODO:
# - use formatNumber from plot-variance.py
# Martin Dittus, 2012
# 

import argparse
from collections import defaultdict
import csv
import math
import os.path
import sys

import numpy as np

import matplotlib
matplotlib.use('PDF')
# matplotlib.use('macosx')

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from pylab import randn, sin

# =========
# = Tools =
# =========

# For filtering
def isValue(v):
    return (v is not None) and (np.isnan(v)==False)

# remove all "None"s
def onlyValues(values):
    return filter(isValue, values)

# p is [0..1]
def percentile(data, p, limit=()):
    values = sorted(onlyValues(data))
    if (len(values)==0):
        return float('nan')
    if (len(values)==1):
        return data[0]
    if limit:
        values = [min(max(value, limit[0]), limit[1]) for value in values]

    idx = p * (len(values) - 1)
    if (idx % 1 == 0):
        return values[0]
    else:
        a = values[int(idx)]
        b = values[int(idx) + 1]
        return a + (b - a) * (idx % 1)

# ========
# = Main =
# ========

if __name__ == "__main__":
    
    defaultWidth = 2
    defaultHeight = 0.4
    defaultDpi = 80
    defaultFontsize = 8
        
    parser = argparse.ArgumentParser(description='Create a timeseries plot for multiple data streams.')
    parser.add_argument('filename', help='TSV file of (group, date, item, val1, val2, ...)')
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
    nodata = defaultdict(lambda: dict())
    allDates = set()
    reader = csv.reader(open(args.filename, 'rb'), delimiter='	', quoting=csv.QUOTE_NONE)
    for rec in reader:
        item = rec[2]
        date = rec[1]
        str = rec[int(args.validx)]
        if (str==''):
            val = None
        else:
            try:
                val = float(str)
            except ValueError:
                val = None
        if isValue(val):
            data[date][item] = True
        else:
            nodata[date][item] = True
        allDates.add(date)

    # Prepare data
    dates = sorted(allDates)
    withValues = []
    withoutValues = []
    itemsWithValues = set()
    itemsWithoutValues = set()

    for date in dates:
        withValues.append(len(data[date].keys()))
        itemsWithValues.update(data[date].keys())

        withoutValues.append(len(nodata[date].keys()))
        itemsWithoutValues.update(nodata[date].keys())

    numWithValues = len(itemsWithValues)
    numWithoutValues = len(itemsWithoutValues)

    print "%d with value, %d without, and %d dates" % (sum(withValues), sum(withoutValues), len(allDates))

    # graph dimensions
    numpoints = len(withValues)
    noData = (numWithValues==0 and numWithoutValues==0)
    width = numpoints * 1.3
    textpos = numpoints * 1.3
    wvHeight = max(withValues)
    wovHeight = max(withoutValues)

    # Graph
    figsize = (args.width, args.height)
    fig = plt.figure(figsize=figsize, dpi=args.dpi)
    fig.subplots_adjust(wspace=0, hspace=0.1)
    gs = gridspec.GridSpec(3, 1)

    # Plot 1
    ax1 = plt.subplot(gs[:-1, :]) # top 2/3rd
    ax1.set_frame_on(False)
    ax1.axes.get_xaxis().set_visible(False)
    ax1.axes.get_yaxis().set_visible(False)
    ax1.set_xlim(0, width)
    ax1.axes.set_ylim(0, max(wvHeight, 1))

    if noData==False:
        plt.bar(range(numpoints), withValues, 
        color='#666666', linewidth=0)

    plt.text(width, wvHeight * 0.1, numWithValues, 
        size=args.fontsize, color='#666666', 
        horizontalalignment='right', verticalalignment='bottom')

    # Plot 2
    ax2 = plt.subplot(gs[-1, :]) # bottom 1/3rd
    ax2.set_frame_on(False)
    ax2.axes.get_xaxis().set_visible(False)
    ax2.axes.get_yaxis().set_visible(False)
    ax2.set_xlim(0, width)
    ax2.axes.set_ylim(max(wovHeight, 1), 0) # inverted

    if noData==False:
        plt.bar(range(numpoints), withoutValues, 
        color='#cccccc', linewidth=0)

    plt.text(width, wovHeight * 0.1, numWithoutValues, 
        size=args.fontsize * 0.8, color='#cccccc', 
        horizontalalignment='right', verticalalignment='top')

    # Done.
    plt.savefig(args.outfilename, bbox_inches='tight')
