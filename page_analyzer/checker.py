import requests
from bs4 import BeautifulSoup


def get_check_info(url):
    try:
        # осуществление запроса get на url
        response = requests.get(url, timeout=10)
        # получение статус ответа (с исключением 4хх и 5хх ошибок)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Ошибка при проверке URL {url}: {e}")
        return None
    
    # создание парсера BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # получение тега h1
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text().strip() if h1_tag else ""

    # получение тега title
    title_tag = soup.find("title")
    title = title_tag.get_text().strip() if title_tag else ""

    # получение meta
    meta_description = soup.find("meta", attrs={"name": "description"})
    description = meta_description.get("content").strip() if meta_description else ""  # noqa: E501

    status_code = response.status_code

    return {"status_code": status_code, "h1": h1, "title": title, "description": description}  # noqa: E501
  