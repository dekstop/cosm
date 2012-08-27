# -*- coding: utf-8 -*-
import argparse
import csv
import sys

from sqlalchemy import *
from sqlalchemy.orm.query import Query
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.sql.expression import *

from app import *

# ========
# = Util =
# ========

def encode(str):
    if str is None:
        return None
    if isinstance(str, basestring)==False:
        return str
    return str.encode('utf-8')

def default(str, defaultstr):
    if str is None:
        return defaultstr
    return str

# Write a ranking query result set to a CSV file. 
# The query needs to select three columns:
# - one or more string columns, the name is specified via the title or attribute parameter
# - an integer column called 'num_streams'
# - an integer column called 'num_measures'
def writeRankingCsv(query, filename, column='name', title=None):
    if not type(column) is list:
        column = [column]
    if title is None:
        title = column
    elif not type(title) is list:
        title = [title]

    with open(filename, 'w') as of:
        writer = csv.writer(of, delimiter='	', quoting=csv.QUOTE_NONE, quotechar='')
	writer.writerow(title + ['num_streams', 'num_measures'])
        for rec in query:
            val = [default(encode(getattr(rec, attr)), '(no value available)') for attr in column]
            writer.writerow(
                val + [
                str(rec.num_streams), 
                str(rec.num_measures)
            ])

def writeInfoFile(args, filename):
    with open(filename, 'w') as of:
        for k in sorted(vars(args).keys()):
            v = getattr(args, k)
            if v is not None:
                of.write("%s = %s\n" % (k, v))

# ========
# = Main =
# ========

DATETIMEFORMAT = '%Y-%m-%dT%H:%M:%S'
DATEFORMAT = '%Y-%m-%d'

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description='Export summary statistics for a group of datastreams.',
        epilog='Date parameters need to be provided in this format: %s' % DATETIMEFORMAT)
    parser.add_argument('fromdate', help='start date, inclusive')
    parser.add_argument('todate', help='end date, exclusive')
    parser.add_argument('outdir', help='name of output directory')

    parser.add_argument('-t', '--filter-tags', action='store', dest='tags', 
        help='a comma-separated list of stream tags, or a filename (with one term per line)')
    parser.add_argument('-u', '--filter-units', action='store', dest='units', 
        help='a comma-separated list of stream units, or a filename (with one term per line)')
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
    parser.add_argument('-n', '--not-null', action='store_true', dest='notnull', 
        help='exclude records where measured value is null (not numeric)')

    parser.add_argument('--raw-data', action="store_true", dest='rawdata', 
        help='include raw sensor data in the export')

    args = parser.parse_args()
    
    # ========
    # = Init =
    # ========

    fromdate = datetime.strptime(args.fromdate, DATETIMEFORMAT)
    todate = datetime.strptime(args.todate, DATETIMEFORMAT)
    
    if (os.path.exists(args.outdir)==False):
        # print "Making directory: %s" % (args.streamfile)
        os.makedirs(args.outdir)
    
    writeInfoFile(args, os.path.join(args.outdir, "__info__.txt"))

    tags = None
    if (args.tags is not None):
        if os.path.isfile(args.tags):
            with open(args.tags) as f:
                tags = f.read().splitlines()
        else:
            tags = args.tags.decode("utf-8").split(',')
    
    units = None
    if (args.units is not None):
        if os.path.isfile(args.units):
            with open(args.units) as f:
                units = f.read().splitlines()
        else:
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
        latitude.sort()
    
    longitude = None
    if (args.longitude is not None):
        longitude = [Decimal(x) for x in args.longitude.split(',')]
        longitude.sort()
    
    #getDb().echo = True
    session = getSession()

    # ================
    # = Make filters =
    # ================
    
    # Build SQL filter snippets for our export queries.

    dateFilter = and_(
        Data.updated >= fromdate, 
        Data.updated < todate
    )

    aggregatedDateFilter = and_(
        DataDays.date >= fromdate.strftime(DATEFORMAT), 
        DataDays.date < todate.strftime(DATEFORMAT)
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

    generalFilters = [
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
    
    dataTableFilters = [dateFilter] + generalFilters
    aggregationTableFilters = [aggregatedDateFilter] + generalFilters

    # ===============
    # = Sensor Data = 
    # ===============
    
    if (args.rawdata==True):
    
        query = session.query(
                Stream.id.label('streamid'),
                Environment.latitude.label('latitude'),
                Environment.longitude.label('longitude'),
                Data.updated.label('updated'),
                Stream.unit.label('unit'),
                Data.value.label('value')
            ).join(Environment, Data).\
            filter(*dataTableFilters)
    
        with open(os.path.join(args.outdir, "data.txt"), 'w') as of:
            writer = csv.writer(of, delimiter='	', quoting=csv.QUOTE_NONE, quotechar='')
            writer.writerow(['streamid', 'latitude', 'longitude', 'updated', 'unit', 'value'])
    
            for rec in query:
                writer.writerow([ # .encode('utf-8')
                    str(rec.streamid), 
                    str(rec.latitude), 
                    str(rec.longitude), 
                    str(rec.updated), 
                    encode(rec.unit),
                    str(rec.value)
                ])

    # ====================
    # = Aggregation Data = 
    # ====================

    query = select([
            DataDays.date.label('day'), 
            Stream.id.label('streamid'),
            DataDays.count.label('count'),
            DataDays.min.label('min'),
            DataDays.max.label('max'),
            DataDays.mean.label('mean'),
            DataDays.median.label('median'),
            DataDays.sd.label('sd')
        ], 
	#from_obj = [DataDays.__table__, Stream.__table__, Environment.__table__], # next time raw SQL is king.
        whereclause = and_(
            Stream.id == DataDays.streamid,
            Environment.id == Stream.envid,
            *aggregationTableFilters
        ),
        group_by = ['day, stream.id, count, min, max, mean, median, sd'], # Postgres wants all these, despite the unique constraint
        order_by = ['day, stream.id'],
        bind=getDb())
        
    result = session.connection().execute(query).fetchall()

    with open(os.path.join(args.outdir, "data_stream_days.txt"), 'w') as of:
        writer = csv.writer(of, delimiter='	', quoting=csv.QUOTE_NONE, quotechar='')
        writer.writerow(['date', 'streamid', 'count', 'min', 'max', 'mean', 'median', 'sd'])
    
        for rec in result:
            writer.writerow([ # .encode('utf-8')
                str(rec.day),
                str(rec.streamid),
                str(rec.count),
                str(rec.min),
                str(rec.max),
                str(rec.mean),
                str(rec.median),
                str(rec.sd)
            ])
 
    # ===============
    # = Daily Count = 
    # ===============
    
    # query = session.query(
    #         Data.__table__, 
    #         ToDay(Data.updated).label('day'), 
    #         func.count(Stream.id.distinct()).label('num_streams'),
    #         func.count(Data.id.distinct()).label('num_measures'),
    #     ).join(Stream, Environment).\
    #     filter(*dataTableFilters).\
    #     group_by('day').order_by('day')

    query = select([
            ToDay(Data.updated).label('day'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
            func.min(Data.value).label('min'), 
            func.max(Data.value).label('max'), 
            func.avg(Data.value).label('mean'), 
            # func.median(Data.value).label('median'), 
            # func.stddev(Data.value).label('sd')
        ], 
        whereclause = and_(
            Stream.id == Data.streamid,
            Environment.id == Stream.envid,
            *dataTableFilters
        ),
        group_by = 'day',
        order_by = 'day',
        bind=getDb())

    result = session.connection().execute(query).fetchall()
    
    writeRankingCsv(result, os.path.join(args.outdir, "data_days.txt"), column='day')
    
    # ================
    # = Hourly Count = 
    # ================
    
    # query = session.query(
    #         Data.__table__, 
    #         ToHour(Data.updated).label('hour'), 
    #         func.count(Stream.id.distinct()).label('num_streams'),
    #         func.count(Data.id.distinct()).label('num_measures'),
    #     ).join(Stream, Environment).\
    #     filter(*dataTableFilters).\
    #     group_by('hour').order_by('hour')
    
    query = select([
            ToHour(Data.updated).label('hour'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ], 
        whereclause = and_(
            Stream.id == Data.streamid,
            Environment.id == Stream.envid,
            *dataTableFilters
        ),
        group_by = 'hour',
        order_by = 'hour',
        bind=getDb())

    result = session.connection().execute(query).fetchall()

    writeRankingCsv(result, os.path.join(args.outdir, "data_hours.txt"), column='hour')

    # ====================
    # = Environment Tags =
    # ====================

    # Tag frequency for streams

    query = session.query(
            func.lower(Tag.name).label('tag'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Tag.environments, Stream, Data).\
        filter(*dataTableFilters).\
        group_by('tag').order_by('num_streams desc')

    writeRankingCsv(query, os.path.join(args.outdir, "environment_tags.txt"), column='tag')

    # ===============
    # = Stream Tags =
    # ===============

    # Tag frequency for streams

    query = session.query(
            func.lower(Tag.name).label('tag'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Tag.streams, Environment, Data).\
        filter(*dataTableFilters).\
        group_by('tag').order_by('num_streams desc')

    writeRankingCsv(query, os.path.join(args.outdir, "stream_tags.txt"), column='tag')

    # =========
    # = Units =
    # =========
    
    # Unit frequency for streams

    query = session.query(
            func.lower(Stream.unit).label('unit'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Data, Environment).\
        filter(*dataTableFilters).\
        group_by('unit').order_by('num_streams desc')

    writeRankingCsv(query, os.path.join(args.outdir, "units.txt"), column='unit')

    # ===============
    # = Coordinates =
    # ===============
    
    # Ranking of geo-coordinates for streams

    query = session.query(
            Environment.latitude.label('latitude'), 
            Environment.longitude.label('longitude'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Data).\
        filter(*dataTableFilters).\
        group_by('latitude', 'longitude').order_by('num_streams desc')

    writeRankingCsv(query, os.path.join(args.outdir, "coordinates.txt"), column=['latitude', 'longitude'])

    # ============
    # = Location =
    # ============
    
    # Location name frequency for streams

    query = session.query(
            func.lower(Environment.location).label('location'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Data).\
        filter(*dataTableFilters).\
        group_by('location').order_by('num_streams desc')

    writeRankingCsv(query, os.path.join(args.outdir, "locations.txt"), column='location')

    # ==========
    # = Domain =
    # ==========
    
    # Location domain frequency for streams

    query = session.query(
            func.lower(Environment.location_domain).label('location_domain'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Data).\
        filter(*dataTableFilters).\
        group_by('location_domain').order_by('num_streams desc')

    writeRankingCsv(query, os.path.join(args.outdir, "location_domains.txt"), column='location_domain')

    # ============
    # = Exposure =
    # ============
    
    # Location domain frequency for streams

    query = session.query(
            func.lower(Environment.location_exposure).label('location_exposure'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Data).\
        filter(*dataTableFilters).\
        group_by('location_exposure').order_by('num_streams desc')

    writeRankingCsv(query, os.path.join(args.outdir, "location_exposures.txt"), column='location_exposure')

    # ===============
    # = Disposition =
    # ===============
    
    # Location domain frequency for streams

    query = session.query(
            func.lower(Environment.location_disposition).label('location_disposition'), 
            func.count(Stream.id.distinct()).label('num_streams'),
            func.count(Data.id.distinct()).label('num_measures'),
        ).join(Stream, Data).\
        filter(*dataTableFilters).\
        group_by('location_disposition').order_by('num_streams desc')

    writeRankingCsv(query, os.path.join(args.outdir, "location_dispositions.txt"), column='location_disposition')
