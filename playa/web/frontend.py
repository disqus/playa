"""
playa.web.frontend
~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from playa import app
from playa.db import db

from collections import defaultdict
from flask import render_template, redirect, request, flash, url_for

from playa.forms import NewPlaylistForm, EditPlaylistForm
from playa.web.oauth import login_required


@app.before_request
def check_state():
    if request.path.startswith('/static/'):
        return

    if not app.player.is_ready():
        return render_template('loading.html')


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


## API methods (move to api.py)
@app.route('/play/random', methods=['GET', 'POST'])
@login_required
def play_random():
    app.player.play_random()

    return redirect('/')


@app.route('/play/filename', methods=['GET', 'POST'])
@login_required
def play_filename():
    if 'filename' in request.form:
        for filename in request.form.getlist('filename'):
            app.player.play_filename(filename)

    return redirect('/')


@app.route('/play/album', methods=['GET', 'POST'])
@login_required
def play_album():
    songs_by_artist = app.player.list_by_metadata(key='artist', value=request.form['artist'])
    album_list = request.form.getlist('album')
    for filename in songs_by_artist:
        metadata = app.player.get_metadata(filename)
        if metadata.get('album') in album_list:
            app.player.play_filename(filename)

    return redirect('/')


@app.route('/queue/clear', methods=['GET', 'POST'])
@login_required
def clear_queue():
    app.player.clear_queue()

    return redirect('/')


@app.route('/play/next', methods=['GET', 'POST'])
@login_required
def next_track():
    app.player.skip_song()

    return redirect('/')


@app.route('/play', methods=['GET', 'POST'])
@login_required
def start_playing():
    if not app.player.queue:
        # # can't play
        # return
        app.player.play_random()

    app.player.start_audio()

    return redirect('/')


@app.route('/stop', methods=['GET', 'POST'])
@login_required
def stop_playing():
    app.player.stop_audio()

    return redirect('/')


## Browse panes
@app.route('/artists', methods=['GET'])
@login_required
def artists():
    artists = sorted(app.player.list_by_metadata(key='artist'), key=lambda x: x.lower())
    return render_template('browse/artists.html', **{
        'artists': artists,
    })


@app.route('/artists/<artist>', methods=['GET'])
@login_required
def show_artist(artist):
    songs = list(app.player.list_by_metadata(key='artist', value=artist))

    albums = defaultdict(int)
    for song in songs:
        metadata = app.player.get_metadata(song)
        if 'album' in metadata:
            albums[metadata['album']] += 1

    return render_template('browse/artist_details.html', **{
        'artist': artist,
        'albums': albums,
        'songs': songs,
    })


@app.route('/genres', methods=['GET'])
@login_required
def genres():
    genres = sorted(app.player.list_by_metadata(key='genre'), key=lambda x: x.lower())
    return render_template('browse/genres.html', **{
        'genres': genres,
    })


@app.route('/genres/<genre>', methods=['GET'])
def show_genre(genre):
    songs = app.player.list_by_metadata(key='genre', value=genre)

    return render_template('browse/genre_details.html', **{
        'genre': genre,
        'songs': songs,
    })


## Playlists
@app.route('/playlists', methods=['GET'])
@login_required
def playlists():
    return render_template('playlists/index.html', **{
        'playlists': db['playlists'].values(),
    })


@app.route('/playlists/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit_playlist(id):
    playlist = db['playlists'][id]
    form = EditPlaylistForm(name=playlist.name)
    if form.validate_on_submit():
        playlist = db['playlists'].new(name=form.name.data)

        flash("Success")

        return redirect(url_for('edit_playlist', id=playlist.id))

    return render_template('playlists/edit.html', **{
        'playlist': playlist,
        'form': form,
    })


@app.route('/playlists/add', methods=['GET', 'POST'])
@login_required
def add_playlist():
    form = NewPlaylistForm()
    if form.validate_on_submit():
        playlist = db['playlists'].new(name=form.name.data)

        flash("Success")

        return redirect(url_for('edit_playlist', id=playlist.id))

    return render_template('playlists/add.html', **{
        'form': form,
    })


## Search
@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q')

    if query:
        results = [
            (filename, app.player.get_metadata(filename))
            for filename, weight in app.player.find_song(request.args['q'])
        ]
    else:
        results = None

    return render_template('search.html', **{
        'query': query,
        'results': results,
    })
