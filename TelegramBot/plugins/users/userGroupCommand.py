import datetime
import json

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, User

from TelegramBot.database import database
from TelegramBot.helpers.filters import game_group
from pyrogram.helpers import ikb
from TelegramBot import redis
import asyncio

r_key = "FSCBOT:GAME"


# balance 当前余额 回调
@Client.on_callback_query(filters.regex(r"^balance"))
async def balance(bot: Client, cq: CallbackQuery):
    user_info = await database.get_user_info(cq.from_user.id)
    if not user_info:
        await database.save_user(cq.from_user)
        user_info = await database.get_user_info(cq.from_user.id)

    balance = user_info.get("balance", 0.00)
    await cq.answer(f"当前余额：{balance}Ks", show_alert=True)


# touzhu 用户当期投注 回调
@Client.on_callback_query(filters.regex(r"^touzhu"))
async def touzhu(bot: Client, cq: CallbackQuery):
    data = await redis.get(r_key)
    if not data:
        pass
    else:
        data = json.loads(data)
        data = data.get("data")
        bet_data = []
        for i in data:
            if i.get("id") == cq.from_user.id:
                bet_data.append(i)
        if not bet_data:
            await cq.answer("您当前没有投注记录", show_alert=True)
        else:
            text = "**投注记录**\n\n"
            for i in bet_data:
                # 动物 赔率 下注金额
                text += f"{i.get('xiazhu')} (赔率 {i.get('peilv')}) 下注 {i.get('amount')}Ks\n"
            await cq.answer(text, show_alert=True)


# liushui 用户今日流水 回调
@Client.on_callback_query(filters.regex(r"^liushui"))
async def liushui(bot: Client, cq: CallbackQuery):
    start_time = datetime.datetime.now().strftime("%Y-%m-%d 00:00:00")
    end_time = datetime.datetime.now().strftime("%Y-%m-%d 23:59:59")
    bet_data = await database.get_user_bet_record(cq.from_user.id, start_time, end_time)
    if not bet_data:
        await cq.answer("今日暂无投注记录", show_alert=True)
    else:
        liushui = 0
        shuying = 0
        for i in bet_data:
            liushui += i.get("amount")
            shuying += i.get("paicai") - i.get("amount")
        text = f"今日流水：{liushui}\n今日收益：{shuying}Ks"
        await cq.answer(text, show_alert=True)


# xinxi 用户信息 回调
@Client.on_callback_query(filters.regex(r"^xinxi"))
async def xinxi(bot: Client, cq: CallbackQuery):
    user_info = await database.get_user_info(cq.from_user.id)
    if not user_info:
        await database.save_user(cq.from_user)
        user_info = await database.get_user_info(cq.from_user.id)

    balance = user_info.get("balance", 0.00)
    text = f"【账号】{cq.from_user.id}\n【昵称】{cq.from_user.full_name}\n【余额】{balance}Ks"
    await cq.answer(text, show_alert=True)


############  这些是玩家群内的操作  ############
# 群内发送 1 显示 当前下注 和 余额
@Client.on_message(game_group & filters.regex(r"^1$"))
async def show_current_bet(bot: Client, message: Message):
    data = await redis.get(r_key)
    if not data:
        return await message.reply_text("游戏未开始")
    else:
        data = json.loads(data)
        qihao = data.get("qihao")
        data = data.get("data")
        bet_data = []
        for i in data:
            if i.get("id") == message.from_user.id:
                bet_data.append(i)
        if not bet_data:
            text = "您当前没有投注记录"
        else:
            text = f"**{qihao}期投注记录**\n\n"
            for i in bet_data:
                text += f"{i.get('xiazhu')} (赔率 {i.get('peilv')}) 下注 {i.get('amount')}Ks\n"

        # 查询当前余额
        user_info = await database.get_user_info(message.from_user.id)
        if not user_info:
            await database.save_user(message.from_user)
            user_info = await database.get_user_info(message.from_user.id)
        balance = user_info.get("balance", 0.00)
        text += f"\n\n【余额】{balance}Ks"

        await message.reply_text(text)


# 群内发送 2 显示 历史开奖 10 期
@Client.on_message(game_group & filters.regex(r"^2$"))
async def show_history_kj(bot: Client, message: Message):
    kj_data = await database.get_kj()
    if not kj_data:
        return await message.reply_text("当前没有开奖记录")
    else:
        text = "**历史开奖**\n\n"
        for i in kj_data:
            text += f"`{i.get('qihao')} ｜ {i.get('result')}`\n"
        await message.reply_text(text)


# 群内发送 3\33\333 显示 今日充值等
@Client.on_message(game_group & filters.regex(r"^3$|^33$|^333$"))
async def show_user_analysis(bot: Client, message: Message):
    analyze_data = await get_user_analyze(message.from_user, message.text)
    await message.reply_text(analyze_data)


async def get_user_analyze(user: User, query: str) -> str:
    analysis_functions = {
        "3": [get_day_analysis(0)],
        "33": [get_day_analysis(0), get_day_analysis(1)],
        "333": [get_day_analysis(0), get_day_analysis(1), get_day_analysis(2)],
    }

    analyses = analysis_functions.get(query, [])
    return "\n".join(await asyncio.gather(*[func(user) for func in analyses]))


def get_day_analysis(days_ago: int):
    async def analyze(user: User) -> str:
        today = datetime.datetime.now()
        target_date = today - datetime.timedelta(days=days_ago)
        start_time = target_date.strftime("%Y-%m-%d 00:00:00")
        end_time = target_date.strftime("%Y-%m-%d 23:59:59")

        bet_data = await database.get_user_bet_record(user.id, start_time, end_time)
        chongzhidata, tixiandata = await database.get_user_bill_by_time(
            user.id, start_time, end_time
        )

        chongzhi = sum(i.get("amount", 0) for i in chongzhidata)
        tixian = sum(i.get("amount", 0) for i in tixiandata)

        liushui = 0
        yingli = 0
        touzhu_count = 0
        for i in bet_data:
            touzhu_count += 1
            yingli += i.get("paicai", 0) - i.get("amount", 0)
            liushui += i.get("amount", 0)

        day_prefix = {0: "今日", 1: "昨日", 2: "前日"}.get(days_ago, f"{days_ago}天前")

        text = f"{day_prefix}充值：{chongzhi}\n"
        text += f"{day_prefix}提现：{tixian}\n"
        text += f"{day_prefix}流水：{liushui}\n"
        text += f"{day_prefix}盈利：{yingli}\n"
        text += f"{day_prefix}投注：{touzhu_count}次\n"

        if days_ago == 0:
            text = f"用户昵称：`{user.full_name}`\n用户账号：`{user.id}`\n\n" + text

        return text

    return analyze


# 群内发送 取消/撤回 取消本期投注
@Client.on_message(game_group & filters.regex(r"^取消$|^撤回$"))
async def cancel_bet(bot: Client, message: Message):
    data = await redis.get(r_key)
    if not data:
        return await message.reply_text("游戏未开始")
    data = json.loads(data)
    betdata = data.get("data", [])

    user_id = message.from_user.id
    cancelled_bets = []
    total_refund = 0

    # 检查是否封盘
    if not data.get("bet"):
        return await message.reply_text("已封盘，无法取消投注")

    # 分离当前用户的投注和其他用户的投注
    new_betdata = []
    for bet in betdata:
        if bet.get("id") == user_id:
            cancelled_bets.append(bet)
            total_refund += bet.get("amount", 0)
        else:
            new_betdata.append(bet)

    if not cancelled_bets:
        return await message.reply_text("您当前没有投注记录")

    # 退还金额
    if total_refund > 0:
        await database.add_balance(
            User(
                id=user_id,
                first_name=message.from_user.full_name,
                username=message.from_user.username,
            ),
            total_refund,
            "balance",
            reason=f"撤单 {data.get('qihao')} 期",
        )

    # 更新 Redis 中的数据
    data["data"] = new_betdata
    await redis.set(r_key, json.dumps(data))

    # 生成取消投注的详细信息
    cancel_details = "\n".join(
        [f"{bet['xiazhu']} {bet['amount']}Ks" for bet in cancelled_bets]
    )

    await message.reply_text(
        f"取消投注成功\n已退还总金额：{total_refund}Ks\n取消的投注：\n{cancel_details}"
    )


# 群内发送 查/余额 查询当前余额
@Client.on_message(game_group & filters.regex(r"^查$|^余额$"))
async def check_balance(bot: Client, message: Message):
    user_info = await database.get_user_info(message.from_user.id)
    if not user_info:
        await database.save_user(message.from_user)
        user_info = await database.get_user_info(message.from_user.id)

    balance = user_info.get("balance", 0.00)
    await message.reply_text(f"当前余额：{balance}Ks")


# 群内发送 充值/提现/上分/下分
@Client.on_message(game_group & filters.regex(r"^充值$|^提现$|^上分$|^下分$"))
async def chongzhi_tixian(bot: Client, message: Message):
    if not message.from_user:
        return
    username = message.from_user.username
    if not username:
        name = message.from_user.full_name
    else:
        name = f"[{message.from_user.full_name}](https://t.me/{username})"

    userid = message.from_user.id

    user_info = await database.get_user_info(userid)
    if not user_info:
        await database.save_user(message.from_user)
        user_info = await database.get_user_info(userid)

    balance = user_info.get("balance", 0.00)

    text = f"😼{name}\n"
    text += f"💎`{userid}`\n"
    text += f"💰账户余额：`{balance}`\n"
    text += "⭐️点击进入→[上下分群](https://t.me/TDLDSXFQ)\n"
    text += "⚠️主动私聊您的都是骗子"

    button = ikb(
        [
            [("客服1", "https://t.me/xianxin1", "url")],
            [("客服2", "https://t.me/MLH55N", "url")],
        ]
    )

    await message.reply_text(text, reply_markup=button, disable_web_page_preview=True)
