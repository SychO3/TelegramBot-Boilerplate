from pyrogram import Client, filters
from pyrogram.types import Message, BotCommand

# from TelegramBot import bot
from TelegramBot.config import SUDO_USERID
from TelegramBot.database import database
from TelegramBot.helpers.decorators import ratelimiter

# START_BUTTON = [
#     [
#         InlineKeyboardButton("📖 Commands", callback_data="COMMAND_BUTTON"),
#         InlineKeyboardButton("👨‍💻 About me", callback_data="ABOUT_BUTTON"),
#     ],
#     [
#         InlineKeyboardButton(
#             "🔭 Original Repo",
#             url="https://github.com/sanjit-sinha/TelegramBot-Boilerplate",
#         )
#     ],
# ]
#
#
# COMMAND_BUTTON = [
#     [
#         InlineKeyboardButton("Users", callback_data="USER_BUTTON"),
#         InlineKeyboardButton("Sudo", callback_data="SUDO_BUTTON"),
#     ],
#     [InlineKeyboardButton("Developer", callback_data="DEV_BUTTON")],
#     [InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")],
# ]
#
#
# GOBACK_1_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")]]
# GOBACK_2_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="COMMAND_BUTTON")]]


@Client.on_message(filters.command(["start", "help"]) & filters.private)
@ratelimiter
async def start(bot: Client, message: Message):
    await message.reply_text(
        text=f"Hello {message.from_user.mention}, I am a Community Bot.", quote=False
    )
    await database.save_user(message.from_user)
    await bot.set_bot_commands(
        [
            BotCommand("start", "开始"),
            # BotCommand("help", "Get help"),
        ]
    )
    if message.from_user.id in SUDO_USERID:
        await bot.set_bot_commands(
            [
                BotCommand("start", "开始"),
                BotCommand("c", "管理分类"),
                BotCommand("d", "管理名单"),
            ]
        )
        await message.reply_text(
            text="使用 /c 来管理分类\n使用 /d 来管理名单", quote=False
        )

    # return await message.reply_text(
    #     START_CAPTION, reply_markup=InlineKeyboardMarkup(START_BUTTON), quote=True
    # )


# @Client.on_callback_query(filters.regex("_BUTTON"))
# @ratelimiter
# async def botCallbacks(_, cq: CallbackQuery):
#     clicker_user_id = cq.from_user.id
#     user_id = cq.message.reply_to_message.from_user.id
#
#     if clicker_user_id != user_id:
#         return await cq.answer("This command is not initiated by you.")
#
#     if cq.data == "SUDO_BUTTON":
#         if clicker_user_id not in SUDO_USERID:
#             return await cq.answer(
#                 "You are not in the sudo user list.", show_alert=True
#             )
#         await cq.edit_message_text(
#             SUDO_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
#         )
#
#     elif cq.data == "DEV_BUTTON":
#         if clicker_user_id not in OWNER_USERID:
#             return await cq.answer(
#                 "This is developer restricted command.", show_alert=True
#             )
#         await cq.edit_message_text(
#             DEV_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
#         )
#
#     if cq.data == "ABOUT_BUTTON":
#         await cq.edit_message_text(
#             ABOUT_CAPTION, reply_markup=InlineKeyboardMarkup(GOBACK_1_BUTTON)
#         )
#
#     elif cq.data == "START_BUTTON":
#         await cq.edit_message_text(
#             START_CAPTION, reply_markup=InlineKeyboardMarkup(START_BUTTON)
#         )
#
#     elif cq.data == "COMMAND_BUTTON":
#         await cq.edit_message_text(
#             COMMAND_CAPTION, reply_markup=InlineKeyboardMarkup(COMMAND_BUTTON)
#         )
#
#     elif cq.data == "USER_BUTTON":
#         await cq.edit_message_text(
#             USER_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
#         )
#     await cq.answer()
#
#
# @Client.on_message(filters.new_chat_members, group=1)
# async def new_chat(_, message: Message):
#     """
#     Get notified when someone add bot in the group, then saves that group chat_id
#     in the database.
#     """
#
#     chat_id = message.chat.id
#     for new_user in message.new_chat_members:
#         if new_user.id == bot.me.id:
#             await database.save_chat(chat_id)


# @Client.on_message(filters.command(["test"]) & filters.private)
# async def test(bot:Client, message: Message):
#     # print(message.chat.title, message.chat.id)
#
#     # -1002341709850 天地会-海外资源总舵
#     # -1002001786090 天地会-海外资源一分舵
#     # -1001996497850 天地会-海外资源二分舵
#     # -1002015321051 天地会-海外资源三分舵
#     # -1002005014532 天地会-海外资源五分舵
#     # -1002005278134 天地会-海外资源六分舵
#
#     # -1002494606273 频道
#
#     chat_info = await bot.get_chat("https://t.me/tiandihui1")
#
#     print(chat_info)

task_group = [
    -1002341709850,
    -1002001786090,
    -1001996497850,
    -1002015321051,
    -1002005014532,
    -1002005278134,
    -1002494606273,
]


@Client.on_message(filters.chat(task_group) & filters.text)
async def save_group_info(_, message: Message):
    chat_id = message.chat.id
    chat_title = message.chat.title
    chat_username = message.chat.username
    chat_type = message.chat.type

    info = {
        "chat_id": chat_id,
        "chat_title": chat_title,
        "chat_username": chat_username,
        "chat_type": chat_type.value,
    }

    await database.save_chat(**info)
