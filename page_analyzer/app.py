import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from .repository import ChecksRepository, UrlsRepository
from .validator import validate

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = UrlsRepository(app.config['DATABASE_URL'])
checks_repo = ChecksRepository(app.config['DATABASE_URL'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/urls')
def urls():
    urls = repo.get_urls()
    return render_template('/urls.html', urls=urls)

@app.route('/urls', methods = ['POST'])
@app.route('/', methods=['POST'])
def create_url():
    url = request.form.get('url')
    url_data = {
        'name': url,
    }

    errors = validate(url_data)

    if not errors:
        existing_url = repo.find_by_name(url)
        if existing_url:
            flash("Страница уже существует", 'error')
            return redirect(url_for('show_urls', id=existing_url['id']))

    if errors:
        for field, error in errors.items():
            flash(f"{field}: {error}", 'error')
        if request.path == '/':
            return render_template('index.html', url_data=url_data, errors=errors), 422
        else:
            return render_template('urls.html', url_data=url_data, errors=errors), 422

    saved_id = repo.save(url_data)

    flash("Страница успешно добавлена", 'success')
    return redirect(url_for('show_urls', id=saved_id))

@app.route('/urls/<int:id>')
def show_urls(id):
    url = repo.find(id)
    if not url:
        flash('Страница не найдена','error')
        return redirect(url_for('urls'))

    checks = checks_repo.get_checks_by_url_id(id)

    return render_template('show_urls.html', url=url, checks=checks)


@app.route('/urls/<int:id>/checks', methods = ['POST'])
def check_url(id):
    url = repo.find(id)
    if not url:
        flash('Страница не найдена','error')
        return redirect(url_for('urls'))


    check_id = checks_repo.create_check(id, url['name'])

    if check_id:
        flash("Страница успешно проверена",'success')
    else:
        flash("Произошла ошибка при проверке",'error')

    return redirect(url_for('show_urls', id=id))


if __name__ == '__main__':
    app.run(debug=True)
