import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
import sqlite3
import re
import requests

class ContestBot:
    def __init__(self, token_file, db_file):
        # Инициализация базы данных SQLite
        self.db_file = db_file  # Сохраняем путь к файлу базы данных в атрибуте
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.create_table()


        self.token = self.read_token(token_file)
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)

    def check_vk_link(self, link):
        # Проверяем, является ли ссылка на пост в ВКонтакте
        if not link.startswith("https://vk.com/"):
            return False, "Это не ссылка на ВКонтакте"

        return True, "Ссылка валидна"

    def create_table(self):
        # Создание таблицы для хранения ответов и баллов пользователей
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_responses (
                               user_id INTEGER PRIMARY KEY,
                               stage_1_response TEXT,
                               stage_2_response TEXT,
                               stage_4_response TEXT,
                               stage_5_response TEXT,
                               score INTEGER DEFAULT 0)''')
        self.conn.commit()

    def save_response(self, user_id, stage, response):
        # Сохранение ответа пользователя в базе данных
        stage_column = f"stage_{stage}_response"
        self.cursor.execute(f"INSERT OR REPLACE INTO user_responses (user_id, {stage_column}) VALUES (?, ?)",
                            (user_id, response))
        self.conn.commit()

    def update_score(self, user_id, score):
        # Обновление баллов пользователя в базе данных
        current_score = self.get_score(user_id)
        new_score = current_score + score
        self.cursor.execute("UPDATE user_responses SET score=? WHERE user_id=?", (new_score, user_id))
        self.conn.commit()

    def get_score(self, user_id):
        # Получение текущего балла пользователя из базы данных
        self.cursor.execute("SELECT score FROM user_responses WHERE user_id=?", (user_id,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return 0


    def close(self):
        # Закрытие соединения с базой данных
        self.conn.close()

    def read_token(self, token_file):
        with open(token_file, "r") as file:
            return file.read().strip()

    def start_bot(self):
        for event in self.longpoll.listen():
            try:
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.text.lower() in ["/start", "поехали"]:
                        self.start_contest(event.user_id)
            except Exception as e:
                print(e)

    def start_contest(self, user_id):
        self.send_message(user_id, "Приветствуем тебя, Первый! Сегодня стартует масштабный квест первичных отделений. Мы приглашаем тебя и твою команду выполнить творческие задания. Победу одержат самые дружные и активные первички!")

        # Проведение 5 этапов конкурса
        for i in range(1, 6):
            if i == 1:
                self.stage_1(user_id)
            elif i == 2:
                self.stage_2(user_id)
            elif i == 3:
                self.stage_3(user_id)
            elif i == 4:
                self.stage_4(user_id)
            elif i == 5:
                self.stage_5(user_id)

    def send_message(self, user_id, message):
        self.vk.messages.send(user_id=user_id, message=message, random_id=random.randint(1, 2**31))

    def stage_1(self, user_id):
        # Задание 1: Сними видео и отправь ссылку
        self.send_message(user_id, "1. Сними видео до 1 минуты с ответом на вопрос: «Что для меня Движение Первых?» Размести ролик на своей страничке ВК/сообществе отделения с тегами #ДвижениеПервых59 #КвестОтделений59. Проследи, чтобы страничка была открытой! Отправь ссылку на свой ролик нашему чат-боту.")

        # Ожидание ответа от пользователя
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.user_id == user_id:
                    response = event.text.strip()  # Получаем текст сообщения от пользователя

                    # Проверка ссылки на ВКонтакте
                    is_vk_link, reason = self.check_vk_link(response)
                    if is_vk_link:
                        # Сохранение ответа в базе данных и начисление баллов
                        self.save_response(user_id, 1, response)
                        self.update_score(user_id, 5)

                        # Переход на следующий этап
                        self.send_message(user_id, "Отлично! Вы успешно завершили первый этап конкурса. Переходим к следующему этапу.")
                        break  # Завершаем цикл после успешной обработки ответа
                    else:
                        # В случае неверной ссылки, отправляем пользователю сообщение с причиной и продолжаем ожидать ответа
                        self.send_message(user_id, f"К сожалению, ваша ссылка не является ссылкой на ВКонтакте. Причина: {reason}")

    def stage_2(self, user_id):
        # Задание 2: Сделай креативную фотографию
        self.send_message(user_id, "2. Моё первичное отделение. Сделай креативную фотографию своего первичного отделения. На фотографии должны быть представлены участники и ваш председатель. Опубликуй её на своей страничке ВК/сообществе отделения с хэштегами #ДвижениеПервых59 #КвестОтделений59. Проследи, чтобы страничка была открытой! Отправь ссылку на пост с фото нашему чат-боту.")
        # Здесь нужно реализовать логику проверки отправленной ссылки

    def stage_3(self, user_id):
        # Задание 3: Викторина
        pass  # Здесь будет реализовано задание в виде викторины

    def stage_4(self, user_id):
        # Задание 4: Создай презентацию
        pass  # Здесь будет реализовано задание с презентацией

    def stage_5(self, user_id):
        # Задание 5: Социально-значимое дело
        pass  # Здесь будет реализовано задание социально-значимого дела

    # Другие методы для выполнения различных этапов конкурса

# Создаем экземпляр бота и запускаем его
if __name__ == "__main__":
    bot = ContestBot("Token.txt", "contest_data.db")
    bot.start_bot()
    bot.close()
