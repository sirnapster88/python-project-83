import psycopg

from psycopg.rows import dict_row

def get_db(app):
    database_url = app.config['DATABASE_URL']
    return psycopg.connect(database_url)


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
            return cur.fetchone()
    
    def find_by_name(self, name):
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """SELECT * FROM urls where name = %s""",
                (name,)
            )
            return cur.fetchone()


    def save(self, url_data):
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO urls (name) VALUES (%s) RETURNING id""",
                (url_data['name'],)
            )
            saved_id = cur.fetchone()[0]
            self.conn.commit()
        return saved_id
       
