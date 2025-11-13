import psycopg

from psycopg.rows import dict_row

def get_db(app):
    try:
        database_url = app.config['DATABASE_URL']
        if database_url.startswith('postgresql://'):
            if 'sslmode' not in database_url:
                database_url += "?sslmode=require"
        print("Успешно подключился к БД")
        return psycopg.connect(database_url)
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}") 



class UrlsRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_urls(self):
        with self.conn.cursor() as cur:
            cur.execute('SELECT * FROM urls')
            return cur.fetchall()

    def find(self, id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """SELECT * FROM urls WHERE id = %s""",
                    (id,)
                )
                return cur.fetchone()
            print ("Запись найдена!")
        except Exception as e:
            print(f"Ошибка поиска:{e}")
            raise


    def save(self, url_data):
        try: 
            with self.conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO urls (name) VALUES (%s) RETURNING id""",
                    (url_data['name'],)
                )
                saved_id = cur.fetchone()[0]
            self.conn.commit()
            print("Запись добалвена!")
            return saved_id
        except Exception as e:
            print(f"Ошибка добавления в БД:{e}")
            raise
