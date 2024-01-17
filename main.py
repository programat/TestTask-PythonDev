
# подключение встроенных в python библиотек
import json, os, datetime

# подключение сторонней библиотеки requests
import requests


url_todos = "https://json.medrocket.ru/todos"
url_users = "https://json.medrocket.ru/users"


# Функция для записи отчета в файл
def write_report(username, company, email, report_time, tasks):
    # Формирование имени файла
    file_name = f"{username}.txt"

    # Проверка существования файла и переименование, если нужно
    if os.path.exists(os.path.join("tasks", file_name)):
        old_file_name = f"old_{username}_{report_time}.txt"
        os.rename(os.path.join("tasks", file_name), os.path.join("tasks", old_file_name))

    # Запись отчета в файл
    with open(os.path.join("tasks", file_name), "w") as file:
        file.write(f"# Отчёт для {company}.\n")
        file.write(f"{username} <{email}> {report_time}\n")
        file.write(f"Всего задач: {len(tasks)}\n\n")

        # Актуальные задачи
        active_tasks = [task for task in tasks if not task["completed"]]
        file.write(f"## Актуальные задачи ({len(active_tasks)}):\n")
        for task in active_tasks:
            truncated_title = task["title"][:46] + "…" if len(task["title"]) > 46 else task["title"]
            file.write(f"- {truncated_title}\n")
        file.write("\n")

        # Завершенные задачи
        completed_tasks = [task for task in tasks if task["completed"]]
        file.write(f"## Завершённые задачи ({len(completed_tasks)}):\n")
        for task in completed_tasks:
            truncated_title = task["title"][:46] + "…" if len(task["title"]) > 46 else task["title"]
            file.write(f"- {truncated_title}\n")

if __name__ == '__main__':
    todos_data = requests.get(url_todos).json()
    users_data = requests.get(url_users).json()

    # Создание директории tasks
    if not os.path.exists("tasks"):
        os.makedirs("tasks")

    # Обработка данных и запись отчетов
    for user in users_data:
        user_id = user["id"]
        username = user["username"]
        company = user["company"]["name"]
        email = user["email"]
        report_time = datetime.now().strftime("%d.%m.%Y %H:%M")

        user_tasks = [task for task in todos_data if task["userId"] == user_id]

        write_report(username, company, email, report_time, user_tasks)


