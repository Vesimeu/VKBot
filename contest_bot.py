#file contest_bot.py
import json
import os

import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
from database_handler import DatabaseHandler

class ContestBot:
    def __init__(self, token_file, db_file):
        self.db_handler = DatabaseHandler(db_file)

        self.token = self.read_token(token_file)
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)

    def check_vk_link(self, link):
        if not link.startswith("https://vk.com/"):
            return False, "Это не ссылка на ВКонтакте"
        return True, "Ссылка валидна"

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
    def create_keyboard(self, options):
        # Создаем клавиатуру с кнопками для вариантов ответов
        keyboard = {
            "one_time": True,
            "buttons": [
                [
                    {
                        "action": {
                            "type": "text",
                            "payload": "{\"button\": \"1\"}",
                            "label": option
                        },
                        "color": "default"
                    }
                ] for option in options
            ]
        }
        return keyboard

    def get_user_response(self, user_id):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.user_id == user_id:
                    response = event.text.strip()  # Получаем текст сообщения от пользователя

                    # Проверка ссылки на ВКонтакте
                    is_vk_link, reason = self.check_vk_link(response)
                    if is_vk_link:
                        return response, True, "Ссылка валидна"
                    else:
                        return None, False, f"К сожалению, ваша ссылка не является ссылкой на ВКонтакте. Причина: {reason}"

    def start_contest(self, user_id):
        self.send_message(user_id, "Приветствуем тебя, Первый! Сегодня стартует масштабный квест первичных отделений. Мы приглашаем тебя и твою команду выполнить творческие задания. Победу одержат самые дружные и активные первички!")

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

    def send_message(self, user_id, message, keyboard=None):
        # Отправка сообщения пользователю с возможностью прикрепления клавиатуры
        if keyboard is None:
            self.vk.messages.send(
                user_id=user_id,
                message=message,
                random_id=random.randint(1, 2 ** 31)
            )
        else:
            self.vk.messages.send(
                user_id=user_id,
                message=message,
                random_id=random.randint(1, 2 ** 31),
                keyboard=json.dumps(keyboard, ensure_ascii=False)
            )

    def stage_1(self, user_id):
        self.send_message(user_id,
                          "1. Сними видео до 1 минуты с ответом на вопрос: «Что для меня Движение Первых?» Размести ролик на своей страничке ВК/сообществе отделения с тегами #ДвижениеПервых59 #КвестОтделений59. Проследи, чтобы страничка была открытой! Отправь ссылку на свой ролик нашему чат-боту.")

        response, is_valid, reason = self.get_user_response(user_id)
        if is_valid:
            print(response)
            # Сохранение ответа в базе данных и начисление баллов
            self.db_handler.save_response(user_id, 1, response)
            self.db_handler.update_score(user_id, 5)

            # Переход на следующий этап
            self.send_message(user_id,
                              "Отлично! Вы успешно завершили первый этап конкурса. Переходим к следующему этапу.")
        else:
            # В случае неверной ссылки, отправляем пользователю сообщение с причиной
            self.send_message(user_id, reason)
    def stage_2(self, user_id):
        self.send_message(user_id,
                          "2. Моё первичное отделение. Сделай креативную фотографию своего первичного отделения. На фотографии должны быть представлены участники и ваш председатель. Опубликуй её на своей страничке ВК/сообществе отделения с хэштегами #ДвижениеПервых59 #КвестОтделений59. Проследи, чтобы страничка была открытой! Отправь ссылку на пост с фото нашему чат-боту.")

        response, is_valid, reason = self.get_user_response(user_id)
        if is_valid:
            # Сохранение ответа в базе данных и начисление баллов
            self.db_handler.save_response(user_id, 2, response)
            self.db_handler.update_score(user_id, 5)

            # Переход на следующий этап
            self.send_message(user_id,
                              "Отлично! Вы успешно завершили второй этап конкурса. Переходим к следующему этапу 'Викторина'.")
        else:
            # В случае неверной ссылки, отправляем пользователю сообщение с причиной
            self.send_message(user_id, reason)

    def stage_3(self, user_id):
        # Вопросы и ответы для викторины
        questions = [
            {
                "question": "Какие технологии используются для создания искусственного интеллекта?",
                "options": ["нейронные сети", "машинное обучение", "искусственные нейроны", "квантовые компьютеры"],
                "correct_answer": "нейронные сети"
            },
            {
                "question": "Какое животное является символом наставничества, педагогики и воспитания?",
                "options": ["енот", "пеликан", "филин", "медведь"],
                "correct_answer": "пеликан"
            },
            {
                "question": "Какому виду искусства посвящен проект Движения Первых «Школьная классика»?",
                "options": ["музыка", "изобразительное искусство", "театр", "кино"],
                "correct_answer": "театр"
            },
            {
                "question": "В какой стране возник вид спорта самбо?",
                "options": ["Япония", "СССР", "Великобритания", "Франция"],
                "correct_answer": "СССР"
            },
            {
                "question": "Как называется платформа, на которой можно получать волонтерские часы за добровольческую деятельность?",
                "options": ["госуслуги", "добро.ру", "будьвдвижении.рф", "национальныепроектыроссии.рф"],
                "correct_answer": "добро.ру"
            },
            {
                "question": "В чём была особенность первой российской газеты «Вести-Куранты», которая начала издаваться при Михаиле Романове?",
                "options": ["К ней был доступ только у царя и бояр", "Её печатали в Европе",
                            "Каждая её страница продавалась отдельно"],
                "correct_answer": "К ней был доступ только у царя и бояр"
            },
            {
                "question": "Какой символ используется для обозначения Юннатского движения?",
                "options": ["Зеленый листок", "Солнце", "Дерево", "Сова"],
                "correct_answer": "Зеленый листок"
            },
            {
                "question": "Как по нормам международной дипломатии определяются отношения волка и зайца из «Ну, погоди!»?",
                "options": ["Сепаратизм", "Конфликт", "Милитаризм", "Нейтралитет"],
                "correct_answer": "Конфликт"
            },
            {
                "question": "В каком городе России вы можете увидеть Храм всех религий?",
                "options": ["Суздаль", "Самара", "Казань", "Москва"],
                "correct_answer": "Казань"
            },
            {
                "question": "Что из этого не относится к утвержденным государственным символам?",
                "options": ["герб", "гимн", "флаг", "Конституция"],
                "correct_answer": "Конституция"
            },
            {
                "question": "Как называется проект Движения Первых, посвященный проведению тренировок вместе с известными спортсменами?",
                "options": ["Вызов Первых", "Пилоты будущего", "Открытые тренировки", "Игры будущего"],
                "correct_answer": "Открытые тренировки"
            },
            {
                "question": "С какого возраста лицо может самостоятельно заключать трудовой договор?",
                "options": ["с 12 лет", "с 14 лет", "с 16 лет", "с 18 лет"],
                "correct_answer": "с 16 лет"
            }
        ]

        # Отправляем вопросы по очереди
        for idx, question_data in enumerate(questions, start=1):
            question_text = f"{idx}. {question_data['question']}\n"
            options_text = "\n".join([f"{chr(97 + i)}. {option}" for i, option in enumerate(question_data['options'])])

            message = f"{question_text}{options_text}"
            self.send_message(user_id, message, keyboard=self.create_keyboard(question_data['options']))

            # Ожидаем ответа от пользователя
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    if event.user_id == user_id:
                        user_answer = event.text.strip().lower()
                        correct_answer = question_data['correct_answer'].lower()

                        # Проверяем ответ пользователя
                        if user_answer == correct_answer:
                            # Начисляем балл за правильный ответ
                            self.db_handler.update_score(user_id, 1)
                            self.send_message(user_id, "Правильно! Вы заработали 1 балл.")
                        else:
                            self.send_message(user_id, f"Неправильно. Правильный ответ: {correct_answer}")

                        break  # Переходим к следующему вопросу
    def stage_4(self, user_id):
        self.send_message(user_id, "Создай презентацию из 4-5 слайдов в формате .pptx или .pdf. "
                                   "Отрази деятельность твоего первичного отделения и совета Первых первичного отделения. "
                                   "Отправь сюда ссылку на яндекс или гугл диск с презентацией. !")
        self.send_message(user_id, "Загрузите вашу презентацию на Яндекс Диск или Google Диск и отправьте ссылку сюда.")

        # Ожидаем ответа от пользователя
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.user_id == user_id:
                    response = event.text.strip()  # Получаем текст сообщения от пользователя

                    # Проверка ссылки на яндекс или гугл диск
                    if "yandex" in response.lower() or "google" in response.lower():
                        # Сохранение ссылки в базе данных
                        self.db_handler.save_presentation_link(user_id, response)
                        # Начисление баллов
                        self.db_handler.update_score(user_id, 5)
                        self.send_message(user_id, "Спасибо! Ваша презентация успешно отправлена.")
                        break
                    else:
                        self.send_message(user_id, "Пожалуйста, отправьте ссылку на презентацию в формате Яндекс Диск или Google Диск.")

    def stage_5(self, user_id):
        self.send_message(user_id,
                          "5. Социально-значимое дело. Придумай и реализуй со своими единомышленниками полезное дело. Например, можно смастерить скворечник, прибраться во дворе, помочь бабушке из соседнего подъезда. Размести пост на своей страничке или в группе отделения с описанием и фотографией социально-значимого дела. Это может быть общий пост для всей вашей команды. Не забудьте указать своё первичное отделение и хештеги: #ДвижениеПервых59 #КвестОтделений59 Ждём ссылку от каждого участника команды, чтобы чат-бот посчитал вам баллы. Отправляй скорее!")

        # Ожидание ответа от пользователя
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                if event.user_id == user_id:
                    response = event.text.strip()  # Получаем текст сообщения от пользователя

                    # Проверка ссылки на ВКонтакте
                    is_vk_link, _ = self.check_vk_link(response)
                    if is_vk_link:
                        # Сохраняем ссылку в базе данных и начисляем баллы
                        self.db_handler.save_response(user_id, 5, response)
                        self.db_handler.update_score(user_id, 5)

                        # Отправляем пользователю сообщение об успешном завершении конкурса
                        self.send_message(user_id,
                                          f"Отлично! Вы прошли последний этап конкурса! Суммарно вы набрали {self.db_handler.get_score(user_id)} баллов.")
                    else:
                        # В случае неверной ссылки, отправляем пользователю сообщение и продолжаем ожидать ответа
                        self.send_message(user_id,
                                          "К сожалению, ваша ссылка не является ссылкой на ВКонтакте. Попробуйте ещё раз.")

    # Другие методы для выполнения различных этапов конкурса

    # Создаем экземпляр бота и запускаем его
if __name__ == "__main__":
    bot = ContestBot("Token.txt", "contest_data.db")
    bot.start_bot()
    bot.close()