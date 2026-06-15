# Telegram Proxy Bridge

Прокси-сервер для обхода блокировки Telegram API. Принимает HTTPS-запросы от сервера в РФ и форвардит их в Telegram, а также принимает вебхуки от Telegram и пересылает на РФ-сервер.

Поддерживает **несколько ботов** — не требует регистрации токенов, работает с любыми.

## Архитектура

```
РФ-сервер ──HTTPS──> Прокси ──HTTPS──> api.telegram.org
                                 │
Telegram ──HTTPS──> Прокси ──HTTPS──> РФ-сервер
```

- **FastAPI (Python)** — лёгкий backend
- **Self-signed SSL** — не требует домена
- **Docker Compose** — один сервис, простой деплой

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/{path}` | Прокси РФ → Telegram. `path` = `bot<token>/sendMessage` и т.д. |
| `POST` | `/webhook/{token}` | Прокси Telegram → РФ. Форвардит на `rf_server_url/webhook/{token}` |
| `GET` | `/health` | Проверка здоровья |

Аутентификация: header `X-Proxy-Auth` с секретным ключом из конфига.

## Быстрый старт

### 1. Клонировать и сгенерировать сертификат

```bash
git clone <repo-url>
cd api-telegram-proxy-bridge
./generate-certs.sh
```

### 2. Настроить `config.yaml`

```yaml
auth_key: "мой-секретный-ключ"
rf_server_url: "https://мой-рф-сервер.ру"
```

### 3. Запустить

```bash
docker compose up -d
```

## Использование

### Из РФ-сервера

Отправляйте POST-запросы на прокси с заголовком `X-Proxy-Auth`:

```
POST https://<IP_прокси>:443/api/bot<TOKEN>/sendMessage
Content-Type: application/json
X-Proxy-Auth: мой-секретный-ключ

{"chat_id": 123, "text": "Hello"}
```

SSL verification отключить на стороне клиента.

### Вебхуки от Telegram

При установке вебхука укажите:

```
https://<IP_прокси>:443/webhook/<TOKEN>
```

Прокси форварднёт запрос на `https://мой-рф-сервер.ру/webhook/<TOKEN>`.

## Требования

- Docker + Docker Compose v2
- Открытый порт 443 на сервере
- Ubuntu/Debian (инструкция для других ОС может отличаться)

## Файлы

```
├── app/
│   ├── config.py          # загрузка конфига
│   └── main.py            # эндпоинты
├── Dockerfile
├── docker-compose.yml
├── config.yaml            # настройки
├── generate-certs.sh      # генерация self-signed SSL
└── .env.example
```
