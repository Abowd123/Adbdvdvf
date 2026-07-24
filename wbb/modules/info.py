"""
MIT License

Copyright (c) 2024 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os

from pyrogram import filters
from pyrogram.types import Message

from wbb import SUDOERS, app
from wbb.core.sections import section
from wbb.utils.dbfunctions import is_gbanned_user, user_global_karma
from wbb.utils.strings import tr

__MODULE__ = tr("INFO_MODULE")
__HELP__ = tr("INFO_HELP")


async def get_user_info(user, already=False):
    if not already:
        user = await app.get_users(user)
    if not user.first_name:
        return [tr("INFO_DELETED_ACCOUNT"), None]
    user_id = user.id
    username = user.username
    first_name = user.first_name
    mention = user.mention("رابط")
    dc_id = user.dc_id
    photo_id = user.photo.big_file_id if user.photo else None
    is_gbanned = await is_gbanned_user(user_id)
    is_sudo = user_id in SUDOERS
    is_premium = user.is_premium
    karma = await user_global_karma(user_id)
    body = {
        tr("LBL_ID"): user_id,
        tr("LBL_DC"): dc_id,
        tr("LBL_NAME"): [first_name],
        tr("LBL_USERNAME"): [("@" + username) if username else tr("INFO_NULL")],
        tr("LBL_MENTION"): [mention],
        tr("LBL_SUDO"): is_sudo,
        tr("LBL_PREMIUM"): is_premium,
        tr("LBL_KARMA"): karma,
        tr("LBL_GBANNED"): is_gbanned,
    }
    caption = section(tr("INFO_USER_INFO"), body)
    return [caption, photo_id]


async def get_chat_info(chat, already=False):
    if not already:
        chat = await app.get_chat(chat)
    chat_id = chat.id
    username = chat.username
    title = chat.title
    type_ = str(chat.type).split(".")[1]
    is_scam = chat.is_scam
    description = chat.description
    members = chat.members_count
    is_restricted = chat.is_restricted
    link = f"[رابط](t.me/{username})" if username else tr("INFO_NULL")
    dc_id = chat.dc_id
    photo_id = chat.photo.big_file_id if chat.photo else None
    body = {
        tr("LBL_ID"): chat_id,
        tr("LBL_DC"): dc_id,
        tr("LBL_TYPE"): type_,
        tr("LBL_NAME"): [title],
        tr("LBL_USERNAME"): [("@" + username) if username else tr("INFO_NULL")],
        tr("LBL_MENTION"): [link],
        tr("LBL_MEMBERS"): members,
        tr("LBL_SCAM"): is_scam,
        tr("LBL_RESTRICTED"): is_restricted,
        tr("LBL_DESCRIPTION"): [description],
    }
    caption = section(tr("INFO_CHAT_INFO"), body)
    return [caption, photo_id]


@app.on_message(filters.command(["info", "معلومات"]))
async def info_func(_, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user.id
    elif not message.reply_to_message and len(message.command) == 1:
        user = message.from_user.id
    elif not message.reply_to_message and len(message.command) != 1:
        user = message.text.split(None, 1)[1]

    m = await message.reply_text(tr("INFO_PROCESSING"))

    try:
        info_caption, photo_id = await get_user_info(user)
    except Exception as e:
        return await m.edit(tr("INFO_ERR_CHAT", err=str(e)))

    if not photo_id:
        return await m.edit(info_caption, disable_web_page_preview=True)
    photo = await app.download_media(photo_id)

    await message.reply_photo(photo, caption=info_caption, quote=False)
    await m.delete()
    os.remove(photo)


@app.on_message(filters.command(["chat_info", "معلومات_الدردشة"]))
async def chat_info_func(_, message: Message):
    splited = message.text.split()
    if len(splited) == 1:
        chat = message.chat.id
        if chat == message.from_user.id:
            return await message.reply_text(
                tr("INFO_USAGE_CHAT")
            )
    else:
        chat = splited[1]
    try:
        m = await message.reply_text(tr("INFO_PROCESSING"))

        info_caption, photo_id = await get_chat_info(chat)
        if not photo_id:
            return await m.edit(info_caption, disable_web_page_preview=True)

        photo = await app.download_media(photo_id)
        await message.reply_photo(photo, caption=info_caption, quote=False)

        await m.delete()
        os.remove(photo)
    except Exception as e:
        await m.edit(e)
