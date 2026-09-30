-- ФРИЛАНС-БИРЖА — СХЕМА БАЗЫ ДАННЫХ (PostgreSQL 14+)

-- ЧАСТЬ 0. ОЧИСТКА (для повторного запуска)

DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS milestones CASCADE;
DROP TABLE IF EXISTS contracts CASCADE;
DROP TABLE IF EXISTS proposals CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS users CASCADE;

DROP TYPE IF EXISTS notification_type;
DROP TYPE IF EXISTS milestone_status;
DROP TYPE IF EXISTS contract_role_user;
DROP TYPE IF EXISTS contract_status;
DROP TYPE IF EXISTS proposal_status;
DROP TYPE IF EXISTS project_status;
DROP TYPE IF EXISTS project_category;
DROP TYPE IF EXISTS user_role;

-- ЧАСТЬ 1. ENUM-ТИПЫ

CREATE TYPE user_role AS ENUM (
    'client',
    'freelancer',
    'admin'
);

CREATE TYPE project_category AS ENUM (
    'development',
    'design',
    'marketing',
    'writing',
    'other'
);

CREATE TYPE project_status AS ENUM (
    'draft',
    'open',
    'in_progress',
    'completed',
    'cancelled'
);

CREATE TYPE proposal_status AS ENUM (
    'pending',
    'accepted',
    'rejected',
    'withdrawn'
);

CREATE TYPE contract_status AS ENUM (
    'active',
    'completed',
    'cancelled'
);

CREATE TYPE contract_role_user AS ENUM (
    'freelancer',
    'customer'
);

CREATE TYPE milestone_status AS ENUM (
    'pending',
    'completed',
    'approved'
);

CREATE TYPE notification_type AS ENUM (
    'proposal',
    'message',
    'contract',
    'milestone',
    'review',
    'system'
);

-- ЧАСТЬ 2. ТАБЛИЦЫ

-- Таблица 1. users
CREATE TABLE users (
    id                 SERIAL PRIMARY KEY,
    email              VARCHAR(255) NOT NULL,
    username           VARCHAR(100) NOT NULL,
    hashed_password    VARCHAR(255) NOT NULL,
    role               user_role    NOT NULL DEFAULT 'client',
    full_name          VARCHAR(255) NOT NULL,
    bio                TEXT,
    skills             VARCHAR(100)[],
    rating             REAL         NOT NULL DEFAULT 0.0
                       CHECK (rating >= 0 AND rating <= 5),
    completed_projects INTEGER      NOT NULL DEFAULT 0
                       CHECK (completed_projects >= 0),
    is_active          BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_email    UNIQUE (email),
    CONSTRAINT uq_users_username UNIQUE (username)
);

CREATE INDEX idx_users_email    ON users (email);
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_role     ON users (role);

-- Таблица 2. projects
CREATE TABLE projects (
    id            SERIAL PRIMARY KEY,
    title         VARCHAR(255)     NOT NULL,
    description   TEXT             NOT NULL,
    budget        INTEGER          NOT NULL CHECK (budget > 0),
    deadline      TIMESTAMPTZ      NOT NULL,
    category      project_category NOT NULL,
    customer_id   INTEGER          NOT NULL,
    freelancer_id INTEGER,
    status        project_status   NOT NULL DEFAULT 'draft',
    created_at    TIMESTAMPTZ      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMPTZ      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_projects_customer
        FOREIGN KEY (customer_id) REFERENCES users(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_projects_freelancer
        FOREIGN KEY (freelancer_id) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_projects_title      ON projects (title);
CREATE INDEX idx_projects_customer   ON projects (customer_id);
CREATE INDEX idx_projects_freelancer ON projects (freelancer_id);
CREATE INDEX idx_projects_status     ON projects (status);
CREATE INDEX idx_projects_category   ON projects (category);

-- Таблица 3. proposals (без FK на contracts — создаётся позже)
CREATE TABLE proposals (
    id             SERIAL PRIMARY KEY,
    project_id     INTEGER         NOT NULL,
    freelancer_id  INTEGER         NOT NULL,
    contract_id    INTEGER         UNIQUE,
    cover_letter   TEXT            NOT NULL,
    bid_amount     INTEGER         NOT NULL CHECK (bid_amount > 0),
    estimated_days INTEGER         NOT NULL CHECK (estimated_days > 0),
    status         proposal_status NOT NULL DEFAULT 'pending',
    created_at     TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_proposals_project
        FOREIGN KEY (project_id) REFERENCES projects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_proposals_freelancer
        FOREIGN KEY (freelancer_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_proposal_per_freelancer
        UNIQUE (project_id, freelancer_id)
);

CREATE INDEX idx_proposals_project    ON proposals (project_id);
CREATE INDEX idx_proposals_freelancer ON proposals (freelancer_id);
CREATE INDEX idx_proposals_contract   ON proposals (contract_id);
CREATE INDEX idx_proposals_status     ON proposals (status);

-- Таблица 4. contracts
CREATE TABLE contracts (
    id            SERIAL PRIMARY KEY,
    project_id    INTEGER         NOT NULL UNIQUE,
    proposal_id   INTEGER         NOT NULL UNIQUE,
    customer_id   INTEGER         NOT NULL,
    freelancer_id INTEGER         NOT NULL,
    final_price   INTEGER         NOT NULL CHECK (final_price > 0),
    start_date    TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date      TIMESTAMPTZ,
    status        contract_status NOT NULL DEFAULT 'active',
    created_at    TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_contracts_project
        FOREIGN KEY (project_id) REFERENCES projects(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_contracts_proposal
        FOREIGN KEY (proposal_id) REFERENCES proposals(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_contracts_customer
        FOREIGN KEY (customer_id) REFERENCES users(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_contracts_freelancer
        FOREIGN KEY (freelancer_id) REFERENCES users(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_contracts_dates
        CHECK (end_date IS NULL OR end_date >= start_date),
    CONSTRAINT chk_contracts_different_users
        CHECK (customer_id <> freelancer_id)
);

CREATE INDEX idx_contracts_project    ON contracts (project_id);
CREATE INDEX idx_contracts_proposal   ON contracts (proposal_id);
CREATE INDEX idx_contracts_customer   ON contracts (customer_id);
CREATE INDEX idx_contracts_freelancer ON contracts (freelancer_id);
CREATE INDEX idx_contracts_status     ON contracts (status);

-- Обратный FK: proposals.contract_id → contracts.id
ALTER TABLE proposals
    ADD CONSTRAINT fk_proposals_contract
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
        ON DELETE SET NULL ON UPDATE CASCADE;

-- Таблица 5. milestones
CREATE TABLE milestones (
    id          SERIAL PRIMARY KEY,
    contract_id INTEGER          NOT NULL,
    title       VARCHAR(255)     NOT NULL,
    description TEXT,
    due_date    TIMESTAMPTZ      NOT NULL,
    status      milestone_status NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMPTZ      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_milestones_contract
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_milestones_contract ON milestones (contract_id);
CREATE INDEX idx_milestones_status   ON milestones (status);
CREATE INDEX idx_milestones_due_date ON milestones (due_date);

-- Таблица 6. reviews
CREATE TABLE reviews (
    id           SERIAL PRIMARY KEY,
    contract_id  INTEGER     NOT NULL,
    from_user_id INTEGER     NOT NULL,
    to_user_id   INTEGER     NOT NULL,
    rating       INTEGER     NOT NULL DEFAULT 5
                 CHECK (rating BETWEEN 1 AND 5),
    comment      TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reviews_contract
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_reviews_from_user
        FOREIGN KEY (from_user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_reviews_to_user
        FOREIGN KEY (to_user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_reviews_different_users
        CHECK (from_user_id <> to_user_id),
    CONSTRAINT uq_review_per_contract_author
        UNIQUE (contract_id, from_user_id)
);

CREATE INDEX idx_reviews_contract  ON reviews (contract_id);
CREATE INDEX idx_reviews_from_user ON reviews (from_user_id);
CREATE INDEX idx_reviews_to_user   ON reviews (to_user_id);

-- Таблица 7. chat_messages
CREATE TABLE chat_messages (
    id          SERIAL PRIMARY KEY,
    contract_id INTEGER     NOT NULL,
    sender_id   INTEGER     NOT NULL,
    message     TEXT        NOT NULL,
    is_read     BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_messages_contract
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_messages_sender
        FOREIGN KEY (sender_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_messages_not_empty
        CHECK (length(trim(message)) > 0)
);

CREATE INDEX idx_messages_contract      ON chat_messages (contract_id);
CREATE INDEX idx_messages_sender        ON chat_messages (sender_id);
CREATE INDEX idx_messages_contract_time ON chat_messages (contract_id, created_at DESC);
CREATE INDEX idx_messages_unread        ON chat_messages (contract_id, is_read)
    WHERE is_read = FALSE;

-- Таблица 8. notifications
CREATE TABLE notifications (
    id           SERIAL PRIMARY KEY,
    type         notification_type NOT NULL,
    to_user_id   INTEGER           NOT NULL,
    description  VARCHAR           NOT NULL,
    is_read      BOOLEAN           NOT NULL DEFAULT FALSE,
    contract_id  INTEGER,
    project_id   INTEGER,
    from_user_id INTEGER,
    created_at   TIMESTAMPTZ       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMPTZ       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_to_user
        FOREIGN KEY (to_user_id) REFERENCES users(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_notifications_from_user
        FOREIGN KEY (from_user_id) REFERENCES users(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_notifications_contract
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_notifications_project
        FOREIGN KEY (project_id) REFERENCES projects(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_notifications_description
        CHECK (length(trim(description)) > 0)
);

CREATE INDEX idx_notifications_to_user  ON notifications (to_user_id);
CREATE INDEX idx_notifications_contract ON notifications (contract_id);
CREATE INDEX idx_notifications_project  ON notifications (project_id);
CREATE INDEX idx_notifications_unread   ON notifications (to_user_id, is_read)
    WHERE is_read = FALSE;

-- КОНЕЦ СКРИПТА