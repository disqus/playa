from playa import app

from flask import render_template, redirect, request

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/play/random', methods=['POST'])
def play_random():
    app.player.play_random()
    
    return redirect('/')

@app.route('/play/filename', methods=['POST'])
def play_filename():
    if 'filename' in request.form:
        app.player.play_filename(request.form['filename'])
    
    return redirect('/')

@app.route('/play/next', methods=['POST'])
def next_track():
    app.player.play_next()
    
    return redirect('/')

@app.route('/stop', methods=['POST'])
def next_track():
    app.player.stop_playing()
    
    return redirect('/')

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