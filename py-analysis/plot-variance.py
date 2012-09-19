# Overlaid sparkline plots to visually show variances in related time series data streams.
#
# Notes:
# - we're computing the coefficient of variation for sensor values. This is not appropriate in
#   a number of cases:
#   - when values are approaching zero, in which case the CoV will approach infinity
#   - when values are on an interval scale, not ratio scale (when values can be negative), in
#     which case the CoV may not be meaningful
# TODO:
# - horizontal alignment of numbers at their decimal points, regardless of formats and suffixes
# - formatting: add number scales for fractions too -- atm I don't think my data warrants it.
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
# matplotlib.use('MacOSX')
# matplotlib.use('AGG')
matplotlib.use('PDF')
# ValueError: Unrecognized backend string "png": valid strings are ['ps', 'Qt4Agg', 'GTK', 'GTKAgg', 'svg', 'agg', 'cairo', 'MacOSX', 'GTKCairo', 'WXAgg', 'TkAgg', 'QtAgg', 'FltkAgg', 'pdf', 'CocoaAgg', 'emf', 'gdk', 'template', 'WX']
# matplotlib.use('macosx')

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

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

# Coefficient of variation
def cov(sd, mean):
    if (mean==0):
        return 0
    return sd / mean

# =================
# = Number Format =
# =================

# Scales this value to below 10,000
# Returns the value and an SI symbol suffix
def scaleValue(v):
    suffixes = ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    sidx = 0
    while sidx<len(suffixes) and v >= (1000 * 10):
        v = v / 1000
        sidx = sidx + 1
    return (v, suffixes[sidx])

# Formats to four significant digits.
# Assumes 10,000 > v >= 0.001
def formatDigits(v):
    if v==0:
        return "0.0"
    if v>=1000:
        format = "{:,.0f}"
    elif v>=100:
        format = "{:.1f}"
    elif v>=10:
        format = "{:.2f}"
    else:
        format = "{:.3f}"
    return format.format(v)

# Not needed -- Python 2.7 formatting added a thousands separator!
# # Takes a numeric string
# # Inserts commas at all the appropriate places
# def formatThousands(fv):
#     text = ''
#     if (fv.find('.')>0):
#         digits = fv[:fv.find('.')]
#         frac = fv[fv.find('.'):]
#     else:
#         digits = fv
#         frac = ''
#     ndigits = len(digits)
#     nsegments = ndigits / 3
#     rem = ndigits % 3
#     if (rem>0):
#         text = digits[:rem] + ','
#         ofs = 1
#     else:
#         ofs = 0
#     for i in range(nsegments-ofs):
#         text += digits[rem:rem+3] + ','
#         rem += 3
#     text += digits[rem:rem+3]
#     return text + frac

# It's always hard, this.
# To test:
# values = [
#     (0.0, "0.0"),
#     (0.0001234, "0.000"), 
#     (0.0012345, "0.001"),
#     (0.0123456, "0.012"),
#     (0.1234567, "0.123"),
#     (1.2345, "1.235"),
#     (12.345, "12.35"),
#     (123.45, "123.5"),
#     (1234.5, "1,235"),
#     (12345.67890, "12.35K"),
#     (123456.7890, "123.5K"),
#     (1234567.890, "1,235K"),
#     (12345678.90, "12.35M"),
#     (123456789.0, "123.5M"),
#     (1234567890.1234, "1,235M"),
#     (12345678901.234, "12.35B"),
#     (123456789012.34, "123.5B"),
#     (1234567890123.4, "1,235B"),
#     (12345678901234.5, "12.35T"),
# ]
# for a, b in values:
#     print a, formatLabel(a), b
#     # assert formatLabel(a) == b, ("%s != %s" % (formatLabel(a), b))
def formatLabel(v):
    if isValue(v)==False:
        return '(no numbers)'
    v, suffix = scaleValue(v)
    return formatDigits(v) + suffix

# ========
# = Main =
# ========

if __name__ == "__main__":
    
    defaultWidth = 2
    defaultHeight = 0.4
    defaultDpi = 10
    defaultFontsize = 8
        
    parser = argparse.ArgumentParser(description='Create a timeseries plot for multiple data streams.')
    parser.add_argument('filename', help='TSV file of (date, item, val1, val2, ...)')
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

    parser.add_argument('--with-header', action="store_true", dest='withHeader', 
        help='skip first line')
    
    parser.add_argument('--plot-range', action="store_true", dest='plotRange', 
        help='show y-axis ticks and labels')

    args = parser.parse_args()
    
    if (os.path.isfile(args.filename)==False):
        print "File doesn't exist: %s" % (args.filename)
        sys.exit(1)

    # Load
    data = dict()
    allDates = set()
    reader = csv.reader(open(args.filename, 'rb'), delimiter='	', quoting=csv.QUOTE_NONE)
    if args.withHeader:
        # print "Skipping first line."
        reader.next()
    for rec in reader:
        item = rec[1]
        date = rec[0]
        str = rec[int(args.validx)]
        if (str=='' or str=='None'):
            val = None
        else:
            try:
                val = float(str)
            except ValueError:
                print rec
                raise
                # sys.exit(1)
        if (item in data)==False:
            data[item] = defaultdict(lambda: None)
        data[item][date] = val
        allDates.add(date)

    if len(allDates)==0:
        print "No data in file."
        sys.exit()

    print "%d data streams and %d dates" % (len(data.keys()), len(allDates))

    # Prepare data
    dates = sorted(allDates)
    timeseries = []
    for item in data.keys():
        x = [data[item][date] for date in dates]
        timeseries.append(x)

    noData = (len(onlyValues([x for sublist in timeseries for x in sublist]))==0)

    # summary stats: sd, mean, coefficient of variation
    sdeviations = [np.std(onlyValues(values)) for values in zip(*timeseries)]
    means = [np.mean(onlyValues(values)) for values in zip(*timeseries)]
    covs = [cov(sd, mean) for sd, mean in zip(sdeviations, means)]

    numpoints = len(means)
    meanval = np.mean(means)
    # medianval = np.median(means)

    meancov = None
    # variances = [np.var(onlyValues(values)) for values in zip(*timeseries)]
    if noData==False:
        meansd = np.mean(sdeviations)
        meancov = np.mean(covs)
        mincov = min(covs)
        mincovpos = covs.index(mincov)
        maxcov = max(covs)
        maxcovpos = covs.index(maxcov)
    
    # Graph
    figsize = (args.width, args.height)
    fig = plt.figure(figsize=figsize, dpi=args.dpi)
    # fig.set_facecolor("#ffffff")
    ax1 = plt.axes(frameon=False)

    ax1.axes.get_xaxis().set_visible(False)
    if args.plotRange:
        ax1.axes.get_yaxis().set_major_locator(MaxNLocator(4)) # set bins for ticks
        ax1.tick_params(axis='y', direction='out') # ticks are facing outwards
        ax1.yaxis.tick_left() # don't plot right-hand ticks
    else:
        ax1.axes.get_yaxis().set_visible(False)

    # graph dimensions
    if noData:
        lower = 0
        higher = 0
    else:
        lower = min(onlyValues([percentile(onlyValues(values), .01) for values in zip(*timeseries)]))
        higher = max(onlyValues([percentile(onlyValues(values), .99) for values in zip(*timeseries)]))
    if math.isnan(lower):
        lower = 0
    if math.isnan(higher):
        higher = 0
    if lower==higher:
        if lower==0.0:
            lower = -0.00000001
            higher = 0.00000001
        higher = higher * 1.1
        lower = lower * 0.9
    width = numpoints * 1.3
    # height = maxval - minval
    height = higher - lower
    ymargin = height * 0.2
    textpos = numpoints * 1.03
    textVOffset = - height * 0.15

    ax1.axes.set_xlim(0, width)
    ax1.axes.set_ylim(
        lower - ymargin, 
        higher + ymargin)

    # Plots
    for ts in timeseries:
        allNone = len(onlyValues(ts))==0
        if (allNone or len(ts)==0):
            # plt.plot([0] * len(allDates), marker='x', color='#999999', linewidth=0.5)
            pass
        else:
            plt.plot(ts, color='#cccccc', alpha=0.5, linewidth=0.2)
    if noData==False:
        plt.plot(means, color='#333333', linewidth=0.5)

    # Labels
    plt.text(textpos, higher + textVOffset, len(timeseries), 
        size=args.fontsize, color='#999999', 
        horizontalalignment='left', verticalalignment='bottom')
    if noData==False:
        plt.text(textpos, (lower+higher)/2 + textVOffset, formatLabel(meanval), 
            size=args.fontsize, color='#999999', 
            horizontalalignment='left', verticalalignment='bottom')
    plt.text(textpos, lower + textVOffset, formatLabel(meancov), 
        size=args.fontsize, color='#333333', 
        horizontalalignment='left', verticalalignment='bottom')

    # Dots
    if noData==False:
        if isValue(maxcov):
            plt.plot([maxcovpos], [higher + ymargin], '.', 
                color='#ff6666', alpha=1, 
                markeredgewidth=10000, clip_on=False)
        if isValue(mincov):
            plt.plot([mincovpos], [lower - ymargin], '.', 
                color='#6666ff', alpha=1, 
                markeredgewidth=100000, clip_on=False)

    # Adjust axes
    if args.plotRange:
        for label in ax1.axes.get_yticklabels(): 
            label.set_fontsize(args.fontsize/2.0)
            label.set_color('#cccccc')
        for line in ax1.axes.get_yticklines(): 
            line.set_color('#cccccc')
        
    # ax1.axes.get_yaxis().label.set_size(args.fontsize/2.0)
    

    # Done.
    plt.savefig(args.outfilename, bbox_inches='tight')
