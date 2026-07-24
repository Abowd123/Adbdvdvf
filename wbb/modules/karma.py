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
import re

from pyrogram import filters

from wbb import app
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly
from wbb.core.sections import section
from wbb.utils.dbfunctions import (
    alpha_to_int,
    get_karma,
    get_karmas,
    int_to_alpha,
    is_karma_on,
    karma_off,
    karma_on,
    update_karma,
)
from wbb.utils.filter_groups import karma_negative_group, karma_positive_group
from wbb.utils.functions import get_specific_usernames
from wbb.utils.strings import tr

__MODULE__ = tr("KARMA_MODULE")
__HELP__ = tr("KARMA_HELP")

regex_upvote = r"^(\++|\+1|thx|tnx|tq|ty|thankyou|thank you|thanx|thanks|pro|cool|good|agree|👍|\++ .+)$"
regex_downvote = r"^(-+|-1|not cool|disagree|worst|bad|👎|-+ .+)$"


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_upvote, re.IGNORECASE)
    & ~filters.via_bot
    & ~filters.bot,
    group=karma_positive_group,
)
@capture_err
async def upvote(_, message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user:
        return
    if not message.from_user:
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        return
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma + 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    else:
        karma = 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        tr("KARMA_INCREMENTED", mention=user_mention, karma=karma)
    )


@app.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_downvote, re.IGNORECASE)
    & ~filters.via_bot
    & ~filters.bot,
    group=karma_negative_group,
)
@capture_err
async def downvote(_, message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user:
        return
    if not message.from_user:
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma - 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    else:
        karma = 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)

    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma - 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    else:
        karma = 1
        new_karma = {"karma": karma}
        await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        tr("KARMA_DECREMENTED", mention=user_mention, karma=karma)
    )


@app.on_message(filters.command(["karma", "كارما"]) & filters.group)
@capture_err
async def command_karma(_, message):
    chat_id = message.chat.id
    
    if not message.reply_to_message:
        m = await message.reply_text(tr("KARMA_ANALYZING"))
        
        try:
            karma = await get_karmas(chat_id)
            if not karma:
                return await m.edit(tr("KARMA_NONE_DB"))
            
            karma_dicc = {}
            for i in karma:
                try:
                    user_id = await alpha_to_int(i)
                    user_karma = karma[i]["karma"]
                    karma_dicc[str(user_id)] = user_karma
                except Exception as e:
                    continue
            
            if not karma_dicc:
                return await m.edit(tr("KARMA_NONE_DB"))
            
            karma_sorted = sorted(
                karma_dicc.items(),
                key=lambda item: item[1],
                reverse=True
            )
            
            try:
                user_ids_needed = [int(uid) for uid, _ in karma_sorted]
                userdb = await get_specific_usernames(app, user_ids_needed)
            except Exception as e:
                return await m.edit(tr("KARMA_ERR_USERDATA", err=str(e)))
            
            karma_display = {}
            limit = 0
            
            for user_id_str, karma_count in karma_sorted:
                if limit >= 15:
                    break
                
                user_id_int = int(user_id_str)
                
                if user_id_int not in userdb:
                    continue
                
                username = userdb[user_id_int]
                karma_display[f"@{username}"] = [f"**{karma_count}**"]
                limit += 1
            
            if not karma_display:
                return await m.edit(tr("KARMA_NO_VALID"))
            
            msg = tr("KARMA_LIST_HEADER", chat=message.chat.title)
            await m.edit(section(msg, karma_display))
            
        except Exception as e:
            await m.edit(tr("KARMA_ERR_GENERIC", err=str(e)))
            rais
    
    else:
        if not message.reply_to_message.from_user:
            return await message.reply(tr("KARMA_ANON"))
        
        user_id = message.reply_to_message.from_user.id
        try:
            karma = await get_karma(chat_id, await int_to_alpha(user_id))
            karma_value = karma["karma"] if karma else 0
            await message.reply_text(tr("KARMA_TOTAL_POINTS", points=karma_value))
        except Exception as e:
            await message.reply_text(tr("KARMA_ERR_FETCH", err=str(e)))



@app.on_message(filters.command(["karma_toggle", "تبديل_الكارما"]) & ~filters.private)
@adminsOnly("can_change_info")
async def captcha_state(_, message):
    usage = tr("KARMA_TOGGLE_USAGE")
    if len(message.command) != 2:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state in ("enable", "تفعيل"):
        await karma_on(chat_id)
        await message.reply_text(tr("KARMA_ENABLED"))
    elif state in ("disable", "تعطيل"):
        await karma_off(chat_id)
        await message.reply_text(tr("KARMA_DISABLED"))
    else:
        await message.reply_text(usage)
