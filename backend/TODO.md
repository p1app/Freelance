# TODO — ошибки бэкенда

Аудит проведён по исходникам `backend/src` (все роутеры, схемы, сервисы, репозитории, модели, core, миграции).
Код бэкенда не изменялся — это только чек-лист. Пункты, помеченные **[проверено запуском]**, подтверждены
запуском Python/компиляцией SQL, а не только чтением кода.

Приоритеты: **P0** — падения/неверные данные, **P1** — доступ и контракт API, **P2** — пагинация/сортировки,
**P3** — мёртвый код и инфраструктура, **РЕШИТЬ** — требует твоего решения (влияет на фронтенд).

---

## Уже исправлено

- [x] `project_service.py:15` — битый импорт `from backend.src.repository.proposal_repo import ...`
      (`ModuleNotFoundError`, приложение не стартовало). Сейчас `import main` проходит: **[проверено запуском]**.

---

## P0 — падения и неверные данные

- [ ] **`GET /users/freelancers` с фильтром `skills` → 500.** `repository/user_repo.py:148`, `:165` —
      `func.or_(*conditions)` компилируется в `WHERE or(lower('python') = ANY (users.skills))`, а функции
      `or()` в Postgres нет → `ProgrammingError` → generic-хендлер отдаёт 500. **[проверено запуском]**
      Заменить на `or_` из `sqlalchemy` (уже импортирован в `project_repo.py:4`).
      Дополнительно: `skills.any(func.lower(skill))` сравнивает lower входа с сырыми значениями массива —
      нужен `func.lower` и по колонке, иначе «Python» не найдётся в сохранённом `Python`.
- [ ] **`GET /users/me/stats`: «Завершено» считает не то.** `service/user_service.py:79` —
      `completed_count=total_projects_freelance` (все проекты фрилансера, включая `in_progress`).
      Это плитка «Завершено» в профиле. Брать `user.completed_projects` (инкрементится в
      `user_repo.py:202`) или считать проекты со статусом `COMPLETED`.
- [ ] **Фильтры проектов не применяются.** `repository/project_repo.py:74-118` (`ProjectRepository.list` —
      единственное место с `category/status/budget_min/budget_max/search`) не вызывается нигде: grep пустой.
      `service/project_service.py:205` использует `get_open_projects(page, page_size)`.
      Из-за этого поиск/категория/бюджет на фронте не работают.
- [ ] **`models/notification_model.py:4` падает при импорте.** `Notification(Base): pass` →
      `InvalidRequestError: Class Notification does not have a __table__ or __tablename__`. **[проверено запуском]**
      Спасает только то, что модуля нет в `models/__init__.py`. Доделать модель или удалить файл.
- [ ] **Наивное время в контрактах.** `repository/contract_repo.py:19` (`start_date=datetime.now()`) и
      `:100` (`end_date=datetime.now()`) при колонках `DateTime(timezone=True)` → сдвиг на оффсет сервера
      (тот же класс бага, что правился миграцией `ac0f7b3dc882`). Нужен `datetime.now(UTC)`.
- [ ] **Гонка при принятии отклика → 500 вместо 409.** `service/proposal_service.py:178-197`: проверка
      `get_by_project` и последующие шаги без блокировки. Два параллельных `accept` на один проект: второй
      проходит проверку, `ProjectRepository.assign_freelancer` ищет проект `WHERE status == OPEN`, не находит,
      возвращает `None`, затем `project_service.py:197` делает `ProjectResponse.model_validate(None)` →
      `ValidationError` → 500 (либо `IntegrityError` на unique `project_id`). Нужен `SELECT ... FOR UPDATE`
      по проекту или корректный 409.
- [ ] **Операции не атомарны: коммит в каждом репозитории, `rollback` нет нигде.**
      `accept_proposal` = accept → reject_others → assign_freelancer (проект становится `in_progress`) →
      create_contract: если падает создание контракта, проект остаётся «в работе» без контракта, а остальные
      отклики уже отклонены. То же в `contract_service.py:172-183`: контракт завершён, а проект/счётчик могут
      не обновиться. Решение: один commit на операцию (`async with session.begin()`).
- [ ] **`PATCH /projects/{id}/assign` создаёт невалидное состояние.** `project_service.py:179-198`:
      ставит фрилансера и `in_progress` **без контракта**, не проверяя существование пользователя и его роль
      (несуществующий id → `IntegrityError` → 500). Фронт этот эндпоинт не использует — можно закрыть/удалить.
- [ ] **`GET /projects/{id}` публичный и отдаёт все отклики.** `project_service.py:62-84` кладёт `proposals`
      (сопроводительные письма, ставки) в ответ без авторизации — утечка. Фронт поле не использует.
      Не отдавать его в публичном ответе либо отдавать только заказчику.
- [ ] **`ValueError` из валидаторов моделей → 500, а не 400/422.** Обработчик есть только под `AppException`
      (`main.py:62-67`), остальное уходит в generic → «Internal server error». Примеры:
      `project_model.py:75-82` (смена `freelancer_id` вне `OPEN`), `:84-90` (COMPLETED без исполнителя),
      `milestone_model.py:40-50`. Сейчас прикрыто проверками в сервисах, но это потенциальные 500.

---

## P1 — доступ, безопасность, контракт API

- [ ] **Заблокированный пользователь продолжает работать с API.** `core/security.py:55-66`:
      `get_current_user` не проверяет `is_active` (проверяет только `get_current_active_user`, `:83-88`).
      Напрямую его используют `/users/me` (GET/PUT/DELETE), чат, контракты, этапы, отзывы → блокировка
      обходится. Добавить проверку в `get_current_user`.
- [ ] **`/auth/refresh` не ротирует и не отзывает токены; `logout` — пустышка.**
      `service/auth_service.py:83-84` просто возвращает словарь. Старый refresh живёт до истечения,
      «выход» на сервере ничего не значит. Нужен blacklist/denylist (Redis в конфиге есть, не используется).
- [ ] **`ContractResponse` без `project_title`.** Свойство `Contract.project_title` есть
      (`models/contract_model.py:107-109`), но в схему списка (`schemas/contract_schema.py:10-22`) не добавлено
      → фронт показывает «Контракт #id». Добавить одно поле.
- [ ] **`Review.rating`: схема `float` 1.0–5.0, колонка `Integer` + `CHECK 1..5`.**
      `review_schema.py:8,13,30` против `review_model.py:31,66`. Оценка 4.5 проходит валидацию и падает на
      вставке. Либо `int` в схеме, либо `Numeric(2,1)` в БД.
- [ ] **`UserRepository.create` кладёт `password` в `hashed_password`.** `repository/user_repo.py:18`.
      Безопасно только потому, что `AuthService.register` сначала мутирует Pydantic-модель
      (`auth_service.py:32`). Любая перестановка строк = пароли в открытом виде. Передавать
      `hashed_password` явным параметром.
- [ ] **Мягкое удаление противоречит FK.** `models/contract_model.py:33-42`: `customer_id`/`freelancer_id`
      объявлены `ondelete="SET NULL"` при `nullable=False` → физическое удаление пользователя невозможно.
      Либо `RESTRICT`, либо явно закрепить soft-delete.
- [ ] **Админский `DELETE /admin/projects/{id}`** (`service/admin_service.py:115-124`) удаляет проект в любом
      статусе, каскадом унося контракт, этапы, сообщения и отзывы (`project_model.py:60-67`,
      `contract_model.py:86-105`). Ограничить статусами или сделать soft-delete.
- [ ] **JWT в query-параметре WebSocket** (`routers/ws_router.py:34`) — токен попадает в логи и историю.
      По возможности передавать через первый кадр после подключения или через cookie.

---

## P2 — пагинация, сортировки, чат

- [ ] **Чат отдаёт самые старые сообщения.** `repository/chat_repo.py:33-46`: `order_by(created_at.asc())`
      + `offset` → страница 1 = первые 20 сообщений, свежие — на последней странице. Фронт грузит только
      первую страницу и листания не имеет. Варианты: сортировать по убыванию и разворачивать список в ответе,
      либо считать offset от конца (`max(0, total - page * page_size)`).
- [ ] **Нет `ORDER BY`** → нестабильные страницы (дубли/пропуски при листании):
      `user_repo.py:103-132` (`/users`), `admin_repo.py:9-38` и `:71-95` (`/admin/users`, `/admin/projects`),
      `contract_repo.py:58-86` (`/contracts/me`), `review_repo.py:64-96` (`/users/{id}/reviews`).
- [ ] **Сортировка отзывов ломается пагинацией.** `service/review_service.py:111-116` сортирует по рейтингу
      **после** `limit/offset` → порядок верен только внутри страницы, при равных рейтингах произвольный.
      Сортировать в SQL + тайбрейкер по `created_at`.
- [ ] **`GET /contracts/{id}/messages` помечает всё прочитанным как побочный эффект GET**
      (`service/chat_service.py:79-83`) — нарушение идемпотентности. Оставить только явный `read-all`.
- [ ] **Валидаторы зависят от порядка присваивания.** `repository/project_repo.py:183-184`: сначала
      `freelancer_id`, потом `status`; работает лишь потому, что валидатор `project_model.py:75-82` требует
      `OPEN`, а статус ещё старый. Перестановка строк → `ValueError` → 500. Ставить статус первым или
      проверять явно в сервисе.
- [ ] **`CheckConstraint("due_date > CURRENT_TIMESTAMP")`** (`models/milestone_model.py:52-55`) — ограничение,
      зависящее от времени: не переживёт `pg_dump`/restore или `VALIDATE CONSTRAINT` для прошедших этапов.
      Проверку «дата в будущем» достаточно держать в схеме.

---

## P3 — мёртвый код и инфраструктура

- [ ] **Мёртвые методы (0 ссылок):** `get_current_user_optional`, `check_contract_exists`,
      `search_by_skills` (к тому же сломанная сигнатура — нет `session`, `user_repo.py:171-184`),
      `get_average_rating`, `get_pending_by_contract`, `get_not_approved_by_contract`, `get_pending_by_project`,
      `get_accepted_by_project`, `get_last_message`, `get_unread_by_user`, `check_milestones_approved`,
      `get_completed_by_user`, `ContractRepository.update`, `ProjectRepository.list` (см. P0-3).
- [ ] **`get_freelancers(data=FreelancerFilter)`** (`repository/user_repo.py:135`) — дефолт равен классу, а не
      `None`. Плюс `search` из `FreelancerFilter` не применяется нигде (единственное использование
      `data.search` — в мёртвом `ProjectRepository.list`).
- [ ] **`core/email_message.py`**: `async def` под `@app.task` (Celery async-таски не поддерживает),
      broker собран как `redis://:{host}:{port}/0` (`:11`, потерян пароль/хост), `celery` тянется в
      зависимостях, а вызов закомментирован (`auth_service.py:39`). Либо починить, либо убрать.
- [ ] **`pyproject.toml:17`** — `uvicorn[standard,standart]`: опечатка в extra. Плюс нет dev-зависимостей
      (pytest/ruff), хотя `# noqa` по коду расставлены.
- [ ] **`core/health_db.py:9`** — голый `except:` глушит всё, включая отмену задачи.
- [ ] **Миграции:** 5 пустых ревизий (`77648a12e30b`, `298af3618627`, `2c4983d050b9`, `5017df8875eb`,
      `758054373eef` — сплошные `pass`), вся схема создаётся в `02f1b3e821ad`. Историю стоит squasher'нуть.
- [ ] **`alembic.ini:89`** — `sqlalchemy.url = driver://user:pass@localhost/dbname` (перекрывается в
      `migration/env.py:35`, но выглядит как незаполненное).
- [ ] **Нет тестов и CI.** По плану — следующий этап после фиксов, иначе тесты закрепят текущее поведение
      (баги из P0–P2), а не ожидаемое.

---

## РЕШИТЬ — рассинхрон схем с фронтендом

Фронт сейчас упирается в эти лимиты: FastAPI на 422 отдаёт `detail` **массивом**, а фронт печатает его как
строку → пользователь видит `[object Object]`. Нужно либо поднять лимиты на бэке, либо я опущу счётчики в
формах — скажи, что первично.

- [ ] **`ProposalCreate.cover_letter` — max 200** (`schemas/proposal_schema.py:9`), в форме фронта 2000.
- [ ] **`ReviewCreate.comment` — max 250** (`schemas/review_schema.py:9`), в форме фронта 500.
- [ ] **`MilestoneCreate.description` — обязателен, min 5** (`schemas/milestone_schema.py:10`), но в модели/БД
      `nullable=True` (`models/milestone_model.py:23`); форма отправляет `null` → 422. Выбрать: обязательный
      (уберу отправку `null`) или nullable (`str | None` в схеме).
- [ ] **Единый формат ошибок 422.** Сейчас `{detail: [ {loc, msg, type}, ... ]}` от FastAPI против
      `{detail: "строка"}` от `AppException`. Обёртка-нормализатор на бэке или на фронте — решить, где.

---

## Что нужно бэку от фронта (для полноты картины)

- [ ] **Эндпоинт «мой отклик по проекту».** Фронт вынужден искать свой отклик перебором `GET /proposals/me`
      (до 5 страниц × 100, без `ORDER BY`). Если появится `GET /projects/{id}/proposals/me` или поле
      `my_proposal` в `ProjectDetailResponse` — уберу цикл, останется один запрос.
- [ ] **`GET /contracts/me`** — см. P1 (`project_title`), иначе карточки контрактов безымянные.
- [ ] **Фильтры `/projects`** — см. P0-3, иначе UI фильтров на фронте остаётся декоративным.

---

## Приложение: что уже сделано на фронте под эти правила

- Кнопки «Принять/Отклонить» показываются только при `project.status === 'open'`
  (`frontend/src/components/proposal/ProposalCard.vue`), поэтому отменённый проект их не показывает даже до
  появления `reject_all`.
- Форма отклика не показывается повторно после перезагрузки: свой отклик грузится с бэкенда
  (`frontend/src/views/ProjectDetailView.vue`, `frontend/src/stores/proposals.js`), при этом отозванный
  отклик повторную отправку не блокирует — как в `get_by_freelancer_and_project` (`status != WITHDRAWN`).
