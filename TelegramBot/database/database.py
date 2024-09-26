from datetime import datetime

from pyrogram.types import User

from TelegramBot.database.MysqlDb import mysql_database as db

from prestool.PresMySql import SqlStr

s = SqlStr()


async def save_user(user: User, invite_code: int = None):
    """
    Save the new user id in the database if it is not already there.
    """

    insert_format = {
        "id": user.id,
        "shangji": invite_code,
        "full_name": user.full_name,
        "username": user.username,
        "balance": 0.00,
        "agent_reward": 0.00,
        "status": True,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    sql = s.insert_sql_str("bot_users", insert_format)
    await db.execute(sql)


async def get_all_user():
    """
    获取所有用户
    """
    sql = s.select_sql_str("bot_users", ["*"])
    return await db.query(sql)


async def get_user_info(user_id: int):
    """
    Get the user information from the database.
    """
    where = {"id": user_id}
    sql = s.select_sql_str("bot_users", ["*"], where)
    result = await db.query(sql)
    if result:
        return result[0]
    else:
        return None


async def add_balance(
    user: User,
    amount: float | int,
    type_: str,
    sudo_user: User = None,
    reason: str = None,
):
    """
    Add the balance to the user account.
    """

    user_info = await get_user_info(user.id)
    if not user_info:
        await save_user(user)
        user_info = await get_user_info(user.id)

    old_balance = user_info.get(type_, 0.00)
    new_balance = old_balance + amount

    update_format = {type_: new_balance}
    where = {"id": user.id}
    sql = s.update_sql_str("bot_users", update_format, where)
    await db.execute(sql)

    insert_format = {
        "id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "old": old_balance,
        "amount": amount,
        "new": new_balance,
        "type": type_,
        "reason": reason,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if sudo_user:
        insert_format["sudo_id"] = sudo_user.id
        insert_format["sudo_name"] = sudo_user.full_name
        insert_format["sudo_username"] = sudo_user.username
    sql = s.insert_sql_str("transactions", insert_format)
    await db.execute(sql)
    return int(old_balance), int(new_balance)


# async def save_chat(chat_id: int):
#     """
#     Save the new chat id in the database if it is not already there.
#     """
#
#     insert_format = {"date": datetime.now()}
#     sql = s.insert_sql_str("chats", insert_format)
#     await db.execute(sql)


async def get_last_qihao():
    """
    Get the last qihao from the database games table.
    """
    sql = s.select_sql_str("games", ["qihao"], order={"qihao": "desc"}, limit=1)
    result = await db.query(sql)
    if result:
        return result[0]["qihao"] + 1
    else:
        return 100000


async def save_kj(data: dict, tabel: str):
    """
    Save the new kj data in the database.
    """
    # insert_format = {
    #     "qihao": data["qihao"],
    #     "data": data["data"],
    #     "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    # }
    sql = s.insert_sql_str(tabel, data)
    await db.execute(sql)


async def get_kj():
    """
    Get the last kj data from the database.
    """
    sql = s.select_sql_str("kj", ["*"], order={"qihao": "desc"}, limit=10)
    return await db.query(sql)


# 获取用户投注记录,根据时间
async def get_user_bet_record(user_id: int, start_time: str, end_time: str):
    """
    获取用户的投注记录。
    """
    sql = f"""
    SELECT * FROM games
    WHERE id = {user_id}
    AND created_at BETWEEN '{start_time}' AND '{end_time}'
    """
    return await db.query(sql)


# 获取用户的流水，根据时间段
async def get_user_flow(user_id: int, start_time: str, end_time: str):
    """
    获取用户的流水。
    """
    liushui = 0
    sql = f"""
    SELECT * FROM games
    WHERE id = {user_id}
    AND created_at BETWEEN '{start_time}' AND '{end_time}'
    """
    result = await db.query(sql)
    if result:
        for record in result:
            liushui += record["amount"]
    return liushui


# 获取用户最近50条投注记录
async def get_user_recent_bet_record(user_id: int):
    """
    获取用户的最近50条投注记录。
    """
    sql = f"""
    SELECT * FROM games
    WHERE id = {user_id}
    ORDER BY created_at DESC
    LIMIT 50
    """
    return await db.query(sql)


# 获取用户的直属代理和二级代理
async def get_user_agent(user_id: int):
    """
    获取用户的直属代理和二级代理。
    """
    zhishu = []
    erji = []
    sql = s.select_sql_str("bot_users", ["*"], where={"shangji": user_id})
    zhishu = await db.query(sql)

    # 获取二级代理
    if zhishu:
        for zhishu_user in zhishu:
            sql = s.select_sql_str(
                "bot_users", ["*"], where={"shangji": zhishu_user["id"]}
            )
            result = await db.query(sql)
            if result:
                for erji_user in result:
                    erji.append(erji_user)
    return zhishu, erji


# 获取用户的直属代理和二级代理的流水，根据时间段
async def get_user_agent_flow(user_id: int, start_time: str, end_time: str):
    """
    获取用户的直属代理和二级代理的流水。
    """
    zhishu_flow = 0
    erji_flow = 0

    zhushu_users, erji_users = await get_user_agent(user_id)
    if zhushu_users:
        for zhushu_user in zhushu_users:
            bet_record = await get_user_bet_record(
                zhushu_user["id"], start_time, end_time
            )
            if bet_record:
                for record in bet_record:
                    zhishu_flow += record["amount"]

    if erji_users:
        for erji_user in erji_users:
            bet_record = await get_user_bet_record(
                erji_user["id"], start_time, end_time
            )
            if bet_record:
                for record in bet_record:
                    erji_flow += record["amount"]

    return zhishu_flow, erji_flow, zhishu_flow + erji_flow


# 获取用户的账单记录，充值，提现。根据条数
async def get_user_bill(user_id: int, limit: int):
    """
    获取用户的账单记录，充值，提现。根据条数
    """
    chongzhi = []
    tixian = []
    sql = s.select_sql_str(
        "transactions",
        ["*"],
        where={"id": user_id, "type": "balance", "reason": "管理员上分"},
        order={"created_at": "desc"},
        limit=limit,
    )
    chongzhi = await db.query(sql)
    sql = s.select_sql_str(
        "transactions",
        ["*"],
        where={"id": user_id, "type": "balance", "reason": "管理员下分"},
        order={"created_at": "desc"},
        limit=limit,
    )
    tixian = await db.query(sql)
    return chongzhi, tixian


# 获取用户的账单记录，根据时间
async def get_user_bill_by_time(user_id: int, start_time: str, end_time: str):
    """
    获取用户的账单记录，根据时间
    """
    chongzhi = []
    tixian = []
    sql = f"""
    SELECT * FROM transactions
    WHERE id = {user_id}
    AND type = 'balance'
    AND reason = '管理员上分'
    AND created_at BETWEEN '{start_time}' AND '{end_time}'
    """
    chongzhi = await db.query(sql)
    sql = f"""
    SELECT * FROM transactions
    WHERE id = {user_id}
    AND type = 'balance'
    AND reason = '管理员下分'
    AND created_at BETWEEN '{start_time}' AND '{end_time}'
    """
    tixian = await db.query(sql)
    return chongzhi, tixian


# 获取用户累计提现的代理佣金
async def get_user_agent_reward(user_id: int):
    """
    获取用户累计提现的代理佣金。
    """
    total = 0
    sql = s.select_sql_str(
        "transactions",
        ["amount"],
        where={"id": user_id, "type": "agent_reward", "reason": "代理佣金扣除"},
        order={"created_at": "desc"},
    )
    result = await db.query(sql)
    if result:
        for record in result:
            total += record["amount"]
    return total


# # 获取用户投注记录,根据 时间 和 is_jiesuan
async def get_user_bet_record_by_time_and_is_jiesuan(
    user_id: int, start_time: str, end_time: str, is_jiesuan: bool
):
    """
    获取用户投注记录,根据 时间 和 is_jiesuan
    """
    sql = f"""
    SELECT * FROM games
    WHERE id = {user_id}
    AND created_at BETWEEN '{start_time}' AND '{end_time}'
    AND is_jiesuan = {is_jiesuan}
    """
    return await db.query(sql)


# 根据 no 修改 is_jiesuan
async def update_is_jiesuan(no: int, is_jiesuan: bool):
    """
    根据 no 修改 is_jiesuan
    """
    sql = f"""
    UPDATE games
    SET is_jiesuan = {is_jiesuan}
    WHERE no = {no}
    """

    await db.execute(sql)


# 所有的 is_jiesuan 设置为 False
async def update_all_is_jiesuan():
    """
    所有的 is_jiesuan 设置为 False
    """
    sql = s.select_sql_str("games")
    result = await db.query(sql)
    if result:
        for record in result:
            if record["is_jiesuan"] is None:
                await update_is_jiesuan(record["no"], False)
