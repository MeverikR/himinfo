from helpers.config import Config

config = Config.get_config()
import asyncpg
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import pypostgresql
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.dml import Insert as InsertObject, Update as UpdateObject
from sqlalchemy.sql.ddl import DDLElement


def get_dialect(**kwargs):
    dialect = pypostgresql.dialect(paramstyle='pyformat', **kwargs)

    dialect.implicit_returning = True
    dialect.supports_native_enum = True
    dialect.supports_smallserial = True  # 9.2+
    dialect._backslash_escapes = False
    dialect.supports_sane_multi_rowcount = True  # psycopg 2.0.9+
    dialect._has_native_hstore = True

    return dialect

_dialect = get_dialect()

def execute_defaults(query):
    if isinstance(query, InsertObject):
        attr_name = 'default'
    elif isinstance(query, UpdateObject):
        attr_name = 'onupdate'
    else:
        return query

    # query.parameters could be a list in a multi row insert
    if isinstance(query.parameters, list):
        for param in query.parameters:
            _execute_default_attr(query, param, attr_name)
    else:
        query.parameters = query.parameters or {}
        _execute_default_attr(query, query.parameters, attr_name)
    return query


def _execute_default_attr(query, param, attr_name):
    for col in query.table.columns:
        attr = getattr(col, attr_name)
        if attr and param.get(col.name) is None:
            if attr.is_sequence:
                param[col.name] = func.nextval(attr.name)
            elif attr.is_scalar:
                param[col.name] = attr.arg
            elif attr.is_callable:
                param[col.name] = attr.arg({})


def compile_query(query, dialect=_dialect, inline=False):
    if isinstance(query, str):
        #query_logger.debug(query)
        return query, ()
    elif isinstance(query, DDLElement):
        compiled = query.compile(dialect=dialect)
        new_query = compiled.string
        #query_logger.debug(new_query)
        return new_query, ()
    elif isinstance(query, ClauseElement):
        query = execute_defaults(query)  # default values for Insert/Update
        compiled = query.compile(dialect=dialect)
        compiled_params = sorted(compiled.params.items())

        mapping = {key: '$' + str(i)
                   for i, (key, _) in enumerate(compiled_params, start=1)}
        new_query = compiled.string % mapping

        processors = compiled._bind_processors
        new_params = [processors[key](val) if key in processors else val
                      for key, val in compiled_params]

        #query_logger.debug(new_query)

        if inline:
            return new_query
        return new_query, new_params


async def init(app):
    """
    Connect to db and return connection object
    :return:
    """
    conn = await asyncpg.connect(**config['db'])
    app['db'] = conn
    return conn

async def close(app):
    """
    Close DB conn
    :return:
    """
    db = app.get('db')
    if db:
        await db.close()


async def get_one_row(query, db):
    if query is not None and db is not None:
        query = compile_query(query)

        return await db.fetchrow(query[0] , *query[1])
    else:
        raise Exception('set query and db please')

async def get_insert_row(query, db):
    if query is not None and db is not None:
        query = compile_query(query)
        return await db.fetchval(query[0] , *query[1] )
    else:
        raise Exception('set query and db please')


async def get_apdate(query, db):
    if query is not None and db is not None:
        query = compile_query(query)
        return await db.fetchval(query[0] , *query[1] )
    else:
        raise Exception('set query and db please')


async def get_row(query, db):
    if query is not None and db is not None:
        query = compile_query(query)
        return await db.fetch(query[0] , *query[1])
    else:
        raise Exception('set query and db please')