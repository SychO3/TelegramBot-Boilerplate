import datetime
import hashlib
import json

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, User, ChatPermissions

from TelegramBot.config import SUDO_USERID
from TelegramBot.database import database
from TelegramBot.helpers.filters import sudo_cmd, game_group
from pyrogram.helpers import ikb
from TelegramBot import redis
import re
from itertools import combinations
import asyncio
from pyrogram.errors import MessageNotModified
from TelegramBot import config
from TelegramBot.logging import log
from pyrogram import enums

from PIL import Image
import io
import aiofiles

BET_CACHE_EXPIRY = 2  # 缓存过期时间，单位为秒
r_key = "FSCBOT:GAME"
ANIMAL_MAP = {
    "虎": "hu",
    "龟": "gui",
    "鸡": "ji",
    "鱼": "yu",
    "象": "xiang",
    "虾": "xia",
}


async def create_combined_image(animals):
    images = []
    for animal in animals:
        img_name = ANIMAL_MAP.get(animal, animal)
        img_path = f"TelegramBot/helpers/assets/{img_name}200.png"
        async with aiofiles.open(img_path, mode="rb") as f:
            img_data = await f.read()
            img = Image.open(io.BytesIO(img_data))
            # 确保所有图像都是RGBA模式
            img = img.convert("RGBA")
            images.append(img)

    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)

    combined_image = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))

    x_offset = 0
    for img in images:
        try:
            # 尝试使用透明度通道粘贴
            combined_image.paste(img, (x_offset, 0), img)
        except ValueError:
            # 如果失败，则不使用透明度通道粘贴
            combined_image.paste(img, (x_offset, 0))
        x_offset += img.width

    img_byte_arr = io.BytesIO()
    combined_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr


async def create_triple_kuo_image():
    # 异步打开原始的"阔"图片
    async with aiofiles.open("TelegramBot/helpers/assets/kuo.png", mode="rb") as f:
        img_data = await f.read()
        original = Image.open(io.BytesIO(img_data))

    # 创建一个新的宽图片
    width, height = original.width * 3, original.height
    new_image = Image.new("RGBA", (width, height))

    # 粘贴三次原始图片
    for i in range(3):
        new_image.paste(original, (i * original.width, 0))

    # 将图片转换为字节流
    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return img_byte_arr


# 开群 之后就开始游戏
@Client.on_message(game_group & sudo_cmd & filters.regex("^开群$"))
async def game_start(bot: Client, m: Message):
    qihao = await database.get_last_qihao()
    # print(qihao)

    # 这儿要设置一个状态，开群之后可以进行下注
    value = {
        "start_at": m.date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_at": None,
        "end_notice_id": None,
        "bet": True,
        "qihao": qihao,
        "data": [],
    }

    await redis.set(r_key, json.dumps(value))

    text = "游戏已经开始，可以开始下注了"
    button = ikb(
        [
            [("✅点击进入上下分群", "https://t.me/TDLDSXFQ", "url")],
            [("✅点击联系客服1", "https://t.me/xianxin1", "url")],
            [("✅点击联系客服2", "https://t.me/MLH55N", "url")],
        ]
    )

    await m.reply_text(text, reply_markup=button, quote=False)

    # 开群之后，给管理员发送操作面板
    a_text = await a_text_(value)

    a_button = await a_button_(qihao)

    for sudo in SUDO_USERID:
        try:
            await bot.send_message(sudo, a_text, reply_markup=a_button)
        except Exception as e:
            log(__name__).error(f"发送管理员操作面板失败：{e}")
        await asyncio.sleep(1)

    try:
        await bot.set_chat_permissions(
            config.GAME_GROUP_ID, permissions=ChatPermissions(all_perms=True)
        )
    except Exception as e:
        log(__name__).error(f"设置群组权限失败：{e}")


# 关群
@Client.on_message(game_group & sudo_cmd & filters.regex("^关群$"))
async def game_end(bot: Client, m: Message):
    await redis.delete(r_key)
    #     text = """结束了
    # 结束了
    # ㊗️老板盈利多多💰，天天开心🔥
    # 老岛直播时间🇲🇲为：
    # 🌍下午12：00～6：00
    # 🌍晚上8：00～12：00"""
    text = "游戏已结束，㊗️老板盈利多多💰，天天开心🔥"
    button = ikb(
        [
            [("✅点击进入上下分群", "https://t.me/TDLDSXFQ", "url")],
            [("✅点击联系客服1", "https://t.me/xianxin1", "url")],
            [("✅点击联系客服2", "https://t.me/MLH55N", "url")],
        ]
    )
    await m.reply_text(text, reply_markup=button, quote=False)

    # 群组设置为禁言
    try:
        await bot.set_chat_permissions(
            config.GAME_GROUP_ID, permissions=ChatPermissions(all_perms=False)
        )
    except Exception as e:
        log(__name__).error(f"设置群组权限失败：{e}")


async def a_text_(game_data):
    # 总下注金额
    total_bet_amount = sum(g.get("amount") for g in game_data.get("data", []))
    # 总下注人数
    total_bet_user_count = len(set(g.get("id") for g in game_data.get("data", [])))
    qihao = game_data.get("qihao")
    text = f"第 **{qihao}** 期管理面板\n\n"
    bet = "🟢" if game_data.get("bet") else "🔴"
    text += f"下注状态：{bet}\n"
    text += f"总下注金额：**{total_bet_amount}**Ks\n"
    text += f"总下注人数：**{total_bet_user_count}**人\n"
    text += f"开始时间：{game_data.get('start_at')}\n"
    end_at = game_data.get("end_at")
    if end_at:
        text += f"结束时间：{end_at}\n"
    text += "\n=============================\n"
    return text


async def a_button_(qihao):
    a_button = ikb(
        [
            [("🔄刷新", f"admin_refresh_{qihao}", "callback_data")],
            [
                ("🔴下注结束", f"admin_end_{qihao}", "callback_data"),
                ("🔴进行开奖", f"admin_kj_{qihao}", "callback_data"),
            ],
            [("🔴撤销所有下注", f"admin_revoke_{qihao}", "callback_data")],
        ]
    )
    return a_button


def two_char_combinations(s):
    comb = combinations(s, 2)
    return ["".join(pair) for pair in comb]


def is_same_chars(str1: str, str2: str) -> bool:
    """
    判断两个字符串是否包含相同的字符，不考虑顺序。
    可以处理任意长度的字符串，包括单个字符。

    :param str1: 第一个字符串
    :param str2: 第二个字符串
    :return: 如果两个字符串包含相同的字符（不考虑顺序），返回 True；否则返回 False
    """
    # 将字符串转换为集合，并比较它们是否相等
    return set(str1) == set(str2)


def merge_similar_keys(original_dict: dict) -> dict:
    """
    合并字典中包含相同字符（不考虑顺序）的键的值。

    :param original_dict: 原始字典
    :return: 合并后的新字典
    """
    merged_dict = {}
    processed_keys = set()

    for key1, value1 in original_dict.items():
        if key1 in processed_keys:
            continue

        merged_value = value1
        for key2, value2 in original_dict.items():
            if key1 != key2 and is_same_chars(key1, key2):
                merged_value += value2
                processed_keys.add(key2)

        merged_dict[key1] = merged_value
        processed_keys.add(key1)

    return merged_dict


async def process_bet(m: Message, amount: int, xiazhu: str):
    # 生成唯一的下注标识
    bet_id = hashlib.md5(
        f"{m.from_user.id}:{xiazhu}:{amount}:{m.date.timestamp()}".encode()
    ).hexdigest()

    # 检查是否是重复下注
    cache_key = f"FSCBOT:BET_CACHE:{m.from_user.id}"
    cached_bets = await redis.get(cache_key)

    if cached_bets:
        cached_bets = json.loads(cached_bets)
        if bet_id in cached_bets:
            return await m.reply_text("检测到重复下注，已自动忽略")
    else:
        cached_bets = []

    # 将新的下注添加到缓存
    cached_bets.append(bet_id)
    await redis.set(cache_key, json.dumps(cached_bets), ex=BET_CACHE_EXPIRY)

    game_data = await redis.get(r_key)
    if not game_data:
        return await m.reply_text("游戏还未开始，请稍后再试")

    game_data = json.loads(game_data)
    if not game_data.get("bet"):
        return await m.reply_text(f"第 **{game_data.get('qihao')}** 期封盘中，下注无效")

    user_info = await database.get_user_info(m.from_user.id)
    if not user_info:
        await database.save_user(m.from_user)
        user_info = await database.get_user_info(m.from_user.id)

    xiazhus = two_char_combinations(xiazhu) if len(xiazhu) > 2 else [xiazhu]
    total_xiazhu_amount = amount * len(xiazhus)

    if total_xiazhu_amount > user_info.get("balance", 0.00):
        return await m.reply_text("余额不足，请充值后再试")

    if amount < 1000:
        return await m.reply_text("单笔最低下注 **1000Ks**")

    # redis 中下注的类型 和 对应的总金额 下注之前的
    j = {}
    for i in game_data.get("data"):
        if i.get("id") == m.from_user.id:
            if j.get(i.get("xiazhu")):
                j[i.get("xiazhu")] += amount
            else:
                j[i.get("xiazhu")] = amount

    merged_bets = merge_similar_keys(j)
    # print(merged_bets)
    for bet, tamount in merged_bets.items():
        for xiazhu in xiazhus:
            if is_same_chars(bet, xiazhu):
                if len(xiazhu) == 2:  # 两个动物玩法,下注不超过500000，最少为1000
                    if amount + tamount > 500000:
                        return await m.reply_text("单笔最高下注 **500000Ks**")

                else:  # 单个动物玩法，下注不超过1000000，最少为1000
                    if amount + tamount > 1000000:
                        return await m.reply_text("单笔最高下注 **1000000Ks**")

    text = f"第{game_data.get('qihao')}期\n\n✅成功\n"
    b = 0

    for xiazhu in xiazhus:
        peilv = "6" if len(xiazhu) == 2 else "2,3,4"
        text += f"{xiazhu} -{amount}（赔率 {peilv} 倍）\n"

        g = {
            "qihao": game_data.get("qihao"),
            "id": m.from_user.id,
            "full_name": m.from_user.full_name,
            "username": m.from_user.username,
            "xiazhu": xiazhu,
            "amount": amount,
            "peilv": peilv,
            "status": False,
            "is_jiesuan": False,
            "created_at": m.date.strftime("%Y-%m-%d %H:%M:%S"),
        }

        game_data.setdefault("data", []).append(g)
        await redis.set(r_key, json.dumps(game_data))

        _, b = await database.add_balance(
            m.from_user, -amount, "balance", reason=f"下注 {xiazhu} {amount}"
        )
        log(__name__).info(
            f"用户：期号{game_data.get('qihao')} 用户：{m.from_user.id} {m.from_user.full_name} 下注：{xiazhu} {amount}"
        )

    text += f"\n💰余额: `{b}`Ks"
    await m.reply_text(text, quote=True)


EMOJI_TO_ANIMAL = {
    "🐯": "虎",
    "🐢": "龟",
    "🐔": "鸡",
    "🐟": "鱼",
    "🐘": "象",
    "🦐": "虾",
    "虎": "老虎",
    "🐓": "鸡",
}

ANIMAL_PATTERN = (
    f"({'|'.join(list(EMOJI_TO_ANIMAL.keys()) + list(EMOJI_TO_ANIMAL.values()))})"
)


@Client.on_message(game_group & filters.regex(rf"^{ANIMAL_PATTERN}"))
async def game_bet(_, m: Message):
    # 下注格式 单行 或者 多行
    bet_text = m.text.split("\n")
    for bet in bet_text:
        try:
            amount = re.search(r"\d+", bet).group()
            amount = int(amount)

            # 老虎 替换 为 虎

            xiazhu = re.findall(ANIMAL_PATTERN, bet)
            xiazhu = [
                EMOJI_TO_ANIMAL.get(animal, animal) for animal in xiazhu
            ]  # 将emoji转换为汉字

            # bet = bet.replace("🐓", "鸡")
            # bet = bet.replace("老虎", "虎")
            # xiazhu = [animal.replace("🐓", "鸡") for animal in xiazhu]
            xiazhu = [animal.replace("老虎", "虎") for animal in xiazhu]

            xiazhu = "".join(dict.fromkeys(xiazhu))  # 去重

            if bet[-1] in ["w", "W", "万"]:
                amount = amount * 10000

            if bet[-1] in ["k", "K", "千", "Q", "q"]:
                amount = amount * 1000

        except Exception as e:
            log(__name__).error(f"下注失败：{e}")
            continue

        if not amount or not xiazhu:
            continue

        await process_bet(m, amount, xiazhu)


@Client.on_callback_query(filters.regex(r"^admin_"))
async def admin_manage(bot: Client, cq: CallbackQuery):
    cbdata = cq.data.split("_")
    action = cbdata[1]
    qihao = cbdata[2]

    game_data = await redis.get(r_key)
    if not game_data:
        await cq.answer("游戏还未开始，请在游戏群内发送 开群 开始游戏", show_alert=True)
        return await cq.message.delete()

    game_data = json.loads(game_data)

    # 判断点击的期号是否与redis中一致
    if int(qihao) != game_data.get("qihao"):
        await cq.message.delete()
        return await cq.answer("期号不一致！", show_alert=True)

    if action == "refresh":
        text = await a_text_(game_data)

        try:
            await cq.edit_message_text(text, reply_markup=await a_button_(qihao))
        except MessageNotModified:
            await cq.answer("刷新成功")

    if action == "end":
        if game_data.get("end_at"):
            return await cq.answer(
                f"将在 {game_data.get('end_at')} 结束下注。", show_alert=True
            )

        if not game_data.get("data"):
            return await cq.answer("没有下注记录，无法结束！", show_alert=True)

        game_data["bet"] = True

        # 下注结束时间是当前的时间加上 20 秒
        game_data["end_at"] = (
            datetime.datetime.now() + datetime.timedelta(seconds=20)
        ).strftime("%Y-%m-%d %H:%M:%S")

        mes = await bot.send_animation(
            config.GAME_GROUP_ID, "TelegramBot/helpers/assets/zuihou.gif"
        )
        game_data["end_notice_id"] = mes.id

        await redis.set(r_key, json.dumps(game_data))
        await cq.answer(f"下注结束时间：{game_data.get('end_at')}\n", show_alert=True)

    if action == "revoke":
        if not game_data.get("data"):
            return await cq.answer("没有下注记录，无法撤销！", show_alert=True)

        for g in game_data.get("data"):
            if not g.get("status"):
                to_user = User(
                    id=g.get("id"),
                    first_name=g.get("full_name"),
                    username=g.get("username"),
                )
                await database.add_balance(
                    to_user,
                    g.get("amount"),
                    "balance",
                    reason=f"撤销下注 {g.get('xiazhu')} {g.get('amount')}",
                    sudo_user=cq.from_user,
                )

        game_data["data"] = []
        game_data["bet"] = True
        game_data["end_at"] = None

        await redis.set(r_key, json.dumps(game_data))
        await cq.answer("撤销成功！", show_alert=True)

        log(__name__).info(
            f"管理员 {cq.from_user.id} {cq.from_user.full_name} 撤销了第 {game_data.get('qihao')} 期的所有下注"
        )

    if action == "kj":
        if not game_data.get("end_at"):
            return await cq.answer("请先结束下注", show_alert=True)

        if game_data.get("bet"):
            return await cq.answer(
                f"请在 {game_data.get('end_at')} 后再进行开奖", show_alert=True
            )

        if not game_data.get("data"):
            return await cq.answer("没有下注记录，无法开奖！", show_alert=True)

        # 开奖逻辑
        await cq.edit_message_text(
            text=await a_text_(game_data),
            reply_markup=await kj_button(qihao=qihao, r={}),
        )

        kj_key = f"FSCBOT:GAME:KJ:{qihao}"

        data = {"1": None, "2": None, "3": None}

        await redis.set(kj_key, json.dumps(data))


# 虎|龟|鸡|鱼|象|虾
# kj_button = ikb([
#     [("位置一👉", "kj"), ("虎")
# ])


async def kj_button(qihao, r):
    def create_button(label, key, result):
        return f"{label}★" if r.get(
            key
        ) == result else label, f"kj_{result}_{key}_{qihao}"

    kj_buttons = ikb(
        [
            # [
            #     ("-------------------请在下方选择开奖结果----------------------", f"kj_tip1_{qihao}"),
            # ],
            [
                ("①", f"kj_tip_{qihao}"),
                create_button("虎", "1", "hu"),
                create_button("龟", "1", "gui"),
                create_button("鸡", "1", "ji"),
                create_button("鱼", "1", "yu"),
                create_button("象", "1", "xiang"),
                create_button("虾", "1", "xia"),
            ],
            [
                ("②", f"kj_tip_{qihao}"),
                create_button("虎", "2", "hu"),
                create_button("龟", "2", "gui"),
                create_button("鸡", "2", "ji"),
                create_button("鱼", "2", "yu"),
                create_button("象", "2", "xiang"),
                create_button("虾", "2", "xia"),
            ],
            [
                ("③", f"kj_tip_{qihao}"),
                create_button("虎", "3", "hu"),
                create_button("龟", "3", "gui"),
                create_button("鸡", "3", "ji"),
                create_button("鱼", "3", "yu"),
                create_button("象", "3", "xiang"),
                create_button("虾", "3", "xia"),
            ],
            [
                ("正常开奖", f"kj_zc_{qihao}"),
            ],
            [
                ("开奖为'阔'", f"kj_kw_{qihao}"),
            ],
            [
                ("返回", f"kj_back_{qihao}"),
            ],
        ]
    )
    return kj_buttons


jk_map = {
    "hu": "虎",
    "gui": "龟",
    "ji": "鸡",
    "yu": "鱼",
    "xiang": "象",
    "xia": "虾",
}


@Client.on_callback_query(filters.regex(r"^kj"))
async def kj_manage(bot: Client, cq: CallbackQuery):
    cbdata = cq.data.split("_")
    action = cbdata[1]
    qihao = cbdata[-1]
    kj_key = f"FSCBOT:GAME:KJ:{qihao}"
    r_data = await redis.get(kj_key)
    # 判断点击的期号是否与redis中一致
    redis_data = await redis.get(r_key)
    if not redis_data:
        await cq.message.delete()
        return await cq.answer(
            "游戏还未开始，请在游戏群内发送 开群 开始游戏", show_alert=True
        )
    redis_data = json.loads(redis_data)

    if int(qihao) != redis_data.get("qihao"):
        await cq.message.delete()
        return await cq.answer("期号不一致！", show_alert=True)

    if action == "back":
        await redis.delete(kj_key)
        return await cq.edit_message_reply_markup(await a_button_(qihao=qihao))
    elif action == "tip":
        return await cq.answer("请点击右方按钮选择开奖结果", show_alert=True)
    elif action == "zc":
        data = json.loads(r_data)
        if None in data.values():
            return await cq.answer("开奖结果不完整！", show_alert=True)

        ############ 开奖吧 ############
        # 先保存结果到数据库
        for k, v in data.items():
            data[k] = jk_map.get(v)

        kkk = ", ".join(data.values())
        dangekaijiang = "".join(data.values())

        kj_data = {
            "qihao": qihao,
            "result": ", ".join(data.values()),
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        await database.save_kj(kj_data, "kj")
        await redis.delete(kj_key)

        game_data = await redis.get(r_key)
        game_data = json.loads(game_data)

        # 发送开奖结果到群里
        text = f"🎉`{game_data.get("qihao")}`期数\n"
        text += f"✅开奖结果：{kkk}\n\n—————————————————"
        button = ikb(
            [
                [("当前余额", "balance"), ("当期投注", "touzhu")],
                [
                    ("游戏规则", f"https://t.me/{bot.me.username}", "url"),
                    ("上下分群", "https://t.me/TDLDSXFQ", "url"),
                ],
            ]
        )

        animals = kkk.split(", ")
        combined_image = await create_combined_image(animals)

        await bot.send_photo(
            config.GAME_GROUP_ID,
            photo=combined_image,
            caption=text,
            reply_markup=button,
        )

        # await bot.send_message(config.GAME_GROUP_ID,text,reply_markup=button)

        # 获取所有下注记录

        kjdata = "".join(data.values())

        text = f"🎉`{game_data.get("qihao")}`期数\n"
        text += f"✅开奖结果：{kkk}\n\n"
        button = ikb(
            [
                # [
                #     ("当前余额","balance"),("当期投注","touzhu")
                # ],
                [
                    ("出金", "https://t.me/MLH55N", "url"),
                    ("入金", "https://t.me/xianxin1", "url"),
                ]
                # [("✅点击联系客服1", "https://t.me/xianxin1", "url")],
                # [("✅点击联系客服2", "https://t.me/MLH55N", "url")],
            ]
        )

        kjdata = "".join(dict.fromkeys(kjdata))
        kjdata = two_char_combinations(kjdata)  # 开奖结果两个的

        for g in game_data.get("data"):
            xiazhu = g.get("xiazhu")
            amount = g.get("amount")
            peilv = g.get("peilv")
            if len(xiazhu) == 2:
                # kjdata = "".join(data.values())

                def contains_elements(input_string, elements):
                    for element in elements:
                        if set(element) == set(input_string):
                            return True
                    return False

                if contains_elements(xiazhu, kjdata):
                    pc = amount * int(peilv)
                    a, b = await database.add_balance(
                        User(
                            id=g.get("id"),
                            first_name=g.get("full_name"),
                            username=g.get("username"),
                        ),
                        pc,
                        "balance",
                        reason=f"中奖 {xiazhu} {amount}",
                    )

                    g["paicai"] = pc
                    g["yingli"] = 0
                    g["draw_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    g["status"] = True
                    g["is_jiesuan"] = False

                    await database.save_kj(g, "games")

                    log(__name__).info(
                        f"用户：{g.get('id')} {g.get('full_name')} 下注 {xiazhu} {amount} ，赔率 {peilv} 倍，开奖结果 {kjdata} ，派彩 {pc}。"
                    )

                    text += f"{g.get("full_name")} {xiazhu}➜赢 {pc}Ks({amount}×6倍)\n"

                else:
                    g["paicai"] = 0
                    g["yingli"] = amount
                    g["draw_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    g["status"] = True
                    g["is_jiesuan"] = False

                    await database.save_kj(g, "games")

                    log(__name__).info(
                        f"用户：{g.get('id')} {g.get('full_name')} 下注 {xiazhu} {amount}，赔率 {peilv} 倍，开奖结果 {kjdata} ，派彩 0。"
                    )

            else:  # 下注为单个动物
                # print(f"正确的开奖结果：{dangekaijiang}")
                # print(f"下注为单个动物：{xiazhu}")
                # print(f"开奖结果中包含的下注动物：{dangekaijiang.count(xiazhu)}")
                # print(f"下注金额：{amount}")
                # print(f"赔率：{peilv}")
                # print(f"------------------------------")
                count_ = dangekaijiang.count(xiazhu)
                if count_:
                    if count_ == 1:
                        peilv = 2
                    elif count_ == 2:
                        peilv = 3
                    elif count_ == 3:
                        peilv = 4
                    pc = amount * int(peilv)
                    a, b = await database.add_balance(
                        User(
                            id=g.get("id"),
                            first_name=g.get("full_name"),
                            username=g.get("username"),
                        ),
                        pc,
                        "balance",
                        reason=f"中奖 {xiazhu} {amount}",
                    )

                    g["paicai"] = pc
                    g["yingli"] = 0
                    g["draw_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    g["status"] = True
                    g["is_jiesuan"] = False

                    await database.save_kj(g, "games")

                    log(__name__).info(
                        f"用户：{g.get('id')} {g.get('full_name')} 下注 {xiazhu} {amount} ，赔率 {peilv} 倍，开奖结果 {dangekaijiang} ，派彩 {pc}。"
                    )

                    text += (
                        f"{g.get("full_name")} {xiazhu}➜赢 {pc}Ks({amount}×{peilv}倍)\n"
                    )

                else:
                    g["paicai"] = 0
                    g["yingli"] = amount
                    g["draw_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    g["status"] = True
                    g["is_jiesuan"] = False

                    await database.save_kj(g, "games")

                    log(__name__).info(
                        f"用户：{g.get('id')} {g.get('full_name')} 下注 {xiazhu} {amount} ，赔率 {peilv} 倍，开奖结果 {dangekaijiang} ，派彩 0。"
                    )

            # # 用户当前总余额，只在中奖时显示一次。多次中奖的话，显示在最后面，并且只有一次。
            # user_balance_shown = set()
            # user_balance_text = {}

            # if pc > 0 and g.get("id") not in user_balance_shown:
            #     #user_balance = await database.get_user_balance(g.get("id"))
            #     user_info = await database.get_user_info(g.get("id"))
            #     user_balance = user_info.get("balance", 0.00)
            #     user_balance_text[g.get("id")] = f"总余额: {user_balance}Ks"
            #     user_balance_shown.add(g.get("id"))

            # # 在循环结束后添加余额信息到text
            # for balance_text in user_balance_text.values():
            #     text += balance_text

        # 发送开奖结果到群里
        # await bot.send_message(config.GAME_GROUP_ID,text,reply_markup=button)
        await bot.send_photo(
            config.GAME_GROUP_ID,
            photo="TelegramBot/helpers/assets/gxzj.png",
            caption=text,
            reply_markup=button,
        )

        # 发送 最后10期 的开奖结果
        last_10_kj = await database.get_kj()
        if not last_10_kj:
            pass
        else:
            text = "**期数 ｜ 开奖结果**\n\n"
            for i in last_10_kj:
                text += f"`{i.get('qihao')} ｜ {i.get('result')}`\n"
            await bot.send_message(config.GAME_GROUP_ID, text)

        # 开奖结束后，清空数据
        game_data["data"] = []
        game_data["bet"] = True
        game_data["end_at"] = None
        game_data["end_notice_id"] = None
        game_data["qihao"] = game_data.get("qihao") + 1
        game_data["start_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        await redis.set(r_key, json.dumps(game_data))

        # 修改管理面板按钮
        await cq.answer("开奖成功！", show_alert=True)
        await cq.edit_message_reply_markup(reply_markup=None)

        # 发送新一期的管理面板
        text = await a_text_(game_data)
        button = await a_button_(game_data.get("qihao"))
        for sudo in SUDO_USERID:
            await bot.send_message(sudo, text, reply_markup=button)
            await asyncio.sleep(1)

        text = f"🚨 {game_data.get("qihao")} 期\n\n✅ 开始投注\n\n--------------------------------"
        button = ikb(
            [
                [("账户信息", "xinxi"), ("今日流水", "liushui")],
            ]
        )
        await bot.send_photo(
            config.GAME_GROUP_ID,
            photo="TelegramBot/helpers/assets/ksxz.png",
            caption=text,
            reply_markup=button,
            parse_mode=enums.ParseMode.HTML,
        )

        log(__name__).info(
            f"第 {game_data.get("qihao") - 1} 期开奖成功！ 开奖结果：{kkk}"
        )

    elif action == "kw":  # 开奖为'阔'
        game_data = await redis.get(r_key)
        game_data = json.loads(game_data)
        # 保存开奖记录为三个'阔'
        kj_data = {
            "qihao": qihao,
            "result": "阔, 阔, 阔",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        await database.save_kj(kj_data, "kj")
        await redis.delete(kj_key)

        # 发送开奖结果到群里
        text = f"🎉`{game_data.get("qihao")}`期数\n"
        text += "✅开奖结果：阔, 阔, 阔\n\n"
        text += "✅下注的用户，已退下注本金\n\n"
        text += "✅本期开【阔】全部单子无效！\n\n"
        text += "✅请重新下注！\n\n—————————————————"

        button = ikb(
            [
                [("当前余额", "balance"), ("当期投注", "touzhu")],
                [
                    ("游戏规则", f"https://t.me/{bot.me.username}", "url"),
                    ("上下分群", "https://t.me/TDLDSXFQ", "url"),
                ],
            ]
        )

        await bot.send_photo(
            config.GAME_GROUP_ID,
            photo=await create_triple_kuo_image(),
            caption=text,
            reply_markup=button,
        )

        # await bot.send_message(config.GAME_GROUP_ID, text, reply_markup=button)

        # 直接退款，不同判断结果
        for g in game_data.get("data"):
            if not g.get("status"):
                await database.add_balance(
                    User(
                        id=g.get("id"),
                        first_name=g.get("full_name"),
                        username=g.get("username"),
                    ),
                    g.get("amount"),
                    "balance",
                    reason=f"退款 {g.get('xiazhu')} {g.get('amount')}",
                )
                g["paicai"] = g.get("amount")
                g["yingli"] = 0
                g["draw_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                g["status"] = True
                await database.save_kj(g, "games")

        text = f"🎉`{game_data.get("qihao")}`期数\n"
        text += "✅开奖结果：阔, 阔, 阔\n\n"
        button = ikb(
            [
                # [
                #     ("当前余额","balance"),("当期投注","touzhu")
                # ],
                [
                    ("出金", "https://t.me/MLH55N", "url"),
                    ("入金", "https://t.me/xianxin1", "url"),
                ]
            ]
        )

        await bot.send_photo(
            config.GAME_GROUP_ID,
            photo="TelegramBot/helpers/assets/gxzj.png",
            caption=text,
            reply_markup=button,
        )

        # 发送 最后10期 的开奖结果
        last_10_kj = await database.get_kj()
        if not last_10_kj:
            pass
        else:
            text = "**期数 ｜ 开奖结果**\n\n"
            for i in last_10_kj:
                text += f"`{i.get('qihao')} ｜ {i.get('result')}`\n"
            await bot.send_message(config.GAME_GROUP_ID, text)

        # 开奖结束后，清空数据
        game_data["data"] = []
        game_data["bet"] = True
        game_data["end_at"] = None
        game_data["end_notice_id"] = None
        game_data["qihao"] = game_data.get("qihao") + 1
        game_data["start_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        await redis.set(r_key, json.dumps(game_data))

        # 修改管理面板按钮
        await cq.answer("开奖成功！", show_alert=True)
        await cq.edit_message_reply_markup(reply_markup=None)

        # 发送新一期的管理面板
        text = await a_text_(game_data)
        button = await a_button_(game_data.get("qihao"))
        for sudo in SUDO_USERID:
            await bot.send_message(sudo, text, reply_markup=button)
            await asyncio.sleep(1)

        text = f"🚨 {game_data.get("qihao")} 期\n\n✅ 开始投注\n\n--------------------------------"
        button = ikb([[("账户信息", "xinxi"), ("今日流水", "liushui")]])
        await bot.send_photo(
            config.GAME_GROUP_ID,
            photo="TelegramBot/helpers/assets/ksxz.png",
            caption=text,
            reply_markup=button,
            parse_mode=enums.ParseMode.HTML,
        )

        log(__name__).info(
            f"第 {game_data.get("qihao") - 1} 期开奖成功！ 开奖结果：阔, 阔, 阔"
        )

    else:
        wz = cbdata[2]  # 1|2|3
        jg = cbdata[1]  # 虎|龟|鸡|鱼|象|虾
        data = json.loads(r_data)
        data[wz] = jg
        try:
            await cq.edit_message_reply_markup(await kj_button(qihao=qihao, r=data))
        except MessageNotModified:
            pass
        data = json.dumps(data)
        await redis.set(kj_key, data)


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
