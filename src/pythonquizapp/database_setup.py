import sqlite3
import json
import os


def create_database():
    # Определяем пути
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Поднимаемся на 2 уровня вверх: из src/pythonquizapp в корень проекта
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))

    db_path = os.path.join(project_root, 'quiz.db')
    json_path = os.path.join(script_dir, 'questions.json')

    print(f"Создаем базу данных по пути: {db_path}")

    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Удаляем старую таблицу, чтобы обновить структуру (если она была)
    cursor.execute('DROP TABLE IF EXISTS questions')

    # Создаем новую таблицу
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

    # Читаем вопросы из JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            questions_data = json.load(file)
    except FileNotFoundError:
        print("Ошибка: Файл questions.json не найден!")
        return

    # Вставляем данные
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
    print(f"Успех! База данных обновлена. Загружено вопросов: {len(insert_data)}")


if __name__ == '__main__':
    create_database()