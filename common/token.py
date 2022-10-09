# * coding:utf-8 *

import random
import string
import aioredis
from async_property import async_property

from common.config import get_settings
from common.utils import Singleton

# load_dotenv()
# redis_host = os.getenv("REDIS_HOST")
# redis_port = os.getenv("REDIS_PORT")

redisSettings = {
    "user": "root",
    "password": "",
    "host": "127.0.0.1",
    "port": "26379",
    "db": 1,
}


class Redis(metaclass=Singleton):
    def __init__(self):
        self._session = None

    @async_property
    async def client(self):
        if self._session:
            return self._session
        redisConn = await aioredis.create_pool(
            f"redis://"
            f'{redisSettings.get("user")}:'
            f'{redisSettings.get("password")}@'
            f'{redisSettings.get("host")}:'
            f'{redisSettings.get("port")}/'
            f'{redisSettings.get("db")}',
            encoding="utf-8",
        )
        self._session = aioredis.Redis(pool_or_conn=redisConn)
        return self._session


CHARS = string.ascii_uppercase + string.ascii_lowercase


class Token(object):
    def __init__(self, user_id=None, token=None):
        self._user_id = user_id
        self._token = token
        self._delimiter = "&&"
        self._prefix_length = 12

    @property
    def _prefix(self):
        return "".join([random.choice(CHARS) for _ in range(self._prefix_length)])

    async def get_token(self):
        if self._token:
            return self._token
        client = await Redis().client
        self._token = self._prefix + self._delimiter + self._user_id
        value = "token:" + self._user_id
        await client.set(key=value, value=self._token, expire=60 * 60 * 24)
        return self._token

    async def get_user_id(self):
        if self._user_id:
            return self._user_id
        client = await Redis().client
        skip_len = self._prefix_length + len(self._delimiter)
        user_id = self._token[skip_len:]
        value = await client.get("token:" + user_id)

        if value == self._token:
            await client.expire("token:" + user_id, 60 * 60 * 24)
            self._user_id = user_id
        return self._user_id

    async def clear(self):
        user_id = await self.get_user_id()
        if isinstance(user_id, str):
            client = await Redis().client
            await client.delete("token:" + user_id)
