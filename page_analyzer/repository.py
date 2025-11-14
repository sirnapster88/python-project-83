import psycopg

from psycopg.rows import dict_row

#def get_db(app):
#    database_url = app.config['DATABASE_URL']
#    return psycopg.connect(database_url)


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
       
