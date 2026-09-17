from flask_wtf import FlaskForm
from wtforms import URLField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, Optional, URL, Regexp
from flask_wtf.file import MultipleFileField, FileSize, FileRequired


class YaCutForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Введите корректную ссылку'),
            Length(1, 2048),
        ],
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(
                max=16,
                message='Не более 16 символов.',
            ),
            Optional(),
            Regexp(
                r'^[A-Za-z0-9]+$',
                message=('Указано недопустимое имя для короткой ссылки'),
            ),
        ],
    )
    submit = SubmitField('Создать')


class YaCutAddFilesForm(FlaskForm):
    files = MultipleFileField(
        validators=[
            FileRequired(message='Добавьте хотя бы один файл.'),
            FileSize(
                max_size=10 * 1024 * 1024,
                message='Размер файла не должен превышать 10 МБ.',
            ),
        ],
    )
    submit = SubmitField('Загрузить')
