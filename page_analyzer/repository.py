import psycopg
import requests

from psycopg.rows import dict_row 


class UrlsRepository:
    def __init__(self, db_url):
        self.db_url = db_url
    
    def _get_connection(self):
        return psycopg.connect(self.db_url)

    def get_urls(self):
        conn = self._get_connection()
        try:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute('SELECT * FROM urls')
                return cur.fetchall()
        finally:
            conn.close()

    def find(self, id):
        conn = self._get_connection()
        try:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """SELECT * FROM urls WHERE id = %s""",
                    (id,)
                )
                return cur.fetchone()
        finally:
            conn.close()
    
    def find_by_name(self, name):
        conn = self._get_connection()
        try:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """SELECT * FROM urls where name = %s""",
                    (name,)
                )
                return cur.fetchone()
        finally:
            conn.close()


    def save(self, url_data):
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO urls (name) VALUES (%s) RETURNING id""",
                    (url_data['name'],)
                )
                saved_id = cur.fetchone()[0]
                conn.commit()
            return saved_id
        finally:
            conn.close()
       

class ChecksRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def _get_connection(self):
        return psycopg.connect(self.db_url)

    
    def create_check(self, url_id, url_name):
        conn = self._get_connection()
        try:
            response = requests.get(url_name, timeout=10)
            response.raise_for_status()
            status_code = response.status_code
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO url_checks (url_id, status_code) 
                        VALUES (%s, %s) RETURNING id""",
                    (url_id, status_code) 
                )
                check_id = cur.fetchone()[0]
                conn.commit()
            return check_id
        finally:
            conn.close()
    
    def get_checks_by_url_id(self, url_id):
        conn = self._get_connection()
        try:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """SELECT * FROM url_checks
                        WHERE url_id = %s
                        ORDER BY id DESC""",
                    (url_id,)    
                )
                return cur.fetchall()
        finally:
            conn.close()
                