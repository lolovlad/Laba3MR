# Laba 3: Recommendation mini-project (Poetry + FastAPI + DVC + Docker + CI/CD)

[![build passing](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/USERNAME/REPO/actions)

Камерный pet-проект под лабораторную:
- задача рекомендаций (synthetic interactions)
- FastAPI сервис с endpoint `/recommend`
- DVC + S3 remote на MinIO
- Docker Compose с автосозданием bucket
- GitHub Actions (PR в `develop`)
- управление зависимостями через `poetry`

## Структура

`data/`, `notebooks/`, `src/`, `tests/`, `models/` + инфраструктурные файлы (`Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `dvc.yaml`)

## 1. Настройка репозитория GitHub и Git Flow

### Создать удаленный репозиторий
1. Создай пустой репозиторий на GitHub без `README`/`.gitignore`.
2. В локальном проекте выполни:

```bash
git init
git checkout -b main
git add .
git commit -m "Initial recommender MLOps setup"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

### Поднять ветки Git Flow

```bash
git checkout -b develop
git push -u origin develop
git checkout -b feature/recommender-pipeline
git push -u origin feature/recommender-pipeline
```

Рабочий цикл:
- разработка в `feature/*`
- Pull Request `feature/* -> develop`
- после проверки merge `develop -> main`

## 2. Poetry: установка зависимостей

```bash
poetry install --with dev
poetry run python -V
```

## 3. Генерация данных и обучение модели

```bash
poetry run python -m src.data.generate_data
poetry run python -m src.ml.train
```

Что создается:
- `data/raw/interactions.csv`
- `data/raw/items.csv`
- `models/recommender.joblib`
- `models/metrics.json`

## 4. DVC + MinIO

DVC remote уже настроен в `.dvc/config`:
- `s3://recommender-dvc`
- endpoint `http://localhost:9000`

### Запуск MinIO и создание bucket

```bash
docker compose up -d minio minio-init
```

### Запуск DVC pipeline и push в remote

```bash
poetry run dvc repro
poetry run dvc push
```

Проверка:

```bash
poetry run dvc status -c
```

## 5. Запуск API локально

```bash
poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Пример запроса:

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":1,\"top_k\":5}"
```

## 6. Docker Compose (приложение + MinIO + bucket init)

```bash
docker compose up --build
```

Сервисы:
- `app` (FastAPI)
- `minio` (S3-compatible storage)
- `minio-init` (создает bucket `recommender-dvc`)

## 7. Ноутбук с обработкой и обучением

Файл: `notebooks/recommender_pipeline.ipynb`

Запуск:

```bash
poetry run jupyter notebook
```

В ноутбуке есть:
- генерация данных
- мини-EDA
- запуск обучения
- пример рекомендаций для существующего и нового пользователя

## 8. CI/CD (GitHub Actions)

Workflow: `.github/workflows/ci.yml`

Триггер:
- Pull Request в ветку `develop`

Шаги в CI:
1. установка Poetry и зависимостей
2. `poetry run black --check src tests`
3. `poetry run flake8 src tests`
4. `poetry run pytest -q`

## 9. Пошаговая проверка перед сдачей

1. `poetry install --with dev`
2. `docker compose up -d minio minio-init`
3. `poetry run dvc repro && poetry run dvc push`
4. `poetry run pytest -q`
5. `docker compose up --build` и проверить `/docs`
6. создать PR `feature/* -> develop`, убедиться что GitHub Actions зеленый

## 10. Обновить бейдж перед сдачей

Заменить ссылку в `README` на реальную:
`https://github.com/<user>/<repo>/actions/workflows/ci.yml/badge.svg`
