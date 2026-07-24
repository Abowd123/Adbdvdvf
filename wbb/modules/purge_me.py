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

from pyrogram import filters
from pyrogram.types import Message

from wbb import SUDOERS, USERBOT_ID, USERBOT_PREFIX, app2, eor, log, telegraph
from wbb.utils.strings import tr

__MODULE__ = tr("UBOT_MODULE")
TEXT = tr("UBOT_TEXT")
log.info("Pasting userbot commands on telegraph")

__HELP__ = f"""**الأوامر:** {telegraph.create_page(
    "Userbot Commands",
    html_content=TEXT,
)['url']}"""

log.info("Done pasting userbot commands on telegraph")


@app2.on_message(
    filters.command("help", prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & filters.user(USERBOT_ID)
)
async def get_help(_, message: Message):
    await eor(
        message,
        text=__HELP__,
        disable_web_page_preview=True,
    )


@app2.on_message(
    filters.command(["purgeme", "purge_me"], prefixes=USERBOT_PREFIX)
    & ~filters.forwarded
    & ~filters.via_bot
    & filters.user(USERBOT_ID)
)
async def purge_me_func(_, message: Message):
    if len(message.command) != 2:
        return await message.delete()

    n = message.text.split(None, 1)[1].strip()
    if not n.isnumeric():
        return await eor(message, text=tr("UBOT_INVALID_ARGS"))

    n = int(n)

    if n < 1:
        return await eor(message, text=tr("UBOT_NEED_POSITIVE"))

    chat_id = message.chat.id

    message_ids = [
        m.id
        async for m in app2.search_messages(
            chat_id,
            from_user=int(USERBOT_ID),
            limit=n,
        )
    ]

    if not message_ids:
        return await eor(message, text=tr("UBOT_NO_MESSAGES"))

    # A list containing lists of 100 message chunks
    # because we can't delete more than 100 messages at once,
    # we have to do it in chunks of 100, i'll choose 99 just
    # to be safe.
    to_delete = [
        message_ids[i : i + 99] for i in range(0, len(message_ids), 99)
    ]

    for hundred_messages_or_less in to_delete:
        await app2.delete_messages(
            chat_id=chat_id,
            message_ids=hundred_messages_or_less,
            revoke=True,
        )
