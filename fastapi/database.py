import pymysql
import mariadb


class MariaDB:
    conn = None
    cur = None

    def __init__(self, host, user, password, db, port):
        try:
            conn = mariadb.connect(host=host, user=user, password=password, db=db, port=port, )
            self.conn = conn
            self.cur = self.conn.cursor()
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")

    def insert_news(self, title, detail, url, press, journalist, ):
        sql = "insert into news_article_info(title,detail,url,press,journalist) values (?,?,?,?,?)"
        try:
            self.cur.execute(sql, (title, detail, url, press, journalist))
        except mariadb.Error as e:
            print(f"Error: {e}")
        self.conn.commit()

    def lookup_news_url(self, url):
        sql = "select summary from news_article_info where url=?"
        data = 'null'
        try:
            self.cur.execute(sql,(url,))
        except mariadb.Error as e:
            print(f'Error {e}')
        data = self.cur.fetchall()
        return data





#테스트 문
def main():
    print('it\'s main')
    host = '127.0.0.1'
    username = 'root'
    db_name = 'news'
    password = 'root'
    port = 3306
    db = MariaDB(host, username, password, db_name, port)
    # db.insert_news('충격 ', '아무일도 없었다.', '없음', '실제로 없는 ', '아무도')
    print(db.lookup_news_url('없음')[0][0])


if __name__ == '__main__':
    main()
