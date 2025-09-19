import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
import os
from dotenv import load_dotenv
import handlers
import errors
from aiogram_i18n import I18nContext, LazyProxy, I18nMiddleware, LazyFilter
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from storages.psql.base import close_db_pool, create_db_pool
from functools import partial
from aiogram.fsm.storage.redis import RedisStorage
import msgspec
from middlewares.check_user_middleware import CheckUserMiddleware
from aiogram.fsm.storage.base import DefaultKeyBuilder
from redis.asyncio import Redis

load_dotenv()





async def main():

    storage = RedisStorage(
        redis=Redis.from_url(os.getenv("REDIS_URL")),
        key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        json_loads=msgspec.json.decode,
        json_dumps=partial(lambda obj: str(msgspec.json.encode(obj), encoding="utf-8")),
    )
    dp = Dispatcher(
        storage=storage,
        redis=storage.redis,
    )
    engine, db_pool = await create_db_pool()

    dp.workflow_data.update(
        {"db_pool": db_pool, "db_pool_closer": partial(close_db_pool, engine)},
    )

    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(
            path="locales/{locale}/LC_MESSAGES"
        ),
        default_locale="ru",
    )

    dp.include_routers(handlers.router, errors.router)
    i18n_middleware.setup(dispatcher=dp)
    dp.update.outer_middleware(CheckUserMiddleware())

    bot = Bot(os.getenv("TOKEN"), default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ))

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
    #CREATE EXTENSION IF NOT EXISTS citext;