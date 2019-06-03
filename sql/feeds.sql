CREATE TABLE IF NOT EXISTS feeds(
    id       INTEGER PRIMARY KEY,
    url      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    title    TEXT,
    subtitle TEXT,
    updated  INTEGER
);