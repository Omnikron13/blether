from datetime import datetime
from time import mktime

import db
import feed

from typing import Union, Optional, Tuple


class Episode:
    def __init__(self, id: Union[int, str]):
        self.id          : int
        self.feed        : 'feed.Feed'
        self.guid        : str
        self.url         : str
        self.title       : str
        self.description : Optional[str]
        self.published   : datetime

        if isinstance(id, int):
            sql = 'SELECT * FROM episodes WHERE id=?;'
        else:
            sql = 'SELECT * FROM episodes WHERE guid=?;'

        c = db.connection.cursor()
        c.execute(sql, (id,))
        row = c.fetchone()

        self.id          = row['id']
        #self.feed        = feed.Feed(row['feedID']) # TODO: make sure this doesn't blow shit up
        self.guid        = row['guid']
        self.url         = row['url']
        self.title       = row['title']
        self.description = row['description']
        self.published   = datetime.fromtimestamp(row['published'])


    def __str__(self):
        return self.title


    @staticmethod
    def add(rss, parent) -> Optional['Episode']:
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
    def getbyfeed(f: 'feed.Feed') -> Tuple:
        """
        Get a tuple of all the episodes from a given feed,
        in ascending order of the date they were published.
        """
        sql = 'SELECT id FROM episodes WHERE feedID=? ORDER BY published ASC;'
        c = db.connection.execute(sql, (f.id,))
        return tuple(Episode(x['id']) for x in c.fetchall())
