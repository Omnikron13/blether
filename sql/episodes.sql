CREATE TABLE IF NOT EXISTS episodes(
    id          INTEGER PRIMARY KEY,
    feedID      INTEGER NOT NULL,
    guid        TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    url         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    title       TEXT    NOT NULL,
    description TEXT,
    published   INTEGER NOT NULL,
    FOREIGN KEY (feedID) REFERENCES feeds(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


CREATE INDEX IF NOT EXISTS episodes__feed_index ON episodes (feedID);
