# Telegram Proxy Bridge

Прокси-сервер для работы с Telegram API. Принимает HTTPS-запросы от сервера в РФ и форвардит их в Telegram, а также принимает вебхуки от Telegram и пересылает на РФ-сервер.

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
| `GET, POST, ...` | `/api/{path}` | Прокси РФ → Telegram. `path` = `bot<token>/sendMessage` и т.д. |
| `POST` | `/webhook/{token}` | Прокси Telegram → РФ. Форвардит тело на `rf_server_url` |
| `GET` | `/health` | Проверка здоровья |

Аутентификация: header `X-Proxy-Auth` с секретным ключом из конфига.

## Быстрый старт

### 1. Клонировать и сгенерировать сертификат

```bash
git clone <repo-url>
cd api-telegram-proxy-bridge
./generate-certs.sh <ВНЕШНИЙ_IP_СЕРВЕРА>
```

Сертификат генерируется с CN = IP сервера и SAN, чтобы Telegram его принял.

### 2. Настроить `config.yaml`

```yaml
auth_key: "случайная-строка"
rf_server_url: "https://твой-рф-сервер.ру/полный/путь/вебхука"
```

`rf_server_url` — полный URL, на который прокси будет форвардить вебхуки (вместе с путём).

### 3. Запустить

```bash
docker compose up -d
```

### 4. Установить вебхук для бота

Вебхук устанавливается **через сам прокси** (прямой доступ к `api.telegram.org` из РФ заблокирован):

```bash
curl -k -X POST "https://<IP_ПРОКСИ>:443/api/bot<TOKEN>/setWebhook" \
  -H "X-Proxy-Auth: <auth_key>" \
  -F "url=https://<IP_ПРОКСИ>:443/webhook/<TOKEN>" \
  -F "certificate=@certs/cert.pem"
```

Параметр `certificate` обязателен — Telegram не доверяет self-signed сертификату без него.

### 5. Проверить статус вебхука

```bash
curl -k "https://<IP_ПРОКСИ>:443/api/bot<TOKEN>/getWebhookInfo" \
  -H "X-Proxy-Auth: <auth_key>"
```

В ответе должно быть `has_custom_certificate: true` и `pending_update_count: 0`.

## Использование

### Из РФ-сервера

Отправляйте запросы любого метода (GET, POST, ...) на прокси с заголовком `X-Proxy-Auth`:

```
POST https://<IP_ПРОКСИ>:443/api/bot<TOKEN>/sendMessage
Content-Type: application/json
X-Proxy-Auth: <auth_key>

{"chat_id": 123, "text": "Hello"}
```

SSL verification отключить на стороне клиента.

### Вебхуки от Telegram

Telegram отправляет апдейты на `https://<IP_ПРОКСИ>:443/webhook/<TOKEN>`.
Прокси форвардит тело запроса на `rf_server_url` из конфига.

## Если сертификат протух или сменился IP

```bash
cd /opt/telegram-proxy
rm -f certs/cert.pem certs/key.pem
./generate-certs.sh <НОВЫЙ_IP>
docker compose up -d --build
# Переустановить вебхук с новым сертификатом
```

## Требования

- Docker + Docker Compose v2
- Открытый порт 443 на сервере
- Ubuntu/Debian

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
