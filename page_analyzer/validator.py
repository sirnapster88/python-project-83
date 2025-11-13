from urllib.parse import urlparse


def validate(url_data):
    errors = {}
    url = url_data.get('name','').strip()

    if not url:
        errors['name'] = "Не может быть пустым"
        return errors

    if len(url) > 255:
        errors['name'] = "URL не должен превышать 255 символов"
        return errors

    if not is_valid_url(url):
        errors['name'] = "Некорректный URL"
        
    return errors

def is_valid_url(url):
    result = urlparse(url)
    try:
        return (result.scheme in ['http', 'https'] and
                result.netloc != ''
                )
    except Exception:
        return False


