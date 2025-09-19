from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram_i18n import I18nContext

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, i18n: I18nContext):
    await message.answer(i18n.get("start"))
