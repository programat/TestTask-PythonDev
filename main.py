
# подключение встроенных в python библиотек
import json, os
from datetime import datetime

# подключение сторонней библиотеки requests
import requests


url_todos = "https://json.medrocket.ru/todos"
url_users = "https://json.medrocket.ru/users"

def get_tasks():
    response = requests.get(url_todos)
    return response.json()

def get_users():
    response = requests.get(url_users)
    return response.json()


def generate_report(user, tasks):
    company_name = user['company']['name']
    full_name = user['name']
    email = user['email']
    report_time = datetime.now().strftime('%d.%m.%Y %H:%M')

    report_content = f"# Отчёт для {company_name}.\n{full_name} <{email}> {report_time}\n"

    if tasks:
        total_tasks = len(tasks)
        report_content += f"Всего задач: {total_tasks}\n\n"

        active_tasks = [task for task in tasks if task.get('completed', False)]
        completed_tasks = [task for task in tasks if task.get('completed', True)]

        report_content += f"## Актуальные задачи ({len(active_tasks)}):\n"
        for task in active_tasks:
            task_title = task['title'][:46] + '…' if len(task['title']) > 46 else task['title']
            report_content += f"- {task_title}\n"

        report_content += "\n## Завершённые задачи ({len(completed_tasks)}):\n"
        for task in completed_tasks:
            task_title = task['title'][:46] + '…' if len(task['title']) > 46 else task['title']
            report_content += f"- {task_title}\n"
    else:
        report_content += "Пользователь не имеет задач.\n"

    return report_content

def create_reports():
    tasks = get_tasks()
    users = get_users()

    if not os.path.exists('tasks'):
        os.makedirs('tasks')

    for user in users:
        user_id = user.get('id')
        user_name = user['username']

        user_tasks = [task for task in tasks if task.get('userId') == user_id]

        if user_tasks or user_tasks == []:
            report_content = generate_report(user, user_tasks)

            report_filename = f"{user_name}.txt"
            old_report_filename = f"old_{user_name}_{datetime.now().strftime('%Y-%m-%dT%H:%M')}.txt"

            if os.path.exists(os.path.join('tasks', report_filename)):
                os.rename(os.path.join('tasks', report_filename), os.path.join('tasks', old_report_filename))

            with open(os.path.join('tasks', report_filename), 'w') as report_file:
                report_file.write(report_content)

if __name__ == '__main__':
    create_reports()


