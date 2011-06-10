from playa import app

@app.context_processor
def player():
    return {
        'current_song': app.player.get_current_song(),
        'player': app.player,
    }
