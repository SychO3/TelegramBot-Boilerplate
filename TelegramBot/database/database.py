from datetime import datetime

from pyrogram.types import User

from TelegramBot.database.MysqlDb import mysql_database as db

from prestool.PresMySql import SqlStr

s = SqlStr()


async def save_user(user: User):
    """
    Save the new user id in the database if it is not already there.
    """

    insert_format = {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    sql = s.insert_sql_str("users", insert_format)
    await db.execute(sql)


async def save_chat(**kwargs):
    """
    Save the new chat id in the database if it is not already there.
    """
    kwargs["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = s.insert_sql_str("chats", kwargs)
    await db.execute(sql)


class Catalogs:
    def __init__(self):
        self.table = "catalogs"

    async def get_catalogs(self):
        sql = s.select_sql_str(self.table)
        return await db.query(sql)

    async def edit_catalog(self, catalog_id: int, catalog_name: str):
        sql = s.update_sql_str(
            self.table, {"catalog_name": catalog_name}, {"catalog_id": catalog_id}
        )
        await db.execute(sql)

    async def add_catalog(self, catalog_name: str):
        insert_format = {
            "catalog_name": catalog_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        sql = s.insert_sql_str(self.table, insert_format)
        await db.execute(sql)

    async def delete_catalog(self, catalog_id: int):
        sql = s.delete_sql_str(self.table, {"catalog_id": catalog_id})
        await db.execute(sql)

    async def get_catalog_name(self, catalog_id: int):
        sql = s.select_sql_str(self.table, ["catalog_name"], {"catalog_id": catalog_id})
        result = await db.query(sql)
        return result[0]["catalog_name"]


class Contacts:
    def __init__(self):
        self.table = "contacts"

    async def get_contacts(self, catalog_id: int):
        sql = s.select_sql_str(self.table, ["*"], {"catalog_id": catalog_id})
        return await db.query(sql)

    async def add_contact(self, catalog_id: int, contact_name: str):
        insert_format = {
            "catalog_id": catalog_id,
            "text": contact_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        sql = s.insert_sql_str(self.table, insert_format)
        await db.execute(sql)

    async def delete_contact(self, contact_id: int):
        sql = s.delete_sql_str(self.table, {"contact_id": contact_id})
        await db.execute(sql)

    async def edit_contact(self, contact_id: int, contact_name: str):
        sql = s.update_sql_str(
            self.table, {"text": contact_name}, {"contact_id": contact_id}
        )
        await db.execute(sql)

    async def del_all_contacts(self, catalog_id: int):
        sql = s.delete_sql_str(self.table, {"catalog_id": catalog_id})
        await db.execute(sql)

    async def get_all_contacts(self):
        sql = s.select_sql_str(self.table)
        return await db.query(sql)


class Guarantees:
    def __init__(self):
        self.table = "guarantees"

    async def get_guarantees(self):
        sql = s.select_sql_str(self.table)
        return await db.query(sql)

    async def get_guarantee(self, guarantee_id: int):
        sql = s.select_sql_str(self.table, ["*"], {"id": guarantee_id})
        result = await db.query(sql)
        return result

    async def add_guarantee(self, guarantee_data: dict[str, str]):
        guarantee_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(guarantee_data)
        sql = s.insert_sql_str(self.table, guarantee_data)
        await db.execute(sql)

    async def edit_guarantee(self, guarantee_id: int, guarantee_data: dict[str, str]):
        sql = s.update_sql_str(self.table, guarantee_data, {"id": guarantee_id})
        await db.execute(sql)

    async def delete_guarantee(self, guarantee_id: int):
        sql = s.delete_sql_str(self.table, {"id": guarantee_id})
        await db.execute(sql)


# async def add_message_log(chat_id: int, message_id: int):
#     insert_format = {
#         "chat_id": chat_id,
#         "message_id": message_id,
#         "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     }
#
#     sql = s.insert_sql_str("message_logs", insert_format)
#     await db.execute(sql)
#
# async def get_message_log(chat_id: int):
#     sql = s.select_sql_str("message_logs", ["message_id"], {"chat_id": chat_id})
#     result = await db.query(sql)
#     return result
#
# async def delete_message_log(chat_id: int):
#     sql = s.delete_sql_str("message_logs", {"chat_id": chat_id})
#     await db.execute(sql)


class MessageLog:
    def __init__(self):
        self.table = "message_logs"

    async def add_message_log(self, chat_id: int, message_id: int):
        insert_format = {
            "chat_id": chat_id,
            "message_id": message_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        sql = s.insert_sql_str(self.table, insert_format)
        await db.execute(sql)

    async def get_message_log(self, chat_id: int):
        sql = s.select_sql_str(self.table, ["message_id"], {"chat_id": chat_id})
        result = await db.query(sql)
        return result

    async def delete_message_log(self, chat_id: int):
        sql = s.delete_sql_str(self.table, {"chat_id": chat_id})
        await db.execute(sql)
