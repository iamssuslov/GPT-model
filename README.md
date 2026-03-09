# My Local GPT

Локальный AI-ассистент, работающий на LLM, запущенной локально через Ollama.

## Технологии

* Python
* FastAPI
* Ollama
* Local LLM

## Архитектура

Проект использует слой `LLMProvider`, который позволяет менять движок модели:

* OllamaProvider
* MLXProvider (будет добавлен позже)

Это позволит перейти с Ollama на MLX без изменения бизнес-логики.

## Запуск

Создать окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Установить Ollama и скачать модель:

```bash
ollama run gemma3
```

Запустить сервер:

```bash
fastapi dev app/main.py
```

API документация:

```
http://127.0.0.1:8000/docs
```
