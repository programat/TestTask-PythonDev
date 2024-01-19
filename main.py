# подключение встроенных в Python библиотек
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
            # Вывод ошибки и повтор запроса
            print(f"Ошибка при получении данных (попытка {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                sleep(5)  # Пауза перед повторной попыткой
            else:
                raise RuntimeError(f"Не удалось получить данные после {MAX_RETRIES} попыток. Программа завершает "
                                   f"выполнение.")


def generate_report_content(user, tasks):
    full_name = user.get('name')
    email = user.get('email')

    # Если поле "name" в "company" отсутствует или равно None, устанавливаем значение по умолчанию
    company_name = user.get('company', {}).get('name', None) or '[ОТСУТСТВУЕТ НАЗВАНИЕ КОМПАНИИ]'

    report_time = dt.now().strftime('%d.%m.%Y %H:%M')

    report_content = (
        f"# Отчёт для {company_name}.\n"
        f"{full_name} <{email}> {report_time}\n"
    )

    if tasks:
        active_tasks = [task for task in tasks if not task.get('completed', False) and task.get('title')]
        completed_tasks = [task for task in tasks if task.get('completed', False) and task.get('title')]

        # Проверка корректно заполоненных задач
        total_tasks = len(tasks)
        correct_tasks = len(active_tasks) + len(completed_tasks)
        if correct_tasks != total_tasks:
            print(f"Внимание! У пользователя с id={user.get('id')} "
                  f"неверно заполненных задач: {abs(total_tasks - correct_tasks)} из {total_tasks}")
        if correct_tasks == 0:
            report_content += "Пользователь не имеет задач.\n"
            return report_content

        report_content += f"Всего задач: {correct_tasks}\n\n"

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
    old_report_filename = f"old_{user_name}_{dt.now().strftime('%Y-%m-%dT%H:%M')}.txt"

    try:
        # Переименование актуального файла в старый
        if os.path.exists(os.path.join('tasks', report_filename)):
            os.rename(os.path.join('tasks', report_filename), os.path.join('tasks', old_report_filename))

        # Запись нового отчёта в актуальный файл
        with open(os.path.join('tasks', report_filename), 'w') as report_file:
            report_file.write(report_content)

        # Проверка целостности и корректности временного файла
        expected_size = len(report_content.encode('utf-8'))
        actual_size = os.path.getsize(os.path.join('tasks', report_filename))

        if expected_size != actual_size:
            # В случае проблем с записью файла
            print("Внимание: Файл записан не полностью или некорректно. Откат изменений файла.")
            raise RuntimeError()

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")

        # В случае ошибки, восстановление актуального файла
        if os.path.exists(os.path.join('tasks', old_report_filename)):
            os.rename(os.path.join('tasks', old_report_filename), os.path.join('tasks', report_filename))


def create_reports():
    try:
        # Получение данных о задачах и пользователях
        tasks = get_json_data(url_todos)
        users = get_json_data(url_users)

        if not os.path.exists('tasks'):
            os.makedirs('tasks')

        # Создание отчета для каждого пользователя
        for user in users:
            # Обязательные поля должны существовать и не равны None
            user_id = user.get('id', None)
            user_name = user.get('username', None)
            full_name = user.get('name', None)
            email = user.get('email', None)
            company = user.get('company', None)

            if None in [user_id, user_name, full_name, email, company]:
                print(f"Ошибка при обработке данных пользователя: "
                      f"Отсутствует обязательная информация: [id={user_id}, username={user_name}, "
                      f"full_name = {full_name}, email = {email}, company={company}]")
            else:
                user_tasks = [task for task in tasks if task.get('userId') == user_id]

                if user_tasks or user_tasks == []:
                    report_content = generate_report_content(user, user_tasks)
                    if report_content is not None:
                        create_report_file(user_name, report_content)

        print("\nПрограмма успешно завершила выполнение!")

    except Exception as e:
        print(f"\nПрограмма завершила работу с неожиданной ошибкой: {e}")


if __name__ == '__main__':
    create_reports()
