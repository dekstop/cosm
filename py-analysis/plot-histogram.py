# Sparkline plots to visually show tag (item) distribution in a histogram.
#
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

import matplotlib.pyplot as plt
from pylab import randn, sin

# ========
# = Main =
# ========

if __name__ == "__main__":
    
    defaultWidth = 2
    defaultHeight = 0.4
    defaultDpi = 80
    defaultFontsize = 8
        
    parser = argparse.ArgumentParser(description='Create a histogram plot.')
    parser.add_argument('filename', help='TSV histogram data of (tag, count1, count1, ...)')
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
    data = []
    reader = csv.reader(open(args.filename, 'rb'), delimiter='	', quoting=csv.QUOTE_NONE)
    for rec in reader:
        item = rec[0]
        val = int(rec[int(args.validx)])
        data.append(val)

    # Prepare data
    data.sort(reverse=True)
    maxcount = max(data)

    print "%d items, max count is %d" % (len(data), maxcount)
    
    # Graph
    figsize = (args.width, args.height)
    fig = plt.figure(figsize=figsize, dpi=args.dpi)
    ax1 = plt.axes(frameon=False)

    ax1.axes.get_xaxis().set_visible(False)
    ax1.axes.get_yaxis().set_visible(False)

    # graph dimensions
    numpoints = len(data)
    width = numpoints * 1.3
    textpos = numpoints * 1.3
    height = maxcount

    # Plot
    plt.bar(range(numpoints), data, 
        color='#666666', linewidth=0)

    plt.text(textpos, 0, maxcount,
        size=args.fontsize, color='#666666', 
        horizontalalignment='right', verticalalignment='bottom')

    # Done.
    plt.savefig(args.outfilename, bbox_inches='tight')
