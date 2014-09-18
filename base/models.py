# -*- coding: utf-8 -*-

from tornado import gen
from common.decorators import redis_connection
from common.cache import Memcached
__author__ = 'oks'


class RedisModel(object):
    REDIS_KEY = u"General"

    def __init__(self, entity_id):
        self.entity_id = entity_id

    @property
    def type(self):
        return self.__class__.__name__

    def refresh_related_objects(self):
        # must implement in child-class
        pass

    @classmethod
    @gen.coroutine
    def from_redis_by_id(cls, *args):
        # abstract method
        raise NotImplementedError()

    @classmethod
    @redis_connection()
    def remove_from_redis(cls, conn, entity_id):
        yield gen.Task(conn.delete, u"{name}:{id}".format(name=cls.REDIS_KEY, id=entity_id))

    @redis_connection()
    def update_entity(self, **kwargs):
        pass


class PSQLModel(object):
    MEM_KEY_ID = None
    PSQL_TABLE = None
    PSQL_COLUMNS = None

    def __init__(self, entity_id):
        self.id = entity_id
        self.psql_table = self.PSQL_TABLE
        self.psql_columns = self.PSQL_COLUMNS
        self.initialize()

    def initialize(self):
        assert self.psql_table, u'PSQL table name not specified'
        assert self.psql_columns, u'PSQL columns name not specified'

    @property
    def type(self):
        return self.__class__.__name__

    def flush_memcached(self):
        if self.MEM_KEY_ID:
            Memcached.set_object_cached(self.MEM_KEY_ID % self.id, self)

    def delete_memcached(self, refresh_related_objects=False):
        if self.MEM_KEY_ID:
            Memcached.delete_cached_object(self.MEM_KEY_ID % self.id)

        if refresh_related_objects:
            self.refresh_related_objects()

    @classmethod
    def delete_memcached_by_id(cls, entity_id):
        Memcached.delete_cached_object(cls.MEM_KEY_ID % entity_id)

    def refresh_related_objects(self):
        # must implement in child-class
        pass

    @classmethod
    @gen.coroutine
    def from_db_by_id(cls, *args):
        # abstract method
        raise NotImplementedError()


    @classmethod
    @gen.coroutine
    def get_by_id(cls, entity_id):
        entity_id = entity_id
        if cls.MEM_KEY_ID:
            entity = Memcached.get_cached_object(cls.MEM_KEY_ID % entity_id)
            if entity:
                raise gen.Return(entity)
        entity, rd_entity = yield gen.Task(cls.from_db_by_id, entity_id)
        if entity and cls.MEM_KEY_ID:
            entity.flush_memcached()
        raise gen.Return(entity)


def get_update_sql_query(tbl, update_params, where_params=None):
    if where_params is None:
        where_params = {}

    sql_string = u"UPDATE {table_name} SET".format(table_name=tbl)
    for i, title in enumerate(update_params.keys()):
        sql_string = u"{prefix} {title}=%({title})s".format(prefix=sql_string, title=title)
        if i < len(update_params.keys()) - 1:
            sql_string += ','

    sql_string = u"{prefix} WHERE".format(prefix=sql_string)
    for i, title in enumerate(where_params.keys()):
        sql_string = u"{prefix} {title}=%({title})s".format(prefix=sql_string, title=title)
        if i < len(where_params.keys()) - 1:
            sql_string += u' AND '

    update_params.update(where_params)
    return sql_string, update_params


def get_insert_sql_query(tbl, insert_data):
    sql_fields = u""
    sql_values = u""
    for i, title in enumerate(insert_data.keys()):
        sql_fields = u"{prefix} {title}".format(prefix=sql_fields, title=title)
        sql_values = u"{prefix} %({title})s".format(prefix=sql_values, title=title)
        if i < len(insert_data.keys()) - 1:
            sql_fields += u','
            sql_values += u','
    print tbl
    print insert_data
    sql_string = u'INSERT INTO {table_name} ({fields}) VALUES ({values})'.format(table_name=tbl, fields=sql_fields, values=sql_values)
    return sql_string, insert_data
