import sqlite3
from prettytable import PrettyTable

def view_table(db_file, table_name):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Получаем имена столбцов
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]

    # Получаем данные из таблицы
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # Формируем таблицу для вывода
    table = PrettyTable(columns)
    for row in rows:
        table.add_row(row)

    # Выводим таблицу
    print(table)

    conn.close()

if __name__ == "__main__":
    # Укажите путь к файлу базы данных и имя таблицы
    db_file = "contest_data.db"
    table_name = "user_responses"
    view_table(db_file, table_name)
