import importlib
import re

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from smudge.locales.strings import tld
from smudge.plugins import all_plugins
from smudge.utils.help_menu import help_buttons
from smudge.database import set_db_lang

from typing import Union

HELP = {}

for plugin in all_plugins:
    imported_plugin = importlib.import_module("smudge.plugins." + plugin)
    if hasattr(imported_plugin, "plugin_help") and hasattr(
        imported_plugin, "plugin_name"
    ):
        plugin_name = imported_plugin.plugin_name
        plugin_help = imported_plugin.plugin_help
        HELP.update({plugin: [{"name": plugin_name, "help": plugin_help}]})


@Client.on_message(filters.command("start", prefixes="/"))
@Client.on_callback_query(filters.regex(r"start"))
async def start_command(c: Client, m: Union[Message, CallbackQuery]):
    if isinstance(m, CallbackQuery):
        chat_id = m.message.chat.id
        chat_type = m.message.chat.type
        reply_text = m.edit_message_text
    else:
        chat_id = m.chat.id
        chat_type = m.chat.type
        reply_text = m.reply_text

    me = await c.get_me()
    if chat_type == "private":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=(await tld(chat_id, "main_start_btn_lang")),
                        callback_data="setchatlang",
                    ),
                    InlineKeyboardButton(
                        text=(await tld(chat_id, "main_start_btn_help")),
                        callback_data="menu",
                    ),
                ],
            ]
        )
        text = (await tld(chat_id, "start_message_private")).format(
            m.from_user.first_name
        )
        await reply_text(text, reply_markup=keyboard, disable_web_page_preview=True)
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Start", url=f"https://t.me/{me.username}?start=start"
                    )
                ]
            ]
        )
        text = await tld(m.chat.id, "start_message")
        await reply_text(text, reply_markup=keyboard, disable_web_page_preview=True)


@Client.on_callback_query(filters.regex("menu"))
async def button(c: Client, cq: CallbackQuery):
    keyboard = InlineKeyboardMarkup(await help_buttons(cq, HELP))
    text = await tld(cq.message.chat.id, "main_help_text")
    await cq.edit_message_text(text, reply_markup=keyboard)


async def help_menu(c, cq, text):
    keyboard = [
        [
            InlineKeyboardButton(
                await tld(cq.message.chat.id, "main_btn_back"), callback_data="menu"
            )
        ]
    ]
    text = (await tld(cq.message.chat.id, "avaliable_commands")).format(text)
    await cq.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query(filters.regex(pattern=".*help_plugin.*"))
async def but(c: Client, cq: CallbackQuery):
    plug_match = re.match(r"help_plugin\((.+?)\)", cq.data)
    plug = plug_match.group(1)
    text = await tld(cq.message.chat.id, str(HELP[plug][0]["help"]))
    await help_menu(c, cq, text)


@Client.on_callback_query(filters.regex(r"en-US"))
async def english(c: Client, m: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=(await tld(m.message.chat.id, "main_btn_back")),
                    callback_data="setchatlang",
                )
            ],
        ]
    )
    if m.message.chat.type == "private":
        await set_db_lang(m.from_user.id, "en-US")
    elif m.message.chat.type == "supergroup" or "group":
        await set_db_lang(m.message.chat.id, "en-US")
    text = await tld(m.message.chat.id, "lang_save")
    await m.edit_message_text(text, reply_markup=keyboard)


@Client.on_callback_query(filters.regex(r"pt-BR"))
async def portuguese(c: Client, m: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=(await tld(m.message.chat.id, "main_btn_back")),
                    callback_data="setchatlang",
                )
            ],
        ]
    )
    if m.message.chat.type == "private":
        await set_db_lang(m.from_user.id, "pt-BR")
    elif m.message.chat.type == "supergroup" or "group":
        await set_db_lang(m.message.chat.id, "pt-BR")
    text = await tld(m.message.chat.id, "lang_save")
    await m.edit_message_text(text, reply_markup=keyboard)


@Client.on_message(filters.command(["setlang"]))
@Client.on_callback_query(filters.regex(r"setchatlang"))
async def setlang(c: Client, cq: Union[Message, CallbackQuery]):
    if isinstance(cq, CallbackQuery):
        chat_id = cq.message.chat.id
        chat_type = cq.message.chat.type
        reply_text = cq.edit_message_text
    else:
        chat_id = cq.chat.id
        chat_type = cq.chat.type
        reply_text = cq.reply_text

    if chat_type == "private":
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🇧🇷 PT-BR (Português)", callback_data="pt-BR"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🇺🇸 EN-US (American English)", callback_data="en-US"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=(await tld(chat_id, "main_btn_back")),
                        callback_data="start_command",
                    )
                ],
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🇧🇷 PT-BR (Português)", callback_data="pt-BR"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🇺🇸 EN-US (American English)", callback_data="en-US"
                    )
                ],
            ]
        )
    text = await tld(chat_id, "main_select_lang")
    await reply_text(text, reply_markup=keyboard)
    return


@Client.on_message(filters.new_chat_members)
async def logging(c: Client, m: Message):
    bot = await c.get_me()
    bot_id = bot.id
    if bot_id in [z.id for z in m.new_chat_members]:
        await c.send_message(
            chat_id=m.chat.id,
            text=(
                "/ᐠ. ｡.ᐟ\ᵐᵉᵒʷ  Olá, obrigado por me adicionar aqui!\n"
                "Não se esqueça de <b>mudar meu idioma usando /setlang</b>\n\n"
                "/ᐠ. ｡.ᐟ\ᵐᵉᵒʷ  Hi, thanks for adding me here!\n"
                "Don't forget to <b>change my language using /setlang</b>\n"
            ),
            disable_notification=True,
        )
