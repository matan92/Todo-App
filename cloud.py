import requests

BASE_URL = "https://todo-app-63714-default-rtdb.europe-west1.firebasedatabase.app/"

def get_tasks():
    url = BASE_URL + "tasks.json"
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        return response.json()
    return {}

def add_task(task_text):
    url = BASE_URL + "tasks.json"
    data = {"text": task_text, "completed": False}
    requests.post(url, json=data)

def update_task(task_id, new_data):
    url = BASE_URL + f"tasks/{task_id}.json"
    requests.patch(url, json=new_data)

def delete_task(task_id):
    url = BASE_URL + f"tasks/{task_id}.json"
    requests.delete(url)
