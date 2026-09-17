from flask import (
    render_template,
    redirect,
    flash,
    get_flashed_messages,
    url_for,
)

from . import app, db

import secrets
import string

from .forms import YaCutForm, YaCutAddFilesForm
from .models import URLMap
from .yandex import async_upload_files_to_yadisk


# Генератор случайной строки для короткой ссылки, a-z , A-Z, 0-9
def get_unique_short_id(length: int = 6):
    characters = string.ascii_letters + string.digits
    result = ''.join(secrets.choice(characters) for _ in range(length))
    return result


@app.route('/', methods=['GET', 'POST'])
def index():
    form = YaCutForm()
    short_links = get_flashed_messages(category_filter=['short_link'])
    if form.validate_on_submit():
        if form.custom_id.data:
            short_id = form.custom_id.data
            if (
                short_id == 'files'
                or URLMap.query.filter_by(short=short_id).first()  # noqa: W503
            ):
                form.custom_id.errors.append(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
                return render_template('yacut.html', form=form)
        else:
            short_id = get_unique_short_id()
            while URLMap.query.filter_by(short=short_id).first():
                short_id = get_unique_short_id()

        url_map = URLMap(
            short=short_id,
            original=form.original_link.data,
        )
        db.session.add(url_map)
        db.session.commit()
        short_link = url_for(
            'redirect_to_original_link', short_id=short_id, _external=True
        )
        # Сохраняем короткую ссылку в сессию
        flash(short_link, 'short_link')
        # Перенаправляем пользователя на главную
        return redirect(url_for('index'))
    return render_template(
        'yacut.html',
        form=form,
        short_link=short_links[0] if short_links else None,
    )


@app.route('/files', methods=['GET', 'POST'])
async def add_files():
    form = YaCutAddFilesForm()

    if form.validate_on_submit():
        result = await async_upload_files_to_yadisk(form.files.data)

        for url, filename in result:
            short_id = get_unique_short_id()

            while URLMap.query.filter_by(short=short_id).first():
                short_id = get_unique_short_id()

            url_map = URLMap(
                short=short_id,
                original=url,
            )

            db.session.add(url_map)

            short_link = url_for(
                'redirect_to_original_link',
                short_id=short_id,
                _external=True,
                # _scheme='https',
            )
            # Сохраняем короткую ссылку в сессию
            flash((filename, short_link), 'short_link')

        db.session.commit()
        # Перенаправляем пользователя на главную
        return redirect(url_for('add_files'))

    short_links = get_flashed_messages(
        category_filter=['short_link'],
    )

    return render_template(
        'add_files.html',
        form=form,
        short_links=short_links if short_links else None,
    )


@app.route('/<short_id>')
def redirect_to_original_link(short_id):
    link = URLMap.query.filter_by(short=short_id).first_or_404()
    response = redirect(link.original, code=302)
    response.headers['Referrer-Policy'] = (
        'no-referrer'  # фикс для Chrome при редиректе на yandex
    )
    return response
