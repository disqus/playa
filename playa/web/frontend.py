from playa import app

from collections import defaultdict
from flask import render_template, redirect, request

@app.before_request
def check_state():
    if not app.player.is_ready():
        return render_template('loading.html')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/play/random', methods=['GET', 'POST'])
def play_random():
    app.player.play_random()
    
    return redirect('/')

@app.route('/play/filename', methods=['GET', 'POST'])
def play_filename():
    if 'filename' in request.form:
        for filename in request.form.getlist('filename'):
            app.player.play_filename(filename)
    
    return redirect('/')

@app.route('/play/album', methods=['GET', 'POST'])
def play_album():
    songs_by_artist = app.player.list_by_metadata(key='artist', value=request.form['artist'])
    album_list = request.form.getlist('album')
    for filename in songs_by_artist:
        metadata = app.player.get_metadata(filename)
        if metadata.get('album') in album_list:
            app.player.play_filename(filename)
    
    return redirect('/')


@app.route('/playlist/clear', methods=['GET', 'POST'])
def clear_playlist():
    app.player.clear_playlist()
    
    return redirect('/')

@app.route('/play/next', methods=['GET', 'POST'])
def next_track():
    app.player.skip_song()
    
    return redirect('/')

@app.route('/play', methods=['GET', 'POST'])
def start_playing():
    app.player.start_playing()
    
    return redirect('/')

@app.route('/stop', methods=['GET', 'POST'])
def stop_playing():
    app.player.stop_playing()
    
    return redirect('/')

@app.route('/artists', methods=['GET'])
def artists():
    artists = sorted(app.player.list_by_metadata(key='artist'), key=lambda x: x.lower())
    return render_template('browse/artists.html', **{
        'artists': artists,
    })

@app.route('/artists/<artist>', methods=['GET'])
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

@app.route('/search', methods=['GET'])
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