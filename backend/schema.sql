PRAGMA foreign_keys = ON;

-- ======================
-- Snake table
-- ======================
CREATE TABLE IF NOT EXISTS Snake (
    snake_id INTEGER PRIMARY KEY AUTOINCREMENT,
    common_name TEXT NOT NULL,
    scientific_name TEXT NOT NULL,
    venom_level TEXT NOT NULL CHECK (
        venom_level IN ('non-venomous', 'mild', 'high')
    ),
    description TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_snake_unique
ON Snake(common_name, scientific_name);

-- ======================
-- Feature table
-- ======================
CREATE TABLE IF NOT EXISTS Feature (
    feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- ======================
-- Region table
-- ======================
CREATE TABLE IF NOT EXISTS Region (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- ======================
-- SnakeFeature (junction)
-- ======================
CREATE TABLE IF NOT EXISTS SnakeFeature (
    snake_id INTEGER NOT NULL,
    feature_id INTEGER NOT NULL,
    weight INTEGER NOT NULL CHECK (weight BETWEEN 1 AND 5),
    PRIMARY KEY (snake_id, feature_id),
    FOREIGN KEY (snake_id)
        REFERENCES Snake(snake_id)
        ON DELETE CASCADE,
    FOREIGN KEY (feature_id)
        REFERENCES Feature(feature_id)
        ON DELETE CASCADE
);

-- ======================
-- SnakeRegion (junction)
-- ======================
CREATE TABLE IF NOT EXISTS SnakeRegion (
    snake_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    PRIMARY KEY (snake_id, region_id),
    FOREIGN KEY (snake_id)
        REFERENCES Snake(snake_id)
        ON DELETE CASCADE,
    FOREIGN KEY (region_id)
        REFERENCES Region(region_id)
        ON DELETE CASCADE
);

-- ======================
-- User table
-- ======================
CREATE TABLE IF NOT EXISTS User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- ======================
-- Question table
-- ======================
CREATE TABLE IF NOT EXISTS Question (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snake_id INTEGER NOT NULL,
    question_type TEXT NOT NULL CHECK (
        question_type IN ('identify_by_image', 'identify_by_description', 'venom_level', 'scientific_name')
    ),
    question_text TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (snake_id)
        REFERENCES Snake(snake_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_question_snake
ON Question(snake_id);

CREATE INDEX IF NOT EXISTS idx_question_type
ON Question(question_type);

-- ======================
-- Answer table
-- ======================
CREATE TABLE IF NOT EXISTS Answer (
    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    answer_text TEXT NOT NULL,
    is_correct INTEGER NOT NULL DEFAULT 0 CHECK (is_correct IN (0, 1)),
    FOREIGN KEY (question_id)
        REFERENCES Question(question_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_answer_question
ON Answer(question_id);

-- ======================
-- Quiz table
-- ======================
CREATE TABLE IF NOT EXISTS Quiz (
    quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    total INTEGER NOT NULL DEFAULT 10,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    FOREIGN KEY (user_id)
        REFERENCES User(user_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_quiz_user
ON Quiz(user_id);

-- ======================
-- Attempt table
-- ======================
CREATE TABLE IF NOT EXISTS Attempt (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    snake_id INTEGER NOT NULL,
    question_id INTEGER,
    answer_id INTEGER,
    quiz_id INTEGER,
    correct INTEGER NOT NULL CHECK (correct IN (0, 1)),
    timestamp TEXT NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES User(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (snake_id)
        REFERENCES Snake(snake_id)
        ON DELETE CASCADE,
    FOREIGN KEY (question_id)
        REFERENCES Question(question_id)
        ON DELETE SET NULL,
    FOREIGN KEY (answer_id)
        REFERENCES Answer(answer_id)
        ON DELETE SET NULL,
    FOREIGN KEY (quiz_id)
        REFERENCES Quiz(quiz_id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_attempt_user
ON Attempt(user_id);

-- ======================
-- AuthToken table
-- ======================
CREATE TABLE IF NOT EXISTS AuthToken (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'user')),
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES User(user_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_authtoken_user
ON AuthToken(user_id);

CREATE INDEX IF NOT EXISTS idx_authtoken_expires
ON AuthToken(expires_at);

-- ======================
-- SnakeImage table
-- ======================
CREATE TABLE IF NOT EXISTS SnakeImage (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snake_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0,1)),
    uploaded_at TEXT NOT NULL,
    FOREIGN KEY (snake_id)
        REFERENCES Snake(snake_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_snakeimage_snake
ON SnakeImage(snake_id); 

CREATE TABLE IF NOT EXISTS Question (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snake_id INTEGER NOT NULL,
    question_type TEXT NOT NULL CHECK (
        question_type IN ('identify_by_image', 'identify_by_description', 'venom_level', 'scientific_name')
    ),
    question_text TEXT,
    difficulty INTEGER NOT NULL DEFAULT 1 CHECK (difficulty BETWEEN 1 AND 5),
    created_at TEXT NOT NULL,
    FOREIGN KEY (snake_id)
        REFERENCES Snake(snake_id)
        ON DELETE CASCADE
);