import json
import os


def merge_json_files():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_file = os.path.join(base_dir, 'questions.json')

    # Список файлов, которые нужно добавить
    new_files = ['new_50.json']

    all_questions = []

    # 1. Читаем основной файл
    try:
        with open(main_file, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
            print(f"В основном файле найдено: {len(all_questions)} вопросов.")
    except FileNotFoundError:
        print("Основной файл questions.json не найден. Будет создан новый.")

    # 2. Читаем новые файлы и добавляем вопросы
    for filename in new_files:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    new_data = json.load(f)
                    all_questions.extend(new_data)
                    print(f"Из файла {filename} добавлено: {len(new_data)} вопросов.")
            except json.JSONDecodeError:
                print(f"Ошибка чтения {filename}. Проверьте, что это валидный JSON.")
        else:
            print(f"Файл {filename} не найден (пропускаем).")

    # 3. Сохраняем результат обратно в questions.json
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)
        print(f"\nГотово! Общее количество вопросов теперь: {len(all_questions)}")


if __name__ == '__main__':
    merge_json_files()