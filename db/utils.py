# -*- coding: utf-8 -*-

import copy
from db.orm import MODELS
from db.tables import TABLES
from common.utils import zip_values

__author__ = 'mayns'

ALL_TABLES = copy.deepcopy(MODELS)
ALL_TABLES.update(TABLES)


def get_update_sql_query(tbl, update_params, where_params=None):
    if where_params is None:
        where_params = {}

    sql_string = u"UPDATE {table_name} SET".format(table_name=tbl)
    for i, k in enumerate(update_params.keys()):
        sql_string = u"{prefix} {title}='{value}'".format(prefix=sql_string, title=k, value=update_params[k])
        if i < len(update_params.keys()) - 1:
            sql_string += ','

    sql_string = u"{prefix} WHERE".format(prefix=sql_string)
    for i, k in enumerate(where_params.keys()):
        store = ALL_TABLES[tbl][k].store
        v = where_params[k] if not store else store(where_params[k])
        sql_string = u"{prefix} {title}='{value}'".format(prefix=sql_string, title=k, value=v)
        if i < len(where_params.keys()) - 1:
            sql_string += u' AND '

    sql_string += ' RETURNING id'
    return sql_string


def get_insert_sql_query(tbl, insert_data):
    # TODO: check all PostgreSQL rules on storage data types and symbols

    """

    :type insert_data: dict
    :return: valid SQL request query
    :rtype: unicode
    """
    column_values = zip_values(ALL_TABLES[tbl].keys(), insert_data)
    fields = u", ".join([v[0] for v in column_values])
    values = []

    for value in column_values:
        store = ALL_TABLES[tbl][value[0]].store
        if not store:
            values.append(value[1])
            continue
        values.append(store(value[1]))
    values = u"'" + u"', '".join([v for v in values]) + u"'" if len(values) > 1 else u"'{}'".format(values[0])
    values = values.replace(u'%', u'%%')

    sql_string = u'INSERT INTO {table_name} ({fields}) VALUES ({values}) RETURNING id'.format(table_name=tbl,
                                                                                              fields=fields,
                                                                                              values=values)
    return sql_string