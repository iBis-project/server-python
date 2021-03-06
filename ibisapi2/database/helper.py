import logging
import sqlalchemy
import geoalchemy2


def create_engine(user, password, database, host='127.0.0.1', port=5432):
    """
    Creates database engine

    :param user: database user
    :param password: database password
    :param database: database name
    :param host: database host (default 127.0.0.1)
    :param port: database port (default 5432)
    :return: database engine created by sqlalchemy
    """
    db_url = ['postgresql', '://', user, ':', password, '@', host, ':', str(port), '/',
              database]
    logging.debug('PgSQL database url:' + ''.join(db_url))
    return sqlalchemy.create_engine(''.join(db_url))


def create_tables():
    """
    Creates iBis database structure (empty tables).

    :rtype : sqlalchemy.MetaData
    :param engine: sqlalchemy engine for databse to create table in
    :return: dict of tables and sqlalchemy table metadata
    """
    metadata = sqlalchemy.MetaData()
    tables = {'metadata':metadata}
    tables['tracks'] = sqlalchemy.Table('tracks', metadata,
                     sqlalchemy.Column('id', sqlalchemy.BigInteger, primary_key=True, index=True),
                     sqlalchemy.Column('created', sqlalchemy.TIMESTAMP, nullable=False),
                     sqlalchemy.Column('uploaded', sqlalchemy.TIMESTAMP, nullable=False),
                     sqlalchemy.Column('length', sqlalchemy.Numeric(16, 8), nullable=False),
                     sqlalchemy.Column('duration', sqlalchemy.BigInteger, nullable=False),
                     sqlalchemy.Column('num_points', sqlalchemy.BigInteger, nullable=False),
                     sqlalchemy.Column('public', sqlalchemy.Boolean, nullable=False),
                     sqlalchemy.Column('name', sqlalchemy.Text),
                     sqlalchemy.Column('comment', sqlalchemy.Text),
                     sqlalchemy.Column('city', sqlalchemy.Text),
                     sqlalchemy.Column('data_hash', sqlalchemy.Text, unique=True),
                     sqlalchemy.Column('extension_geom', geoalchemy2.Geometry('POLYGON'), index=True),  # geo index?
                     sqlalchemy.Column('track', geoalchemy2.Geometry('LINESTRING'))
                     )
    tables['track_points'] = sqlalchemy.Table('track_points', metadata,
                     sqlalchemy.Column('id', None, sqlalchemy.ForeignKey('tracks.id', ondelete='CASCADE'),
                                       nullable=False, index=True),
                     sqlalchemy.Column('geom', geoalchemy2.Geometry('POINT', 4326), nullable=False, index=True),
                     sqlalchemy.Column('altitude', sqlalchemy.Numeric(16, 8)),
                     sqlalchemy.Column('accuracy', sqlalchemy.Numeric(11, 8)),
                     sqlalchemy.Column('time', sqlalchemy.TIMESTAMP, nullable=False),
                     sqlalchemy.Column('velocity', sqlalchemy.Numeric(11, 8)),
                     sqlalchemy.Column('shock', sqlalchemy.Numeric(16, 8))
                     )
    tables['users'] = sqlalchemy.Table('users', metadata,
                     sqlalchemy.Column('name', sqlalchemy.Text, unique=True, index=True),
                     sqlalchemy.Column('password', sqlalchemy.Text),
                     sqlalchemy.Column('rights', sqlalchemy.BigInteger),
                     sqlalchemy.Column('enabled', sqlalchemy.Boolean)
                     )
    tables['profiles'] = sqlalchemy.Table('profiles', metadata,
                     sqlalchemy.Column('id', sqlalchemy.BigInteger, primary_key=True, index=True),
                     sqlalchemy.Column('name', sqlalchemy.Text)
                     )
    tables['profile_description'] = sqlalchemy.Table('profile_description', metadata,
                     sqlalchemy.Column('id', None, sqlalchemy.ForeignKey('profiles.id'), unique=True),  # index?
                     sqlalchemy.Column('language', sqlalchemy.Text),
                     sqlalchemy.Column('description', sqlalchemy.Text)
                     )
    tables['way_types'] = sqlalchemy.Table('way_types', metadata,
                     sqlalchemy.Column('id', sqlalchemy.Text, primary_key=True, index=True)
                     )
    tables['way_type_description'] = sqlalchemy.Table('way_type_description', metadata,
                     sqlalchemy.Column('id', None, sqlalchemy.ForeignKey('way_types.id')),  # not unique, index?
                     sqlalchemy.Column('language', sqlalchemy.Text),
                     sqlalchemy.Column('description', sqlalchemy.Text)
                     )
    tables['cost_static'] = sqlalchemy.Table('cost_static', metadata,
                     sqlalchemy.Column('id', None, sqlalchemy.ForeignKey('way_types.id')),
                     sqlalchemy.Column('cost_forward', sqlalchemy.Numeric(16, 8)),
                     sqlalchemy.Column('cost_reverse', sqlalchemy.Numeric(16, 8)),
                     sqlalchemy.Column('profile', None, sqlalchemy.ForeignKey('profiles.id')),
                     sqlalchemy.UniqueConstraint('id', 'profile'),
                     # place a unique index on id, profile
                     sqlalchemy.Index('idx_id_profile', 'id', 'profile', unique=True)
                     )
    tables['cost_dynamic'] = sqlalchemy.Table('cost_dynamic', metadata,
                     sqlalchemy.Column('segment_id', sqlalchemy.BigInteger, index=True),
                     sqlalchemy.Column('track_id', None, sqlalchemy.ForeignKey('tracks.id')),
                     sqlalchemy.Column('cost_forward', sqlalchemy.Numeric(16, 8)),
                     sqlalchemy.Column('cost_reverse', sqlalchemy.Numeric(16, 8))
                     )
    tables['cost_dynamic_precalculated'] = sqlalchemy.Table('cost_dynamic_precalculated', metadata,
                     sqlalchemy.Column('segment_id', sqlalchemy.BigInteger, primary_key=True, unique=True, index=True),
                     sqlalchemy.Column('cost_forward', sqlalchemy.Numeric(16, 8)),
                     sqlalchemy.Column('cost_reverse', sqlalchemy.Numeric(16, 8)),
                     sqlalchemy.Column('relevance', sqlalchemy.Numeric(16, 8))
                     )
    return tables
