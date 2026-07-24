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
import asyncio
import re
from contextlib import suppress
from time import time

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait
from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChatPermissions,
    ChatPrivileges,
    Message,
)

from wbb import BOT_ID, SUDOERS, app, log
from wbb.core.decorators.errors import capture_err
from wbb.core.keyboard import ikb
from wbb.utils.dbfunctions import (
    add_warn,
    get_warn,
    int_to_alpha,
    remove_warns,
    save_filter,
)
from wbb.utils.functions import (
    extract_user,
    extract_user_and_reason,
    time_converter,
)
from wbb.utils.strings import tr

__MODULE__ = "Admin"
__HELP__ = """/ban - \u062d\u0638\u0631 \u0645\u0633\u062a\u062e\u062f\u0645
/dban - \u062d\u0630\u0641 \u0627\u0644\u0631\u0633\u0627\u0644\u0629 \u0627\u0644\u0645\u064f\u0631\u062f \u0639\u0644\u064a\u0647\u0627 \u0648\u062d\u0638\u0631 \u0645\u064f\u0631\u0633\u0650\u0644\u0647\u0627
/tban - \u062d\u0638\u0631 \u0645\u0633\u062a\u062e\u062f\u0645 \u0644\u0645\u062f\u0629 \u0645\u062d\u062f\u062f\u0629
/unban - \u0625\u0644\u063a\u0627\u0621 \u062d\u0638\u0631 \u0645\u0633\u062a\u062e\u062f\u0645
/listban - \u062d\u0638\u0631 \u0645\u0633\u062a\u062e\u062f\u0645 \u0645\u0646 \u0627\u0644\u0645\u062c\u0645\u0648\u0639\u0627\u062a \u0627\u0644\u0645\u0630\u0643\u0648\u0631\u0629 \u0641\u064a \u0631\u0633\u0627\u0644\u0629
/listunban - \u0625\u0644\u063a\u0627\u0621 \u062d\u0638\u0631 \u0645\u0633\u062a\u062e\u062f\u0645 \u0645\u0646 \u0627\u0644\u0645\u062c\u0645\u0648\u0639\u0627\u062a \u0627\u0644\u0645\u0630\u0643\u0648\u0631\u0629 \u0641\u064a \u0631\u0633\u0627\u0644\u0629
/warn - \u062a\u062d\u0630\u064a\u0631 \u0645\u0633\u062a\u062e\u062f\u0645
/dwarn - \u062d\u0630\u0641 \u0627\u0644\u0631\u0633\u0627\u0644\u0629 \u0627\u0644\u0645\u064f\u0631\u062f \u0639\u0644\u064a\u0647\u0627 \u0648\u062a\u062d\u0630\u064a\u0631 \u0645\u064f\u0631\u0633\u0650\u0644\u0647\u0627
/rmwarns - \u0625\u0632\u0627\u0644\u0629 \u0643\u0644 \u062a\u062d\u0630\u064a\u0631\u0627\u062a \u0645\u0633\u062a\u062e\u062f\u0645
/warns - \u0639\u0631\u0636 \u062a\u062d\u0630\u064a\u0631\u0627\u062a \u0645\u0633\u062a\u062e\u062f\u0645
/kick - \u0637\u0631\u062f \u0645\u0633\u062a\u062e\u062f\u0645
/dkick - \u062d\u0630\u0641 \u0627\u0644\u0631\u0633\u0627\u0644\u0629 \u0627\u0644\u0645\u064f\u0631\u062f \u0639\u0644\u064a\u0647\u0627 \u0648\u0637\u0631\u062f \u0645\u064f\u0631\u0633\u0650\u0644\u0647\u0627
/purge - \u062d\u0630\u0641 \u0645\u062c\u0645\u0648\u0639\u0629 \u0631\u0633\u0627\u0626\u0644
/purge [n] - \u062d\u0630\u0641 \u0639\u062f\u062f "n" \u0645\u0646 \u0627\u0644\u0631\u0633\u0627\u0626\u0644 \u0628\u062f\u0621\u0627\u064b \u0645\u0646 \u0627\u0644\u0631\u0633\u0627\u0644\u0629 \u0627\u0644\u0645\u064f\u0631\u062f \u0639\u0644\u064a\u0647\u0627
/del - \u062d\u0630\u0641 \u0627\u0644\u0631\u0633\u0627\u0644\u0629 \u0627\u0644\u0645\u064f\u0631\u062f \u0639\u0644\u064a\u0647\u0627
/promote - \u062a\u0631\u0642\u064a\u0629 \u0639\u0636\u0648
/fullpromote - \u062a\u0631\u0642\u064a\u0629 \u0639\u0636\u0648 \u0628\u0643\u0627\u0645\u0644 \u0627\u0644\u0635\u0644\u0627\u062d\u064a\u0627\u062a
/demote - \u062a\u0646\u0632\u064a\u0644 \u0639\u0636\u0648
/pin - \u062a\u062b\u0628\u064a\u062a \u0631\u0633\u0627\u0644\u0629
/mute - \u0643\u062a\u0645 \u0645\u0633\u062a\u062e\u062f\u0645
/tmute - \u0643\u062a\u0645 \u0645\u0633\u062a\u062e\u062f\u0645 \u0644\u0645\u062f\u0629 \u0645\u062d\u062f\u062f\u0629
/unmute - \u0625\u0644\u063a\u0627\u0621 \u0643\u062a\u0645 \u0645\u0633\u062a\u062e\u062f\u0645
/ban_ghosts - \u062d\u0638\u0631 \u0627\u0644\u062d\u0633\u0627\u0628\u0627\u062a \u0627\u0644\u0645\u062d\u0630\u0648\u0641\u0629
/report | @admins | @admin - \u0627\u0644\u0625\u0628\u0644\u0627\u063a \u0639\u0646 \u0631\u0633\u0627\u0644\u0629 \u0644\u0644\u0645\u0634\u0631\u0641\u064a\u0646
/invite - \u0625\u0631\u0633\u0627\u0644 \u0631\u0627\u0628\u0637 \u062f\u0639\u0648\u0629 \u0627\u0644\u0645\u062c\u0645\u0648\u0639\u0629"""


async def member_permissions(chat_id: int, user_id: int):
    perms = []
    member = (await app.get_chat_member(chat_id, user_id)).privileges
    if not member:
        return []
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    if member.can_manage_video_chats:
        perms.append("can_manage_video_chats")
    return perms


from wbb.core.decorators.permissions import adminsOnly

admins_in_chat = {}


async def list_admins(chat_id: int):
    global admins_in_chat
    if chat_id in admins_in_chat:
        interval = time() - admins_in_chat[chat_id]["last_updated_at"]
        if interval < 3600:
            return admins_in_chat[chat_id]["data"]

    admins_in_chat[chat_id] = {
        "last_updated_at": time(),
        "data": [
            member.user.id
            async for member in app.get_chat_members(
                chat_id, filter=ChatMembersFilter.ADMINISTRATORS
            )
        ],
    }
    return admins_in_chat[chat_id]["data"]


# Admin cache reload


@app.on_chat_member_updated()
async def admin_cache_func(_, cmu: ChatMemberUpdated):
    if cmu.old_chat_member and cmu.old_chat_member.promoted_by:
        admins_in_chat[cmu.chat.id] = {
            "last_updated_at": time(),
            "data": [
                member.user.id
                async for member in app.get_chat_members(
                    cmu.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
                )
            ],
        }
        log.info(f"Updated admin cache for {cmu.chat.id} [{cmu.chat.title}]")


# Purge Messages


@app.on_message(filters.command(["purge", "\u062a\u0637\u0647\u064a\u0631"]) & ~filters.private)
@adminsOnly("can_delete_messages")
async def purgeFunc(_, message: Message):
    repliedmsg = message.reply_to_message
    await message.delete()

    if not repliedmsg:
        return await message.reply_text(tr("PURGE_REPLY"))

    cmd = message.command
    if len(cmd) > 1 and cmd[1].isdigit():
        purge_to = repliedmsg.id + int(cmd[1])
        if purge_to > message.id:
            purge_to = message.id
    else:
        purge_to = message.id

    chat_id = message.chat.id
    message_ids = []

    for message_id in range(
        repliedmsg.id,
        purge_to,
    ):
        message_ids.append(message_id)

        # Max message deletion limit is 100
        if len(message_ids) == 100:
            await app.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True,  # For both sides
            )

            # To delete more than 100 messages, start again
            message_ids = []

    # Delete if any messages left
    if len(message_ids) > 0:
        await app.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True,
        )


# Kick members


@app.on_message(
    filters.command(["kick", "dkick", "\u0637\u0631\u062f", "\u0637\u0631\u062f_\u062d\u0630\u0641"])
    & ~filters.private
)
@adminsOnly("can_restrict_members")
async def kickFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text(tr("USER_NOT_FOUND"))
    if user_id == BOT_ID:
        return await message.reply_text(tr("CANT_KICK_SELF"))
    if user_id in SUDOERS:
        return await message.reply_text(tr("KICK_SUDO"))
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(tr("CANT_KICK_ADMIN"))
    mention = (await app.get_users(user_id)).mention
    by = message.from_user.mention if message.from_user else tr("ANON")
    msg = tr("KICK_MSG", mention=mention, by=by, reason=reason or tr("NO_REASON"))
    if message.command[0] in ("dkick", "\u0637\u0631\u062f_\u062d\u0630\u0641"):
        await message.reply_to_message.delete()
    await message.chat.ban_member(user_id)
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg)
    await asyncio.sleep(1)
    await message.chat.unban_member(user_id)


# Ban members


@app.on_message(
    filters.command(["ban", "dban", "tban", "\u062d\u0638\u0631", "\u062d\u0638\u0631_\u062d\u0630\u0641", "\u062d\u0638\u0631_\u0645\u0624\u0642\u062a"])
    & ~filters.private
)
@adminsOnly("can_restrict_members")
async def banFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)

    if not user_id:
        return await message.reply_text(tr("USER_NOT_FOUND"))
    if user_id == BOT_ID:
        return await message.reply_text(tr("CANT_BAN_SELF"))
    if user_id in SUDOERS:
        return await message.reply_text(tr("BAN_SUDO"))
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(tr("CANT_BAN_ADMIN"))

    try:
        mention = (await app.get_users(user_id)).mention
    except IndexError:
        mention = (
            message.reply_to_message.sender_chat.title
            if message.reply_to_message
            else tr("ANON")
        )

    by = message.from_user.mention if message.from_user else tr("ANON")
    msg = tr("BAN_MSG", mention=mention, by=by) + "\n"
    if message.command[0] in ("dban", "\u062d\u0638\u0631_\u062d\u0630\u0641"):
        await message.reply_to_message.delete()
    if message.command[0] in ("tban", "\u062d\u0638\u0631_\u0645\u0624\u0642\u062a"):
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_ban = await time_converter(message, time_value)
        msg += tr("BANNED_FOR", time=time_value) + "\n"
        if temp_reason:
            msg += tr("REASON", reason=temp_reason)
        with suppress(AttributeError):
            if len(time_value[:-1]) < 3:
                await message.chat.ban_member(user_id, until_date=temp_ban)
                replied_message = message.reply_to_message
                if replied_message:
                    message = replied_message
                await message.reply_text(msg)
            else:
                await message.reply_text(tr("MAX_99"))
        return
    if reason:
        msg += tr("REASON", reason=reason)
    await message.chat.ban_member(user_id)
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg)


# Unban members


@app.on_message(filters.command(["unban", "\u0627\u0644\u063a\u0627\u0621_\u062d\u0638\u0631"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def unban_func(_, message: Message):
    # we don't need reasons for unban, also, we
    # don't need to get "text_mention" entity, because
    # normal users won't get text_mention if the user
    # they want to unban is not in the group.
    reply = message.reply_to_message

    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await message.reply_text(tr("CANT_UNBAN_CHANNEL"))

    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = message.reply_to_message.from_user.id
    else:
        return await message.reply_text(tr("UNBAN_PROVIDE"))
    await message.chat.unban_member(user)
    umention = (await app.get_users(user)).mention
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(tr("UNBANNED", mention=umention))


# Ban users listed in a message


@app.on_message(SUDOERS & filters.command(["listban", "\u0642\u0627\u0626\u0645\u0629_\u062d\u0638\u0631"]) & ~filters.private)
async def list_ban_(c, message: Message):
    userid, msglink_reason = await extract_user_and_reason(message)
    if not userid or not msglink_reason:
        return await message.reply_text(tr("LISTBAN_PROVIDE"))
    if (
        len(msglink_reason.split(" ")) == 1
    ):  # message link included with the reason
        return await message.reply_text(tr("LISTBAN_NEED_REASON"))
    # seperate messge link from reason
    lreason = msglink_reason.split()
    messagelink, reason = lreason[0], " ".join(lreason[1:])

    if not re.search(
        r"(https?://)?t(elegram)?\.me/\w+/\d+", messagelink
    ):  # validate link
        return await message.reply_text(tr("INVALID_LINK"))

    if userid == BOT_ID:
        return await message.reply_text(tr("CANT_BAN_SELF_SIMPLE"))
    if userid in SUDOERS:
        return await message.reply_text(tr("BAN_SUDO"))
    splitted = messagelink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(tr("BANNING_MULTI"))
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall(r"@\w+", msgtext)
    except:
        return await m.edit_text(tr("CANT_GET_GROUPS"))
    count = 0
    for username in gusernames:
        try:
            await app.ban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            continue
        count += 1
    mention = (await app.get_users(userid)).mention

    msg = tr(
        "LISTBAN_MSG",
        mention=mention,
        userid=userid,
        admin=message.from_user.mention,
        count=count,
        reason=reason,
    )
    await m.edit_text(msg)


# Unban users listed in a message


@app.on_message(SUDOERS & filters.command(["listunban", "\u0642\u0627\u0626\u0645\u0629_\u0627\u0644\u063a\u0627\u0621_\u062d\u0638\u0631"]) & ~filters.private)
async def list_unban_(c, message: Message):
    userid, msglink = await extract_user_and_reason(message)
    if not userid or not msglink:
        return await message.reply_text(tr("LISTUNBAN_PROVIDE"))

    if not re.search(
        r"(https?://)?t(elegram)?\.me/\w+/\d+", msglink
    ):  # validate link
        return await message.reply_text(tr("INVALID_LINK"))

    splitted = msglink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(tr("UNBANNING_MULTI"))
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall(r"@\w+", msgtext)
    except:
        return await m.edit_text(tr("CANT_GET_GROUPS"))
    count = 0
    for username in gusernames:
        try:
            await app.unban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            continue
        count += 1
    mention = (await app.get_users(userid)).mention
    msg = tr(
        "LISTUNBAN_MSG",
        mention=mention,
        userid=userid,
        admin=message.from_user.mention,
        count=count,
    )
    await m.edit_text(msg)


# Delete messages


@app.on_message(filters.command(["del", "\u062d\u0630\u0641"]) & ~filters.private)
@adminsOnly("can_delete_messages")
async def deleteFunc(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text(tr("DEL_REPLY"))
    await message.reply_to_message.delete()
    await message.delete()


# Promote Members


@app.on_message(
    filters.command(["promote", "fullpromote", "\u062a\u0631\u0642\u064a\u0629", "\u062a\u0631\u0642\u064a\u0629_\u0643\u0627\u0645\u0644\u0629"])
    & ~filters.private
)
@adminsOnly("can_promote_members")
async def promoteFunc(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text(tr("USER_NOT_FOUND"))

    bot = (await app.get_chat_member(message.chat.id, BOT_ID)).privileges
    if user_id == BOT_ID:
        return await message.reply_text(tr("CANT_PROMOTE_SELF"))
    if not bot:
        return await message.reply_text(tr("BOT_NOT_ADMIN"))
    if not bot.can_promote_members:
        return await message.reply_text(tr("BOT_NO_PERMS"))

    umention = (await app.get_users(user_id)).mention

    if message.command[0] in ("fullpromote", "\u062a\u0631\u0642\u064a\u0629_\u0643\u0627\u0645\u0644\u0629"):
        await message.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=bot.can_change_info,
                can_invite_users=bot.can_invite_users,
                can_delete_messages=bot.can_delete_messages,
                can_restrict_members=bot.can_restrict_members,
                can_pin_messages=bot.can_pin_messages,
                can_promote_members=bot.can_promote_members,
                can_manage_chat=bot.can_manage_chat,
                can_manage_video_chats=bot.can_manage_video_chats,
            ),
        )
        return await message.reply_text(tr("FULLY_PROMOTED", mention=umention))

    await message.chat.promote_member(
        user_id=user_id,
        privileges=ChatPrivileges(
            can_change_info=False,
            can_invite_users=bot.can_invite_users,
            can_delete_messages=bot.can_delete_messages,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=bot.can_manage_chat,
            can_manage_video_chats=bot.can_manage_video_chats,
        ),
    )
    await message.reply_text(tr("PROMOTED", mention=umention))


# Demote Member


@app.on_message(filters.command(["demote", "\u062a\u0646\u0632\u064a\u0644"]) & ~filters.private)
@adminsOnly("can_promote_members")
async def demote(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text(tr("USER_NOT_FOUND"))
    if user_id == BOT_ID:
        return await message.reply_text(tr("CANT_DEMOTE_SELF"))
    if user_id in SUDOERS:
        return await message.reply_text(tr("DEMOTE_SUDO"))
    try:
        member = await app.get_chat_member(message.chat.id, user_id)
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            await message.chat.promote_member(
                user_id=user_id,
                privileges=ChatPrivileges(
                    can_change_info=False,
                    can_invite_users=False,
                    can_delete_messages=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_chat=False,
                    can_manage_video_chats=False,
                ),
            )
            umention = (await app.get_users(user_id)).mention
            await message.reply_text(tr("DEMOTED", mention=umention))
        else:
            await message.reply_text(tr("NOT_ADMIN"))
    except Exception as e:
        await message.reply_text(e)


# Pin Messages


@app.on_message(
    filters.command(["pin", "unpin", "\u062a\u062b\u0628\u064a\u062a", "\u0627\u0644\u063a\u0627\u0621_\u062a\u062b\u0628\u064a\u062a"])
    & ~filters.private
)
@adminsOnly("can_pin_messages")
async def pin(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text(tr("PIN_REPLY"))
    r = message.reply_to_message
    if message.command[0] in ("unpin", "\u0627\u0644\u063a\u0627\u0621_\u062a\u062b\u0628\u064a\u062a"):
        await r.unpin()
        return await message.reply_text(
            tr("UNPINNED", link=r.link),
            disable_web_page_preview=True,
        )
    await r.pin(disable_notification=True)
    await message.reply(
        tr("PINNED", link=r.link),
        disable_web_page_preview=True,
    )
    msg = tr("PIN_CHECK", link=r.link)
    filter_ = dict(type="text", data=msg)
    await save_filter(message.chat.id, "~pinned", filter_)


# Mute members


@app.on_message(
    filters.command(["mute", "tmute", "\u0643\u062a\u0645", "\u0643\u062a\u0645_\u0645\u0624\u0642\u062a"])
    & ~filters.private
)
@adminsOnly("can_restrict_members")
async def mute(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text(tr("USER_NOT_FOUND"))
    if user_id == BOT_ID:
        return await message.reply_text(tr("CANT_MUTE_SELF"))
    if user_id in SUDOERS:
        return await message.reply_text(tr("MUTE_SUDO"))
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(tr("CANT_MUTE_ADMIN"))
    mention = (await app.get_users(user_id)).mention
    keyboard = ikb({tr("BTN_UNMUTE"): f"unmute_{user_id}"})
    by = message.from_user.mention if message.from_user else tr("ANON")
    msg = tr("MUTE_MSG", mention=mention, by=by) + "\n"
    if message.command[0] in ("tmute", "\u0643\u062a\u0645_\u0645\u0624\u0642\u062a"):
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_mute = await time_converter(message, time_value)
        msg += tr("MUTED_FOR", time=time_value) + "\n"
        if temp_reason:
            msg += tr("REASON", reason=temp_reason)
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.restrict_member(
                    user_id,
                    permissions=ChatPermissions(),
                    until_date=temp_mute,
                )
                replied_message = message.reply_to_message
                if replied_message:
                    message = replied_message
                await message.reply_text(msg, reply_markup=keyboard)
            else:
                await message.reply_text(tr("MAX_99"))
        except AttributeError:
            pass
        return
    if reason:
        msg += tr("REASON", reason=reason)
    await message.chat.restrict_member(user_id, permissions=ChatPermissions())
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg, reply_markup=keyboard)


# Unmute members


@app.on_message(filters.command(["unmute", "\u0627\u0644\u063a\u0627\u0621_\u0643\u062a\u0645"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def unmute(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text(tr("USER_NOT_FOUND"))
    await message.chat.unban_member(user_id)
    umention = (await app.get_users(user_id)).mention
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(tr("UNMUTED", mention=umention))


# Ban deleted accounts


@app.on_message(filters.command(["ban_ghosts", "\u062d\u0638\u0631_\u0627\u0644\u0645\u062d\u0630\u0648\u0641\u064a\u0646"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def ban_deleted_accounts(_, message: Message):
    chat_id = message.chat.id
    deleted_users = []
    banned_users = 0
    m = await message.reply(tr("FINDING_GHOSTS"))

    async for i in app.get_chat_members(chat_id):
        if i.user.is_deleted:
            deleted_users.append(i.user.id)
    if len(deleted_users) > 0:
        for deleted_user in deleted_users:
            try:
                await message.chat.ban_member(deleted_user)
            except Exception:
                pass
            banned_users += 1
        await m.edit(tr("BANNED_GHOSTS", count=banned_users))
    else:
        await m.edit(tr("NO_GHOSTS"))


@app.on_message(
    filters.command(["warn", "dwarn", "\u062a\u062d\u0630\u064a\u0631", "\u062a\u062d\u0630\u064a\u0631_\u062d\u0630\u0641"])
    & ~filters.private
)
@adminsOnly("can_restrict_members")
async def warn_user(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    chat_id = message.chat.id
    if not user_id:
        return await message.reply_text(tr("USER_NOT_FOUND"))
    if user_id == BOT_ID:
        return await message.reply_text(tr("CANT_WARN_SELF"))
    if user_id in SUDOERS:
        return await message.reply_text(tr("WARN_SUDO"))
    if user_id in (await list_admins(chat_id)):
        return await message.reply_text(tr("CANT_WARN_ADMIN"))
    user, warns = await asyncio.gather(
        app.get_users(user_id),
        get_warn(chat_id, await int_to_alpha(user_id)),
    )
    mention = user.mention
    keyboard = ikb({tr("BTN_REMOVE_WARN"): f"unwarn_{user_id}"})
    if warns:
        warns = warns["warns"]
    else:
        warns = 0
    if message.command[0] in ("dwarn", "\u062a\u062d\u0630\u064a\u0631_\u062d\u0630\u0641"):
        await message.reply_to_message.delete()
    if warns >= 2:
        await message.chat.ban_member(user_id)
        await message.reply_text(tr("WARNS_EXCEEDED", mention=mention))
        await remove_warns(chat_id, await int_to_alpha(user_id))
    else:
        warn = {"warns": warns + 1}
        by = message.from_user.mention if message.from_user else tr("ANON")
        msg = tr(
            "WARN_MSG",
            mention=mention,
            by=by,
            reason=reason or tr("NO_REASON"),
            count=warns + 1,
        )
        replied_message = message.reply_to_message
        if replied_message:
            message = replied_message
        await message.reply_text(msg, reply_markup=keyboard)
        await add_warn(chat_id, await int_to_alpha(user_id), warn)


@app.on_callback_query(filters.regex("unwarn_"))
async def remove_warning(_, cq: CallbackQuery):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            tr("CB_NO_PERMS", permission=permission),
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if not warns or warns == 0:
        return await cq.answer(tr("NO_WARNINGS_CB"))
    warn = {"warns": warns - 1}
    await add_warn(chat_id, await int_to_alpha(user_id), warn)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += tr("WARN_REMOVED_BY", mention=from_user.mention)
    await cq.message.edit(text)


# Rmwarns


@app.on_message(filters.command(["rmwarns", "\u0645\u0633\u062d_\u0627\u0644\u062a\u062d\u0630\u064a\u0631\u0627\u062a"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def remove_warnings(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text(tr("RMWARNS_REPLY"))
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    chat_id = message.chat.id
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if warns == 0 or not warns:
        await message.reply_text(tr("NO_WARNINGS", mention=mention))
    else:
        await remove_warns(chat_id, await int_to_alpha(user_id))
        await message.reply_text(tr("WARNS_REMOVED", mention=mention))


# Warns


@app.on_message(filters.command(["warns", "\u0627\u0644\u062a\u062d\u0630\u064a\u0631\u0627\u062a"]) & ~filters.private)
@capture_err
async def check_warns(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text(tr("USER_NOT_FOUND"))
    warns = await get_warn(message.chat.id, await int_to_alpha(user_id))
    mention = (await app.get_users(user_id)).mention
    if warns:
        warns = warns["warns"]
    else:
        return await message.reply_text(tr("NO_WARNINGS", mention=mention))
    return await message.reply_text(tr("HAS_WARNINGS", mention=mention, warns=warns))


# Report


@app.on_message(
    (
        filters.command(["report", "\u062a\u0628\u0644\u064a\u063a"])
        | filters.command(["admins", "admin"], prefixes="@")
    )
    & ~filters.private
)
@capture_err
async def report_user(_, message):
    if len(message.text.split()) <= 1 and not message.reply_to_message:
        return await message.reply_text(tr("REPORT_REPLY"))

    reply = message.reply_to_message if message.reply_to_message else message
    reply_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
    user_id = (
        message.from_user.id if message.from_user else message.sender_chat.id
    )

    list_of_admins = await list_admins(message.chat.id)
    linked_chat = (await app.get_chat(message.chat.id)).linked_chat
    if linked_chat is not None:
        if (
            reply_id in list_of_admins
            or reply_id == message.chat.id
            or reply_id == linked_chat.id
        ):
            return await message.reply_text(tr("REPLY_IS_ADMIN"))
    else:
        if reply_id in list_of_admins or reply_id == message.chat.id:
            return await message.reply_text(tr("REPLY_IS_ADMIN"))

    user_mention = (
        reply.from_user.mention if reply.from_user else reply.sender_chat.title
    )
    text = tr("REPORTED", mention=user_mention)
    admin_data = [
        i
        async for i in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]  # will it give floods ???
    for admin in admin_data:
        if admin.user.is_bot or admin.user.is_deleted:
            # return bots or deleted admins
            continue
        text += f"[\u2063](tg://user?id={admin.user.id})"

    await reply.reply_text(text)


@app.on_message(filters.command(["invite", "\u062f\u0639\u0648\u0629"]))
@adminsOnly("can_invite_users")
async def invite(_, message):
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        link = (await app.get_chat(message.chat.id)).invite_link
        if not link:
            link = await app.export_chat_invite_link(message.chat.id)
        text = tr("INVITE_LINK", link=link)
        if message.reply_to_message:
            await message.reply_to_message.reply_text(
                text, disable_web_page_preview=True
            )
        else:
            await message.reply_text(text, disable_web_page_preview=True)
