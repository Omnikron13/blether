from __future__ import annotations
from datetime import datetime

import feedparser

import db
from episode import Episode

from typing import Union, Optional, Tuple


class Feed:
    _feeds = dict()

    @property
    def updated(self):
        return self._updated

    @updated.setter
    def updated(self, v: Union[int, datetime, None]):
        if isinstance(v, int):
            self._updated = datetime.fromtimestamp(v)
        else:
            self._updated = v


    def __new__(cls, id):
        if id in cls._feeds.keys():
            return cls._feeds[id]
        f = super(Feed, cls).__new__(cls)
        cls._feeds[id] = f
        return f


    def __init__(self, id):
        # Skip init if already done, which is the case when avoiding duplication
        if hasattr(self, 'id'):
            return

        self.id       : int
        self.url      : str
        self.title    : str
        self.subtitle : Optional[str]
        self.episodes : Tuple

        self._updated : Optional[datetime]
        self._rss     : Optional[feedparser.FeedParserDict]

        sql = 'SELECT * FROM feeds WHERE id=?;'
        c = db.connection.cursor()
        c.execute(sql, (id,))
        row = c.fetchone()
        self.id       = row['id']
        self.url      = row['url']
        self.title    = row['title']
        self.subtitle = row['subtitle']
        self.updated  = row['updated']
        self.episodes = Episode.getbyfeed(self)

        self._rss = None


    def __str__(self):
        return self.title


    @staticmethod
    def add(url: str) -> Feed:
        """
        Add new feed to the db
        :param url: RSS feed url to add
        :return: Feed object
        """
        sql = 'INSERT INTO feeds(url) VALUES(?);'
        c = db.cursor()
        c.execute(sql, (url,))
        f = Feed(c.lastrowid)
        f.update()
        return f


    @classmethod
    def _loadfeeds(cls):
        """Fills _feeds dictionary from db. Intended to be called once on startup."""
        cls._feeds = {f.id:f for f in Feed.getall()}


    @staticmethod
    def getall() -> Tuple[Feed]:
        """
        Get all feeds currently in the db
        :return: All current feeds
        """
        sql = 'SELECT id FROM feeds;'
        c = db.cursor()
        c.execute(sql)
        return tuple(Feed(x['id']) for x in c.fetchall())

    @staticmethod
    def maxtitlelength():
        sql = 'SELECT MAX(LENGTH(title)) FROM feeds;'
        c = db.connection.execute(sql)
        return c.fetchone()[0]


    def update(self):
        """
        Re-download and parse the RSS file, updating local db accordingly.
        """
        self._rss = feedparser.parse(self.url)
        self.title = self._rss.feed.title
        self.subtitle = self._rss.feed.subtitle
        self.updated = datetime.utcnow()

        for entry in self._rss.entries:
            Episode.add(entry, self)
        self.episodes = Episode.getbyfeed(self)

        sql = 'UPDATE feeds SET title=?, subtitle=?, updated=? WHERE id=?;'
        values = (
            self.title,
            self.subtitle,
            self.updated.timestamp(),
            self.id,
        )

        c = db.cursor()
        c.execute(sql, values)

        db.connection.commit()


Feed._loadfeeds()
