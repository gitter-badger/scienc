# -*- coding: utf-8 -*-

# from project.handlers import CkeditorSampleHandler
from common import handlers as cm_handlers
from project import handlers as pr_handlers
from scientist import handlers as sc_handlers

__author__ = 'oks'

url_handlers = [
    # common
    (r"/api/login", cm_handlers.LoginHandler),
    (r"/api/logout", cm_handlers.LogoutHandler),
    (r"/api/not-found", cm_handlers.NotFoundHandler),
    (r"/api/xsrf", cm_handlers.CSRFHandler),
    (r"/api/user", cm_handlers.UserHandler),

    # scientists
    (r"/api/scientist(/\d+)?", sc_handlers.ScientistHandler),
    (r"/api/scientist/(\d+)/role", sc_handlers.ScientistHandler),
    (r"/api/scientists", sc_handlers.ScientistsListHandler),

    # projects
    (r"/api/project(/\d+)?", pr_handlers.ProjectHandler),
    (r"/api/projects", pr_handlers.ProjectsListHandler),
    (r"/api/project/(\d+)/like", pr_handlers.ProjectsListHandler),
    (r"/api/project/(\d+)/participation", pr_handlers.ProjectsListHandler),
    # (r"/ckeditor/samples/", CkeditorSampleHandler),

    (r"/api/.*", cm_handlers.NotFoundRedirectHandler),

]