# подключение встроенных в python библиотек
import os
from datetime import datetime as dt
from time import sleep

# подключение сторонней библиотеки requests
import requests

MAX_RETRIES = 3  # Максимальное количество попыток
url_todos = "https://json.medrocket.ru/todos"
url_users = "https://json.medrocket.ru/users"


def get_json_data(url):
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                sleep(5)  # Пауза перед повторной попыткой
            else:
                raise RuntimeError(f"Не удалось получить данные после {MAX_RETRIES} попыток. Программа завершает "
                                   f"выполнение.")


def generate_report_content(user, tasks):
    company_name = user['company']['name']
    full_name = user['name']
    email = user['email']

    report_time = dt.now().strftime('%d.%m.%Y %H:%M')

    report_content = (
        f"# Отчёт для {company_name}.\n"
        f"{full_name} <{email}> {report_time}\n"
    )

    if tasks:
        total_tasks = len(tasks)
        report_content += f"Всего задач: {total_tasks}\n\n"

        active_tasks = [task for task in tasks if task.get('completed', False)]
        completed_tasks = [task for task in tasks if task.get('completed', True)]

        def format_task_title(task_title):
            return task_title[:46] + '…' if len(task_title) > 46 else task_title

        report_content += f"## Актуальные задачи ({len(active_tasks)}):\n"
        for task in active_tasks:
            report_content += f"- {format_task_title(task['title'])}\n"

        report_content += f"\n## Завершённые задачи ({len(completed_tasks)}):\n"
        for task in completed_tasks:
            report_content += f"- {format_task_title(task['title'])}\n"
    else:
        report_content += "Пользователь не имеет задач.\n"

    return report_content


def create_report_file(user_name, report_content):
    report_filename = f"{user_name}.txt"
    temp_report_filename = f"temp_{user_name}.txt"  # нужен для проверки корректности записи
    old_report_filename = f"old_{user_name}_{dt.now().strftime('%Y-%m-%dT%H:%M')}.txt"

    try:
        # Создание временного файла
        with open(os.path.join('tasks', temp_report_filename), 'w') as temp_report_file:
            temp_report_file.write(report_content)

        # Проверка целостности и корректности временного файла
        expected_size = len(report_content.encode('utf-8'))
        actual_size = os.path.getsize(os.path.join('tasks', temp_report_filename))

        if expected_size == actual_size:
            # Если всё корректно, переименование актуального файла в старый и временного в актуальный
            if os.path.exists(os.path.join('tasks', report_filename)):
                os.rename(os.path.join('tasks', report_filename), os.path.join('tasks', old_report_filename))

            os.rename(os.path.join('tasks', temp_report_filename), os.path.join('tasks', report_filename))

        else:
            print("Внимание: Файл записан не полностью или некорректно. Удаление временного файла.")
            raise RuntimeError()

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")

        # В случае ошибки, удаление старого файла
        if os.path.exists(os.path.join('tasks', temp_report_filename)):
            os.remove(os.path.join('tasks', temp_report_filename))
        # В случае ошибки, восстановление старого файла
        if os.path.exists(os.path.join('tasks', old_report_filename)):
            os.rename(os.path.join('tasks', old_report_filename), os.path.join('tasks', report_filename))


def create_reports():
    try:
        tasks = get_json_data(url_todos)
        users = get_json_data(url_users)

        if not os.path.exists('tasks'):
            os.makedirs('tasks')

        for user in users:
            user_id = user.get('id')
            user_name = user['username']

            user_tasks = [task for task in tasks if task.get('userId') == user_id]

            if user_tasks or user_tasks == []:
                report_content = generate_report_content(user, user_tasks)
                create_report_file(user_name, report_content)

    except Exception as e:
        print(f"Неожиданная ошибка: {e}")


if __name__ == '__main__':
    create_reports()
