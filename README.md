# File Exchange — Fullstack Test Task

MVP файлообменника с фоновой проверкой контента и системой алертов.

**Стек:** FastAPI · SQLAlchemy · Celery · Redis · PostgreSQL · Next.js · Docker

---

## Быстрый старт

```bash
# Поднять все сервисы
docker compose -f docker-compose.dev.yml up

# Применить миграции (в отдельном терминале)
docker exec -it backend alembic upgrade head
```

- Фронтенд: http://localhost:3000/test
- Swagger UI: http://localhost:8000/docs

---

## Makefile

В корне проекта есть `Makefile` с удобными командами:

```bash
make up          # docker compose up
make down        # docker compose down
make migrate     # alembic upgrade head

make test        # запустить тесты
make test-v      # тесты с подробным выводом
```

---

## Тесты

Тесты запускаются внутри контейнера. При первом запуске нужно установить dev-зависимости:

```bash
docker exec -it backend sh -c "uv pip install --system aiosqlite httpx pytest pytest-asyncio pytest-mock"
```

После этого достаточно:

```bash
make test
```

Или напрямую:

```bash
docker exec -it backend pytest
docker exec -it backend pytest -v  # подробный вывод
```

**Покрытие:**
- `tests/unit/` — логика сканирования, репозитории (20 кейсов)
- `tests/integration/` — все HTTP-эндпоинты (16 кейсов)

---

## Структура проекта

```
.
├── backend/
│   ├── src/
│   │   ├── config.py          # Pydantic Settings
│   │   ├── database.py        # SQLAlchemy engine, get_session
│   │   ├── models.py          # ORM-модели
│   │   ├── schemas.py         # Pydantic-схемы
│   │   ├── dependencies.py    # DI-провода
│   │   ├── repositories/      # SQL-запросы
│   │   ├── services/          # бизнес-логика
│   │   ├── routers/           # HTTP-эндпоинты
│   │   └── tasks/             # Celery pipeline
│   ├── migrations/            # Alembic
│   └── tests/
│       ├── unit/
│       └── integration/
└── frontend/
    └── src/
        ├── app/page.tsx       # страница
        ├── components/        # FileTable, AlertsTable, UploadModal, PageHeader
        ├── hooks/             # useFiles, useAlerts
        ├── lib/               # api.ts, utils.ts
        └── types/             # FileItem, AlertItem
```

---

## API

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/files` | Список всех файлов |
| `POST` | `/files` | Загрузить файл |
| `GET` | `/files/{id}` | Получить файл по ID |
| `PATCH` | `/files/{id}` | Обновить название |
| `DELETE` | `/files/{id}` | Удалить файл |
| `GET` | `/files/{id}/download` | Скачать файл |
| `GET` | `/alerts` | Список алертов |

---

## Переменные окружения

Задаются в `.env.dev`. Ключевые:

| Переменная | Описание |
|---|---|
| `POSTGRES_*` | Параметры подключения к БД |
| `CELERY_BROKER_URL` | URL Redis-брокера |

Для фронтенда в `frontend/.env.production`:

| Переменная | Описание |
|---|---|
| `NEXT_PUBLIC_API_URL` | Базовый URL бэкенда (default: `http://localhost:8000`) |

---

## Что изменено относительно оригинала

### Исправленные баги

- **Неверная env-переменная** — `tasks.py` читал `REDIS_URL` вместо `CELERY_BROKER_URL`
- **`updated_at` не обновлялся** при изменениях вне ORM — добавлен PostgreSQL-триггер
- **Мёртвый код** — функция `get_file_path()` объявлена, но не использовалась
- **`processing_status` зависал** в `"processing"` при ошибке обработки

### Архитектура бэкенда

Монолитный `service.py` разбит на слои: routers → services → repositories. Добавлены `config.py` (Pydantic Settings), `database.py` (единый engine), `dependencies.py` (DI). Сессия БД передаётся через `Depends(get_session)`.

### Оптимизации

- **3 Celery-задачи → 1** — сканирование, метаданные и алерт в одной транзакции (1 SELECT вместо 3)
- **NullPool в воркере** — устраняет конфликт event loop при `asyncio.run()`
- **Потоковая запись файлов** — чанки по 1 МБ вместо загрузки всего файла в память
- **Индексы** на `files.created_at`, `alerts.file_id`, `alerts.created_at`

### Фронтенд

`page.tsx` (~700 строк) разбит на слои: `types/`, `lib/`, `hooks/`, `components/`. URL бэкенда вынесен в `NEXT_PUBLIC_API_URL`. Добавлена кнопка удаления файла.
