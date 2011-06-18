from playa import app
from playa.web.helpers import get_now_playing

@app.context_processor
def player():
    return {
        'now_playing': get_now_playing(),
        'total_songs': app.player.get_num_songs(),
        'playlist_songs': app.player.get_num_playlist_songs(),
        'player': app.player,
    }
