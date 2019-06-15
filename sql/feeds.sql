CREATE TABLE IF NOT EXISTS feeds(
    id       INTEGER PRIMARY KEY,
    url      TEXT NOT NULL UNIQUE COLLATE NOCASE,
    title    TEXT,
    subtitle TEXT,
    etag     TEXT,
    modified TEXT,
    updated  INTEGER
);