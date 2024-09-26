from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    BotCommandScopeAllPrivateChats,
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand,
)

from TelegramBot.database import database
from TelegramBot.helpers.decorators import ratelimiter
from datetime import datetime
from pyrogram.helpers import ikb
from TelegramBot import log

START_BUTTON = [
    [KeyboardButton("🏧佣金提现"), KeyboardButton("🏠代理中心")],
    [
        KeyboardButton("游戏规则"),
        KeyboardButton("开始游戏"),
        KeyboardButton("我要充值"),
    ],
    [
        KeyboardButton("最近投注"),
        KeyboardButton("账单记录"),
        KeyboardButton("个人中心"),
    ],
]

START_COMMANDS = [
    BotCommand("start", "开始使用"),
    BotCommand("admin", "管理员统计"),
    # BotCommand("balance", "Check your balance"),
]


@Client.on_message(filters.command(["start", "help"]))
@ratelimiter
async def start(bot: Client, message: Message):
    # await database.save_user(message.from_user)
    text = f"您好 {message.from_user.full_name}，欢迎使用机器人！"
    await message.reply_text(
        text, reply_markup=ReplyKeyboardMarkup(START_BUTTON, resize_keyboard=True)
    )
    await bot.set_bot_commands(START_COMMANDS, scope=BotCommandScopeAllPrivateChats())
    # 检查是否带有参数
    param = message.command[1] if len(message.command) > 1 else None
    if param:
        if param.isdigit():
            # 如果邀请码等于自己，则不保存
            if int(param) == message.from_user.id:
                await database.save_user(message.from_user)
                return

            await database.save_user(message.from_user, int(param))
            log(__name__).info(
                f"用户 {int(param)} 邀请了 {message.from_user.full_name}({message.from_user.id})"
            )
        else:  # 其他参数
            await database.save_user(message.from_user)


@Client.on_message(filters.new_chat_members, group=1)
async def new_chat(_, message: Message):
    """
    Get notified when someone add bot in the group, then saves that group chat_id
    in the database.
    """

    chat_id = message.chat.id
    await message.reply_text(
        f"Hello {message.from_user.full_name}, thanks for adding me to this group."
    )
    await message.reply_text(f"Chat ID: `{chat_id}`")


## 游戏规则
@Client.on_message(filters.private & filters.regex("^游戏规则$"))
async def game_rules(_, message: Message):
    text = """**游戏玩法**
- 下注指令
[动物名] [金额]
例如
鸡 5000 或 鸡5k
龟 1万

- 搭线玩法
输入多个不重复的动物+金额
例如
鸡鱼 15k
🐢🐘🐔 1w
支持Emoji表情
❗️注意：金额仅支持阿拉伯数字

- 其他指令
- [1] 查看本期下注
- [2] 查看今日流水
- [3] 查看历史开奖
- [取消/撤回] 取消本期下注
- [查/余额] 查询余额"""
    await message.reply_text(text)


## 个人中心
@Client.on_message(filters.private & filters.regex("^个人中心$"))
async def personal_center(_, message: Message):
    user_info = await database.get_user_info(message.from_user.id)
    balance = user_info.get("balance", 0.00)
    # 开始时间为2024年1月1日00:00:00
    start_time = datetime(2024, 1, 1, 0, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
    # 结束时间为当前时间
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_flow = await database.get_user_flow(
        message.from_user.id, start_time, end_time
    )
    text = f"📇**个人中心**\n\n用户账号：`{message.from_user.id}`\n用户昵称：`{message.from_user.full_name}`\n游戏余额：`{balance}`Ks\n\n"
    text += f"累计流水：{total_flow}"
    await message.reply_text(text)


# 开始游戏
@Client.on_message(filters.private & filters.regex("^开始游戏$"))
async def start_game(_, message: Message):
    text = "加入群组，开始游戏！"
    url = "https://t.me/TDGJLD888"
    await message.reply_text(
        f"[{text}]({url})", quote=False, disable_web_page_preview=True
    )


# 我要充值
@Client.on_message(filters.private & filters.regex("^我要充值$"))
async def recharge(_, message: Message):
    text = "联系客服充值/提现"
    url = "https://t.me/xianxin1"
    await message.reply_text(
        f"[{text}]({url})", quote=False, disable_web_page_preview=True
    )


# 代理中心
@Client.on_message(filters.private & filters.regex("^🏠代理中心$"))
async def agent_center(bot: Client, message: Message):
    xiaji_users, erji_users = await database.get_user_agent(message.from_user.id)

    invite_url = f"https://t.me/{bot.me.username}?start={message.from_user.id}"
    text = "邀请好友前来游戏，轻松日入百万！\n(永久享受直属代理2%总流水抽佣)\n(永久享受二级代理1%总流水抽佣)\n\n"
    text += f"邀请链接：`{invite_url}`\n\n"
    text += f"直属代理已邀请：{len(xiaji_users)}人\n\n"
    text += f"二级代理已邀请：{len(erji_users)}人\n\n"
    leiji_tixian = await database.get_user_agent_reward(message.from_user.id)
    text += f"✅累计提现佣金：{-leiji_tixian}Ks\n\n"
    total = len(xiaji_users) + len(erji_users)
    if total == 0:
        return await message.reply_text(text, quote=False)

    text += "⬇️以下只显示直属代理"
    button = ikb(
        [
            [(f"查看直属代理: {len(xiaji_users)}人", "tuandui_zs")],
            [(f"查看二级代理: {len(erji_users)}人", "tuandui_erji")],
        ]
    )
    await message.reply_text(text, reply_markup=button)


# tuandui 查看团队回调
@Client.on_callback_query(filters.regex(r"^tuandui"))
async def tuandui(_, cq: CallbackQuery):
    xiaji_users, erji_users = await database.get_user_agent(cq.from_user.id)
    cb_data = cq.data.split("_")
    action = cb_data[1]
    if action == "zs":
        users = xiaji_users
        text = f"**直属代理列表：共{len(xiaji_users)}人**\n\n"
    else:
        users = erji_users
        text = f"**二级代理列表：共{len(erji_users)}人**\n\n"

    for user in users:
        if user.get("username"):
            text += f"[{user.get('full_name')}](https://t.me/{user.get('username')})\n"
        else:
            text += f"[{user.get('full_name')}](tg://user?id={user.get('id')})\n"

    await cq.message.reply(text, quote=False, disable_web_page_preview=True)


# 最近投注
@Client.on_message(filters.private & filters.regex("^最近投注$"))
async def recent_bet(_, message: Message):
    data = await database.get_user_recent_bet_record(message.from_user.id)
    if not data:
        await message.reply_text("暂无投注记录", quote=False)
    else:
        text = "**最近50条投注**\n\n"
        for i in data:
            created_at = i.get("created_at").strftime("%m-%d %H:%M")
            text += f"{created_at} {i.get('xiazhu')} 下注 {i.get('amount')}Ks\n"
        await message.reply_text(text, quote=False)


# 账单记录
@Client.on_message(filters.private & filters.regex("^账单记录$"))
async def bill_record(_, message: Message):
    chongzhi, tixian = await database.get_user_bill(message.from_user.id, 20)
    if not chongzhi and not tixian:
        await message.reply_text("暂无账单记录", quote=False)
    else:
        text = "**最近20条账单**\n\n"
        if chongzhi:
            text += "**充值**\n"
            for i in chongzhi:
                created_at = i.get("created_at").strftime("%m-%d %H:%M")
                text += f"{i.get('created_at')} {i.get('amount')}Ks\n"
        if tixian:
            text += "**提现**\n"
            for i in tixian:
                created_at = i.get("created_at").strftime("%m-%d %H:%M")
                text += f"{created_at} {i.get('amount')}Ks\n"
        await message.reply_text(text, quote=False)


# 通过 start 带有参数
# @Client.on_message(filters.private & filters.command("start"),group=100)
# async def start_with_param(_, message: Message):
#     param = message.command[1] if len(message.command) > 1 else None
#     if param:
#         print(param)
#         # param 为邀请码, 整数
#         if param.isdigit():
#             await database.save_user(message.from_user, int(param))
#             print("是数字")
#         else: # 其他参数
#             pass


# 佣金提现
@Client.on_message(filters.private & filters.regex("^🏧佣金提现$"))
async def commission_withdraw(_, message: Message):
    user_info = await database.get_user_info(message.from_user.id)
    if not user_info:
        await database.save_user(message.from_user)
        user_info = await database.get_user_info(message.from_user.id)
    agent_reward = user_info.get("agent_reward", 0.00)
    text = f"**可提现佣金：{agent_reward}Ks**\n\n"
    text += "**点击下方按钮，提交提现申请**  "
    button = ikb(
        [
            [("客服1", "https://t.me/xianxin1", "url")],
            [("客服2", "https://t.me/MLH55N", "url")],
        ]
    )
    await message.reply_text(text, reply_markup=button, quote=False)


# 群ID和用户ID
@Client.on_message(filters.group & filters.regex("^id$"))
async def group_id(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await message.reply_text(f"群ID：`{chat_id}`\n用户ID：`{user_id}`", quote=False)
