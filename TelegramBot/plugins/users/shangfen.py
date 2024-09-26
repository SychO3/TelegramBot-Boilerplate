from pyrogram import Client, filters
from pyrogram.types import Message
import datetime
from TelegramBot.database import database
from TelegramBot.helpers.filters import shangfen_group, sudo_cmd
from pyrogram.helpers import ikb
from TelegramBot import config
from TelegramBot import log

KEFU_BUTTON = ikb(
    [
        [("客服1", "https://t.me/xianxin1", "url")],
        [("客服2", "https://t.me/MLH55N", "url")],
    ]
)

GAME_BOTTON = ikb(
    [
        [("点击进入游戏", "https://t.me/TDGJLD888", "url")],
    ]
)


## 查询
@Client.on_message(shangfen_group & filters.regex("^1$"))
async def shangfen_1(bot: Client, m: Message):
    user_info = await database.get_user_info(m.from_user.id)
    if not user_info:
        await database.save_user(m.from_user)
        user_info = await database.get_user_info(m.from_user.id)

    balance = user_info.get("balance", 0.00)
    agent_reward = user_info.get("agent_reward", 0.00)
    text = f"**用户信息**\n账号：`{m.from_user.id}`\n昵称：`{m.from_user.full_name}`\n"
    text += f"余额：`{balance}`Ks\n佣金：`{agent_reward}`Ks\n\n"
    text += "**流水检测**\n"
    # start_time = 今日00:00:00
    start_time = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # end_time = 当前时间
    end_time = datetime.datetime.now()
    liushui = await database.get_user_flow(
        m.from_user.id,
        start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    text += f"今日流水：`{liushui}`"
    await m.reply_text(text, reply_markup=KEFU_BUTTON)

    log(__name__).info(
        f"用户 {m.from_user.full_name}({m.from_user.id}) 在 上分群 查询了信息"
    )


## 增加游戏余额，格式为：+任意数字
@Client.on_message(shangfen_group & filters.regex("^\\+\\d+") & sudo_cmd)
async def shangfen_add_balance(bot: Client, m: Message):
    r = m.reply_to_message
    if not r:
        return await m.reply_text("请回复一个用户")

    reply_user = r.from_user

    if int(m.text[1:]) < 0:
        return await m.reply_text("请输入一个正数")

    user_info = await database.get_user_info(reply_user.id)
    if not user_info:
        await database.save_user(reply_user)
        user_info = await database.get_user_info(reply_user.id)

    old, new = await database.add_balance(
        reply_user, int(m.text), "balance", m.from_user, reason="管理员上分"
    )

    text = f"〖您的账号〗`{reply_user.id}`\n〖您的昵称〗`{reply_user.full_name}`\n"
    text += (
        f"〖上分成功〗上分`{int(m.text)}`Ks\n〖账户资金〗`{old}+{int(m.text)}={new}Ks`"
    )

    await m.reply_text(text, reply_markup=GAME_BOTTON)

    # 发送消息到游戏群
    text = f"**贵宾{reply_user.full_name}，充值{int(m.text)}Ks，请查收**"
    await bot.send_message(chat_id=config.GAME_GROUP_ID, text=text)

    log(__name__).info(
        f"管理员 {m.from_user.full_name}({m.from_user.id}) 给用户 {reply_user.full_name}({reply_user.id}) 增加 {int(m.text)}Ks"
    )


## 减少代理佣金，格式为：yj任意数字
@Client.on_message(shangfen_group & filters.regex("^yj\\d+") & sudo_cmd)
async def shangfen_add_agent_reward(_, m: Message):
    r = m.reply_to_message
    if not r:
        return await m.reply_text("请回复一个用户")

    reply_user = r.from_user

    if int(m.text[2:]) < 0:
        return await m.reply_text("请输入一个正数")

    user_info = await database.get_user_info(reply_user.id)
    if not user_info:
        await database.save_user(reply_user)
        user_info = await database.get_user_info(reply_user.id)

    if user_info.get("agent_reward") < int(m.text[2:]):
        return await m.reply_text("代理佣金不足")

    old, new = await database.add_balance(
        reply_user, -int(m.text[2:]), "agent_reward", m.from_user, reason="代理佣金扣除"
    )

    text = f"💎**代理** `{reply_user.full_name}`**, 佣金:{int(m.text[2:])} 请查收！**"

    await m.reply_text(text, quote=False, reply_markup=None)

    log(__name__).info(
        f"管理员 {m.from_user.full_name}({m.from_user.id}) 给用户 {reply_user.full_name}({reply_user.id}) 提现 {int(m.text[2:])}Ks 代理佣金"
    )


# 管理员下分操作 格式为： x 数字
@Client.on_message(shangfen_group & filters.regex("^x\\d+") & sudo_cmd)
async def tixian_balance(bot: Client, m: Message):
    r = m.reply_to_message
    if not r:
        return await m.reply_text("请回复一个用户")

    reply_user = r.from_user

    if int(m.text[1:]) < 0:
        return await m.reply_text("请输入一个正数")

    user_info = await database.get_user_info(reply_user.id)
    if not user_info:
        await database.save_user(reply_user)
        user_info = await database.get_user_info(reply_user.id)

    if user_info.get("balance") < int(m.text[1:]):
        return await m.reply_text("余额不足")

    # 今日流水
    start_time = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_time = datetime.datetime.now()
    liushui = await database.get_user_flow(
        reply_user.id,
        start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time.strftime("%Y-%m-%d %H:%M:%S"),
    )

    # 今日充值
    today_chongzhi, today_tixian = await database.get_user_bill_by_time(
        reply_user.id,
        start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    today_chongzhi = sum([i.get("amount") for i in today_chongzhi])

    if liushui < 1 * today_chongzhi:
        return await m.reply_text("今日流水不足，无法提现")

    old, new = await database.add_balance(
        reply_user, -int(m.text[1:]), "balance", m.from_user, reason="管理员下分"
    )

    text = f"〖您的账号〗`{reply_user.id}`\n〖您的昵称〗`{reply_user.full_name}`\n"
    text += f"〖提现成功〗提现`{int(m.text[1:])}`Ks\n〖账户资金〗`{old}-{int(m.text[1:])}={new}Ks`"

    await m.reply_text(text, reply_markup=GAME_BOTTON)

    # 发送消息到游戏群
    text = f"**贵宾{reply_user.full_name}，提现{int(m.text[1:])}Ks成功，请查收**"
    await bot.send_message(chat_id=config.GAME_GROUP_ID, text=text)

    log(__name__).info(
        f"管理员 {m.from_user.full_name}({m.from_user.id}) 给用户 {reply_user.full_name}({reply_user.id}) 提现 {int(m.text[1:])}Ks"
    )
