from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from TelegramBot import bot
from TelegramBot.config import OWNER_USERID, SUDO_USERID
from TelegramBot.database import database
from TelegramBot.helpers.decorators import ratelimiter
from TelegramBot.helpers.start_constants import (
    START_CAPTION,
    SUDO_TEXT,
    DEV_TEXT,
    ABOUT_CAPTION,
    COMMAND_CAPTION,
    USER_TEXT,
)

START_BUTTON = [
    [
        InlineKeyboardButton("📖 Commands", callback_data="COMMAND_BUTTON"),
        InlineKeyboardButton("👨‍💻 About me", callback_data="ABOUT_BUTTON"),
    ],
    [
        InlineKeyboardButton(
            "🔭 Original Repo",
            url="https://github.com/sanjit-sinha/TelegramBot-Boilerplate",
        )
    ],
]


COMMAND_BUTTON = [
    [
        InlineKeyboardButton("Users", callback_data="USER_BUTTON"),
        InlineKeyboardButton("Sudo", callback_data="SUDO_BUTTON"),
    ],
    [InlineKeyboardButton("Developer", callback_data="DEV_BUTTON")],
    [InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")],
]


GOBACK_1_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="START_BUTTON")]]
GOBACK_2_BUTTON = [[InlineKeyboardButton("🔙 Go Back", callback_data="COMMAND_BUTTON")]]


@Client.on_message(filters.command(["start", "help"]))
@ratelimiter
async def start(_, message: Message):
    await database.save_user(message.from_user)
    return await message.reply_text(
        START_CAPTION, reply_markup=InlineKeyboardMarkup(START_BUTTON), quote=True
    )


@Client.on_callback_query(filters.regex("_BUTTON"))
@ratelimiter
async def botCallbacks(_, cq: CallbackQuery):
    clicker_user_id = cq.from_user.id
    user_id = cq.message.reply_to_message.from_user.id

    if clicker_user_id != user_id:
        return await cq.answer("This command is not initiated by you.")

    if cq.data == "SUDO_BUTTON":
        if clicker_user_id not in SUDO_USERID:
            return await cq.answer(
                "You are not in the sudo user list.", show_alert=True
            )
        await cq.edit_message_text(
            SUDO_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
        )

    elif cq.data == "DEV_BUTTON":
        if clicker_user_id not in OWNER_USERID:
            return await cq.answer(
                "This is developer restricted command.", show_alert=True
            )
        await cq.edit_message_text(
            DEV_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
        )

    if cq.data == "ABOUT_BUTTON":
        await cq.edit_message_text(
            ABOUT_CAPTION, reply_markup=InlineKeyboardMarkup(GOBACK_1_BUTTON)
        )

    elif cq.data == "START_BUTTON":
        await cq.edit_message_text(
            START_CAPTION, reply_markup=InlineKeyboardMarkup(START_BUTTON)
        )

    elif cq.data == "COMMAND_BUTTON":
        await cq.edit_message_text(
            COMMAND_CAPTION, reply_markup=InlineKeyboardMarkup(COMMAND_BUTTON)
        )

    elif cq.data == "USER_BUTTON":
        await cq.edit_message_text(
            USER_TEXT, reply_markup=InlineKeyboardMarkup(GOBACK_2_BUTTON)
        )
    await cq.answer()


@Client.on_message(filters.new_chat_members, group=1)
async def new_chat(_, message: Message):
    """
    Get notified when someone add bot in the group, then saves that group chat_id
    in the database.
    """

    chat_id = message.chat.id
    for new_user in message.new_chat_members:
        if new_user.id == bot.me.id:
            await database.save_chat(chat_id)
