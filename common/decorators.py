# -*- coding: utf-8 -*-

import functools

__author__ = 'oks'


def psql_connection(function):
    @functools.wraps(function)
    def call(self, *args, **kwargs):
        from db.connections import PSQLClient
        conn = PSQLClient.get_client()
        return function(self, conn, *args, **kwargs)
    return call


