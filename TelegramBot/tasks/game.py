import json

from TelegramBot import config
from pyrogram import Client
import datetime
from TelegramBot.logging import log
from pyrogram.helpers import ikb
from TelegramBot.database import database
from pyrogram.types import User


r_key = "FSCBOT:GAME"


# 停止下注的任务
async def stop_bet(bot: Client, redis):
    value = await redis.get(r_key)
    if not value:
        return

    value = json.loads(value)

    end_at = value.get("end_at")
    if not end_at:
        return

    end_at = datetime.datetime.strptime(end_at, "%Y-%m-%d %H:%M:%S")
    now = datetime.datetime.now()

    if now >= end_at and value.get("bet"):
        value["bet"] = False
        await redis.set(r_key, json.dumps(value))

        await bot.delete_messages(config.GAME_GROUP_ID, [value.get("end_notice_id")])

        text = f"**{value.get('qihao')} 期**\n— — — — - 封盘线 - — — — —\n\n"

        for i in value.get("data"):
            text += f"**{i.get("full_name")}**  {i.get("xiazhu")}➜{i.get("amount")} ( {i.get("peilv")} 倍赔率 ) \n"

        text += "\n— 已封盘,线上下注全部有效 —"

        button = ikb(
            [
                [("上下分群", "https://t.me/TDLDSXFQ", "url")],
            ]
        )

        await bot.send_photo(
            config.GAME_GROUP_ID,
            photo="TelegramBot/helpers/assets/tz.png",
            caption=text,
            reply_markup=button,
        )

        log(__name__).info(f"第 {value.get('qihao')} 期停止下注, 等待开奖")
        return


# 计算代理佣金
async def calculate_agent_reward(bot: Client, redis):
    """
    计算代理佣金，时间：每日 59:59:59
    Args:
        bot (Client): _description_
        redis (_type_): _description_
    """
    # 获取所有用户
    users = await database.get_all_user()
    for user in users:
        try:
            user_id = user.get("id")
            start_time = datetime.datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_time = datetime.datetime.now()

            start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
            zhishu_flow = 0
            erji_flow = 0

            zhushu_users, erji_users = await database.get_user_agent(user_id)
            # print(f"用户 {user_id} 的直属代理和二级代理 {zhushu_users} {erji_users}")
            # print("================================================")
            if zhushu_users:
                for zhushu_user in zhushu_users:
                    bet_record = (
                        await database.get_user_bet_record_by_time_and_is_jiesuan(
                            zhushu_user["id"], start_time, end_time, False
                        )
                    )
                    if bet_record:
                        # print(f"获取到直属下级投注记录 {len(bet_record)} 条")
                        for record in bet_record:
                            # 1196223161 的流水减一半
                            zhishu_id = record["id"]
                            if zhishu_id == 1196223161:
                                zhishu_flow += record["amount"] / 2
                            else:
                                zhishu_flow += record["amount"]

                            await database.update_is_jiesuan(record["no"], True)

            if erji_users:
                for erji_user in erji_users:
                    bet_record = (
                        await database.get_user_bet_record_by_time_and_is_jiesuan(
                            erji_user["id"], start_time, end_time, False
                        )
                    )
                    if bet_record:
                        # print(f"获取到二级下级投注记录 {len(bet_record)} 条")
                        for record in bet_record:
                            erji_flow += record["amount"]

                            await database.update_is_jiesuan(record["no"], True)

            total_flow = zhishu_flow + erji_flow

            if total_flow < 0:
                continue

            zhushu_yongjin = zhishu_flow * 0.02
            erji_yongjin = erji_flow * 0.01

            total_yongjin = int(zhushu_yongjin + erji_yongjin)

            if total_yongjin > 0:
                await database.add_balance(
                    User(
                        id=user_id,
                        first_name=user.get("full_name"),
                        username=user.get("username"),
                    ),
                    total_yongjin,
                    "agent_reward",
                    reason="自动结算代理佣金",
                )
                # await bot.send_message(user_id, f"您的代理佣金已结算，请联系客服进行提现")
        except Exception as e:
            log(__name__).error(f"计算代理佣金失败，用户ID：{user_id}, 错误信息：{e}")
            continue

    # log(__name__).info(f"代理佣金计算完成")
