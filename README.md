# Laba 3: Recommendation mini-project (Poetry + FastAPI + DVC + Docker + CI/CD)

[![build passing](https://github.com/lolovlad/Laba3MR/actions/workflows/ci.yml/badge.svg)](https://github.com/lolovlad/Laba3MR/actions/workflows/ci.yml)

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

### Как добавить новую версию данных через DVC

Если данные изменились (новая выгрузка, новая генерация, изменения препроцессинга), делай так:

1. Обнови данные локально:
```bash
poetry run python -m src.data.generate_data
```

2. Пересчитай pipeline и обнови `dvc.lock`:
```bash
poetry run dvc repro
```

3. Отправь новую версию данных/артефактов в remote (MinIO):
```bash
poetry run dvc push
```

4. Зафиксируй изменения метаданных в Git:
```bash
git add dvc.lock dvc.yaml .dvc/config
git commit -m "data: update dataset version"
git push
```

Важно:
- в Git коммитятся **только** DVC-метафайлы (`dvc.lock`, `dvc.yaml`, `.dvc/*.dvc`, конфиги),
- сами большие данные и модели хранятся в DVC remote (MinIO), а не в Git.

Как откатиться к старой версии данных:
```bash
git checkout <commit_with_old_dvc_lock>
poetry run dvc pull
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
5. `docker compose config -q` (проверка compose-конфига)
6. `docker build -t laba3mr-app:ci .` (проверка сборки контейнера)

## 9. Пошаговая проверка перед сдачей

1. `poetry install --with dev`
2. `docker compose up -d minio minio-init`
3. `poetry run dvc repro && poetry run dvc push`
4. `poetry run pytest -q`
5. `docker compose config -q`
6. `docker compose up --build` и проверить `/docs`
7. создать PR `feature/* -> develop`, убедиться что GitHub Actions зеленый




## 1. Почему мы используем DVC, а не просто храним данные в Git LFS?
Мы используем DVC вместо Git LFS, потому что DVC лучше подходит для работы с данными в ML-проектах. Git LFS в основном просто хранит большие файлы в репозитории, но не управляет их версиями на уровне пайплайнов и не отслеживает связи между данными, моделями и экспериментами. DVC позволяет не только хранить данные отдельно от Git, но и описывать этапы обработки данных и обучения моделей, что делает весь процесс более структурированным и воспроизводимым.

## 2. Как обеспечить воспроизводимость эксперимента через полгода?
Воспроизводимость эксперимента через длительное время обеспечивается за счёт фиксации всех ключевых компонентов проекта. Для этого сохраняются версии данных, кода, зависимостей и параметров модели. Также используются инструменты вроде DVC и виртуальных окружений, которые позволяют восстановить точно такую же среду, в которой проводился эксперимент. Это позволяет заново запустить обучение модели и получить сопоставимый результат даже спустя несколько месяцев.


## 3. Что произойдет с CI/CD пайплайном при падении тестов?
При падении тестов CI/CD пайплайн останавливается на этапе проверки и не допускает дальнейшее развертывание или публикацию изменений. Это сделано для того, чтобы в основную ветку не попадал нерабочий или нестабильный код. В таком случае разработчики получают уведомление о сбое, исправляют ошибки и повторно запускают pipeline после внесения изменений.
