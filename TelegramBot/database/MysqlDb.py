from sys import exit as exciter
import aiomysql
import urllib.parse
from pymysql.err import MySQLError
from TelegramBot.config import MYSQL_URI
from TelegramBot.logging import log


class Database:
    def __init__(self, uri):
        self.uri = uri
        self.pool = None
        self._parse_uri()

    def _parse_uri(self):
        # 解析MYSQL_URI
        result = urllib.parse.urlparse(self.uri)
        self.user = result.username
        self.password = result.password
        self.host = result.hostname
        self.port = result.port or 3306  # 如果端口未指定，默认使用3306
        self.db = result.path[1:]  # path的第一个字符是'/'，所以需要去掉

    async def init_pool(self):
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            minsize=5,
            maxsize=100,
            autocommit=True,
            pool_recycle=60,
        )

    async def query(self, sql, *args):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(sql, args)
                result = await cursor.fetchall()
                return result

    async def execute(self, sql, *args):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute(sql, args)
                    await conn.commit()
                except MySQLError as e:
                    if e.args[0] == 1062:  # 忽略重复键错误
                        pass
                    else:
                        await conn.rollback()
                        log(__name__).error(f"MySQL Error: {e}")
                        raise

    async def ensure_pool(self):
        if self.pool is None:
            await self.init_pool()


async def check_mysql_url(mysql_url: str) -> bool:
    try:
        # 解析mysql_url以获取连接参数
        result = urllib.parse.urlparse(mysql_url)
        user = result.username
        password = result.password
        host = result.hostname
        port = result.port or 3306  # 如果端口未指定，默认使用3306
        db = result.path[1:]  # path的第一个字符是'/'，所以需要去掉

        # 创建连接池
        pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
        )

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")

        # 关闭连接池
        pool.close()
        await pool.wait_closed()

        log(__name__).info("Database connection successful!")
        return True

    except Exception as e:
        log(__name__).error(f"MySQL Connection failed: {e}")
        exciter(1)


# 实例化 Database 类
mysql_database = Database(MYSQL_URI)

# asyncio.get_event_loop().run_until_complete(mysql_database.ensure_pool())
