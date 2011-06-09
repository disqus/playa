from __future__ import absolute_import
import sqlite3

from flask import _request_ctx_stack

class SQLite3(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        self.app = app
        self.app.config.setdefault('SQLITE3_DATABASE', ':memory:')
        self.app.after_request(self.after_request)
        self.app.before_request(self.before_request)

    def connect(self):
        return sqlite3.connect(self.app.config['SQLITE3_DATABASE'])

    def before_request(self):
        ctx = _request_ctx_stack.top
        ctx.sqlite3_db = self.connect()

    def after_request(self, response):
        ctx = _request_ctx_stack.top
        ctx.sqlite3_db.close()
        return response

    def get_db(self):
        ctx = _request_ctx_stack.top
        if ctx is not None:
            return ctx.sqlite3_db