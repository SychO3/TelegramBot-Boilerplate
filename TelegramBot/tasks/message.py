from pyrogram import Client
import asyncio

task_group = [
    -1002341709850,
    -1002001786090,
    -1001996497850,
    -1002015321051,
    -1002005014532,
    -1002005278134,
    -1002494606273,
]

text = """
您好，欢迎各位老板来到天地会资源社群，本机器人可以为您:
①提供资源供给名单，快速找到你需要的资源
②查询天地会担保人员名单及担保金额和主营业务，在寻找资源的路上为您保驾护航。

目前本社群做免费资源名单收录，请联系总舵主 @tiandihui_sdk  提交你的主营业务，为您添加到机器人名单里面。"""


async def send_messages(bot: Client):
    """半小时一次，并且置顶。推送新消息之前删除旧消息"""
    from TelegramBot.database.database import MessageLog

    message_log = MessageLog()

    for chat_id in task_group:
        # 删除旧消息
        old_message_id = await message_log.get_message_log(chat_id)
        if old_message_id:
            for message_id in old_message_id:
                try:
                    await bot.delete_messages(chat_id, message_id["message_id"])
                except Exception as e:
                    print(f"group_id{chat_id},delete message error: {e}")

                await asyncio.sleep(0.5)

        # 发送新消息
        try:
            sent_message = await bot.send_message(chat_id, text)
            await message_log.add_message_log(chat_id, sent_message.id)

            # 置顶
            await bot.pin_chat_message(chat_id, sent_message.id)
        except Exception as e:
            print(f"group_id{chat_id},send message error: {e}")

        await asyncio.sleep(0.7)
