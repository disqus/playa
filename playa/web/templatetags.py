from playa import app

@app.template_filter('duration')
def duration(seconds):
    return '%s:%s' % (int(seconds / 60), ('0' + str(int(seconds % 60)))[-2:])