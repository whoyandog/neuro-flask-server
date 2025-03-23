# Neuro Flask Server (Прототип)

Прототип Flask-сервера для обработки промптов и взаимодействия с различными нейросетями (ChatGPT, DeepSeek и др.). 

## Установка и запуск

1. **Клонирование репозитория:**
```bash
git clone ...
cd neuro-flask-server
```

2. **Настройка окружения:**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. **Установка зависимостей:**
```bash
pip install -r requirements.txt
```

4. **Настройка конфигурации:**
```bash
cp .env.example .env
# Отредактируйте .env файл, добавив свои API ключи
```

5. **Запуск сервера:**
```bash
python run.py
```

Сервер запускается по адресу: `http://localhost:5151`

## API Endpoints

- `POST /api/process` - Обработка сообщения
- `GET /api/prompts` - Список доступных промптов
- `GET /api/prompts/<model_name>` - Промпты для конкретной модели
- `POST /api/reload` - Перезагрузка промптов

### Пример запроса:
```bash
curl -X POST http://localhost:5151/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chatgpt",
    "message": "Привет!",
    "prompt_template": "base"
  }'
```

## Структура промптов

Промпты хранятся в YAML-файлах в директории `prompts/`:
```
prompts/
  chatgpt/
    base.yaml
  deepseek/
    base.yaml
  openrouter-deepseek/
    base.yaml
    code.yaml
```