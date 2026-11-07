import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import sqlite3
import os
import json


class PythonQuizApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title="Викторина Python")

        self.correct_option = None
        self.explanation_text = ""
        self.current_level = ""
        self.current_question_num = 0
        self.score = 0
        self.round_questions = []  # <--- Новый список для хранения 10 вопросов раунда

        try:
            self.init_database()
        except Exception as e:
            self.main_window.dialog(toga.ErrorDialog("Ошибка БД", str(e)))

        self.show_main_menu()
        self.main_window.show()

    def init_database(self):
        db_path = os.path.join(str(self.paths.data), "quiz.db")

        if not os.path.exists(db_path):
            json_path = os.path.join(str(self.paths.app), "questions.json")

            if not os.path.exists(json_path):
                raise FileNotFoundError(f"Не найден файл: {json_path}")

            with open(json_path, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute('''
                           CREATE TABLE questions
                           (
                               id             INTEGER PRIMARY KEY AUTOINCREMENT,
                               level          TEXT NOT NULL,
                               question_text  TEXT NOT NULL,
                               option_a       TEXT NOT NULL,
                               option_b       TEXT NOT NULL,
                               option_c       TEXT NOT NULL,
                               option_d       TEXT NOT NULL,
                               correct_option TEXT NOT NULL,
                               explanation    TEXT NOT NULL
                           )
                           ''')

            insert_data = []
            for q in questions_data:
                insert_data.append((
                    q['level'], q['question_text'], q['option_a'],
                    q['option_b'], q['option_c'], q['option_d'],
                    q['correct_option'], q['explanation']
                ))

            cursor.executemany('''
                               INSERT INTO questions (level, question_text, option_a, option_b, option_c, option_d,
                                                      correct_option, explanation)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                               ''', insert_data)

            conn.commit()
            conn.close()

    def get_db_connection(self):
        db_path = os.path.join(str(self.paths.data), "quiz.db")
        return sqlite3.connect(db_path)

    def show_main_menu(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=20, align_items=CENTER, flex=1))

        try:
            image_path = os.path.join(str(self.paths.app), 'resources', 'python_logo.png')
            logo = toga.ImageView(
                toga.Image(path=image_path),
                style=Pack(height=250, width=250, margin_bottom=20)
            )
            self.main_box.add(logo)
        except Exception as e:
            print(f"Картинка не найдена: {e}")

        title = toga.Label(
            "Выберите уровень\nсложности",
            style=Pack(font_size=22, font_weight="bold", margin_bottom=30, text_align=CENTER)
        )
        self.main_box.add(title)

        btn_beginner = toga.Button("Новичок", on_press=self.start_quiz, style=Pack(margin=10, width=250), id="beginner")
        btn_intermediate = toga.Button("Средний", on_press=self.start_quiz, style=Pack(margin=10, width=250),
                                       id="intermediate")
        btn_advanced = toga.Button("Тяжелый", on_press=self.start_quiz, style=Pack(margin=10, width=250), id="advanced")

        self.main_box.add(btn_beginner)
        self.main_box.add(btn_intermediate)
        self.main_box.add(btn_advanced)

        self.main_window.content = self.main_box

    def start_quiz(self, widget):
        try:
            self.start_quiz_level(widget.id)
        except Exception as e:
            self.main_window.dialog(toga.ErrorDialog("Ошибка запуска", str(e)))

    # --- ОБНОВЛЕННЫЙ МЕТОД ЗАПУСКА ИГРЫ ---
    def start_quiz_level(self, level):
        self.current_level = level
        self.current_question_num = 1
        self.score = 0

        # Загружаем 10 случайных уникальных вопросов из БД
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT question_text, option_a, option_b, option_c, option_d, correct_option, explanation FROM questions WHERE level = ? ORDER BY RANDOM() LIMIT 10",
            (self.current_level,)
        )
        self.round_questions = cursor.fetchall()
        conn.close()

        # Если в базе вдруг меньше 10 вопросов, игра все равно запустится
        if len(self.round_questions) == 0:
            self.main_window.dialog(toga.InfoDialog("Ой", "Для этого уровня пока нет вопросов!"))
            self.show_main_menu()
            return

        self.load_next_question()

    # --- ОБНОВЛЕННЫЙ МЕТОД ЗАГРУЗКИ ВОПРОСА ---
    def load_next_question(self):
        # Если вопросы закончились - показываем результат
        # Проверяем и на 10 вопросов, и на случай если в базе меньше 10
        if self.current_question_num > 10 or self.current_question_num > len(self.round_questions):
            self.show_results()
            return

        # Достаем вопрос из нашего заранее подготовленного списка
        # current_question_num начинается с 1, а индексы в списке с 0
        row = self.round_questions[self.current_question_num - 1]

        question_text, opt_a, opt_b, opt_c, opt_d, self.correct_option, self.explanation_text = row

        quiz_box = toga.Box(style=Pack(direction=COLUMN, margin=10, flex=1))

        top_bar = toga.Box(style=Pack(direction=ROW, align_items=CENTER, margin_bottom=15))

        progress_label = toga.Label(
            f"Вопрос {self.current_question_num} из {len(self.round_questions)}",
            style=Pack(font_size=14, color="#888888")
        )

        spacer = toga.Box(style=Pack(flex=1))
        btn_exit = toga.Button("В меню", on_press=self.back_to_menu, style=Pack(font_size=12))

        top_bar.add(progress_label)
        top_bar.add(spacer)
        top_bar.add(btn_exit)
        quiz_box.add(top_bar)

        question_label = toga.MultilineTextInput(
            value=question_text,
            readonly=True,
            style=Pack(font_size=16, font_weight="bold", margin_bottom=20, flex=1)
        )
        quiz_box.add(question_label)

        self.answers_box = toga.Box(style=Pack(direction=COLUMN))

        self.btn_a = toga.Button(f"A) {opt_a}", on_press=self.check_answer, id="A", style=Pack(margin=5))
        self.btn_b = toga.Button(f"B) {opt_b}", on_press=self.check_answer, id="B", style=Pack(margin=5))
        self.btn_c = toga.Button(f"C) {opt_c}", on_press=self.check_answer, id="C", style=Pack(margin=5))
        self.btn_d = toga.Button(f"D) {opt_d}", on_press=self.check_answer, id="D", style=Pack(margin=5))

        self.answers_box.add(self.btn_a)
        self.answers_box.add(self.btn_b)
        self.answers_box.add(self.btn_c)
        self.answers_box.add(self.btn_d)
        quiz_box.add(self.answers_box)

        self.explanation_label = toga.MultilineTextInput(
            value="",
            readonly=True,
            style=Pack(font_size=14, margin_top=20, margin_bottom=20, flex=1)
        )
        quiz_box.add(self.explanation_label)

        self.btn_next = toga.Button("Следующий вопрос", on_press=self.next_question, style=Pack(margin=10))
        self.btn_next.enabled = False
        quiz_box.add(self.btn_next)

        self.main_window.content = quiz_box

    def check_answer(self, widget):
        selected_option = widget.id

        self.btn_a.enabled = False
        self.btn_b.enabled = False
        self.btn_c.enabled = False
        self.btn_d.enabled = False

        buttons = {"A": self.btn_a, "B": self.btn_b, "C": self.btn_c, "D": self.btn_d}

        if selected_option == self.correct_option:
            self.score += 1
            widget.style.background_color = "#4CAF50"
            self.explanation_label.value = f"✅ Верно!\n\n💡 {self.explanation_text}"
            self.explanation_label.style.color = "#2E7D32"
        else:
            widget.style.background_color = "#F44336"
            buttons[self.correct_option].style.background_color = "#4CAF50"
            self.explanation_label.value = f"❌ Неверно! Правильный ответ: {self.correct_option}.\n\n💡 {self.explanation_text}"
            self.explanation_label.style.color = "#C62828"

        self.btn_next.enabled = True

    def next_question(self, widget):
        self.current_question_num += 1
        self.load_next_question()

    def show_results(self):
        result_box = toga.Box(style=Pack(direction=COLUMN, margin=20, align_items=CENTER, flex=1))

        title = toga.Label(
            "Раунд завершен!",
            style=Pack(font_size=22, font_weight="bold", margin_bottom=20, text_align=CENTER)
        )
        result_box.add(title)

        if self.score >= 9:
            message = "Невероятно! Вы настоящий Python-гуру! 🐍👑"
        elif self.score >= 6:
            message = "Отличный результат! Вы хорошо знаете Python. 👍"
        else:
            message = "Есть над чем поработать. Продолжайте учиться! 💪"

        # Учитываем количество вопросов в раунде (на случай, если их меньше 10)
        total_q = len(self.round_questions)

        score_label = toga.MultilineTextInput(
            value=f"Вы ответили правильно на {self.score} из {total_q} вопросов.",
            readonly=True,
            style=Pack(font_size=18, font_weight="bold", margin_bottom=10, flex=1)
        )
        result_box.add(score_label)

        message_label = toga.MultilineTextInput(
            value=message,
            readonly=True,
            style=Pack(font_size=16, font_style="italic", margin_bottom=30, flex=1)
        )
        result_box.add(message_label)

        btn_restart = toga.Button("Пройти заново", on_press=self.restart_quiz, style=Pack(margin=10, width=250))
        result_box.add(btn_restart)

        btn_back = toga.Button("В главное меню", on_press=self.back_to_menu, style=Pack(margin=10, width=250))
        result_box.add(btn_back)

        self.main_window.content = result_box

    def restart_quiz(self, widget):
        self.start_quiz_level(self.current_level)

    def back_to_menu(self, widget):
        self.show_main_menu()


def main():
    return PythonQuizApp()