#file database_handler.py
import sqlite3

class DatabaseHandler:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_responses (
                               user_id INTEGER PRIMARY KEY,
                               stage_1_response TEXT,
                               stage_2_response TEXT,
                               stage_4_response TEXT,
                               stage_5_response TEXT,
                               score INTEGER DEFAULT 0)''')
        self.conn.commit()

    def save_response(self, user_id, stage, response):
        stage_column = f"stage_{stage}_response"
        self.cursor.execute(f"SELECT COUNT(*) FROM user_responses WHERE user_id=?", (user_id,))
        count = self.cursor.fetchone()[0]

        if count == 0:
            self.cursor.execute(f"INSERT INTO user_responses (user_id, {stage_column}) VALUES (?, ?)",
                                (user_id, response))
        else:
            self.cursor.execute(f"UPDATE user_responses SET {stage_column}=? WHERE user_id=?", (response, user_id))

        self.conn.commit()

    def get_score(self, user_id):
        """
        Возвращает количество баллов, набранных пользователем с заданным идентификатором.

        Parameters:
        - user_id (int): Идентификатор пользователя.

        Returns:
        - int: Количество баллов пользователя.
        """
        self.cursor.execute("SELECT score FROM user_responses WHERE user_id=?", (user_id,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return 0

    def update_score(self, user_id, score):
        current_score = self.get_score(user_id)
        new_score = current_score + score
        self.cursor.execute("UPDATE user_responses SET score=? WHERE user_id=?", (new_score, user_id))
        self.conn.commit()

    def save_presentation_link(self, user_id, link):
        self.cursor.execute("UPDATE user_responses SET stage_4_response=? WHERE user_id=?", (link, user_id))
        self.conn.commit()

    def get_score(self, user_id):
        self.cursor.execute("SELECT score FROM user_responses WHERE user_id=?", (user_id,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return 0

    def close(self):
        self.conn.close()
