from playa import app

@app.context_processor
def player():
    return {
        'current_track': app.player.get_current_track(),
        'player': app.player,
    }
