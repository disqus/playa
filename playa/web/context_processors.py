from playa import app

@app.context_processor
def player():
    return {
        'current_song': app.player.get_current_song(),
        'total_songs': app.player.get_num_songs(),
        'playlist_songs': app.player.get_num_playlist_songs(),
        'player': app.player,
    }
