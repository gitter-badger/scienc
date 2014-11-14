# -*- coding: utf-8 -*-

from tornado import gen
import logging
import momoko
import psycopg2
import settings
from common.connections import PSQLClient

__author__ = 'mayns'

TABLES = [u'countries', u'main_cities', u'cities', u'schools', u'universities', u'faculties',  u'chairs', u'scientists',
          u'projects', u'languages']


def create_db():
    from psycopg2 import connect
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

    dbs_param = settings.SCIENCE_DB
    root_con = connect(dbname=u'postgres', user=settings.PSQL_ROOT_USER, host=dbs_param[u'host'],
                       port=dbs_param[u'port'], password=settings.PSQL_ROOT_PASSWORD)
    root_cursor = root_con.cursor()
    root_cursor.execute(u'SELECT 1 FROM pg_roles WHERE rolname={}'.format(dbs_param[u'user']))
    exist_user = root_cursor.fetchone()
    if not exist_user:
        root_cursor.execute(u'CREATE USER {}'.format(dbs_param[u'user']))
    root_cursor.execute(u'ALTER USER {} WITH PASSWORD %s'.format(dbs_param[u'user']), (dbs_param[u'password'],))
    root_cursor.execute(u'ALTER USER {} CREATEDB'.format(dbs_param[u'user']))
    root_con.commit()
    root_con.close()

    con = connect(dbname=u'postgres', user=dbs_param[u'user'], host=dbs_param[u'host'],
                  port=dbs_param[u'port'], password=dbs_param[u'password'])
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = con.cursor()
    cursor.execute(u'SELECT 1 FROM pg_database WHERE datname={}'.format(dbs_param[u'database']))
    exist_db = cursor.fetchone()
    if not exist_db:
        cursor.execute(u'CREATE DATABASE {}'.format(dbs_param[u'database']))
    con.commit()
    con.close()


@gen.coroutine
def create_relations():
    try:
        # yield delete_tables()
        # yield create_project_relation(partition)
        yield create_scientists_relation()
        # yield create_charmed_relation(partition)
        logging.info(u'done')

    except (psycopg2.Warning, psycopg2.Error) as error:
        raise Exception(str(error))


@gen.coroutine
def delete_tables():
        conn = PSQLClient.get_client()
        for table in TABLES:
            try:
                logging.info(u'LOG deleting {}'.format(table))
                print u'PRINT deleting {}'.format(table)
                yield momoko.Op(conn.execute, u'DROP TABLE %s CASCADE' % table)
                logging.info(u'deleted')
            except Exception, ex:
                print ex
                continue


@gen.coroutine
def create_scientists_relation():
    logging.info(u'creating scientists relation')
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    """CREATE TABLE scientists (
                    id bigserial primary key,
                    email text,
                    first_name text,
                    last_name text,
                    middle_name text,
                    dob text,
                    gender text,
                    image_small bytea,
                    image_medium bytea,
                    image_large bytea,
                    location_country text,
                    location_city text,
                    middle_education  json,
                    high_education  json,
                    publications  text[],
                    interests  text,
                    project_ids  bigserial[],
                    about  text,
                    contacts  text[],
                    desired_projects_ids  text[],
                    managing_projects_ids  text[],
                    dt_created timestamptz,
                    dt_last_visit timestamptz;""")

    # yield momoko.Op(conn.execute, u"CREATE INDEX scientists_projects_gin ON scientists USING GIN(project_ids);")


@gen.coroutine
def create_charmed_relation():
    logging.info(u'creating this... you know what')
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    'CREATE TABLE charmed ('
                    'id varchar(255) primary key,'
                    'val text;')


@gen.coroutine
def create_project_relation():
    logging.info(u'creating project relation')
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    """CREATE TABLE projects (
                    id varchar(80) primary key,
                    manager text,
                    research_fields text[],
                    title text,
                    description_short text,
                    views integer,
                    likes integer,
                    responses integer,
                    organization_type text,
                    organization_structure text,
                    'start_date text, '
                    'end_date text, '
                    'objective text, '
                    'description_full text, '
                    'usage_possibilities text, '
                    'results text, '
                    'related_data text, '
                    'leader text, '
                    'participants text[], '
                    'missed_participants text[], '
                    'tags text[], '
                    'contact_manager text, '
                    'contacts text[], '
                    'project_site text);""")

    yield momoko.Op(conn.execute, u"CREATE INDEX title_ru_idx ON projects "
                                  u"USING GIN (to_tsvector('russian', title));")
    yield momoko.Op(conn.execute, u"CREATE INDEX title_en_idx ON projects "
                                  u"USING GIN (to_tsvector('english', title));")

    yield momoko.Op(conn.execute, u"CREATE INDEX organization_structure_ru_idx ON projects "
                                  u"USING GIN (to_tsvector('russian', organization_structure));")
    yield momoko.Op(conn.execute, u"CREATE INDEX organization_structure_en_idx ON projects "
                                  u"USING GIN (to_tsvector('english', organization_structure));")

    yield momoko.Op(conn.execute, u"CREATE INDEX description_full_ru_idx ON projects "
                                  u"USING GIN (to_tsvector('russian', description_full));")
    yield momoko.Op(conn.execute, u"CREATE INDEX description_full_en_idx ON projects "
                                  u"USING GIN (to_tsvector('english', description_full)); ")


# ---------------------- EDUCATION & LOCATION TABLES --------------------------

@gen.coroutine
def create_country_relation():
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    'CREATE TABLE countries ('
                    'id varchar(80) primary key,'
                    'title_en text,'
                    'title_ru text);')

    yield momoko.Op(conn.execute, u"CREATE INDEX countries_ru_idx ON countries "
                                  u"USING GIN(to_tsvector('russian', title_ru));")
    yield momoko.Op(conn.execute, u"CREATE INDEX countries_en_idx ON countries "
                                  u"USING GIN(to_tsvector('english', title_en));")


@gen.coroutine
def create_city_relation():
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    'CREATE TABLE cities ('
                    'cid varchar(80) primary key,'
                    'id varchar(80) REFERENCES countries(id),'
                    'region text DEFAULT NULL,'
                    'area text DEFAULT NULL,'
                    'title text);')

    yield momoko.Op(conn.execute, u"CREATE INDEX region_ru_idx ON cities "
                                  u"USING GIN(to_tsvector('russian', region));")
    yield momoko.Op(conn.execute, u"CREATE INDEX region_en_idx ON cities "
                                  u"USING GIN(to_tsvector('english', region));")
    yield momoko.Op(conn.execute, u"CREATE INDEX area_ru_idx ON cities "
                                  u"USING GIN(to_tsvector('russian', area));")
    yield momoko.Op(conn.execute, u"CREATE INDEX area_en_idx ON cities "
                                  u"USING GIN(to_tsvector('english', area));")
    yield momoko.Op(conn.execute, u"CREATE INDEX cities_ru_idx ON cities "
                                  u"USING GIN(to_tsvector('russian', title));")
    yield momoko.Op(conn.execute, u"CREATE INDEX cities_en_idx ON cities "
                                  u"USING GIN(to_tsvector('english', title));")


@gen.coroutine
def create_main_city_relation():
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    'CREATE TABLE main_cities ('
                    'mcid varchar(80) primary key,'
                    'cid varchar(80) REFERENCES cities (cid));')


@gen.coroutine
def create_university_relation():
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    'CREATE TABLE universities ('
                    'uid varchar(80) primary key,'
                    'cid varchar(80) REFERENCES cities (cid),'
                    'title text);')
    yield momoko.Op(conn.execute, u"CREATE INDEX universities_ru_idx ON universities "
                                  u"USING GIN(to_tsvector('russian', title));")
    yield momoko.Op(conn.execute, u"CREATE INDEX universities_en_idx ON universities "
                                  u"USING GIN(to_tsvector('english', title));")


@gen.coroutine
def create_faculty_relation():
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    'CREATE TABLE faculties ('
                    'fid varchar(80) primary key,'
                    'uid varchar(80) REFERENCES universities(uid),'
                    'title text);')
    yield momoko.Op(conn.execute, u"CREATE INDEX faculties_ru_idx ON faculties "
                                  u"USING GIN(to_tsvector('russian', title));")
    yield momoko.Op(conn.execute, u"CREATE INDEX faculties_en_idx ON faculties "
                                  u"USING GIN(to_tsvector('english', title));")


@gen.coroutine
def create_chair_relation():
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    'CREATE TABLE chairs ('
                    'chid varchar(80) primary key,'
                    'fid varchar(80) REFERENCES faculties(fid),'
                    'title text);')
    yield momoko.Op(conn.execute, u"CREATE INDEX chairs_ru_idx ON chairs "
                                  u"USING GIN(to_tsvector('russian', title));")
    yield momoko.Op(conn.execute, u"CREATE INDEX chairs_en_idx ON chairs "
                                  u"USING GIN(to_tsvector('english', title));")


@gen.coroutine
def create_school_relation():
    conn = PSQLClient.get_client()
    yield momoko.Op(conn.execute,
                    'CREATE TABLE schools ('
                    'scid varchar(80) primary key,'
                    'cid varchar(80) REFERENCES cities(cid),'
                    'title text);')
    yield momoko.Op(conn.execute, u"CREATE INDEX schools_ru_idx ON schools "
                                  u"USING GIN(to_tsvector('russian', title));")
    yield momoko.Op(conn.execute, u"CREATE INDEX schools_en_idx ON schools "
                                  u"USING GIN(to_tsvector('english', title));")