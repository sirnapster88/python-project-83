from urllib.parse import urlparse

import psycopg2
import requests
from bs4 import BeautifulSoup
from psycopg2.extras import RealDictCursor


class UrlsRepository:
    """Репозиторий для работы с БД Urls"""

    def __init__(self, db_url):
        self.db_url = db_url

    def _get_connection(self):
        # создание подключения
        return psycopg2.connect(self.db_url)

    def get_urls(self):
        # получение всей таблицы urls
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM urls")
                return cur.fetchall()
        finally:
            conn.close()

    def find(self, id):
        # поиск в таблице urls по id url
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""SELECT * FROM urls WHERE id = %s""", (id,))
                return cur.fetchone()
        finally:
            conn.close()

    def find_by_name(self, name):
        # поиск в таблице urls по имени url
        conn = self._get_connection()
        try:
            normalized_name = self._normalize_url(name)
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""SELECT * FROM urls where name = %s""", (normalized_name,))  # noqa: E501
                return cur.fetchone()
        finally:
            conn.close()

    def _normalize_url(self, url):
        try:
            parced = urlparse(url)
            normalized = f"{parced.scheme}://{parced.netloc}"
            return normalized
        except Exception:
            return url

    def save(self, url_data):
        # функция добавления новой записи в таблицу urls
        conn = self._get_connection()
        try:
            normalized_name = self._normalize_url(url_data["name"])
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO urls (name) VALUES (%s) RETURNING id""", (normalized_name,))  # noqa: E501
                saved_id = cur.fetchone()[0]
                conn.commit()
            return saved_id
        finally:
            conn.close()

    def get_url_with_checks(self):
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT
                            u.id,
                            u.name,
                            uc.created_at,
                            uc.status_code
                        FROM urls u
                        LEFT JOIN url_checks uc ON u.id=uc.url_id
                        AND uc.id = (SELECT MAX(id) FROM url_checks 
                        WHERE url_id = u.id)
                        ORDER BY u.id DESC"""
                )
                return cur.fetchall()
        finally:
            conn.close()


class ChecksRepository:
    """Репозиторий для работы с таблицей проверок url_checks"""

    def __init__(self, db_url):
        self.db_url = db_url

    def _get_connection(self):
        # создание подключения
        return psycopg2.connect(self.db_url)

    def create_check(self, url_id, url_name):
        # создание в таблице url_checks новой записи о проверке
        conn = self._get_connection()
        try:
            # осуществление запроса get на url
            response = requests.get(url_name, timeout=10)
            # получение статус ответа (с исключением 4хх и 5хх ошибок)
            response.raise_for_status()

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

            # выполнение записи в таблицу url_checks новых данных
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO url_checks 
                        (url_id, status_code, h1, title, description)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                    (url_id, status_code, h1, title, description),
                )
                check_id = cur.fetchone()[0]
                conn.commit()
            return check_id
        except Exception as e:
            print(f"Ошибка при создании проверки:{e}")
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO url_checks (url_id) VALUES (%s)
                        RETURNING ID""",
                        (url_id,),
                    )
                check_id = cur.fetchone()[0]
                conn.commit()
                return check_id
            except Exception as inner_e:
                print(f"Ошибка при создании пустой проверки:{inner_e}")
                return None
        finally:
            conn.close()

    def get_checks_by_url_id(self, url_id):
        # получение списка уже проведенных проверок по url
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """SELECT * FROM url_checks
                        WHERE url_id = %s
                        ORDER BY id DESC""",
                    (url_id,),
                )
                return cur.fetchall()
        finally:
            conn.close()
