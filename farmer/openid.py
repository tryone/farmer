# coding: utf-8

import json
import hashlib
from functools import wraps

from django.http.response import (HttpResponseRedirectBase,
        HttpResponseForbidden)
from django.contrib.auth import models

from farmer.settings import SYSADMINS


USER_COOKIE_NAME = 'openid'
DOUVATAR_URL = 'http://douvatar.dapps.douban.com/mirror/%s?s=32&r=x&d=http%%3A//img3.douban.com/icon/user_normal.jpg'

class HttpResponseSeeOther(HttpResponseRedirectBase):
    status_code = 303


def require_login(func):
    @wraps(func)
    def _(req, *args, **kwargs):
        if validate_cookie(req):
            return func(req, *args, **kwargs)
        return HttpResponseSeeOther('/openid2/login?continue=%s' % req.path)
    return _

class RequireLogin(object):

    def __init__(self):
        pass

    def __call__(self, func):
        @wraps(func)
        def _(req, *args, **kwargs):
            if validate_cookie(req):
                if req.uid not in SYSADMINS:
                    return HttpResponseForbidden('who are you?')
                return func(req, *args, **kwargs)
            return HttpResponseSeeOther('/openid2/login?continue=%s' % req.path)
        return _

    def admins(self, func):
        @wraps(func)
        def _(req, *args, **kwargs):
            def is_admin(uid):
                admins = set(u.username for u in models.User.objects.all())
                return uid in admins

            if not validate_cookie(req):
                return HttpResponseSeeOther(
                        '/openid2/login?continue=%s' % req.path)

            if not is_admin(req.uid):
                return HttpResponseForbidden(
                        'Only admins allowed. Please contact sa@douban.com')

            return func(req, *args, **kwargs)
        return _

require_login = RequireLogin()


def validate_cookie(request):
    cookies = request.COOKIES.get(USER_COOKIE_NAME, '{}')
    try:
        session = json.loads(cookies)
        if request.session[session['openid']] == session['session']:
            request.openid = session
            request.uid = uid_from_session(session)
            email = '%s@douban.com' % request.uid
            request.icon_url = DOUVATAR_URL % hashlib.md5(email.encode('utf-8').lower()).hexdigest()
            return True
    except:
        request.openid = None
        request.uid = None
        request.icon_url = None
        return False

def uid_from_session(session):
    ''' Openid session example:

        {\"openid\": \"http://openid2.dapps.douban.com/server/id/everbird/\"\054 \"session\": \"db9fd319a147ec57460085c37205f0\"}
    '''
    if session:
        return session['openid'].split('/')[-2]
