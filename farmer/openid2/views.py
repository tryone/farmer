import json
import binascii
import os
from urllib import urlencode
from openid.consumer.consumer import Consumer, SUCCESS
from openid.extensions import sreg
from openid.store import filestore

from django.shortcuts import HttpResponse
from django.conf import settings

from farmer.utils import (HttpResponseSeeOther, require_login,
        USER_COOKIE_NAME, uid_from_session)


store = None
def get_store():
    global store
    if store is None:
        store = filestore.FileOpenIDStore(settings.OPENID_FILESTORE_PATH)
    return store

sreg.data_fields = {'username': 'test',
    'email': 'test@douban.com',
    'groups': '[]',
    'uid': '0'}


def login(request):
    continue_url = request.GET.get('continue') \
            or request.META.get('HTTP_REFERER', '/openid2/')
    consumer = Consumer({}, get_store())
    authreq = consumer.begin('http://openid2.dapps.douban.com/server/yadis/')
    sregreq = sreg.SRegRequest(optional=['username', 'uid'],
            required=['email', 'groups'])
    authreq.addExtension(sregreq)
    http_domain = request.build_absolute_uri().replace(request.get_full_path(), '')
    verify_url = http_domain + '/openid2/verify?' + urlencode({'continue': continue_url})
    url = authreq.redirectURL(return_to=verify_url,
            realm=http_domain)

    return HttpResponseSeeOther(url)


def verify(request):
    return_to = request.GET.get('continue', '/openid2/')
    data = {k: v for k,v in request.GET.iteritems()}
    consumer = Consumer({}, get_store())
    http_domain = request.build_absolute_uri().replace(request.get_full_path(), '')
    authres = consumer.complete(data, http_domain + '/openid2/verify')
    resp = HttpResponseSeeOther(return_to)
    if authres.status is SUCCESS:
        user = authres.identity_url
        request.session[user] = session = binascii.b2a_hex(os.urandom(15))
        one_month = 3600 * 24 * 30
        resp.set_cookie(USER_COOKIE_NAME,
                json.dumps(dict(openid=user, session=session)),
                expires=one_month)
    return resp


@require_login
def logout(request):
    continue_url = request.GET.get('continue') or request.META.get('HTTP_REFERER', '/')
    http_domain = request.build_absolute_uri().replace(request.get_full_path(), '')
    this_url = http_domain + continue_url.replace(http_domain, '')
    openid2_logout_url = "http://openid2.dapps.douban.com/auth/logout/?next=%s" % this_url
    resp = HttpResponseSeeOther(openid2_logout_url)
    resp.delete_cookie(USER_COOKIE_NAME)
    session = request.openid
    if session:
        user = session['openid']
        if request.session.has_key(user):
            del request.session[user]
    return resp


@require_login
def index(request):
    session = request.openid
    if not session:
        return HttpResponse('Oops! No session! Are you kiding?', mimetype='text/plain')
    return HttpResponse('Hi there, %s' % request.uid, mimetype='text/plain')
