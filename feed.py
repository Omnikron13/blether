from __future__ import annotations
from datetime import datetime

import feedparser

import db
from episode import Episode
from unique import Unique

from typing import(
    Union,
    Optional,
    Tuple,
)


class Feed(metaclass=Unique):
    def __init__(self, id):
        self.id          : int
        self.url         : str
        self.title       : str
        self.description : Optional[str]
        self.etag        : str
        self.modified    : str

        self._updated : Optional[datetime]
        self._rss     : Optional[feedparser.FeedParserDict]

        sql = 'SELECT * FROM feeds WHERE id=?;'
        c = db.connection.cursor()
        c.execute(sql, (id,))
        row = c.fetchone()
        self.id          = row['id']
        self.url         = row['url']
        self.title       = row['title']
        self.description = row['description']
        self.etag        = row['etag']
        self.updated     = row['updated']
        self.modified    = row['modified']

        self._rss = None


    @property
    def updated(self):
        return self._updated

    @updated.setter
    def updated(self, v: Union[int, datetime, None]):
        if isinstance(v, int):
            self._updated = datetime.fromtimestamp(v)
        else:
            self._updated = v

    @property
    def episodes(self):
        return Episode.getbyfeed(self)


    def __str__(self):
        return self.title


    @staticmethod
    def add(url: str) -> Feed:
        """
        Add new feed to the db
        :param url: RSS feed url to add
        :return: Feed object
        """

        # First we ensure we're not duplicating anything, checking the db
        # first rather than wasting bandwidth
        sql = 'SELECT COUNT(*) FROM feeds WHERE url=?;'
        count = db.connection.execute(sql, (url,)).fetchone()[0]
        if count:
            raise Feed.Error('URL already in feed table in db')

        rss = feedparser.parse(url)

        # This will throw if the rss is malformed, but also if the url is junk
        # or the url doesn't point to an rss feed, etc.
        # TODO: throw more fine-grained exceptions, or at least different descriptions
        if rss.bozo:
            raise Feed.Error(
                'There was an error parsing the given feed, and it could not be added'
            ) from rss.bozo_exception

        etag = rss.etag if hasattr(rss, 'etag') else None
        modified = rss.modified if hasattr(rss, 'modified') else None

        sql = 'INSERT INTO feeds(url, title, description, etag, modified) VALUES(?,?,?,?,?);'
        c = db.cursor()
        c.execute(sql, (url, rss.feed.title, rss.feed.description, etag, modified))
        f = Feed(c.lastrowid)
        f._rss = rss
        f._update_episodes()
        db.connection.commit()
        return f


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
        self._rss = feedparser.parse(self.url, etag=self.etag, modified=self.modified)

        # HTTP 304 - Not Modified
        if self._rss.status is 304:
            self.updated = datetime.utcnow()
            sql = 'UPDATE feeds SET updated=? WHERE id=?;'
            db.connection.execute(sql, (self.updated.timestamp(), self.id))
            return

        # This will throw if the rss is malformed, but also if the url is junk
        # or the url doesn't point to an rss feed, etc.
        # TODO: raise Feed custom exception instead
        if self._rss.bozo:
            raise self._rss.bozo_exception

        self.title = self._rss.feed.title
        self.description = self._rss.feed.description
        self.etag = self._rss.etag if hasattr(self._rss, 'etag') else None
        self.modified = self._rss.modified
        self.updated = datetime.utcnow()

        self._update_episodes()

        sql = 'UPDATE feeds SET title=?, description=?, etag=?, modified=?, updated=? WHERE id=?;'
        values = (
            self.title,
            self.description,
            self.etag,
            self.modified,
            self.updated.timestamp(),
            self.id,
        )

        c = db.cursor()
        c.execute(sql, values)

        db.connection.commit()


    def _update_episodes(self):
        for entry in self._rss.entries:
            Episode.add(entry, self)


    class Error(Exception):
        pass
