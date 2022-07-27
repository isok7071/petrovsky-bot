import os
from re import sub
from time import time
import psycopg2
import psycopg2.extras
import telebot
username = '1233'
password = r'123'

bot = telebot.TeleBot(
    "TOKEN", parse_mode=None)
replacements_url = r"https://portal.petrocollege.ru/_api/Web/Lists/GetByTitle('Замены')/Items?$top=10&$orderby=Id desc"    


class db:
    def __init__(self):
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            print("БД подключена")
        except:
            print("\n\nОшибка с подключением к базе данных\n\n")

    def close_db(self):
        self.conn.close()

class Subscribe(db):
    def create(self, user_id, file, query_column):
        try:
            self.cursor.execute('INSERT INTO subscribe (user_id, schedule_type, query_column) VALUES (%s, %s, %s)', (user_id, file, query_column))
            self.conn.commit()
            self.close_db()
        except:
            self.close_db()
    
    def delete_by_user_id(self, user_id):
        try:
            self.cursor.execute('DELETE FROM subscribe WHERE user_id = %s', (user_id, ))
            self.conn.commit()
            self.close_db()
        except:
            self.close_db()


    def get_one_user_by_id(self, user_id):
        try:
            self.cursor.execute('SELECT * FROM subscribe WHERE user_id = %s', (user_id, ))
            result =  self.cursor.fetchone()
            self.close_db()
            return result
        except:
            self.close_db()
      
    def read(self):
        try:
            self.cursor.execute('SELECT * FROM subscribe')
            result =  self.cursor.fetchall()
            self.close_db()
            return result
        except:
            self.close_db()
    
    def count(self):
        try:
            self.cursor.execute('SELECT COUNT(id) FROM subscribe')
            result =  self.cursor.fetchall()
            self.close_db()
            return result
        except:
            self.close_db()


"""

class User_commands(db):
    def create(self, user_id, file, query_column):
        try:
            self.cursor.execute('INSERT INTO user_commands (user_id, query_column, schedule_type) VALUES (%s, %s, %s)', (user_id, query_column, file))
            self.conn.commit()
            self.close_db()
        except:
            self.close_db()
    
    def delete_by_user_id(self, user_id):
        try:
            self.cursor.execute('DELETE FROM user_commands WHERE user_id = %s', (user_id, ) )
            self.conn.commit()
            self.close_db()
        except:
            self.close_db()

    def get_one_user_by_id(self, user_id):
        try:
            self.cursor.execute('SELECT * FROM user_commands WHERE user_id = %s', (user_id, ))
            result =  self.cursor.fetchone()
            self.close_db()
            return result
        except:
            self.close_db()
      
    def read(self):
        try:
            self.cursor.execute('SELECT * FROM user_commands')
            result =  self.cursor.fetchall()
            self.close_db()
            return result
        except:
            self.close_db()
print(User_commands().get_one_user_by_id(1459498902)['schedule_type'])
"""