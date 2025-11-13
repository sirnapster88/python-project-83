import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from .repository import get_db, UrlsRepository
from .validator import validate

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

repo = UrlsRepository(get_db(app))

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
    print(f"Найдены ошибки:{errors}")

    if errors:
        for field, error in errors.items():
            flash(f"{field}: {error}", 'error')
        if request.path == '/':
            return render_template('index.html', url_data=url_data, errors=errors), 422
        else:
            return render_template('urls.html', url_data=url_data, errors=errors), 422
    
    repo.save(url_data)
    
    flash("Страница успешно добавлена", 'success')
    return redirect(url_for('urls'))


if __name__ == '__main__':
    app.run(debug=True)
