from __future__ import annotations
from datetime import datetime
from time import mktime

import db
import feed
from unique import Unique

from typing import(
    Optional,
    Tuple,
    Union,
)


class Episode(metaclass=Unique):
    def __init__(self, id: int):
        self.id          : int
        self._feed       : int
        self.guid        : str
        self.url         : str
        self.title       : str
        self.description : Optional[str]
        self._published  : datetime
        self._played      : Optional[datetime]

        sql = 'SELECT * FROM episodes WHERE id=?;'

        c = db.connection.cursor()
        c.execute(sql, (id,))
        row = c.fetchone()

        self.id          = row['id']
        self._feed       = row['feedID']
        self.guid        = row['guid']
        self.url         = row['url']
        self.title       = row['title']
        self.description = row['description']
        self.published   = row['published']
        self.played      = row['played']


    @property
    def feed(self):
        return feed.Feed(self._feed)

    @property
    def published(self):
        return self._published

    @published.setter
    def published(self, v: Union[int, datetime]):
        if isinstance(v, int):
            self._published = datetime.fromtimestamp(v)
        else:
            self._published = v

    @property
    def played(self) -> Optional[datetime]:
        return self._played

    @played.setter
    def played(self, v: Optional[Union[int, datetime]]):
        if isinstance(v, int):
            self._played = datetime.fromtimestamp(v)
        else:
            self._played = v


    def __str__(self):
        return self.title


    def setplayed(self):
        self.played = datetime.utcnow()
        sql = 'UPDATE episodes SET played=? WHERE id=?;'
        db.cursor().execute(sql, (self.played.timestamp(), self.id))
        db.connection.commit()


    @staticmethod
    def add(rss, parent) -> Optional[Episode]:
        sql = '''
            INSERT OR IGNORE INTO
            episodes(feedID, guid, url, title, description, published)
            VALUES(?,?,?,?,?,?);
        '''
        values = (
            parent.id,
            rss.id,
            rss.enclosures[0].href,
            rss.title,
            rss.description,
            mktime(rss.published_parsed),
        )
        c = db.connection.cursor()
        c.execute(sql, values)
        if c.rowcount is not 0:
            return Episode(c.lastrowid)
        return None


    @staticmethod
    def getall() -> Tuple:
        """
        Get a tuple of all the episodes from all feeds,
        in ascending order of the date they were published.
        """
        sql = 'SELECT id FROM episodes ORDER BY published ASC;'
        c = db.connection.execute(sql)
        return tuple(Episode(x['id']) for x in c.fetchall())


    @staticmethod
    def getbyfeed(f: feed.Feed) -> Tuple:
        """
        Get a tuple of all the episodes from a given feed,
        in ascending order of the date they were published.
        """
        sql = 'SELECT id FROM episodes WHERE feedID=? ORDER BY published ASC;'
        c = db.connection.execute(sql, (f.id,))
        return tuple(Episode(x['id']) for x in c.fetchall())
