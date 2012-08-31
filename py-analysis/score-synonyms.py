# Tag synonymity scores based on tag, item, user relationships
# Clements et al (2008), "Detecting Synonyms in Social Tagging Systems to Improve Content Retrieval"
#
# Martin Dittus, 2012
# 
# Notes:
# - we're using sparse matrices and heavily depend on their internals for performance optimisations.
# - in this script a "tag" is an ID that can be used as index position into data structures.
# - note that matrices rely on positive integers [0..n] for cell access. if needed there's an optional 
#   ability to convert your tag/user/item identifiers to such numeric IDs. ("--as-strings")
# - this script doesn't include a "min number of tagged items per user" threshold, we assume that has already
#   been applied to the input data.
#
# TODO
# - split into two scripts: compute tag similarity (run once per matrix), and synonym scores
# - optimisation: convert to dense matrix but make ID conversion mandatory
#   - it's not really used as a sparse matrix -- we do compare every tax/(user|item|tag) combination
#   - atm the main cost is conversion from matrix rows to numpy arrays
#   - so: use a numpy array instead.
# 

import argparse
import csv
import os.path
import sys

import numpy as np

from scipy.sparse import lil_matrix
from scipy.stats import *


# ======================
# = Fast Sparse Matrix =
# ======================

# A sparse matrix optimised for fast row access operations.
class HMatrix(lil_matrix):

    # Returns a dense array of all values in a row.
    def getRow(self, rowIdx):
        return self[rowIdx,:].toarray()[0]
        # t = np.array([0] * self.shape[1]) # length of num_cols, all 0 values
        # idx = self.rows[rowIdx]
        # data = self.data[rowIdx]
        # t[idx] = data
        # # t = [0] * self.shape[1]
        # # for i,v in zip(idx, data):
        # #     t[i] = v
        # return t

    # Count the number of cells in a row that have a value.
    def numValuesInRow(self, rowIdx):
        return len(self.rows[rowIdx])

    # Remove the values of several rows from a sparse matrix.
    # Needed since sparse matrices have no fancy indexing; otherwise we could e.g. do m[(1,2,3),:] = 0
    # Additionally this avoids wasting cycles on comparisons later.
    def removeRows(self, rows):
        for r in rows:
            self.rows[r] = []
            self.data[r] = []
    
    def reshape(self, shape):
        return HMatrix(super(HMatrix, self).reshape(shape))
    
# =========
# = Tools =
# =========

# Construct and remember numeric IDs for string lists
class IdMapping:
    
    def __init__(self):
        self.counter = 0
        self.namesToId = dict()
        self.idsToNames = dict()
    
    def getOrMakeId(self, str):
        if (str in self.namesToId.keys()):
            return self.namesToId[str]
        self.counter += 1
        id = self.counter
        self.namesToId[str] = id
        self.idsToNames[id] = str
        return id
    
    def getName(self, id):
        return self.idsToNames[id]
    
    def __str__(self):
        return str(self.namesToId)

# Reads TSV files of ([group,] item, tag, count) or ([group,] user, tag, count)
# Returns a 2D sparse matrix of structure (tag, item) or (tag, user)
# Expects that tag, item, and user identifiers are positive ints
# If they're not: can optionally maintain translation tables and accept strings too.
def readTagItemMatrix(filename, asStrings, amap=None, tagmap=None, group=None):
    print "Loading", filename
    reader = csv.reader(open(filename, 'rb'), delimiter='	', quoting=csv.QUOTE_NONE)
    m = HMatrix((2300,2800)) # FIXME this large initial size is a hack -- see below
    
    for rec in reader:
        if group is None:
            a, tag, count = rec
        else:
            samplegroup, a, tag, count = rec
        if (group is None or samplegroup==group):
            if (asStrings==True):
                a = amap.getOrMakeId(a)
                tag = tagmap.getOrMakeId(tag)
            else:
                a = int(a)
                tag = int(tag)
            count = float(count)
            # print tag, a, count

            # ensure matrix is big enough to contain all IDs
            newShape = m.shape
            while (tag>=newShape[0]):
                newShape = (newShape[0]*2, newShape[1])
            while (a>=newShape[1]):
                newShape = (newShape[0], newShape[1]*2)
            if (newShape != m.shape):
                # print "Resizing matrix to", newShape
                # m = m.reshape(newShape)
                # FIXME argh
                raise "Cannot resize matrix to fit data -- lil_matrix may have a resizing bug"

            m[tag,a] = count
            # print m
            # print '----'
    
    # print m
    # print m.nonzero()
    return m

# ===========
# = Scoring =
# ===========

# Takes a 2D sparse matrix of shape (tag, item) or (tag, user)
# Returns a set of tags that have been used less than minUses times (by users, or on items)
def getRarelyUsedTags(m, minUses):
    ft = set()
    tags, items = m.nonzero() # only process tags that have been used
    tags = set(tags) # uniques
    for tag in tags:
        if (m.numValuesInRow(tag) < minUses):
            ft.add(tag)
    return ft

# Takes a 2D sparse matrix of shape (tag, item) or (tag, user)
# Computes pearson correlation coefficients for tag pairs
# Returns a sparse matrix of (tag, tag)
def tagSimilarityScores(m):
    sim = HMatrix((m.shape[0], m.shape[0])) # tag-tag similarity matrix
    utags, uitems = m.nonzero() # only process tags that have been used
    utags = set(utags) # uniques
    for tag1 in utags:
        # print tag1
    # for tag1 in xrange(m.shape[0]):
        tag1Items = m.getRow(tag1)
        # for tag2 in utags:
        tags2 = utags.intersection(xrange(tag1+1, m.shape[0]))
        print "%s: %d comparisons" % (tag1, len(tags2))
        for tag2 in tags2:
            tag2Items = m.getRow(tag2)
            c, p = pearsonr(tag1Items, tag2Items)
            sim[tag1, tag2] = c
    return sim

# ========
# = Main =
# ========

# mapping from assigned IDs back to the original strings
umap = IdMapping()
imap = IdMapping()
tmap = IdMapping()

if __name__ == "__main__":
    
    defaultMinUsersPerTag = 1
    defaultMinItemsPerTag = 1
    defaultMinP = 0.0 # minimum p-value for pearson's correlation coefficient
    defaultMinISim = 0.5
    defaultMaxUSim = 0.0
    
    parser = argparse.ArgumentParser(description='Compute a synonymity score for tags.')
    parser.add_argument('utmfile', help='TSV file of ([groupid,] userid, tagid, number of items)')
    parser.add_argument('itmfile', help='TSV file of ([groupid,] itemid, tagid, number of users)')
    parser.add_argument('outfile', help='TSV file to store (tagid, tagid, score)')
    parser.add_argument('-g', '--group', dest='group', action='store',
        help='the groupid to match (only records with this ID will be loaded.)')
    parser.add_argument('--as-strings', dest='asStrings', action='store_true', 
        help='treat IDs as strings, not positive integers')
    parser.add_argument('-u', '--min-users-per-tag', dest='minUsersPerTag', type=int,
        action='store', default=defaultMinUsersPerTag,
        help='minimum number of users per tag')
    parser.add_argument('-i', '--min-items-per-tag', dest='minItemsPerTag', type=int,
        action='store', default=defaultMinItemsPerTag,
        help='minimum number of items per  tag')
    parser.add_argument('-p', '--min-p', dest='minP', type=float,
        action='store', default=defaultMinP,
        help='minimum 2-tailed p-value for the Pearson correlation coefficient')
    parser.add_argument('-x', '--max-user-similarity', dest='maxUSim', type=float,
        action='store', default=defaultMaxUSim,
        help='maximum user similarity score')
    parser.add_argument('-y', '--min-item-similarity', dest='minISim', type=float,
        action='store', default=defaultMinISim,
        help='minimum item similarity score')
    args = parser.parse_args()
    
    if (os.path.isfile(args.utmfile)==False):
        print "File doesn't exist: %s" % (args.utmfile)
        sys.exit(1)

    if (os.path.isfile(args.itmfile)==False):
        print "File doesn't exist: %s" % (args.itmfile)
        sys.exit(1)
    
    if args.group:
        print "Loading group:", args.group

    # Load
    if (args.asStrings):
        utm = readTagItemMatrix(args.utmfile, args.asStrings, umap, tmap, group=args.group)
        itm = readTagItemMatrix(args.itmfile, args.asStrings, imap, tmap, group=args.group)
        print "%d unique tags, %d unique users, and %d unique items." % (tmap.counter, umap.counter, tmap.counter)
    else:
        utm = readTagItemMatrix(args.utmfile, args.asStrings, group=args.group)
        itm = readTagItemMatrix(args.itmfile, args.asStrings, group=args.group)
    
    # Apply thresholds
    print "Determining tags below threshold"
    lowUTags = getRarelyUsedTags(utm, args.minUsersPerTag)
    lowITags = getRarelyUsedTags(itm, args.minItemsPerTag)
    lowTags = lowUTags.union(lowITags)
    
    print "Removing %s tags below threshold" % (len(lowTags))
    utm.removeRows(lowTags)
    itm.removeRows(lowTags)
    
    # Compute user and item similarity between tag pairs
    print "Computing user similarity"
    usimilarity = tagSimilarityScores(utm)

    print "Computing item similarity"
    isimilarity = tagSimilarityScores(itm)
    
    # Result
    print "Writing", args.outfile
    writer = csv.writer(open(args.outfile, 'wb'), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')
    allwriter = csv.writer(open(args.outfile + ".all", 'wb'), delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')

    tags1, tags2 = usimilarity.nonzero()  # only existing (tag, tag) pairs
    for tag1, tag2 in zip(tags1, tags2):

        usim = usimilarity[tag1, tag2]
        isim = isimilarity[tag1, tag2]

        if (args.asStrings):
            rec = (
                tmap.getName(tag1), 
                tmap.getName(tag2), 
                usim, 
                isim)
        else:
            rec = (tag1, tag2, usim, isim)
        
        allwriter.writerow(rec)
        
        if usim < args.maxUSim and isim >= args.minISim:
            print rec
            writer.writerow(rec)
