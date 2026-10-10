-- insert_db.sql — демо-данные для фриланс-биржи

-- ЧАСТЬ 0. ОЧИСТКА

TRUNCATE TABLE notifications, chat_messages, reviews, milestones,
               contracts, proposals, projects, users
    RESTART IDENTITY CASCADE;

-- ЧАСТЬ 1. ПОЛЬЗОВАТЕЛИ

INSERT INTO users (id, email, username, hashed_password, role, fullname, bio,
                   skills, rating, completed_projects, is_active, created_at, updated_at)
VALUES
    (1, 'admin@freelance.local', 'admin',
     '$argon2id$v=19$m=65536,t=3,p=4$oHRuTQlhrJUSgvB+j7E2hg$Qj5UOtSluwoMKu0nlFG6vZww70hFJMDJccVPqntNlek',
     'ADMIN'::roleenum, 'Администратор платформы',
     'Следит за порядком на платформе и блокирует нарушителей.',
     NULL, 0, 0, TRUE, NOW() - INTERVAL '180 days', NOW() - INTERVAL '180 days'),

    (2, 'ivan.petrov@example.com', 'ivan_client',
     '$argon2id$v=19$m=65536,t=3,p=4$oHRuTQlhrJUSgvB+j7E2hg$Qj5UOtSluwoMKu0nlFG6vZww70hFJMDJccVPqntNlek',
     'CLIENT'::roleenum, 'Иван Петров',
     'Продуктовый менеджер в студии мобильной разработки. Ищу подрядчиков под разовые задачи.',
     NULL, 4.9, 6, TRUE, NOW() - INTERVAL '120 days', NOW() - INTERVAL '3 days'),

    (3, 'maria.sidorova@example.com', 'maria_client',
     '$argon2id$v=19$m=65536,t=3,p=4$oHRuTQlhrJUSgvB+j7E2hg$Qj5UOtSluwoMKu0nlFG6vZww70hFJMDJccVPqntNlek',
     'CLIENT'::roleenum, 'Мария Сидорова',
     'Основатель SaaS-сервиса для логистики. Собираю команду под долгие проекты.',
     NULL, 4.7, 3, TRUE, NOW() - INTERVAL '95 days', NOW() - INTERVAL '5 days'),

    (4, 'oleg.kuznetsov@example.com', 'oleg_client',
     '$argon2id$v=19$m=65536,t=3,p=4$oHRuTQlhrJUSgvB+j7E2hg$Qj5UOtSluwoMKu0nlFG6vZww70hFJMDJccVPqntNlek',
     'CLIENT'::roleenum, 'Олег Кузнецов',
     'Маркетолог, продвигаю онлайн-школы и локальный бизнес.',
     NULL, 4.5, 2, TRUE, NOW() - INTERVAL '70 days', NOW() - INTERVAL '10 days'),

    (5, 'anna.smirnova@example.com', 'anna_dev',
     '$argon2id$v=19$m=65536,t=3,p=4$oHRuTQlhrJUSgvB+j7E2hg$Qj5UOtSluwoMKu0nlFG6vZww70hFJMDJccVPqntNlek',
     'FREELANCER'::roleenum, 'Анна Смирнова',
     'Backend-разработчик: FastAPI, асинхронный SQLAlchemy, PostgreSQL. Люблю аккуратные API и тесты.',
     ARRAY['Python', 'FastAPI', 'PostgreSQL', 'SQLAlchemy', 'Docker', 'REST API'],
     4.8, 12, TRUE, NOW() - INTERVAL '150 days', NOW() - INTERVAL '1 day'),

    (6, 'dmitry.volkov@example.com', 'dmitry_design',
     '$argon2id$v=19$m=65536,t=3,p=4$oHRuTQlhrJUSgvB+j7E2hg$Qj5UOtSluwoMKu0nlFG6vZww70hFJMDJccVPqntNlek',
     'FREELANCER'::roleenum, 'Дмитрий Волков',
     'Продуктовый дизайнер: интерфейсы, дизайн-системы, прототипы в Figma. Делаю понятные макеты без лишних итераций.',
     ARRAY['Figma', 'UI/UX', 'Дизайн-системы', 'Прототипирование', 'Адаптивная верстка'],
     4.6, 8, TRUE, NOW() - INTERVAL '140 days', NOW() - INTERVAL '2 days'),

    (7, 'elena.kozlova@example.com', 'elena_copy',
     '$argon2id$v=19$m=65536,t=3,p=4$oHRuTQlhrJUSgvB+j7E2hg$Qj5UOtSluwoMKu0nlFG6vZww70hFJMDJccVPqntNlek',
     'FREELANCER'::roleenum, 'Елена Козлова',
     'Копирайтер и редактор: статьи для блогов, лендинги, письма. Пишу по фактам, без воды и канцелярита.',
     ARRAY['Копирайтинг', 'SEO', 'Редактура', 'Контент-план', 'Лендинги'],
     4.9, 15, TRUE, NOW() - INTERVAL '130 days', NOW() - INTERVAL '6 hours'),

    (8, 'sergey.novikov@example.com', 'sergey_market',
     '$argon2id$v=19$m=65536,t=3,p=4$oHRuTQlhrJUSgvB+j7E2hg$Qj5UOtSluwoMKu0nlFG6vZww70hFJMDJccVPqntNlek',
     'FREELANCER'::roleenum, 'Сергей Новиков',
     'Специалист по платному трафику: Яндекс Директ, Google Ads, аналитика воронки.',
     ARRAY['Яндекс Директ', 'Google Ads', 'Аналитика', 'SMM', 'Веб-аналитика'],
     4.3, 5, TRUE, NOW() - INTERVAL '110 days', NOW() - INTERVAL '9 days');

-- ЧАСТЬ 2. ПРОЕКТЫ
-- OPEN        — виден в каталоге и принимает отклики
-- DRAFT       — виден заказчику в «Моих проектах»
-- IN_PROGRESS — есть контракт в работе
-- COMPLETED   — контракт завершён (есть отзывы)
-- CANCELLED   — отменён
-- is_deleted  — один проект «удалён» админом (проверка фильтра «Удалённые»)

INSERT INTO projects (id, title, description, budget, deadline, category,
                      customer_id, freelancer_id, status, is_deleted, created_at, updated_at)
VALUES
    (1, 'Разработка интернет-магазина на FastAPI',
     'Нужно REST API и админка для интернет-магазина: каталог, корзина, заказы, интеграция с платёжным шлюзом. Стек: FastAPI, PostgreSQL, Docker. Есть готовый дизайн и описание сущностей.',
     250000, NOW() + INTERVAL '30 days', 'DEVELOPMENT'::projectcategoryenum,
     2, NULL, 'OPEN'::projectstatusenum, FALSE, NOW() - INTERVAL '6 days', NOW() - INTERVAL '6 days'),

    (2, 'Редизайн личного кабинета SaaS-сервиса',
     'Нужно переработать личный кабинет: дашборд, раздел отчётов, настройки команды. Есть текущие макеты и аналитика по проблемным местам. Ожидаем дизайн-систему и адаптив.',
     120000, NOW() + INTERVAL '20 days', 'DESIGN'::projectcategoryenum,
     3, NULL, 'OPEN'::projectstatusenum, FALSE, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),

    (3, 'Лендинг для онлайн-курса по аналитике',
     'Нужен лендинг с формой заявки и подключением метрик. Дизайн есть, требуется верстка и аккуратная адаптация под мобильные. Важна скорость загрузки.',
     60000, NOW() + INTERVAL '14 days', 'DEVELOPMENT'::projectcategoryenum,
     2, NULL, 'OPEN'::projectstatusenum, FALSE, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),

    (4, 'Копирайтинг: 10 статей для блога о логистике',
     'Ищем автора для цикла статей: 10 текстов по 6000-8000 знаков по готовому контент-плану. Нужны понятные заголовки, факты и ссылки на источники.',
     45000, NOW() + INTERVAL '25 days', 'WRITING'::projectcategoryenum,
     4, NULL, 'OPEN'::projectstatusenum, FALSE, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),

    (5, 'Настройка контекстной рекламы для локальных клиник',
     'Нужно собрать кампании в Яндекс Директе по нескольким городам, настроить цели и отчётность. Бюджет на клики обсуждаем отдельно.',
     80000, NOW() + INTERVAL '18 days', 'MARKETING'::projectcategoryenum,
     4, NULL, 'OPEN'::projectstatusenum, FALSE, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),

    (6, 'Мобильное приложение для службы доставки',
     'Черновик: проектируем приложение для курьеров и клиентов. Нужно оценить объём работ и собрать команду. Требования ещё уточняются.',
     400000, NOW() + INTERVAL '60 days', 'DEVELOPMENT'::projectcategoryenum,
     2, NULL, 'DRAFT'::projectstatusenum, FALSE, NOW() - INTERVAL '8 days', NOW() - INTERVAL '1 day'),

    (7, 'Дизайн упаковки для линейки чая',
     'Черновик: нужны макеты упаковки для пяти вкусов, подготовка к печати. Бренд-бук есть, обсудим детали после выбора исполнителя.',
     90000, NOW() + INTERVAL '45 days', 'DESIGN'::projectcategoryenum,
     3, NULL, 'DRAFT'::projectstatusenum, FALSE, NOW() - INTERVAL '7 days', NOW() - INTERVAL '2 days'),

    (8, 'Разработка API для маркетплейса',
     'Проект в работе: API для товаров, заказов и выплат продавцам. Спринты по две недели, код-ревью и тесты обязательны.',
     300000, NOW() + INTERVAL '40 days', 'DEVELOPMENT'::projectcategoryenum,
     3, 5, 'IN_PROGRESS'::projectstatusenum, FALSE, NOW() - INTERVAL '40 days', NOW() - INTERVAL '1 day'),

    (9, 'Дизайн-система для банковского приложения',
     'Завершённый проект: собрали библиотеку компонентов и гайдлайны для мобильного банка.',
     180000, NOW() - INTERVAL '20 days', 'DESIGN'::projectcategoryenum,
     2, 6, 'COMPLETED'::projectstatusenum, FALSE, NOW() - INTERVAL '90 days', NOW() - INTERVAL '5 days'),

    (10, 'Разработка CRM для отдела продаж',
     'Проект отменён заказчиком: поменялись приоритеты, вернёмся к задаче позже.',
     350000, NOW() + INTERVAL '50 days', 'DEVELOPMENT'::projectcategoryenum,
     4, NULL, 'CANCELLED'::projectstatusenum, FALSE, NOW() - INTERVAL '50 days', NOW() - INTERVAL '35 days'),

    (11, '[удалён] Тестовый проект для проверки модерации',
     'Служебный проект: админ пометил его удалённым, чтобы проверить фильтр «Удалённые» и восстановление.',
     10000, NOW() + INTERVAL '10 days', 'OTHER'::projectcategoryenum,
     2, NULL, 'OPEN'::projectstatusenum, TRUE, NOW() - INTERVAL '30 days', NOW() - INTERVAL '20 days'),

    (12, 'Консультация по самозанятости и налогам для фрилансера',
     'Нужна разовая консультация: как оформить самозанятость, какие лимиты дохода и как считать налог при работе с несколькими заказчиками. Нужны понятные расчёты на примерах.',
     15000, NOW() + INTERVAL '12 days', 'OTHER'::projectcategoryenum,
     4, NULL, 'OPEN'::projectstatusenum, FALSE, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day');

-- ЧАСТЬ 3. ОТКЛИКИ
-- Для открытых проектов — PENDING, для проекта в работе один ACCEPTED
-- и отклонённые остальные, для завершённого — ACCEPTED.

INSERT INTO proposals (id, project_id, freelancer_id, cover_letter, bid_amount,
                       estimated_days, status, created_at, updated_at)
VALUES
    (1, 1, 5,
     'Здравствуйте! Делала похожие магазины на FastAPI: каталог, корзина, оплата. Могу собрать API и админку за 25 дней, разобью работу на этапы и покажу промежуточные результаты.',
     240000, 25, 'PENDING'::proposalstatusenum, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),

    (2, 1, 6,
     'Могу дополнительно предложить проработку интерфейса админки и дизайн-систему для карточек товаров, чтобы проект выглядел целостно.',
     260000, 30, 'PENDING'::proposalstatusenum, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),

    (3, 2, 6,
     'Переработаю кабинет: соберу дизайн-систему, переделаю дашборд и отчёты, добавлю адаптив. Первый прототип покажу через неделю после старта.',
     115000, 18, 'PENDING'::proposalstatusenum, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),

    (4, 3, 5,
     'Сверстаю лендинг по макету, подключу формы и метрики, оптимизирую загрузку. Опыт с лендингами под курсы есть.',
     58000, 10, 'PENDING'::proposalstatusenum, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),

    (5, 3, 7,
     'Дополнительно могу написать тексты под лендинг, если нужно — соберу структуру и заголовки под целевую аудиторию.',
     62000, 12, 'REJECTED'::proposalstatusenum, NOW() - INTERVAL '3 days', NOW() - INTERVAL '2 days'),

    (6, 4, 7,
     'Пишу статьи для блогов о логистике и B2B. По контент-плану уложусь в срок, каждую статью сдаю с источниками и подобранными иллюстрациями.',
     42000, 20, 'PENDING'::proposalstatusenum, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),

    (7, 5, 8,
     'Настрою кампании по городам, соберу семантику, подключу цели и сделаю отчёт по стоимости заявки. Есть кейсы в медицине.',
     78000, 15, 'PENDING'::proposalstatusenum, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),

    (8, 8, 5,
     'Готова взять API: спроектирую схему, напишу сервисы и тесты, настрою CI. Работаю спринтами по две недели с демо в конце каждого.',
     290000, 45, 'ACCEPTED'::proposalstatusenum, NOW() - INTERVAL '38 days', NOW() - INTERVAL '35 days'),

    (9, 8, 6,
     'Могу подключиться к интерфейсной части проекта, если понадобится дизайн админки и клиентских страниц.',
     95000, 20, 'REJECTED'::proposalstatusenum, NOW() - INTERVAL '37 days', NOW() - INTERVAL '35 days'),

    (10, 9, 6,
     'Соберу дизайн-систему: компоненты, состояния, гайдлайны и макеты ключевых экранов. Передаю всё в Figma с описанием.',
     180000, 40, 'ACCEPTED'::proposalstatusenum, NOW() - INTERVAL '85 days', NOW() - INTERVAL '80 days'),

    (11, 10, 5,
     'Могу взяться за CRM: модули сделок, задачи и отчёты. Оценка после короткого интервью по процессам.',
     340000, 60, 'WITHDRAWN'::proposalstatusenum, NOW() - INTERVAL '48 days', NOW() - INTERVAL '40 days'),

    (12, 10, 7,
     'Готова написать тексты и подсказки внутри интерфейса CRM, если проект возобновится.',
     40000, 15, 'REJECTED'::proposalstatusenum, NOW() - INTERVAL '47 days', NOW() - INTERVAL '35 days');

-- ЧАСТЬ 4. КОНТРАКТЫ
-- ACTIVE    — проект 8 (есть этапы и чат)
-- COMPLETED — проект 9 (все этапы утверждены, есть отзывы)

INSERT INTO contracts (id, project_id, proposal_id, customer_id, freelancer_id,
                       final_price, start_date, end_date, status, created_at, updated_at)
VALUES
    (1, 8, 8, 3, 5, 290000,
     NOW() - INTERVAL '35 days', NULL, 'ACTIVE'::contractstatusenum,
     NOW() - INTERVAL '35 days', NOW() - INTERVAL '1 day'),

    (2, 9, 10, 2, 6, 180000,
     NOW() - INTERVAL '80 days', NOW() - INTERVAL '5 days', 'COMPLETED'::contractstatusenum,
     NOW() - INTERVAL '80 days', NOW() - INTERVAL '5 days');

-- ЧАСТЬ 5. ЭТАПЫ

INSERT INTO milestones (id, contract_id, title, description, due_date, status, created_at, updated_at)
VALUES
    (1, 1, 'Проектирование схемы данных',
     'Согласовать сущности товаров, заказов и выплат, подготовить миграции.',
     NOW() - INTERVAL '20 days', 'APPROVED'::milestonestatusenum,
     NOW() - INTERVAL '35 days', NOW() - INTERVAL '22 days'),

    (2, 1, 'API каталога и корзины',
     'Эндпоинты каталога, фильтры, корзина, тесты на основные сценарии.',
     NOW() - INTERVAL '5 days', 'APPROVED'::milestonestatusenum,
     NOW() - INTERVAL '30 days', NOW() - INTERVAL '7 days'),

    (3, 1, 'Заказы и выплаты продавцам',
     'Оформление заказа, статусы, расчёт выплат, интеграция с платежным шлюзом.',
     NOW() + INTERVAL '7 days', 'COMPLETED'::milestonestatusenum,
     NOW() - INTERVAL '15 days', NOW() - INTERVAL '2 days'),

    (4, 1, 'Документация и нагрузочные проверки',
     'Описать API в OpenAPI, прогнать нагрузочный тест на каталог, подготовить инструкцию по запуску.',
     NOW() + INTERVAL '20 days', 'PENDING'::milestonestatusenum,
     NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days'),

    (5, 2, 'Аудит и структура дизайн-системы',
     'Разобрать текущие экраны, собрать библиотеку компонентов и токены.',
     NOW() - INTERVAL '60 days', 'APPROVED'::milestonestatusenum,
     NOW() - INTERVAL '80 days', NOW() - INTERVAL '62 days'),

    (6, 2, 'Макеты ключевых экранов',
     'Дашборд, отчёты, настройки команды — в светлой и тёмной темах.',
     NOW() - INTERVAL '30 days', 'APPROVED'::milestonestatusenum,
     NOW() - INTERVAL '60 days', NOW() - INTERVAL '32 days'),

    (7, 2, 'Передача и гайдлайны',
     'Финальные макеты, правила использования компонентов, созвон с командой разработки.',
     NOW() - INTERVAL '10 days', 'APPROVED'::milestonestatusenum,
     NOW() - INTERVAL '30 days', NOW() - INTERVAL '12 days');

-- ЧАСТЬ 6. ОТЗЫВЫ (только по завершённому контракту 2)

INSERT INTO reviews (id, contract_id, from_user_id, to_user_id, rating, comment, created_at, updated_at)
VALUES
    (1, 2, 2, 6, 5,
     'Дизайн-система получилась аккуратной и понятной: разработчики быстро подхватили компоненты. Сроки не сдвинулись ни разу, коммуникация отличная.',
     NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),

    (2, 2, 6, 2, 5,
     'Заказчик с чёткими требованиями и быстрой обратной связью: правки собирались в один список, решения принимались без долгих согласований.',
     NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days');

-- ЧАСТЬ 7. ЧАТ
-- Диалог по активному контракту 1 (часть сообщений не прочитана) и короткая
-- история по завершённому контракту 2.

INSERT INTO chat_messages (id, contract_id, sender_id, message, is_read, created_at, updated_at)
VALUES
    (1, 1, 3, 'Анна, привет! Начинаем с этапа проектирования, доступ к репозиторию отправила на почту.',
     TRUE, NOW() - INTERVAL '35 days', NOW() - INTERVAL '35 days'),
    (2, 1, 5, 'Мария, здравствуйте! Схему данных подготовлю к пятнице, покажу на созвоне.',
     TRUE, NOW() - INTERVAL '34 days', NOW() - INTERVAL '34 days'),
    (3, 1, 5, 'Схема готова, миграции в ветке feature/schema. Обратите внимание на таблицу выплат — там вопрос по комиссии.',
     TRUE, NOW() - INTERVAL '22 days', NOW() - INTERVAL '22 days'),
    (4, 1, 3, 'Посмотрела, комиссию считаем от суммы заказа без доставки. Правьте, если что-то не сходится.',
     TRUE, NOW() - INTERVAL '21 days', NOW() - INTERVAL '21 days'),
    (5, 1, 5, 'Готово: заказы и выплаты работают, этап отправила на утверждение. Жду проверки.',
     FALSE, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
    (6, 1, 5, 'И небольшой вопрос: документацию оформлять в отдельной ветке или рядом с кодом?',
     FALSE, NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours'),
    (7, 2, 2, 'Дмитрий, добрый день! По последнему этапу — когда ждать финальные макеты?',
     TRUE, NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
    (8, 2, 6, 'Собрал всё в один файл, добавил гайдлайны. Отправил на почту и продублировал в Figma.',
     TRUE, NOW() - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
    (9, 2, 2, 'Спасибо, принято. Отзыв оставила, было приятно работать!',
     TRUE, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days');

-- ЧАСТЬ 8. УВЕДОМЛЕНИЯ
-- Часть прочитана, часть нет — чтобы на колокольчике был бейдж.

INSERT INTO notifications (id, type, to_user_id, description, is_read,
                           contract_id, project_id, from_user_id, created_at, updated_at)
VALUES
    (1, 'CONTRACT'::notificationtypeenum, 5,
     'Заключён контракт по проекту «Разработка API для маркетплейса».',
     TRUE, 1, 8, 3, NOW() - INTERVAL '35 days', NOW() - INTERVAL '35 days'),

    (2, 'CONTRACT'::notificationtypeenum, 3,
     'Анна Смирнова приняла условия, контракт по проекту «Разработка API для маркетплейса» создан.',
     TRUE, 1, 8, 5, NOW() - INTERVAL '35 days', NOW() - INTERVAL '35 days'),

    (3, 'MILESTONE'::notificationtypeenum, 3,
     'Этап «Заказы и выплаты продавцам» завершён исполнителем и ждёт вашего утверждения.',
     FALSE, 1, NULL, 5, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),

    (4, 'MESSAGE'::notificationtypeenum, 3,
     'Новое сообщение от Анны Смирновой в чате по контракту.',
     FALSE, 1, NULL, 5, NOW() - INTERVAL '4 hours', NOW() - INTERVAL '4 hours'),

    (5, 'PROPOSAL'::notificationtypeenum, 2,
     'Новый отклик на проект «Разработка интернет-магазина на FastAPI» от Анны Смирновой.',
     FALSE, NULL, 1, 5, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),

    (6, 'PROPOSAL'::notificationtypeenum, 2,
     'Новый отклик на проект «Разработка интернет-магазина на FastAPI» от Дмитрия Волкова.',
     FALSE, NULL, 1, 6, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),

    (7, 'PROPOSAL'::notificationtypeenum, 3,
     'Новый отклик на проект «Редизайн личного кабинета SaaS-сервиса» от Дмитрия Волкова.',
     TRUE, NULL, 2, 6, NOW() - INTERVAL '4 days', NOW() - INTERVAL '3 days'),

    (8, 'REVIEW'::notificationtypeenum, 6,
     'Иван Петров оставил вам отзыв с оценкой 5 по завершённому контракту.',
     FALSE, 2, NULL, 2, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),

    (9, 'MILESTONE'::notificationtypeenum, 5,
     'Этап «Документация и нагрузочные проверки» добавлен в контракт.',
     TRUE, 1, NULL, NULL, NOW() - INTERVAL '15 days', NOW() - INTERVAL '15 days'),

    (10, 'SYSTEM'::notificationtypeenum, 7,
     'Добро пожаловать на Freelance LITE! Заполните профиль и навыки, чтобы заказчики чаще вас находили.',
     TRUE, NULL, NULL, NULL, NOW() - INTERVAL '130 days', NOW() - INTERVAL '130 days'),

    (11, 'SYSTEM'::notificationtypeenum, 8,
     'Ваш профиль прошёл модерацию. Отклики на проекты уже доступны.',
     TRUE, NULL, NULL, NULL, NOW() - INTERVAL '109 days', NOW() - INTERVAL '109 days');

-- ЧАСТЬ 9. SEQUENCES
-- Мы вставляли id вручную, поэтому последовательности нужно сдвинуть,
-- иначе следующая вставка из приложения упадёт на duplicated key.

SELECT setval(pg_get_serial_sequence('users', 'id'),         (SELECT MAX(id) FROM users));
SELECT setval(pg_get_serial_sequence('projects', 'id'),      (SELECT MAX(id) FROM projects));
SELECT setval(pg_get_serial_sequence('proposals', 'id'),     (SELECT MAX(id) FROM proposals));
SELECT setval(pg_get_serial_sequence('contracts', 'id'),     (SELECT MAX(id) FROM contracts));
SELECT setval(pg_get_serial_sequence('milestones', 'id'),    (SELECT MAX(id) FROM milestones));
SELECT setval(pg_get_serial_sequence('reviews', 'id'),       (SELECT MAX(id) FROM reviews));
SELECT setval(pg_get_serial_sequence('chat_messages', 'id'), (SELECT MAX(id) FROM chat_messages));
SELECT setval(pg_get_serial_sequence('notifications', 'id'), (SELECT MAX(id) FROM notifications));

-- ЧАСТЬ 10. ПРОВЕРКА

SELECT 'users'         AS table_name, count(*) FROM users
UNION ALL SELECT 'projects',      count(*) FROM projects
UNION ALL SELECT 'proposals',     count(*) FROM proposals
UNION ALL SELECT 'contracts',     count(*) FROM contracts
UNION ALL SELECT 'milestones',    count(*) FROM milestones
UNION ALL SELECT 'reviews',       count(*) FROM reviews
UNION ALL SELECT 'chat_messages', count(*) FROM chat_messages
UNION ALL SELECT 'notifications', count(*) FROM notifications;

-- КОНЕЦ СКРИПТА
