import validators


def validate(url):
    errors = {}

    url = url.strip()

    if not url:
        errors["name"] = "Не может быть пустым"
        return errors

    if len(url) > 255:
        errors["name"] = "URL не должен превышать 255 символов"
        return errors

    if not validators.url(url):
        errors["name"] = "Некорректный URL"

    return errors
