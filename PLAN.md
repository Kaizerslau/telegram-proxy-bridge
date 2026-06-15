# Telegram Proxy Bridge — план проекта

## Проблема

- Сервер в РФ, Telegram API заблокирован
- Нужен внешний сервер (прокси), который будет принимать запросы от РФ-сервера, пересылать их в Telegram, и наоборот — принимать вебхуки от Telegram и форвардить на РФ-сервер

## Архитектура

```
РФ-сервер ──HTTPS (self-signed)──> Прокси ──HTTPS──> api.telegram.org
                                    │
Telegram ──HTTPS──> Прокси ──HTTPS (self-signed)──> РФ-сервер
```

### Компоненты

- **Traefik** — reverse proxy, LetsEncrypt (если будет домен), терминирование TLS, роутинг по Host
- **FastAPI (Python)** — бизнес-логика:
  - `POST /api/*` — приём запросов от РФ, проксирование в Telegram
  - `POST /webhook/<token>` — приём вебхуков от Telegram, форвард на РФ-сервер
- **Docker Compose** — оркестрация Traefik + App

## Выборы по архитектуре

| Параметр | Решение |
|----------|---------|
| Язык/стек | Python (FastAPI + httpx) |
| Кол-во ботов | Несколько (прокси любые токены) |
| Аутентификация | `X-Proxy-Auth` header (секретный ключ) |
| TLS | Self-signed сертификат (без домена) либо LetsEncrypt (если купить домен) |
| Домен | Нет. Если понадобится — купить зарубежный `.xyz` / `.click` / `.link` (~$1–3/год) |
| Деплой | Docker + Docker Compose |
| Reverse proxy | Traefik v3 (знаком пользователю) |

## Как DPI обходит HTTPS

DPI видит только `IP:443` + зашифрованный TLS. Содержимое (путь, хедеры, тело запроса к Telegram API) не читаемо. По IP блокируют редко — если начнут, сменить сервер или добавить домен.

## Как поднять с нуля на голой Ubuntu

1. Установить Docker + Compose
2. Настроить DNS (если домен)
3. Поправить `config.yaml`
4. `docker compose up -d`

## config.yaml

```yaml
auth_key: "секретный-ключ"
listen_port: 443
ssl_cert: "/certs/cert.pem"
ssl_key: "/certs/key.pem"
rf_server_url: "https://твой-домен.рф"
```

## Что меняется в коде бота на РФ

```python
# Было
bot = Bot(token="TOKEN")
# Стало (пример для aiogram)
bot = Bot(token="TOKEN", base_url="https://<IP_прокси>:443/api")
```

## Структура файлов проекта

```
telegram-proxy/
├── app/
│   ├── main.py           # эндпоинты /api/* и /webhook/*
│   └── config.py         # загрузка config.yaml
├── Dockerfile            # python:3.12-slim + uvicorn
├── docker-compose.yml    # Traefik + App
├── traefik/
│   └── traefik.yml       # статическая конфигурация
├── config.yaml           # настройки прокси
├── .env.example
└── PLAN.md
```
