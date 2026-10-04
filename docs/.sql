-- ФРИЛАНС-БИРЖА — СХЕМА БАЗЫ ДАННЫХ (PostgreSQL 14+)

-- ЧАСТЬ 0. ОЧИСТКА (для повторного запуска)

DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS milestones CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS contracts CASCADE;
DROP TABLE IF EXISTS proposals CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP TYPE IF EXISTS notificationtypeenum;
DROP TYPE IF EXISTS milestonestatusenum;
DROP TYPE IF EXISTS contractstatusenum;
DROP TYPE IF EXISTS proposalstatusenum;
DROP TYPE IF EXISTS projectstatusenum;
DROP TYPE IF EXISTS projectcategoryenum;
DROP TYPE IF EXISTS roleenum;

-- ЧАСТЬ 1. ENUM-ТИПЫ

CREATE TYPE roleenum AS ENUM (
    'CLIENT',
    'FREELANCER',
    'ADMIN'
);

CREATE TYPE projectcategoryenum AS ENUM (
    'DEVELOPMENT',
    'DESIGN',
    'MARKETING',
    'WRITING',
    'OTHER'
);

CREATE TYPE projectstatusenum AS ENUM (
    'DRAFT',
    'OPEN',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);

CREATE TYPE proposalstatusenum AS ENUM (
    'PENDING',
    'ACCEPTED',
    'REJECTED',
    'WITHDRAWN'
);

CREATE TYPE contractstatusenum AS ENUM (
    'ACTIVE',
    'COMPLETED',
    'CANCELLED'
);

CREATE TYPE milestonestatusenum AS ENUM (
    'PENDING',
    'COMPLETED',
    'APPROVED'
);

CREATE TYPE notificationtypeenum AS ENUM (
    'PROPOSAL',
    'MESSAGE',
    'CONTRACT',
    'MILESTONE',
    'REVIEW',
    'SYSTEM'
);

-- ЧАСТЬ 2. ТАБЛИЦЫ

-- Таблица 1. users
CREATE TABLE users (
    email              VARCHAR(255)     NOT NULL,
    username           VARCHAR(100)     NOT NULL,
    hashed_password    VARCHAR(255)     NOT NULL,
    role               roleenum         NOT NULL,
    fullname           VARCHAR(255)     NOT NULL,
    bio                VARCHAR,
    skills             VARCHAR[],
    rating             DOUBLE PRECISION NOT NULL,
    completed_projects INTEGER          NOT NULL DEFAULT 0,
    is_active          BOOLEAN          NOT NULL,
    id                 SERIAL           NOT NULL,
    created_at         TIMESTAMPTZ      NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ      NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email    ON users (email);
CREATE UNIQUE INDEX ix_users_username ON users (username);

-- Таблица 2. projects
CREATE TABLE projects (
    title         VARCHAR(255)        NOT NULL,
    description   VARCHAR             NOT NULL,
    budget        INTEGER             NOT NULL,
    deadline      TIMESTAMPTZ         NOT NULL,
    category      projectcategoryenum NOT NULL,
    customer_id   INTEGER             NOT NULL,
    freelancer_id INTEGER,
    status        projectstatusenum   NOT NULL,
    is_deleted    BOOLEAN             NOT NULL DEFAULT false,
    id            SERIAL              NOT NULL,
    created_at    TIMESTAMPTZ         NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ         NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT projects_customer_id_fkey
        FOREIGN KEY (customer_id) REFERENCES users(id),
    CONSTRAINT projects_freelancer_id_fkey
        FOREIGN KEY (freelancer_id) REFERENCES users(id)
);

CREATE INDEX ix_projects_customer_id   ON projects (customer_id);
CREATE INDEX ix_projects_freelancer_id ON projects (freelancer_id);
CREATE INDEX ix_projects_status        ON projects (status);
CREATE INDEX ix_projects_title         ON projects (title);

-- Таблица 3. proposals
CREATE TABLE proposals (
    project_id     INTEGER            NOT NULL,
    freelancer_id  INTEGER            NOT NULL,
    cover_letter   TEXT               NOT NULL,
    bid_amount     INTEGER            NOT NULL,
    estimated_days INTEGER            NOT NULL,
    status         proposalstatusenum NOT NULL,
    id             SERIAL             NOT NULL,
    created_at     TIMESTAMPTZ        NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ        NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT proposals_freelancer_id_fkey
        FOREIGN KEY (freelancer_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT proposals_project_id_fkey
        FOREIGN KEY (project_id) REFERENCES projects(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_proposal_freelancer_project
        UNIQUE (freelancer_id, project_id)
);

CREATE INDEX ix_proposals_freelancer_id ON proposals (freelancer_id);
CREATE INDEX ix_proposals_project_id    ON proposals (project_id);
CREATE INDEX ix_proposals_status        ON proposals (status);

-- Таблица 4. contracts
CREATE TABLE contracts (
    project_id    INTEGER            NOT NULL,
    proposal_id   INTEGER            NOT NULL,
    customer_id   INTEGER            NOT NULL,
    freelancer_id INTEGER            NOT NULL,
    final_price   INTEGER            NOT NULL,
    start_date    TIMESTAMPTZ        NOT NULL DEFAULT now(),
    end_date      TIMESTAMPTZ,
    status        contractstatusenum NOT NULL,
    id            SERIAL             NOT NULL,
    created_at    TIMESTAMPTZ        NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ        NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_contract_final_price_positive
        CHECK (final_price > 0),
    CONSTRAINT contracts_customer_id_fkey
        FOREIGN KEY (customer_id) REFERENCES users(id)
        ON DELETE RESTRICT,
    CONSTRAINT contracts_freelancer_id_fkey
        FOREIGN KEY (freelancer_id) REFERENCES users(id)
        ON DELETE RESTRICT,
    CONSTRAINT contracts_project_id_fkey
        FOREIGN KEY (project_id) REFERENCES projects(id)
        ON DELETE CASCADE,
    CONSTRAINT contracts_proposal_id_fkey
        FOREIGN KEY (proposal_id) REFERENCES proposals(id)
        ON DELETE RESTRICT
);

CREATE INDEX        ix_contracts_customer_id   ON contracts (customer_id);
CREATE INDEX        ix_contracts_freelancer_id ON contracts (freelancer_id);
CREATE UNIQUE INDEX ix_contracts_project_id    ON contracts (project_id);
CREATE UNIQUE INDEX ix_contracts_proposal_id   ON contracts (proposal_id);

-- Таблица 5. chat_messages
CREATE TABLE chat_messages (
    contract_id INTEGER     NOT NULL,
    sender_id   INTEGER     NOT NULL,
    message     TEXT        NOT NULL,
    is_read     BOOLEAN     NOT NULL,
    id          SERIAL      NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT chat_messages_contract_id_fkey
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
        ON DELETE CASCADE,
    CONSTRAINT chat_messages_sender_id_fkey
        FOREIGN KEY (sender_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX ix_chat_messages_contract_id ON chat_messages (contract_id);
CREATE INDEX ix_chat_messages_sender_id   ON chat_messages (sender_id);

-- Таблица 6. milestones
CREATE TABLE milestones (
    contract_id INTEGER             NOT NULL,
    title       VARCHAR(255)        NOT NULL,
    description TEXT                NOT NULL,
    due_date    TIMESTAMPTZ         NOT NULL,
    status      milestonestatusenum NOT NULL,
    id          SERIAL              NOT NULL,
    created_at  TIMESTAMPTZ         NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ         NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT milestones_contract_id_fkey
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
        ON DELETE CASCADE
);

CREATE INDEX ix_milestones_contract_id ON milestones (contract_id);

-- Таблица 7. notifications
CREATE TABLE notifications (
    type         notificationtypeenum NOT NULL,
    to_user_id   INTEGER              NOT NULL,
    description  VARCHAR              NOT NULL,
    is_read      BOOLEAN              NOT NULL,
    contract_id  INTEGER,
    project_id   INTEGER,
    from_user_id INTEGER,
    id           SERIAL               NOT NULL,
    created_at   TIMESTAMPTZ          NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ          NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT notifications_contract_id_fkey
        FOREIGN KEY (contract_id) REFERENCES contracts(id),
    CONSTRAINT notifications_from_user_id_fkey
        FOREIGN KEY (from_user_id) REFERENCES users(id),
    CONSTRAINT notifications_project_id_fkey
        FOREIGN KEY (project_id) REFERENCES projects(id),
    CONSTRAINT notifications_to_user_id_fkey
        FOREIGN KEY (to_user_id) REFERENCES users(id)
);

-- Таблица 8. reviews
CREATE TABLE reviews (
    contract_id  INTEGER     NOT NULL,
    from_user_id INTEGER     NOT NULL,
    to_user_id   INTEGER     NOT NULL,
    rating       INTEGER     NOT NULL,
    comment      TEXT,
    id           SERIAL      NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_review_rating_range
        CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT reviews_contract_id_fkey
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
        ON DELETE CASCADE,
    CONSTRAINT reviews_from_user_id_fkey
        FOREIGN KEY (from_user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT reviews_to_user_id_fkey
        FOREIGN KEY (to_user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_review_contract_from
        UNIQUE (contract_id, from_user_id)
);

CREATE INDEX ix_reviews_contract_id  ON reviews (contract_id);
CREATE INDEX ix_reviews_from_user_id ON reviews (from_user_id);
CREATE INDEX ix_reviews_to_user_id   ON reviews (to_user_id);

-- КОНЕЦ СКРИПТА