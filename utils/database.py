# +===================================================================================================================+
# ==   CHAUNCEY - A Discord Bot for ArlyDarkfire#4827 (twitch.tv/arlydarkfire)                                       ==
# ==   Created on April 2, 2021 by ShiinaBat                                                                         ==
# +===================================================================================================================+
#
#   database.py is utilizes a singleton pattern to handle all interaction with the database. Created through a
#   combination of solutions found at https://softwareengineering.stackexchange.com/a/362352 and
#   https://stackoverflow.com/a/38078544 with assistance from thegamecracks#1317 from the Discord.py Discord
#   server. Commenting is a little light as I'm not 100% sure on what's happening here yet.
#
#   Copyright 2021 ShiinaBat <shiinabat.code@gmail.com>
#
#   Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby
#   granted, provided that the above copyright notice and this permission notice appear in all copies.
#
#   THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING
#   ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
#   DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
#   PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
#   WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import psycopg2


class Postgres(object):

    def __init__(self):
        self._connection = psycopg2.connect(os.environ.get("DATABASE_URL"))
        self._cursor = self._connection.cursor()
        self.create_tables()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @property
    def connection(self):
        return self._connection

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self._connection.commit()

    async def close(self, commit=True):
        if commit:
            self.commit()
        await self._connection.close()

    def execute(self, sql, params=None):
        self._cursor.execute(sql, params or ())
        self.commit()

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchone(self):
        return self._cursor.fetchone()

    def query(self, sql, params=None):
        self._cursor.execute(sql, params or ())
        return self.fetchall()

    def create_tables(self):
        # create prefix table
        self.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id BIGINT PRIMARY KEY, prefix VARCHAR(3) NOT NULL DEFAULT ';')")