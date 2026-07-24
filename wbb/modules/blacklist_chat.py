from pyrogram import filters
from pyrogram.types import Message

from wbb import SUDOERS, app
from wbb.utils.strings import tr
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import (
    blacklist_chat,
    blacklisted_chats,
    whitelist_chat,
)

__MODULE__ = tr("BLCHAT_MODULE")
__HELP__ = tr("BLCHAT_HELP")


@app.on_message(filters.command(["blacklist_chat", "حظر_دردشة"]) & SUDOERS)
@capture_err
async def blacklist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            tr("BLCHAT_BL_USAGE")
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await message.reply_text(tr("BLCHAT_ALREADY_BL"))
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        return await message.reply_text(
            tr("BLCHAT_BL_OK")
        )
    await message.reply_text(tr("BLCHAT_ERROR"))


@app.on_message(filters.command(["whitelist_chat", "سماح_دردشة"]) & SUDOERS)
@capture_err
async def whitelist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            tr("BLCHAT_WL_USAGE")
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await message.reply_text(tr("BLCHAT_ALREADY_WL"))
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text(
            tr("BLCHAT_WL_OK")
        )
    await message.reply_text(tr("BLCHAT_ERROR"))


@app.on_message(filters.command(["blacklisted_chats", "الدردشات_المحظورة"]) & SUDOERS)
@capture_err
async def blacklisted_chats_func(_, message: Message):
    text = ""
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await app.get_chat(chat_id)).title
        except Exception:
            title = "Private"
        text += f"**{count}. {title}** [`{chat_id}`]\n"
    if text == "":
        return await message.reply_text(tr("BLCHAT_NONE"))
    await message.reply_text(text)
