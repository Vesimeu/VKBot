import sqlite3

# Подключаемся к базе данных (если она уже существует) или создаем новую
conn = sqlite3.connect("contest_data.db")

# Создаем курсор для выполнения операций с базой данных
cursor = conn.cursor()

# Создаем таблицу для хранения ответов и баллов пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS user_responses (
                    user_id INTEGER PRIMARY KEY,
                    stage_1_response TEXT,
                    stage_2_response TEXT,
                    stage_4_response TEXT,
                    stage_5_response TEXT,
                    score INTEGER DEFAULT 0)''')

# Фиксируем изменения в базе данных
conn.commit()

# Закрываем соединение с базой данных
conn.close()
