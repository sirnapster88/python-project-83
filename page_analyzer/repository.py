import psycopg

from psycopg.rows import dict_row

def get_db(app):
    return psycopg.connect(app.config['DATABASE_URL'])


class UrlsRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_urls(self):
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute('SELECT * FROM urls')
            return cur.fetchall()

    def find(self, id):
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """SELECT * FROM urls WHERE id = %s""",
                (id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None


    def save(self, url_data):
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO urls (name) VALUES (%s)""",
                (url_data['name'],)
            )
        self.conn.commit()
