from GNLP.corpus import Corpus
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm

from wtforms import (StringField, SubmitField)

app = Flask(__name__)
app.config['SECRET_KEY'] = "My_SecRet"
corp = Corpus()

@app.before_first_request
def before_first_request():
    corp.from_file("sample.txt")
    corp.file2sequence(preprocess=True)
    corp.count_tokens()

class TextInput(FlaskForm):
    text = StringField("შეიყვანე სიტყვა ან წინადადება")
    submit = SubmitField('დამუშავება')

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    text = None
    form = TextInput()

    if form.validate_on_submit():
        flash('მიმდინარეობს ინფორმაციის დამუშავება')
        text = form.text.data
        sep = text.split()
        checked = []
        for word in sep:
            checked.append(corp.correction(word))

        session['checked'] = " ".join(checked)
        print(session['checked'], checked)
        return redirect(url_for('index'))

    return render_template('home.html', form=form, text=text)

app.run(port=5005, debug=True)
