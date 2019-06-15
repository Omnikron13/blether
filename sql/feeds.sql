CREATE TABLE IF NOT EXISTS feeds(
    id          INTEGER PRIMARY KEY,
    url         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    title       TEXT,
    description TEXT,
    etag        TEXT,
    modified    TEXT,
    updated     INTEGER
);