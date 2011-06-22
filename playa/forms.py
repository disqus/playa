from flaskext.wtf import Form, TextField, Required

class NewPlaylistForm(Form):
    name = TextField('Name', validators=[Required()])

class EditPlaylistForm(Form):
    name = TextField('Name', validators=[Required()])