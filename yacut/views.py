from flask import render_template, redirect

from . import app

import secrets
import string

from .forms import YaCutForm, YaCutAddFilesForm
from .models import URLMap


# Генератор случайной строки для короткой ссылки, a-z , A-Z, 0-9
def get_unique_short_id(length: int = 6):
    characters = string.ascii_letters + string.digits
    result = ''.join(secrets.choice(characters) for _ in range(length))
    return result


@app.route('/', methods=['GET', 'POST'])
def index():
    form = YaCutForm()
    if form.validate_on_submit():
        pass
    return render_template('yacut.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
def add_files():
    form = YaCutAddFilesForm()
    if form.validate_on_submit():
        pass
    return render_template('add_files.html', form=form)


@app.route('/<short_id>')
def redirect_to_original_link(short_id):
    link = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(link.original)
