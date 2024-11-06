from pyrogram.types import Message, CallbackQuery
from pyrogram import Client, filters
from pyrogram.helpers import ikb
from TelegramBot.database.database import Catalogs, Contacts, Guarantees

catalogs_db = Catalogs()
contacts_db = Contacts()
guarantees_db = Guarantees()


async def contact_group_button(catalogs_data: dict):
    buttons = []
    for catalog in catalogs_data:
        buttons.append([(catalog["catalog_name"], f"gcatalog_{catalog['catalog_id']}")])

    markup = ikb(buttons)
    return markup


@Client.on_message(filters.group & filters.regex(r"^导航"))
async def catalogs_group(_, message: Message):
    catalogs = await catalogs_db.get_catalogs()
    if not catalogs:
        return

    text = "点击下方按钮查看联系方式"
    await message.reply(
        text, reply_markup=await contact_group_button(catalogs), quote=False
    )


@Client.on_callback_query(filters.regex(r"^gcatalog"))
async def contact_group_callback(bot: Client, callback: CallbackQuery):
    try:
        catalog_id = int(callback.data.split("_")[1])
        data = await contacts_db.get_contacts(catalog_id)
        text = (
            f"**分类:** {await catalogs_db.get_catalog_name(catalog_id)}\n\n联系方式:\n"
        )
        if data:
            for contact in data:
                text += f"@{contact['text']}\n"
        else:
            text += "该分类下暂时没有联系方式"
        await callback.edit_message_text(
            text,
            reply_markup=await contact_group_button(await catalogs_db.get_catalogs()),
        )
    except Exception as e:
        print(e)


@Client.on_message(filters.group & filters.regex(r"^担保"))
async def guarantees_group(_, message: Message):
    data = await guarantees_db.get_guarantees()
    if not data:
        return
    text = "📚 **担保名单**\n\n"
    # 按照 money 降序排列
    data = sorted(data, key=lambda x: x["money"], reverse=True)
    for guarantee in data:
        text += f"{guarantee['contact']} {guarantee['money']} {guarantee['business']}\n"

    await message.reply(text, quote=False)
