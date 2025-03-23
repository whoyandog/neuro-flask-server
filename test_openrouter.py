import requests
import json
import time
import os

url = "http://localhost:5151/api/process"
headers = {
    "Content-Type": "application/json"
}
data = {
    "model": "openrouter-deepseek",
    "message": "Привет! Как тебя зовут?",
    "prompt_template": "base"
}

def check_logs():
    try:
        if os.path.exists("logs"):
            log_files = os.listdir("logs")
            print(f"Найденные файлы логов: {log_files}")
            
            for log_file in log_files:
                if os.path.getsize(f"logs/{log_file}") > 0:
                    print(f"\nСодержимое {log_file} (последние 20 строк):")
                    with open(f"logs/{log_file}", "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for line in lines[-20:]:
                            print(line.strip())
    except Exception as e:
        print(f"Ошибка при чтении логов: {str(e)}")

try:
    print("Отправка запроса...")
    response = requests.post(url, headers=headers, json=data)
    print(f"Статус: {response.status_code}")
    
    if response.status_code == 200:
        print("Успешный ответ:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print("Ошибка:")
        print(response.text)
    
    print("\nЖдем 2 секунды для записи логов...")
    time.sleep(2)
    
    print("\n--- ПРОВЕРКА ЛОГОВ ---")
    check_logs()
        
except Exception as e:
    print(f"Произошла ошибка: {str(e)}")
    
    print("\n--- ПРОВЕРКА ЛОГОВ ---")
    check_logs() 