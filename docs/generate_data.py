#!/usr/bin/env python3
"""Генератор тестовых данных для PostgreSQL (фриланс-биржа).

Заливает ~300-400 согласованных записей: пользователи, проекты, отклики,
контракты, этапы, отзывы, чат и уведомления.

Запуск (нужен asyncpg — он есть в venv бэкенда):

    cd backend
    .venv/bin/python ../docs/generate_data.py --records 350

    # или со своим DSN
    .venv/bin/python ../docs/generate_data.py --dsn "postgresql://user:pass@host:5432/db"

По умолчанию данные берутся из backend/.env (DB_HOST, DB_PORT, DB_NAME,
DB_USER, DB_PASSWORD). Скрипт ОЧИЩАЕТ таблицы; чтобы дописать к существующим
данным — флаг --append.

Все пользователи входят с одним паролем: --password (по умолчанию password123).
"""

from __future__ import annotations

import argparse
import asyncio
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

try:
    import asyncpg
except ImportError:  # pragma: no cover
    raise SystemExit(
        "Нужен asyncpg. Запускайте через venv бэкенда:\n"
        "  cd backend && .venv/bin/python ../docs/generate_data.py"
    ) from None

# Хэш argon2id для пароля "password123" (тот же алгоритм, что в приложении)
DEFAULT_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$sPZeq7V2bi2FcA5hrHWuNQ$"
    "QSbVPQQmsKlup+FvkmlmP9jyKdqkfi8axXAcuHvcTBA"
)

# ────────────────────────────────────────────────────────────────────────────
# Данные для генерации
# ────────────────────────────────────────────────────────────────────────────

FIRST_M = [
    "Иван", "Дмитрий", "Сергей", "Алексей", "Михаил", "Артём", "Никита",
    "Павел", "Максим", "Егор", "Роман", "Кирилл", "Владимир", "Андрей",
]
FIRST_F = [
    "Анна", "Мария", "Елена", "Ольга", "Татьяна", "Наталья", "Ирина",
    "Юлия", "Екатерина", "Светлана", "Вера", "Полина", "Алина", "Ксения",
]
LAST_M = [
    "Петров", "Смирнов", "Кузнецов", "Волков", "Новиков", "Морозов",
    "Егоров", "Павлов", "Соколов", "Лебедев", "Козлов", "Орлов",
]
LAST_F = [
    "Смирнова", "Петрова", "Кузнецова", "Волкова", "Новикова", "Морозова",
    "Егорова", "Павлова", "Соколова", "Лебедева", "Козлова", "Орлова",
]

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}

SKILLS = {
    "DEVELOPMENT": ["Python", "FastAPI", "Django", "PostgreSQL", "Docker",
                    "React", "Vue.js", "REST API", "CI/CD", "Linux", "Redis"],
    "DESIGN": ["Figma", "UI/UX", "Дизайн-системы", "Прототипирование",
               "Адаптивная вёрстка", "Иллюстрация", "Брендинг"],
    "MARKETING": ["Яндекс Директ", "Google Ads", "SEO", "Аналитика",
                  "SMM", "Email-маркетинг", "Веб-аналитика"],
    "WRITING": ["Копирайтинг", "Редактура", "SEO-тексты", "Сценарии",
                "Контент-план", "Лендинги", "Интервью"],
    "OTHER": ["Консалтинг", "Бухгалтерия", "Юридические вопросы",
              "Переводы", "Обучение", "Организация процессов"],
}

CATEGORIES = list(SKILLS.keys())

PROJECTS = {
    "DEVELOPMENT": [
        ("Разработка API для интернет-магазина",
         "Нужно спроектировать и реализовать REST API: каталог, корзина, заказы, интеграция с платёжным шлюзом. Есть дизайн и описание сущностей, работаем спринтами."),
        ("Личный кабинет на Vue 3",
         "Требуется личный кабинет с дашбордом и отчётами. Нужны адаптив, аккуратные компоненты и понятная структура проекта."),
        ("Интеграция с платёжным провайдером",
         "Нужно подключить приём платежей и подписки, обработать вебхуки, добавить идемпотентность и логирование операций."),
        ("Телеграм-бот для приёма заявок",
         "Бот принимает заявки, сохраняет их в базу и уведомляет менеджера. Нужны админ-команды и защита от спама."),
        ("Оптимизация медленных SQL-запросов",
         "Есть отчёт с тяжёлыми запросами: нужно профилирование, индексы и переписывание проблемных мест без изменения API."),
    ],
    "DESIGN": [
        ("Редизайн личного кабинета SaaS",
         "Нужно переработать дашборд, отчёты и настройки команды, собрать дизайн-систему и подготовить адаптивные макеты."),
        ("Дизайн мобильного приложения",
         "Проектируем приложение для заказа услуг: ключевые экраны, состояния, прототип для тестирования на пользователях."),
        ("Дизайн упаковки продуктовой линейки",
         "Требуются макеты упаковки для пяти вкусов, подготовка файлов к печати и проверка цветопробы."),
        ("Лендинг для онлайн-курса",
         "Нужен продающий лендинг с понятной структурой, блоками программы и формой заявки, дизайн под мобильные."),
        ("Дизайн-система для банка",
         "Собрать библиотеку компонентов, токены и гайдлайны, передать команде разработки в Figma с описанием."),
    ],
    "MARKETING": [
        ("Настройка контекстной рекламы",
         "Нужно собрать кампании в Яндекс Директе по нескольким регионам, настроить цели и отчётность по заявкам."),
        ("SEO-продвижение сайта услуг",
         "Требуется технический аудит, семантика, оптимизация страниц и план контента на три месяца."),
        ("Запуск email-рассылки",
         "Нужно настроить домен, собрать цепочку писем и проверить доставляемость, добавить UTM-метки."),
        ("Аналитика воронки продаж",
         "Собрать сквозную аналитику: события, цели, дашборд по этапам воронки и отчёт по источникам."),
    ],
    "WRITING": [
        ("Цикл статей для блога",
         "Нужны 10 статей по готовому контент-плану: понятные заголовки, факты, ссылки на источники, без воды."),
        ("Тексты для лендинга",
         "Требуются тексты для всех блоков лендинга: оффер, выгоды, программа, ответы на возражения, призывы."),
        ("Редактура технической документации",
         "Нужно вычитать документацию: единый стиль, терминология, структура разделов, исправление ошибок."),
        ("Сценарии для обучающих видео",
         "Написать сценарии для серии коротких видео: структура, реплики, тайминги и подсказки для съёмки."),
    ],
    "OTHER": [
        ("Консультация по самозанятости",
         "Нужна разовая консультация: оформление, лимиты дохода, расчёт налога при работе с несколькими заказчиками."),
        ("Помощь с бухгалтерией ИП",
         "Требуется помощь с отчётностью и документами: разобрать текущее состояние и составить план на квартал."),
        ("Перевод документации на английский",
         "Нужен перевод технической документации с сохранением терминологии и оформлением в исходном формате."),
        ("Организация онлайн-воркшопа",
         "Помочь спланировать и провести воркшоп для команды: программа, материалы, тайминг и обратная связь."),
    ],
}

COVER_LETTERS = [
    "Здравствуйте! Есть похожий опыт: делал проект того же профиля, сроки и бюджет выдерживаю. Могу начать на этой неделе и показывать промежуточный результат раз в несколько дней.",
    "Добрый день! Внимательно прочитал(а) задачу. Вижу, что важно получить результат быстро и без лишних итераций — предлагаю начать с короткого созвона, зафиксировать критерии приёмки и работать по этапам.",
    "Здравствуйте! Готов(а) взяться. В похожих проектах закрывал(а) такую задачу за сопоставимый срок, есть примеры работ. Уточню пару деталей по требованиям — и можно стартовать.",
    "Привет! По задаче всё понятно, объём реалистичный. Работаю аккуратно: план, промежуточные демо, финальная сдача с документацией. Готов(а) обсудить детали в чате.",
    "Здравствуйте! Подхожу по опыту: делал(а) несколько проектов с похожим стеком. Предлагаю разбить работу на этапы, чтобы вы видели прогресс и могли корректировать требования по ходу.",
    "Добрый день! Могу предложить решение чуть шире задачи: помимо основного объёма добавлю проверку на типичные проблемы и короткую инструкцию. Сроки и стоимость указал(а) в отклике.",
]

MILESTONES = {
    "DEVELOPMENT": ["Согласование требований", "Проектирование схемы",
                    "Реализация API", "Тесты и код-ревью", "Документация",
                    "Деплой и проверка"],
    "DESIGN": ["Аудит и структура", "Прототип", "Ключевые экраны",
               "Адаптив и состояния", "Передача макетов"],
    "MARKETING": ["Аудит текущих кампаний", "Семантика и структура",
                  "Запуск кампаний", "Оптимизация и отчёт"],
    "WRITING": ["Согласование контент-плана", "Первые тексты",
                "Правки и редактура", "Финальная сдача"],
    "OTHER": ["Консультация", "План работ", "Основной результат",
              "Итоговая встреча"],
}

CHAT_PHRASES_CLIENT = [
    "Добрый день! Посмотрел(а) статус — как продвигается?",
    "Спасибо, всё принял(а). По правкам отписал(а) в задаче.",
    "Давайте созвонимся завтра и обсудим детали.",
    "Нужны ли от меня ещё какие-то данные?",
    "Отлично, тогда двигаемся по плану.",
    "По срокам всё в силе? У нас встреча с командой в пятницу.",
    "Проверил(а) результат, выглядит хорошо.",
    "Можно чуть подробнее про этот момент?",
]
CHAT_PHRASES_FREELANCER = [
    "Добрый день! Работаю по плану, промежуточный результат выложил(а).",
    "Спасибо за уточнение, учту в следующей итерации.",
    "Да, давайте завтра в 11:00 — скину ссылку на созвон.",
    "Данных достаточно, вопросов пока нет.",
    "Закрыл(а) пункт из списка, обновил(а) статус задачи.",
    "По срокам успеваю, если не появятся новые требования.",
    "Готов(а) к приёмке, можно проверять.",
    "Уточню у вас один момент по требованиям.",
]

NOTIFICATIONS = {
    "PROPOSAL": "Новый отклик на проект «{title}»",
    "CONTRACT": "Заключён контракт по проекту «{title}»",
    "MILESTONE": "Этап «{milestone}» изменил статус",
    "MESSAGE": "Новое сообщение в чате по контракту",
    "REVIEW": "Получен отзыв по завершённому контракту",
    "SYSTEM": "Системное уведомление",
}


# ────────────────────────────────────────────────────────────────────────────
# Вспомогательные функции
# ────────────────────────────────────────────────────────────────────────────

def translit(text: str) -> str:
    return "".join(TRANSLIT.get(ch, ch) for ch in text.lower())


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def build_dsn(args: argparse.Namespace) -> str:
    if args.dsn:
        return args.dsn

    env_file = Path(__file__).resolve().parent.parent / "backend" / ".env"
    env = read_env_file(env_file)
    host = env.get("DB_HOST")
    port = env.get("DB_PORT")
    name = env.get("DB_NAME")
    user = env.get("DB_USER")
    password = env.get("DB_PASSWORD")

    missing = [k for k, v in {"DB_HOST": host, "DB_NAME": name, "DB_USER": user}.items() if not v]
    if missing:
        raise SystemExit(
            "Не задан DSN и не удалось прочитать backend/.env "
            f"(не хватает: {', '.join(missing)}). Передайте --dsn."
        )
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def password_hash(password: str) -> str:
    """argon2-хэш для пароля; если passlib нет — берём хэш для password123."""
    if password == "password123":
        return DEFAULT_PASSWORD_HASH
    try:
        from passlib.context import CryptContext

        return CryptContext(schemes=["argon2"], deprecated="auto").hash(password)
    except ImportError:
        raise SystemExit(
            "Для нестандартного пароля нужен passlib (есть в venv бэкенда). "
            "Либо оставьте пароль по умолчанию: password123"
        ) from None


@dataclass
class Plan:
    """Сгенерированные сущности в памяти (текстовое представление)."""

    users: list[dict]
    projects: list[dict]
    proposals: list[dict]
    contracts: list[dict]
    milestones: list[dict]
    reviews: list[dict]
    messages: list[dict]
    notifications: list[dict]

    def total(self) -> int:
        return sum(
            len(part)
            for part in (
                self.users, self.projects, self.proposals, self.contracts,
                self.milestones, self.reviews, self.messages, self.notifications,
            )
        )


def plan_data(target: int, seed: int, pwd_hash: str) -> Plan:
    rnd = random.Random(seed)
    now = datetime.now(UTC)

    # ── пользователи ────────────────────────────────────────────────────────
    n_users = max(8, round(0.08 * target))
    n_admins = 2
    n_clients = max(3, round(0.4 * (n_users - n_admins)))
    n_freelancers = max(3, n_users - n_admins - n_clients)

    users: list[dict] = []
    used_usernames: set[str] = set()

    def make_user(role: str, idx: int) -> dict:
        is_female = rnd.random() < 0.5
        first = rnd.choice(FIRST_F if is_female else FIRST_M)
        last = rnd.choice(LAST_F if is_female else LAST_M)
        fullname = f"{first} {last}"
        base = f"{translit(first)}.{translit(last)}"
        username = base
        suffix = 1
        while username in used_usernames:
            suffix += 1
            username = f"{base}{suffix}"
        used_usernames.add(username)

        skills = None
        rating = 0
        completed = 0
        bio = None
        if role == "FREELANCER":
            cat = rnd.choice(CATEGORIES)
            skills = rnd.sample(SKILLS[cat], k=rnd.randint(3, 5))
            rating = round(rnd.uniform(3.6, 5.0), 1)
            completed = rnd.randint(0, 25)
            bio = (
                f"Специализируюсь на направлении «{cat.lower()}». "
                f"Опыт {rnd.randint(2, 12)} лет, работаю по этапам с промежуточными демо. "
                "Отвечаю в чате в течение дня."
            )
        elif role == "CLIENT":
            bio = (
                "Заказчик: ищу подрядчиков под задачи продукта. "
                "Даю понятные требования и обратную связь по этапам."
            )

        created = now - timedelta(days=rnd.randint(20, 200), hours=rnd.randint(0, 23))
        return {
            "email": f"{username}@example.com",
            "username": username,
            "hashed_password": pwd_hash,
            "role": role,
            "fullname": fullname,
            "bio": bio,
            "skills": skills,
            "rating": float(rating),
            "completed_projects": completed,
            "is_active": rnd.random() > 0.03,
            "created_at": created,
            "updated_at": created,
        }

    users.append(make_user("ADMIN", 0))
    users.append(make_user("ADMIN", 1))
    users.extend(make_user("CLIENT", i) for i in range(n_clients))
    users.extend(make_user("FREELANCER", i) for i in range(n_freelancers))

    clients_idx = [i for i, u in enumerate(users) if u["role"] == "CLIENT"]
    freelancers_idx = [i for i, u in enumerate(users) if u["role"] == "FREELANCER"]

    # ── проекты ─────────────────────────────────────────────────────────────
    n_projects = max(8, round(0.16 * target))
    statuses = (
        ["OPEN"] * 55 + ["IN_PROGRESS"] * 15 + ["COMPLETED"] * 15
        + ["DRAFT"] * 10 + ["CANCELLED"] * 5
    )
    projects: list[dict] = []
    used_titles: set[str] = set()

    for i in range(n_projects):
        status = rnd.choice(statuses)
        category = rnd.choice(CATEGORIES)
        title, description = rnd.choice(PROJECTS[category])
        title = f"{title}"
        if title in used_titles:
            title = f"{title} #{i + 1}"
        used_titles.add(title)

        created = now - timedelta(days=rnd.randint(5, 120), hours=rnd.randint(0, 23))
        budget = rnd.randrange(15_000, 450_001, 5_000)
        customer = rnd.choice(clients_idx)

        project = {
            "title": title[:255],
            "description": f"{description} Бюджет и сроки обсуждаемы, детали уточним в чате.",
            "budget": budget,
            "deadline": created + timedelta(days=rnd.randint(20, 90)),
            "category": category,
            "customer_id": customer,
            "freelancer_id": None,
            "status": status,
            "is_deleted": rnd.random() < 0.04,
            "created_at": created,
            "updated_at": created,
        }
        if status in ("IN_PROGRESS", "COMPLETED"):
            project["freelancer_id"] = rnd.choice(freelancers_idx)
        if status == "OPEN" and project["is_deleted"]:
            project["status"] = "CANCELLED"
        if status in ("DRAFT", "CANCELLED"):
            project["is_deleted"] = project["is_deleted"] and status == "CANCELLED"
        projects.append(project)

    # ── отклики ─────────────────────────────────────────────────────────────
    proposals: list[dict] = []
    accepted_by_project: dict[int, dict] = {}
    for p_idx, project in enumerate(projects):
        if project["status"] == "DRAFT":
            continue

        status = project["status"]
        if status == "OPEN":
            n = rnd.randint(1, 2)
        elif status in ("IN_PROGRESS", "COMPLETED"):
            n = rnd.randint(2, 3)
        else:
            n = rnd.randint(0, 1)

        candidates = [f for f in freelancers_idx if f != project["customer_id"]]
        chosen = rnd.sample(candidates, k=min(n, len(candidates)))

        if status in ("IN_PROGRESS", "COMPLETED"):
            winner = project["freelancer_id"]
            if winner in chosen:
                chosen.remove(winner)
            chosen.insert(0, winner)

        for pos, freelancer in enumerate(chosen):
            if status in ("IN_PROGRESS", "COMPLETED"):
                p_status = "ACCEPTED" if pos == 0 else rnd.choice(["REJECTED", "REJECTED", "WITHDRAWN"])
            elif status == "CANCELLED":
                p_status = rnd.choice(["REJECTED", "WITHDRAWN"])
            else:
                p_status = "PENDING"

            created = project["created_at"] + timedelta(
                days=rnd.randint(0, 3), hours=rnd.randint(1, 23)
            )
            proposal = {
                "project_idx": p_idx,
                "freelancer_id": freelancer,
                "cover_letter": rnd.choice(COVER_LETTERS),
                "bid_amount": max(5_000, int(project["budget"] * rnd.uniform(0.7, 1.05)) // 1000 * 1000),
                "estimated_days": rnd.choice([7, 10, 14, 20, 25, 30, 45]),
                "status": p_status,
                "created_at": created,
                "updated_at": created + timedelta(days=rnd.randint(0, 3)),
            }
            proposal["idx"] = len(proposals)
            proposals.append(proposal)
            if p_status == "ACCEPTED":
                accepted_by_project[p_idx] = proposal

    # ── контракты ───────────────────────────────────────────────────────────
    contracts: list[dict] = []
    contract_by_project: dict[int, dict] = {}
    for p_idx, project in enumerate(projects):
        if project["status"] not in ("IN_PROGRESS", "COMPLETED"):
            continue
        proposal = accepted_by_project.get(p_idx)
        if not proposal or project["freelancer_id"] is None:
            continue

        start = proposal["created_at"] + timedelta(days=rnd.randint(1, 3))
        completed = project["status"] == "COMPLETED"
        end = start + timedelta(days=rnd.randint(20, 60)) if completed else None
        contract = {
            "project_idx": p_idx,
            "proposal_idx": proposal["idx"],
            "customer_id": project["customer_id"],
            "freelancer_id": project["freelancer_id"],
            "final_price": proposal["bid_amount"],
            "start_date": start,
            "end_date": end,
            "status": "COMPLETED" if completed else "ACTIVE",
            "created_at": start,
            "updated_at": end or start,
        }
        contracts.append(contract)
        contract_by_project[p_idx] = contract

    contract_index = {id(c): i for i, c in enumerate(contracts)}

    # ── этапы ───────────────────────────────────────────────────────────────
    milestones: list[dict] = []
    for contract in contracts:
        project = projects[contract["project_idx"]]
        titles = MILESTONES[project["category"]]
        n = rnd.randint(2, min(3, len(titles)))
        picked = rnd.sample(titles, k=n)
        completed = contract["status"] == "COMPLETED"
        span = (
            (contract["end_date"] - contract["start_date"]).days
            if completed and contract["end_date"] else 30
        )
        span = max(span, n * 3)

        for i, title in enumerate(picked):
            due = contract["start_date"] + timedelta(days=round(span * (i + 1) / n))
            if completed:
                status = "APPROVED"
            else:
                status = rnd.choice(["APPROVED", "APPROVED", "COMPLETED", "PENDING"])
            created = contract["start_date"] + timedelta(days=round(span * i / n))
            milestones.append({
                "contract_idx": contract_index[id(contract)],
                "title": title[:50],
                "description": f"Работы по этапу «{title}»: результат, проверка и обратная связь заказчика.",
                "due_date": due,
                "status": status,
                "created_at": created,
                "updated_at": due,
            })

    # ── отзывы ──────────────────────────────────────────────────────────────
    reviews: list[dict] = []
    comments_good = [
        "Отличная работа: сроки соблюдены, результат совпал с ожиданиями, коммуникация по делу.",
        "Приятно работать: понятные требования, быстрые ответы и готовность обсуждать правки.",
        "Всё сделано аккуратно и в срок, документация и инструкции приложены. Рекомендую.",
        "Задача закрыта полностью, промежуточные результаты показывались вовремя, спасибо!",
    ]
    comments_ok = [
        "В целом всё хорошо, были небольшие задержки по срокам, но результат нас устроил.",
        "Работа выполнена качественно, часть уточнений пришлось переделывать, итог положительный.",
    ]
    for contract in contracts:
        if contract["status"] != "COMPLETED" or not contract["end_date"]:
            continue
        participants = [contract["customer_id"], contract["freelancer_id"]]
        for author in participants:
            if rnd.random() > 0.8:
                continue
            review_target = [p for p in participants if p != author][0]
            rating = rnd.choice([5, 5, 5, 4, 4, 3])
            comment = rnd.choice(comments_good if rating >= 4 else comments_ok)
            created = contract["end_date"] + timedelta(days=rnd.randint(0, 7))
            reviews.append({
                "contract_idx": contract_index[id(contract)],
                "from_user_idx": author,
                "to_user_idx": review_target,
                "rating": rating,
                "comment": comment[:250],
                "created_at": created,
                "updated_at": created,
            })

    # ── сообщения чата ──────────────────────────────────────────────────────
    messages: list[dict] = []
    for contract in contracts:
        n = rnd.randint(2, 4)
        cursor = contract["start_date"] + timedelta(hours=rnd.randint(1, 10))
        participants = [contract["customer_id"], contract["freelancer_id"]]
        for _ in range(n):
            sender = rnd.choice(participants)
            role_phrases = (
                CHAT_PHRASES_CLIENT if sender == contract["customer_id"] else CHAT_PHRASES_FREELANCER
            )
            messages.append({
                "contract_idx": contract_index[id(contract)],
                "sender_id": sender,
                "message": rnd.choice(role_phrases),
                "is_read": rnd.random() < 0.7,
                "created_at": cursor,
                "updated_at": cursor,
            })
            cursor += timedelta(hours=rnd.randint(2, 30))

    # ── уведомления (добираем до целевого количества) ───────────────────────
    notifications: list[dict] = []

    def add_notification(kind: str, to_user: int, **extra) -> None:
        base = {"type": kind, "to_user_id": to_user, "description": "", "is_read": rnd.random() < 0.6,
                "contract_idx": extra.get("contract_idx"), "project_idx": extra.get("project_idx"),
                "from_user_idx": extra.get("from_user_idx")}
        if kind == "PROPOSAL":
            project = projects[extra["project_idx"]]
            base["description"] = NOTIFICATIONS["PROPOSAL"].format(title=project["title"])
        elif kind == "CONTRACT":
            project = projects[extra["project_idx"]]
            base["description"] = NOTIFICATIONS["CONTRACT"].format(title=project["title"])
        elif kind == "MILESTONE":
            base["description"] = NOTIFICATIONS["MILESTONE"].format(milestone=extra["milestone"])
        elif kind == "MESSAGE":
            base["description"] = NOTIFICATIONS["MESSAGE"]
        elif kind == "REVIEW":
            base["description"] = NOTIFICATIONS["REVIEW"]
        else:
            base["description"] = rnd.choice([
                "Добро пожаловать на платформу! Заполните профиль и навыки.",
                "Ваш профиль прошёл модерацию, отклики доступны.",
                "Напоминание: не забудьте указать сроки в отклике.",
            ])
        base["created_at"] = extra["created_at"]
        base["updated_at"] = extra["created_at"]
        notifications.append(base)

    # базовые уведомления по событиям
    for p_idx, project in enumerate(projects):
        related = [p for p in proposals if p["project_idx"] == p_idx]
        for proposal in related[:2]:
            add_notification(
                "PROPOSAL", project["customer_id"], project_idx=p_idx,
                from_user_idx=proposal["freelancer_id"],
                created_at=proposal["created_at"],
            )

    for contract in contracts:
        p_idx = contract["project_idx"]
        add_notification(
            "CONTRACT", contract["freelancer_id"], project_idx=p_idx,
            contract_idx=contract_index[id(contract)],
            from_user_idx=contract["customer_id"],
            created_at=contract["start_date"],
        )
        add_notification(
            "CONTRACT", contract["customer_id"], project_idx=p_idx,
            contract_idx=contract_index[id(contract)],
            from_user_idx=contract["freelancer_id"],
            created_at=contract["start_date"] + timedelta(minutes=5),
        )

    for milestone in milestones:
        contract = contracts[milestone["contract_idx"]]
        add_notification(
            "MILESTONE", contract["customer_id"], milestone=milestone["title"],
            contract_idx=milestone["contract_idx"],
            from_user_idx=contract["freelancer_id"],
            created_at=milestone["updated_at"],
        )

    for message in messages[: max(5, len(messages) // 5)]:
        contract = contracts[message["contract_idx"]]
        recipient = (
            contract["customer_id"]
            if message["sender_id"] == contract["freelancer_id"]
            else contract["freelancer_id"]
        )
        add_notification(
            "MESSAGE", recipient, contract_idx=message["contract_idx"],
            from_user_idx=message["sender_id"], created_at=message["created_at"],
        )

    for review in reviews:
        contract = contracts[review["contract_idx"]]
        add_notification(
            "REVIEW", review["to_user_idx"], contract_idx=review["contract_idx"],
            from_user_idx=review["from_user_idx"], created_at=review["created_at"],
        )

    # SYSTEM-уведомления: по одному на часть пользователей
    for idx, user in enumerate(users[2: 2 + max(3, n_users // 4)]):
        add_notification("SYSTEM", idx + 2, created_at=user["created_at"])

    # ── подгонка под целевой объём ──────────────────────────────────────────
    # Структурные данные важнее уведомлений, поэтому:
    #   1) если их уже больше цели — режем сообщения (они наименее важны);
    #   2) уведомления оставляем в количестве «цель - остальное»;
    #   3) если их не хватает — добираем случайными событиями.
    base_total = (
        len(users) + len(projects) + len(proposals) + len(contracts)
        + len(milestones) + len(reviews) + len(messages)
    )

    while base_total > target and messages:
        messages.pop()
        base_total -= 1

    allowed_notifications = max(0, target - base_total)

    if len(notifications) > allowed_notifications:
        rnd.shuffle(notifications)
        notifications = notifications[:allowed_notifications]

    attempts = 0
    while len(notifications) < allowed_notifications and attempts < allowed_notifications * 20:
        attempts += 1
        if contracts and rnd.random() < 0.5:
            contract = rnd.choice(contracts)
            kind = rnd.choice(["CONTRACT", "MILESTONE", "MESSAGE", "REVIEW"])
            if kind == "REVIEW" and contract["status"] != "COMPLETED":
                kind = "MESSAGE"
            recipient = rnd.choice([contract["customer_id"], contract["freelancer_id"]])
            created = contract["start_date"] + timedelta(days=rnd.randint(0, 30))
            kwargs = {
                "contract_idx": contract_index[id(contract)],
                "from_user_idx": (
                    contract["customer_id"]
                    if recipient == contract["freelancer_id"]
                    else contract["freelancer_id"]
                ),
            }
            if kind == "MILESTONE":
                kwargs["milestone"] = rnd.choice(
                    MILESTONES[projects[contract["project_idx"]]["category"]]
                )
            add_notification(kind, recipient, created_at=created, **kwargs)
        elif projects:
            p_idx = rnd.randrange(len(projects))
            project = projects[p_idx]
            kind = "PROPOSAL" if proposals else "CONTRACT"
            add_notification(
                kind, project["customer_id"], project_idx=p_idx,
                from_user_idx=rnd.choice(freelancers_idx),
                created_at=project["created_at"] + timedelta(hours=rnd.randint(1, 72)),
            )

    return Plan(
        users=users, projects=projects, proposals=proposals, contracts=contracts,
        milestones=milestones, reviews=reviews, messages=messages,
        notifications=notifications,
    )


# ────────────────────────────────────────────────────────────────────────────
# Запись в БД
# ────────────────────────────────────────────────────────────────────────────

TRUNCATE_SQL = """
TRUNCATE TABLE notifications, chat_messages, reviews, milestones,
               contracts, proposals, projects, users
    RESTART IDENTITY CASCADE
"""


async def insert_all(conn: asyncpg.Connection, plan: Plan) -> None:
    user_ids: list[int] = []
    for u in plan.users:
        user_ids.append(await conn.fetchval(
            """
            INSERT INTO users (email, username, hashed_password, role, fullname,
                               bio, skills, rating, completed_projects, is_active,
                               created_at, updated_at)
            VALUES ($1, $2, $3, $4::roleenum, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
            """,
            u["email"], u["username"], u["hashed_password"], u["role"], u["fullname"],
            u["bio"], u["skills"], u["rating"], u["completed_projects"], u["is_active"],
            u["created_at"], u["updated_at"],
        ))

    project_ids: list[int] = []
    for p in plan.projects:
        project_ids.append(await conn.fetchval(
            """
            INSERT INTO projects (title, description, budget, deadline, category,
                                  customer_id, freelancer_id, status, is_deleted,
                                  created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5::projectcategoryenum, $6, $7,
                    $8::projectstatusenum, $9, $10, $11)
            RETURNING id
            """,
            p["title"], p["description"], p["budget"], p["deadline"], p["category"],
            user_ids[p["customer_id"]],
            user_ids[p["freelancer_id"]] if p["freelancer_id"] is not None else None,
            p["status"], p["is_deleted"], p["created_at"], p["updated_at"],
        ))

    proposal_ids: list[int] = []
    for pr in plan.proposals:
        proposal_ids.append(await conn.fetchval(
            """
            INSERT INTO proposals (project_id, freelancer_id, cover_letter,
                                   bid_amount, estimated_days, status,
                                   created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6::proposalstatusenum, $7, $8)
            RETURNING id
            """,
            project_ids[pr["project_idx"]], user_ids[pr["freelancer_id"]],
            pr["cover_letter"], pr["bid_amount"], pr["estimated_days"],
            pr["status"], pr["created_at"], pr["updated_at"],
        ))

    contract_ids: list[int] = []
    for c in plan.contracts:
        contract_ids.append(await conn.fetchval(
            """
            INSERT INTO contracts (project_id, proposal_id, customer_id, freelancer_id,
                                   final_price, start_date, end_date, status,
                                   created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::contractstatusenum, $9, $10)
            RETURNING id
            """,
            project_ids[c["project_idx"]], proposal_ids[c["proposal_idx"]],
            user_ids[c["customer_id"]], user_ids[c["freelancer_id"]],
            c["final_price"], c["start_date"], c["end_date"], c["status"],
            c["created_at"], c["updated_at"],
        ))

    for m in plan.milestones:
        await conn.execute(
            """
            INSERT INTO milestones (contract_id, title, description, due_date,
                                    status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5::milestonestatusenum, $6, $7)
            """,
            contract_ids[m["contract_idx"]], m["title"], m["description"],
            m["due_date"], m["status"], m["created_at"], m["updated_at"],
        )

    for r in plan.reviews:
        await conn.execute(
            """
            INSERT INTO reviews (contract_id, from_user_id, to_user_id, rating,
                                 comment, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            contract_ids[r["contract_idx"]], user_ids[r["from_user_idx"]],
            user_ids[r["to_user_idx"]], r["rating"], r["comment"],
            r["created_at"], r["updated_at"],
        )

    for msg in plan.messages:
        await conn.execute(
            """
            INSERT INTO chat_messages (contract_id, sender_id, message, is_read,
                                       created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            contract_ids[msg["contract_idx"]], user_ids[msg["sender_id"]],
            msg["message"], msg["is_read"], msg["created_at"], msg["updated_at"],
        )

    for n in plan.notifications:
        await conn.execute(
            """
            INSERT INTO notifications (type, to_user_id, description, is_read,
                                       contract_id, project_id, from_user_id,
                                       created_at, updated_at)
            VALUES ($1::notificationtypeenum, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            n["type"], user_ids[n["to_user_id"]], n["description"], n["is_read"],
            contract_ids[n["contract_idx"]] if n["contract_idx"] is not None else None,
            project_ids[n["project_idx"]] if n["project_idx"] is not None else None,
            user_ids[n["from_user_idx"]] if n["from_user_idx"] is not None else None,
            n["created_at"], n["updated_at"],
        )

    # согласуем агрегаты пользователей с фактическими данными
    await conn.execute(
        """
        UPDATE users u
        SET rating = COALESCE(sub.avg_rating, 0)
        FROM (
            SELECT to_user_id, ROUND(AVG(rating)::numeric, 1)::float AS avg_rating
            FROM reviews GROUP BY to_user_id
        ) sub
        WHERE u.id = sub.to_user_id
        """
    )
    await conn.execute(
        """
        UPDATE users u
        SET completed_projects = COALESCE(sub.cnt, 0)
        FROM (
            SELECT freelancer_id, COUNT(*) AS cnt
            FROM contracts WHERE status = 'COMPLETED'
            GROUP BY freelancer_id
        ) sub
        WHERE u.id = sub.freelancer_id
        """
    )


async def run(args: argparse.Namespace) -> None:
    dsn = build_dsn(args)
    pwd_hash = password_hash(args.password)
    plan = plan_data(args.records, args.seed, pwd_hash)

    conn = await asyncpg.connect(dsn)
    try:
        async with conn.transaction():
            if not args.append:
                await conn.execute(TRUNCATE_SQL)
            await insert_all(conn, plan)

        rows = await conn.fetch(
            """
            SELECT 'users' AS t, count(*) AS cnt FROM users
            UNION ALL SELECT 'projects', count(*) FROM projects
            UNION ALL SELECT 'proposals', count(*) FROM proposals
            UNION ALL SELECT 'contracts', count(*) FROM contracts
            UNION ALL SELECT 'milestones', count(*) FROM milestones
            UNION ALL SELECT 'reviews', count(*) FROM reviews
            UNION ALL SELECT 'chat_messages', count(*) FROM chat_messages
            UNION ALL SELECT 'notifications', count(*) FROM notifications
            """
        )
    finally:
        await conn.close()

    print("\nСгенерировано записей:")
    total = 0
    for row in rows:
        print(f"  {row['t']:<16} {row['cnt']}")
        total += row["cnt"]
    print(f"  {'ИТОГО':<16} {total}")
    print(f"\nПользователи входят с паролем: {args.password}")
    if total < 300 or total > 400:
        print(f"Внимание: итог {total} вне диапазона 300-400, поправьте --records.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Генератор тестовых данных для фриланс-биржи")
    parser.add_argument("--records", type=int, default=350, help="целевое число записей (300-400)")
    parser.add_argument("--seed", type=int, default=42, help="seed для воспроизводимости")
    parser.add_argument("--dsn", type=str, default=None, help="DSN PostgreSQL")
    parser.add_argument("--append", action="store_true", help="не очищать таблицы перед вставкой")
    parser.add_argument("--password", type=str, default="password123", help="пароль всех пользователей")
    args = parser.parse_args()

    if args.records < 100:
        raise SystemExit("--records слишком мал: берите 300-400")
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
