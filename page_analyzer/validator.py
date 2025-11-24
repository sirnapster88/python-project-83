import validators
from urllib.parse import urlparse


def validate(url):
    errors = {}
    
    if not url or not url.strip():
        errors["name"] = "Не может быть пустым"
        return errors

    url = url.strip()

    if len(url) > 255:
        errors["name"] = "URL не должен превышать 255 символов"
        return errors

    if not validators.url(url):
        errors["name"] = "Некорректный URL"

    return errors
