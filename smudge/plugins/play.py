
from os import path

from pyrogram import Client
from pyrogram.types import Message, Voice
from pytgcalls.types.input_stream import InputAudioStream
from Client import callsmusic, queues

import converter
from youtube import youtube

from config import BOT_NAME as bn, DURATION_LIMIT, UPDATES_CHANNEL, AUD_IMG, QUE_IMG, GROUP_SUPPORT
from helpers.filters import command, other_filters
from helpers.decorators import errors
from helpers.errors import DurationLimitError
from helpers.gets import get_url, get_file_name
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


@Client.on_message(command("audio") & other_filters)
@errors
async def stream(_, message: Message):

    lel = await m.reply_text(await tld(m.chat.id, "searchinh_audio"))
    sender_id = message.from_user.id
    sender_name = message.from_user.first_name

    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="✨ ɢʀᴏᴜᴘ",
                        url=f"https://t.me/SHIZUKA_VC_SUPPORT"),
                    InlineKeyboardButton(
                        text="⚡ ᴄʜᴀɴɴᴇʟ",
                        url=f"https://t.me/Pratheek_Bots"),
                ]
            ]
        )

    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    url = get_url(message)

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"Video Longer Than {DURATION_LIMIT} Minute(𝐬) Are Not Allowed To Play!"
            )

        file_name = get_file_name(audio)
        file_path = await converter.convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name)) else file_name
        )
    elif url:
        file_path = await converter.convert(youtube.download(url))
    else:
        return await lel.edit_text("! You Did Not Give Me An Audio File Or Yt Link To Stream !")
    ACTV_CALLS = []
    for x in callsmusic.pytgcalls.active_calls:
        ACTV_CALLS.append(int(x.chat_id))    
    if int(message.chat.id) in ACTV_CALLS:
        position = await queues.put(message.chat.id, file=file_path)
        await message.reply_photo(
        photo=f"{QUE_IMG}",
        reply_markup=keyboard,
        caption=f"#⃣ Yᴏᴜʀ Rᴇǫᴜᴇsᴛᴇᴅ Sᴏɴɢ Wᴀs Aᴅᴅᴇᴅ Tᴏ  *Qᴜᴇᴜᴇ* Aᴛ Pᴏsɪᴛɪᴏɴ {position}!\n\n⚡ __𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬 𝗣𝗥𝗔𝗧𝗛𝗘𝗘𝗞 𝗔.𝗜__") 
        return await lel.delete()
    else:
        await callsmusic.pytgcalls.join_group_call(
                message.chat.id, 
                input_stream(
                    InputAudioStream(
                        file_path,
                    ),
                ),
                stream_type=StreamType().local_stream,
            ) 
        costumer = message.from_user.mention
        await message.reply_photo(
        photo=f"{AUD_IMG}",
        reply_markup=keyboard,
        caption=f"🎧 **Now Playing** Song Requested By {costumer}!\n\n⚡ __Pᴏᴡᴇʀᴇᴅ Bʏ Pʀᴀᴛʜᴇᴇᴋ Bᴏᴛs__"
        )
        return await lel.delete()
