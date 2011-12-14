"""
playa.web.oauth
~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import functools
import simplejson
import urllib
import urllib2

from flask import url_for, request, redirect, session

from playa import app, db


class Logout(Exception):
    pass


@app.errorhandler(Logout)
def logout_handler(error):
    try:
        del session['username']
    except KeyError:
        pass
    return redirect(url_for('oauth_authorize'))


def login_required(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('oauth_authorize'))
        return func(*args, **kwargs)
    return wrapped


@app.route('/oauth/authorize/')
def oauth_authorize():
    return redirect('https://disqus.com/api/oauth/2.0/authorize/?%s' % (urllib.urlencode({
        'client_id': app.disqus.public_key,
        'scope': 'read,write',
        'response_type': 'code',
        'redirect_uri': url_for('oauth_callback', _external=True),
    }),))


@app.route('/oauth/callback/')
def oauth_callback():
    code = request.args.get('code')
    error = request.args.get('error')
    if error or not code:
        # TODO: show error
        return redirect('/')

    req = urllib2.Request('https://disqus.com/api/oauth/2.0/access_token/', urllib.urlencode({
        'grant_type': 'authorization_code',
        'client_id': app.disqus.public_key,
        'client_secret': app.disqus.secret_key,
        'redirect_uri': url_for('oauth_callback', _external=True),
        'code': code,
    }))

    resp = urllib2.urlopen(req).read()

    data = simplejson.loads(resp)

    username = data['username']

    db['users'].new(username=username)

    session['username'] = username
    session.permanent = True

    return redirect('/')
