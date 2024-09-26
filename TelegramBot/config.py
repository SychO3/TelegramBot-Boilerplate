from os import getenv

from dotenv import load_dotenv

load_dotenv(".env")

API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")

OWNER_USERID = [int(i) for i in getenv("OWNER_USERID").split(",")]

SUDO_USERID = OWNER_USERID

try:
    SUDO_USERID += [int(i) for i in getenv("SUDO_USERID").split(",")]
except ValueError:
    pass

SUDO_USERID = list(set(SUDO_USERID))

MYSQL_HOST = getenv("MYSQL_HOST")
MYSQL_PORT = int(getenv("MYSQL_PORT"))
MYSQL_USER = getenv("MYSQL_USER")
MYSQL_PASS = getenv("MYSQL_PASS")
MYSQL_NAME = getenv("MYSQL_NAME")


MYSQL_URI = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_NAME}"
)

REDIS_HOST = getenv("REDIS_HOST")
REDIS_PORT = int(getenv("REDIS_PORT"))
REDIS_PASS = getenv("REDIS_PASS")
if REDIS_PASS:
    REDIS_URI = f"redis://:{REDIS_PASS}@{REDIS_HOST}:{REDIS_PORT}"
else:
    REDIS_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}"

SHANGFEN_GROUP_ID = int(getenv("SHANGFEN_GROUP_ID"))
GAME_GROUP_ID = int(getenv("GAME_GROUP_ID"))
