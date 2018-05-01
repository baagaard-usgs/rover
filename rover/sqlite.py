
from time import time
from sqlite3 import connect

from .utils import canonify, uniqueish


class NoResult(Exception):

    def __init__(self, sql, params):
        super().__init__('%s %s' % (sql, params))



class SqliteSupport:
    '''
    Utility class supporting various common database operations.
    '''

    def __init__(self, dbpath, log):
        self._dbpath = canonify(dbpath)
        self._log = log
        self._log.debug('Connecting to sqlite3 %s' % self._dbpath)
        self._db = connect(self._dbpath)
        # https://www.sqlite.org/foreignkeys.html
        self._execute('PRAGMA foreign_keys = ON')
        self._used = False

    def _execute(self, sql, params=tuple()):
        """
        Execute a single command in a transaction.
        """
        c = self._db.cursor()
        self._log.debug('Execute: %s %s' % (sql, params))
        c.execute(sql, params)
        self._db.commit()

    def _fetchsingle(self, sql, params=tuple()):
        """
        Return a single value from a select.

        Raise NoResult if no value.
        """
        c = self._db.cursor();
        self._log.debug('Fetchsingle: %s %s' % (sql, params))
        result = c.execute(sql, params).fetchone()
        if result:
            if len(result) > 1:
                raise Exception('Multiple results for "%s %s"' % (sql, params))
            else:
                return result[0]
        else:
            raise NoResult(sql, params)

    def _fetchone(self, sql, params=tuple()):
        """
        Return a single row from a select.

        Raise NoResult if no row.
        """
        c = self._db.cursor();
        self._log.debug('Fetchone: %s %s' % (sql, params))
        result = c.execute(sql, params).fetchone()
        if result:
            return result
        else:
            raise NoResult(sql, params)

    def _fetchall(self, sql, params=tuple()):
        """
        Return a list of rows from a select.

        Note that it may be better (eg in list-index) to iterate over
        the curosr explicitly.
        """
        c = self._db.cursor();
        self._log.debug('Fetchall: %s %s' % (sql, params))
        return c.execute(sql, params).fetchall()

    def _create_downloaderss_table(self):
        """
        Create the table used by the retriever.  This is here because the
        table may be created by either a retriever or a download manager.
        """
        self._execute('''create table if not exists rover_downloaders (
                           id integer primary key autoincrement,
                           pid integer,
                           table_name text unique,
                           creation_epoch int default (cast(strftime('%s', 'now') as int)),
                           url text unique
                         )''')

    def _clear_dead_retrievers(self):
        for row in self._fetchall('select id, table_name from rover_downloaders where creation_epoch < ?', (time() - 60 * 60,)):
            id, table = row[0]
            self._log.warn('Forcing deletion of table %s' % table)
            self._execute('drop table if exists %s' % table)
            self._execute('delete from rover_downloaders where id = ?', (id,))

    @staticmethod
    def _retrievers_table_name(url, pid):
        return uniqueish('rover_retriever', url)

    def _assert_single_use(self):
        """
        Some classes can only be used once.
        """
        if self._used: raise Exception('Cannot reuse %s' % self.__class__.name)
        self._used = True
