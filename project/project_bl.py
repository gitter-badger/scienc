# -*- coding: utf-8 -*-

from tornado import gen
from project.models import Project

__author__ = 'oks'


class ProjectBL(object):
    @classmethod
    @gen.coroutine
    def create(cls, project_dict):

        project = Project(**project_dict)
        project_id = yield project.save(update=False)
        raise gen.Return(dict(id=project_id))

    @classmethod
    @gen.coroutine
    def update(cls, project_dict):
        project_id = project_dict.pop(u'project_id')
        if not project_id:
            raise Exception(u'No project id provided')
        project = yield Project.get_by_id(project_id)
        project.populate_fields(project_dict)
        yield project.save()
        raise gen.Return(dict(project_id=project_id))

    @classmethod
    @gen.coroutine
    def delete(cls, project_id):
        yield cls.delete(project_id)

    @classmethod
    @gen.coroutine
    def get_all_projects(cls):
        projects_data = yield Project.get_all_json(columns=Project.OVERVIEW_FIELDS)
        raise gen.Return(projects_data)

    @classmethod
    @gen.coroutine
    def get_project(cls, project_id):
        project_data = yield Project.get_json_by_id(project_id)
        raise gen.Return(project_data)