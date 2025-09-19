from . import comands
from aiogram import Router


router = Router()

router.include_routers(
    comands.router,
)
