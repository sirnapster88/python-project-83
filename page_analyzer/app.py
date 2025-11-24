import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from .checker import create_check
from .repository import ChecksRepository, UrlsRepository
from .validator import validate

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")

repo = UrlsRepository(app.config["DATABASE_URL"])
checks_repo = ChecksRepository(app.config["DATABASE_URL"])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls")
def urls():
    urls = repo.get_url_with_checks()
    return render_template("/urls.html", urls=urls)


@app.route("/urls", methods=["POST"])
def create_url_from_index():
    url = request.form.get("url")

    errors = validate(url)

    existing_url = repo.find_by_name(url)
    if existing_url:
        flash("Страница уже существует", "error")
        return redirect(url_for("show_urls", id=existing_url["id"]))

    if errors:
        for error in errors.values():
            flash(error, "error")
            return render_template("index.html", url=url, errors=errors), 422  # noqa: E501

    saved_id = repo.save(url)

    flash("Страница успешно добавлена", "success")
    return redirect(url_for("show_urls", id=saved_id))


@app.route("/urls/<int:id>")
def show_urls(id):
    url = repo.find(id)
    if not url:
        flash("Страница не найдена", "error")
        return redirect(url_for("urls"))

    checks = checks_repo.get_checks_by_url_id(id)

    return render_template("show_urls.html", url=url, checks=checks)


@app.route("/urls/<int:id>/checks", methods=["POST"])
def check_url(id):
    url = repo.find(id)
    if not url:
        flash("Страница не найдена", "error")
        return redirect(url_for("urls"))

    check_data = create_check(url["name"])

    if check_data:
        check_id = checks_repo.create_check(id, check_data)
        if check_id:
            flash("Страница успешно проверена", "success")
        else:
            flash("Ошибка при сохранении результатов проверки", "error")
    else:
        flash("Произошла ошибка при проверке", "error")

    return redirect(url_for("show_urls", id=id))


if __name__ == "__main__":
    app.run(debug=True)
