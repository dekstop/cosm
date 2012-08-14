# -*- coding: utf-8 -*-
import csv
import argparse
import sys

from sqlalchemy import *
# from sqlalchemy.orm import *
# from sqlalchemy.schema import *
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.sql.expression import *

from app import *

# ========
# = Util =
# ========

# Write a ranking query result set to a CSV file.
# The query needs to select three columns:
# - a string column, the name is specified via the nameColumn parameter
# - an integer column called 'num_streams'
# - an integer column called 'num_measures'
def writeRankingCsv(query, nameColumn, filename):
    with open(filename, 'w') as of:
        writer = csv.writer(of, delimiter='	', quoting=csv.QUOTE_NONE)
        writer.writerow([nameColumn, 'num_streams', 'num_measures'])

        for rec in query:
            writer.writerow([
                getattr(rec, nameColumn).encode('utf-8'), 
                str(rec.num_streams), 
                str(rec.num_measures)
            ])

# ========
# = Main =
# ========

DATEFORMAT = '%Y-%m-%dT%H:%M:%S'

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description='Export summary statistics for a group of datastreams.',
        epilog='Date parameters need to be provided in this format: %s' % DATEFORMAT)
    parser.add_argument('fromdate', help='start date, inclusive')
    parser.add_argument('todate', help='end date, exclusive')
    parser.add_argument('outdir', help='name of output directory')

    parser.add_argument('-t', '--filter-tags', action='store', dest='tags', 
        help='a comma-separated list of stream tags')
    parser.add_argument('-u', '--filter-units', action='store', dest='units', 
        help='a comma-separated list of stream units')
    parser.add_argument('-l', '--location', action='store', dest='location', 
        help='a comma-separated list of location names')
    parser.add_argument('-o', '--domain', action='store', dest='domain', 
        help='the location.domain')
    parser.add_argument('-e', '--exposure', action='store', dest='exposure', 
        help='the location.exposure')
    parser.add_argument('-d', '--disposition', action='store', dest='disposition', 
        help='the location.disposition')
    parser.add_argument('--latitude', action='store', dest='latitude', 
        help='a comma-separated list of min and max latitude')
    parser.add_argument('--longitude', action='store', dest='longitude', 
        help='a comma-separated list of min and max longitude')
    parser.add_argument('-n', '--not-null', dest='notnull', 
        action='store_true', help='exclude records where measured value is null (not numeric)')

    args = parser.parse_args()
    
    # ========
    # = Init =
    # ========

    fromdate = datetime.strptime(args.fromdate, DATEFORMAT)
    todate = datetime.strptime(args.todate, DATEFORMAT)
    
    if (os.path.exists(args.outdir)==False):
        # print "Making directory: %s" % (args.streamfile)
        os.makedirs(args.outdir)

    tags = None
    if (args.tags is not None):
        tags = args.tags.decode("utf-8").split(',')
    
    units = None
    if (args.units is not None):
        units = args.units.decode("utf-8").split(',')
    
    locations = None
    if (args.location is not None):
        locations = args.location.decode("utf-8").split(',')
    
    domain = None
    if (args.domain is not None):
        domain = args.domain.decode("utf-8")
    
    exposure = None
    if (args.exposure is not None):
        exposure = args.exposure.decode("utf-8")
    
    disposition = None
    if (args.disposition is not None):
        units = args.disposition.decode("utf-8")
    
    latitude = None
    if (args.latitude is not None):
        latitude = [Decimal(x) for x in args.latitude.split(',')]
    
    longitude = None
    if (args.longitude is not None):
        longitude = [Decimal(x) for x in args.longitude.split(',')]
    
    # getDb().echo = True
    session = getSession()

    # ================
    # = Make filters =
    # ================
    
    # Build SQL filter snippets for our export queries.

    dateFilter = and_(
        Data.updated >= fromdate, 
        Data.updated < todate
    )

    streamsForTagFilter = None
    if (tags is not None):
        tagStreamids = session.query(Stream.id).join(Stream.tags).filter(
            func.lower(Tag.name).in_(tags)
        ).distinct()
        streamsForTagFilter = Stream.id.in_(tagStreamids)
    
    streamUnitFilter = None
    if (units is not None):
        streamUnitFilter = func.lower(Stream.unit).in_(units)
    
    environmentsForLocationFilter = None
    if (locations is not None):
        environmentsForLocationFilter = func.lower(Environment.location).in_(locations)
    
    envDomainFilter = None
    if (domain is not None):
        envDomainFilter = func.lower(Environment.location_domain) == domain
    
    envExposureFilter = None
    if (exposure is not None):
        envExposureFilter = func.lower(Environment.location_exposure) == exposure
    
    envDispositionFilter = None
    if (disposition is not None):
        envDispositionFilter = func.lower(Environment.location_disposition) == disposition
    
    envLatFilter = None
    if (latitude is not None):
        envLatFilter = and_(
            Environment.latitude >= latitude[0],
            Environment.latitude < latitude[1]
        )
    
    envLonFilter = None
    if (longitude is not None):
        envLonFilter = and_(
            Environment.longitude >= longitude[0],
            Environment.longitude < longitude[1]
        )
    
    valueNotNullFilter = None
    if args.notnull:
        valueNotNullFilter = Data.value != null()

    filters = [
        dateFilter, 
        streamUnitFilter, 
        streamsForTagFilter, 
        environmentsForLocationFilter, 
        envDomainFilter,
        envExposureFilter,
        envDispositionFilter,
        envLatFilter,
        envLonFilter,
        valueNotNullFilter
    ]

    # ===============
    # = Sensor Data = 
    # ===============
    
    query = session.query(
            Stream.id.label('streamid'),
            Environment.latitude.label('latitude'),
            Environment.longitude.label('longitude'),
            Data.updated.label('updated'),
            Stream.unit.label('unit'),
            Data.value.label('value')
        ).join(Environment, Data).\
        filter(*filters)
    
    with open(os.path.join(args.outdir, "data.txt"), 'w') as of:
        writer = csv.writer(of, delimiter='	', quoting=csv.QUOTE_NONE)
        writer.writerow(['streamid', 'latitude', 'longitude', 'updated', 'unit', 'value'])

        for rec in query:
            writer.writerow([ # .encode('utf-8')
                str(rec.streamid), 
                str(rec.latitude), 
                str(rec.longitude), 
                str(rec.updated), 
                rec.unit.encode('utf-8'),
                str(rec.value)
            ])

    # ===============
    # = Daily Count = 
    # ===============
    
    query = session.query(
            Data.__table__, 
            ToDay(Data.updated).label('day'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Environment).\
        filter(*filters).\
        group_by('day').order_by('day')
    
    writeRankingCsv(query, 'day', os.path.join(args.outdir, "data_days.txt"))

    # ================
    # = Hourly Count = 
    # ================
    
    query = session.query(
            Data.__table__, 
            ToHour(Data.updated).label('hour'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Environment).\
        filter(*filters).\
        group_by('hour').order_by('hour')
    
    writeRankingCsv(query, 'hour', os.path.join(args.outdir, "data_hours.txt"))

    # ====================
    # = Environment Tags =
    # ====================

    # Tag frequency for streams

    query = session.query(
            func.lower(Tag.name).label('tag_name'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Tag.environments, Stream, Data).\
        filter(*filters).\
        group_by('tag_name').order_by('num_streams desc')

    writeRankingCsv(query, 'tag_name', os.path.join(args.outdir, "environment_tags.txt"))

    # ===============
    # = Stream Tags =
    # ===============

    # Tag frequency for streams

    query = session.query(
            func.lower(Tag.name).label('tag_name'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Tag.streams, Environment, Data).\
        filter(*filters).\
        group_by('tag_name').order_by('num_streams desc')

    writeRankingCsv(query, 'tag_name', os.path.join(args.outdir, "stream_tags.txt"))

    # =========
    # = Units =
    # =========
    
    # Unit frequency for streams

    query = session.query(
            func.lower(Stream.unit).label('unit'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Data, Environment).\
        filter(*filters).\
        group_by('unit').order_by('num_streams desc')

    writeRankingCsv(query, 'unit', os.path.join(args.outdir, "units.txt"))

    # ============
    # = Location =
    # ============
    
    # Location name frequency for streams

    query = session.query(
            func.lower(Environment.location).label('location'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Data).\
        filter(*filters).\
        group_by('location').order_by('num_streams desc')

    writeRankingCsv(query, 'location', os.path.join(args.outdir, "locations.txt"))

    # ==========
    # = Domain =
    # ==========
    
    # Location domain frequency for streams

    query = session.query(
            func.lower(Environment.location_domain).label('location_domain'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Data).\
        filter(*filters).\
        group_by('location_domain').order_by('num_streams desc')

    writeRankingCsv(query, 'location_domain', os.path.join(args.outdir, "location_domains.txt"))

    # ============
    # = Exposure =
    # ============
    
    # Location domain frequency for streams

    query = session.query(
            func.lower(Environment.location_exposure).label('location_exposure'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Data).\
        filter(*filters).\
        group_by('location_exposure').order_by('num_streams desc')

    writeRankingCsv(query, 'location_exposure', os.path.join(args.outdir, "location_exposures.txt"))

    # ===============
    # = Disposition =
    # ===============
    
    # Location domain frequency for streams

    query = session.query(
            func.lower(Environment.location_disposition).label('location_disposition'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Data).\
        filter(*filters).\
        group_by('location_disposition').order_by('num_streams desc')

    writeRankingCsv(query, 'location_disposition', os.path.join(args.outdir, "location_dispositions.txt"))