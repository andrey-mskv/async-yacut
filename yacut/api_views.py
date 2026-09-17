from .models import URLMap
from flask import jsonify, request
from . import app, db
from .views import get_unique_short_id
from .error_handlers import InvalidAPIUsage

import re

SHORT_ID_PATTERN = re.compile(r'^[A-Za-z0-9]+$')


def validate_custom_id(short):
    # if len(short) > 16:
    #     return 'Указанное имя не может быть длиннее 16 символов'
    if len(short) > 16 or not SHORT_ID_PATTERN.match(short):
        return 'Указано недопустимое имя для короткой ссылки'
    return None


@app.route('/api/urls/', methods=['GET'])
def get_urls():
    # Запросить список объектов.
    urls = URLMap.query.all()

    urls_list = [url.to_dict() for url in urls]
    return jsonify({'opinions': urls_list}), 200


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', status_code=404)
    return jsonify({'url': url_map.original}), 200


@app.route('/api/id/', methods=['POST'])
def create_short_url():
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')

    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    short = data.get('custom_id')
    if short:
        error = validate_custom_id(short)
        if error:
            return jsonify({'message': error}), 400
        if URLMap.query.filter_by(short=short).first():
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
    else:
        short = get_unique_short_id(6)

    url = URLMap()
    url.from_dict({'original': data['url'], 'short': short})
    # либо прямой url = URLMap(original=data['url'], short=short)
    db.session.add(url)
    db.session.commit()

    return (
        jsonify(
            {
                'url': url.original,
                'short_link': request.host_url + url.short,
            }
        ),
        201,
    )
