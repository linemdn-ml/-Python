import json
import os


def remove_duplicates():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'questions.json')

    with open(file_path, 'r', encoding='utf-8') as f:
        questions = json.load(f)

    print(f"Изначально вопросов в файле: {len(questions)}")

    seen = set()
    unique_questions = []

    for q in questions:
        # Используем текст вопроса как уникальный ключ
        q_text = q.get('question_text', '').strip()
        if q_text not in seen:
            seen.add(q_text)
            unique_questions.append(q)
        else:
            print(f"Найден дубликат и удален: {q_text}")

    print(f"\nПосле удаления дубликатов осталось: {len(unique_questions)}")

    # Перезаписываем файл без дубликатов
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(unique_questions, f, ensure_ascii=False, indent=2)

    print("Файл questions.json успешно очищен!")


if __name__ == '__main__':
    remove_duplicates()