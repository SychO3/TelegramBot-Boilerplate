from pyrogram.types import Message, CallbackQuery
from pyrogram import Client, filters
from pyrogram.helpers import ikb
from TelegramBot.helpers.filters import sudo_cmd

from TelegramBot.database.database import Guarantees

guarantees_db = Guarantees()


async def guarantees_text():
    text = "📚 **担保名单**\n\n"
    data = await guarantees_db.get_guarantees()
    if data:
        for guarantee in data:
            text += f"{guarantee['id']}. {guarantee['contact']} {guarantee['money']} {guarantee['business']}\n"
    else:
        text += "暂时没有担保名单"
    return text


async def guarantees_buttons():
    buttons = [
        [
            ("➕ 添加", "guarantees_add"),
            ("✍️ 修改", "guarantees_edit"),
            ("❗️ 删除", "guarantees_delete"),
        ],
        [("✖️ 关闭", "close")],
    ]
    markup = ikb(buttons)
    return markup


@Client.on_message(filters.command(["d"]) & sudo_cmd & filters.private)
async def guarantees_admin(_, message: Message):
    text = await guarantees_text()
    markup = await guarantees_buttons()
    await message.reply_text(text, reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^guarantees") & sudo_cmd)
async def guarantees_callback(bot: Client, callback: CallbackQuery):
    try:
        action = callback.data.split("_")[1]
        if action == "add":
            text = "输入需要添加的担保名单。格式为：\n\n`@飞机号 金额 主要业务`\n换行为多个担保名单"
            ask = await bot.ask(callback.from_user.id, text, timeout=60)
            data = ask.text.split("\n")
            for info in data:
                guarantee_data = info.split(" ")
                if len(guarantee_data) == 3:
                    guarantee_data = {
                        "contact": guarantee_data[0],
                        "money": int(guarantee_data[1]),
                        "business": guarantee_data[2],
                    }
                    await guarantees_db.add_guarantee(guarantee_data)
            await ask.reply("添加成功!")

            text = await guarantees_text()
            markup = await guarantees_buttons()
            await callback.edit_message_text(text, reply_markup=markup)

        elif action == "edit":
            text = "输入需要修改的担保名单序号"
            ask = await bot.ask(callback.from_user.id, text, timeout=60)
            guarantee_id = int(ask.text)
            guarantee_data = await guarantees_db.get_guarantee(guarantee_id)
            if not guarantee_data:
                await ask.reply("未找到该担保名单")
                return
            # guarantee_data = guarantee_data[0]
            text = "输入需要修改的担保信息。格式为：\n\n`@飞机号 金额 主要业务`"
            ask = await bot.ask(callback.from_user.id, text, timeout=60)
            guarantee_data = ask.text.split(" ")
            if len(guarantee_data) == 3:
                guarantee_data = {
                    "contact": guarantee_data[0],
                    "money": int(guarantee_data[1]),
                    "business": guarantee_data[2],
                }
                await guarantees_db.edit_guarantee(guarantee_id, guarantee_data)
            await ask.reply("修改成功!")

            text = await guarantees_text()
            markup = await guarantees_buttons()
            await callback.edit_message_text(text, reply_markup=markup)

        elif action == "delete":
            text = "输入需要删除的担保名单序号"
            ask = await bot.ask(callback.from_user.id, text, timeout=60)
            guarantee_id = int(ask.text)
            guarantee_data = await guarantees_db.get_guarantee(guarantee_id)
            if not guarantee_data:
                await ask.reply("未找到该担保名单")
                return
            await guarantees_db.delete_guarantee(guarantee_id)
            await ask.reply("删除成功!")

            text = await guarantees_text()
            markup = await guarantees_buttons()
            await callback.edit_message_text(text, reply_markup=markup)
        else:
            pass
    except Exception as e:
        print(f"{__name__} - error: {e}")
