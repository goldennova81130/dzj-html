#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@time: 2018/12/22
"""
from tornado.escape import json_decode, json_encode, to_basestring, native_str
from tornado.options import options
from tornado.testing import AsyncHTTPSTestCase
from tornado.httpclient import HTTPRequest
from tornado.util import PY3
import re
import controller as c
from controller.app import Application

if PY3:
    import http.cookies as Cookie
else:
    import Cookie

cookie = Cookie.SimpleCookie()


class APITestCase(AsyncHTTPSTestCase):

    def get_app(self):
        options.testing = True
        options.debug = False
        options.port = self.get_http_port()
        return Application(c.handlers, db_name_ext='_test',
                           ui_modules=c.modules,
                           default_handler_class=c.InvalidPageHandler)

    def tearDown(self):
        super(APITestCase, self).tearDown()
        self._app.stop()

    @staticmethod
    def parse_response(response):
        body = response.body and to_basestring(response.body) or '{}'
        return json_decode(body) if body and body.startswith('{') else body

    def get_code(self, response):
        response = self.parse_response(response)
        return response.get('code', 200)

    def assert_code(self, code, response):
        code = code[0] if isinstance(code, tuple) else code
        r2 = self.parse_response(response)
        r_code = r2.get('code', response.code)
        if isinstance(code, list):
            self.assertIn(r_code, [c[0] if isinstance(c, tuple) else c for c in code])
        else:
            self.assertEqual(code, r_code, r2.get('error'))

    def fetch(self, url, **kwargs):
        if isinstance(kwargs.get('body'), dict):
            if isinstance(kwargs['body'].get('data'), dict):
                kwargs['body']['data'] = json_encode(kwargs['body']['data'])
            kwargs['body'] = json_encode(kwargs['body'])
            kwargs['method'] = kwargs.get('method', 'POST')

        headers = kwargs.get('headers', {})
        headers['Cookie'] = ''.join(['%s=%s;' % (x, morsel.value) for (x, morsel) in cookie.items()])

        request = HTTPRequest(self.get_url(url), headers=headers, **kwargs)
        self.http_client.fetch(request, self.stop)

        response = self.wait()
        headers = response.headers
        try:
            sc = headers._dict.get('Set-Cookie') if hasattr(headers, '_dict') else headers.get('Set-Cookie')
            if sc:
                text = native_str(sc)
                text = re.sub(r'Path=/(,)?', '', text)
                cookie.update(Cookie.SimpleCookie(text))
                while True:
                    cookie.update(Cookie.SimpleCookie(text))
                    if ',' not in text:
                        break
                    text = text[text.find(',') + 1:]
        except KeyError:
            pass

        return response

    def add_admin_user(self):
        """ 在创建其他用户前先创建超级管理员，避免测试用例乱序执行时其他用户先创建而成为管理员 """
        return self.fetch('/api/user/register', body={'data': dict(
            email='admin@test.com', name='管理', password='test123')})

    def add_users(self, users, auth=None):
        self.add_admin_user()
        for r in users:
            self.fetch('/api/user/register', body={'data': r})
        self.login_as_admin()
        for r in users:
            self.fetch('/api/user/change', body={'data': dict(email=r['email'], authority=r.get('auth', auth))})

    def login_as_admin(self):
        return self.login('admin@test.com', 'test123')

    def login(self, email, password):
        return self.fetch('/api/user/login', body={'data': dict(email=email, password=password)})
