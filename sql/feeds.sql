CREATE TABLE IF NOT EXISTS feeds(
    id       INTEGER PRIMARY KEY,
    url      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    title    TEXT,
    subtitle TEXT,
    cached   TEXT,
    etag     TEXT,
    updated  INTEGER
);