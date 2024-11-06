from pyrogram.types import Message, CallbackQuery
from pyrogram import Client, filters
from pyrogram.helpers import ikb
from TelegramBot.helpers.filters import sudo_cmd
from TelegramBot.database.database import Catalogs, Contacts

catalogs_db = Catalogs()
contacts_db = Contacts()


async def catalog_text():
    text = "📚 **导航功能**\n\n"
    text += "点击下方按钮以管理分类"
    return text


async def catalog_buttons():
    catalogs = await catalogs_db.get_catalogs()
    buttons = []
    if catalogs:
        for catalog in catalogs:
            buttons.append(
                [(catalog["catalog_name"], f"catalog_{catalog['catalog_id']}")]
            )

    buttons.append([("➕ 添加分类", "catalog_add"), ("✖️ 关闭", "close")])
    markup = ikb(buttons)
    return markup


async def contact_text(catalog_id: int):
    contacts = await contacts_db.get_contacts(catalog_id)
    catalog_name = await catalogs_db.get_catalog_name(catalog_id)
    text = f"**分类:** {catalog_name}\n\n联系方式:\n"
    if contacts:
        for contact in contacts:
            text += f"@{contact['text']}\n"
    else:
        text += "该分类下暂时没有联系方式"
    return text


async def contact_buttons(catalog_id: int):
    buttons = [
        [("➕ 添加联系方式", f"contact_add_{catalog_id}")],
        [
            ("修改名称", f"catalog_edit_{catalog_id}"),
            ("删除分类", f"catalog_delete_{catalog_id}"),
        ],
        [("🔙 返回", "catalog_r"), ("✖️ 关闭", "close")],
    ]

    markup = ikb(buttons)
    return markup


@Client.on_message(filters.command(["c"]) & sudo_cmd & filters.private)
async def catalogs_admin(_, message: Message):
    text = await catalog_text()
    await message.reply_text(text, reply_markup=await catalog_buttons())


@Client.on_callback_query(filters.regex(r"^catalog") & sudo_cmd)
async def catalog_button(bot: Client, callback: CallbackQuery):
    try:
        data = callback.data.split("_")
        if data[1] == "add":
            ask = await bot.ask(
                callback.from_user.id,
                "**👨‍🚀 请输入分类名称:**\n1.可以使用emoji\n2.换行或者空格添加多个",
                timeout=60,
            )
            data = ask.text.split()
            for new_catalog_name in data:
                await catalogs_db.add_catalog(new_catalog_name)
            new_catalog_names = " ".join(data)
            await ask.sent_message.edit(f"🎉分类 **{new_catalog_names}** 已添加！")
            await ask.delete()
            await callback.message.edit_reply_markup(await catalog_buttons())
        elif data[1] == "edit":
            ask = await bot.ask(
                callback.from_user.id, "**👨‍🚀 请输入新的分类名称:**", timeout=60
            )
            await catalogs_db.edit_catalog(int(data[2]), ask.text)
            await ask.sent_message.edit(f"新的分类名称已更新为 **{ask.text}**")
            await ask.delete()
            text = await contact_text(int(data[2]))
            markup = await contact_buttons(int(data[2]))
            await callback.message.edit_text(text, reply_markup=markup)
        elif data[1] == "delete":
            await catalogs_db.delete_catalog(int(data[2]))
            await contacts_db.del_all_contacts(int(data[2]))
            await callback.answer("分类已删除", show_alert=True)
            text = await catalog_text()
            markup = await catalog_buttons()
            await callback.message.edit_text(text, reply_markup=markup)
        elif data[1] == "r":
            text = await catalog_text()
            await callback.message.edit_text(text, reply_markup=await catalog_buttons())
        else:  # 进入分类
            text = await contact_text(int(data[1]))
            markup = await contact_buttons(int(data[1]))
            await callback.message.edit_text(text, reply_markup=markup)
    except Exception as e:
        print(f"{__name__} - error: {e}")


@Client.on_callback_query(filters.regex(r"^contact") & sudo_cmd)
async def contact_admin(bot: Client, callback: CallbackQuery):
    try:
        catalog_id = int(callback.data.split("_")[2])
        contacts = await contacts_db.get_contacts(catalog_id)
        old = ""
        if contacts:
            for contact in contacts:
                old += f"@{contact['text']}\n"

        text = "**👨‍🚀 请输入新的联系方式:**\n1.可以使用emoji\n2.换行或者空格添加多个"
        if old != "":
            text += (
                f"\n\n**当前联系方式:**\n`{old}`\n点击上方可以复制，本次操作会进行覆盖"
            )

        ask = await bot.ask(callback.from_user.id, text, timeout=60)
        data = ask.text.split()
        await contacts_db.del_all_contacts(catalog_id)
        for new_contact in data:
            if new_contact.startswith("@"):
                new_contact = new_contact[1:]

            if new_contact.startswith("https://t.me/"):
                new_contact = new_contact[13:]

            if new_contact.startswith("t.me/"):
                new_contact = new_contact[5:]

            await contacts_db.add_contact(catalog_id, new_contact)

        new_contact_text = " ".join(data)
        await ask.sent_message.edit(f"联系方式已更新为 **{new_contact_text}**")
        await ask.delete()

        text = await contact_text(catalog_id)
        markup = await contact_buttons(catalog_id)
        await callback.message.edit_text(text, reply_markup=markup)
    except Exception as e:
        print(f"{__name__} - error: {e}")


@Client.on_callback_query(filters.regex(r"^close") & sudo_cmd)
async def close_catalogs(_, callback: CallbackQuery):
    await callback.message.delete()
