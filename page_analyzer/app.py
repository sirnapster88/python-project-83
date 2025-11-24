import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer.checker import get_check_info
from page_analyzer.normalizer import normalize_url
from page_analyzer.repository import ChecksRepository, UrlsRepository
from page_analyzer.validator import validate

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
    return render_template("urls.html", urls=urls)


@app.route("/urls", methods=["POST"])
def create_url():
    url = request.form.get("url")

    errors = validate(url)
    for error in errors.values():
        flash(error, "error")
        return render_template("index.html", url=url, errors=errors), 422  # noqa: E501

    normalized_url = normalize_url(url)

    existing_url = repo.find_by_name(normalized_url)
    if existing_url:
        flash("Страница уже существует", "error")
        return redirect(url_for("show_urls_info", id=existing_url["id"]))

    saved_id = repo.save(normalized_url)

    flash("Страница успешно добавлена", "success")
    return redirect(url_for("show_urls_info", id=saved_id))


@app.route("/urls/<int:id>")
def show_urls_info(id):
    url = repo.find(id)
    if not url:
        flash("Страница не найдена", "error")
        return redirect(url_for("urls"))

    checks = checks_repo.get_checks_by_url_id(id)

    return render_template("url_info.html", url=url, checks=checks)


@app.route("/urls/<int:id>/checks", methods=["POST"])
def check_url(id):
    url = repo.find(id)
    if not url:
        flash("Страница не найдена", "error")
        return redirect(url_for("urls"))

    check_data = get_check_info(url["name"])

    if check_data:
        check_id = checks_repo.create_check(id, check_data)
        if check_id:
            flash("Страница успешно проверена", "success")
        else:
            flash("Ошибка при сохранении результатов проверки", "error")
    else:
        flash("Произошла ошибка при проверке", "error")

    return redirect(url_for("show_urls_info", id=id))


if __name__ == "__main__":
    app.run(debug=True)
