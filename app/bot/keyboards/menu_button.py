from aiogram.types import BotCommand
from app.bot.enums.roles import UserRole


def get_main_menu_commands(i18n: dict[str, str], user_role: UserRole) -> list[BotCommand]:
    main_menu_commands = [
        BotCommand(command='/start', description=i18n.get('/start_description')),
        BotCommand(command='/lang', description=i18n.get('/lang_description')),
        BotCommand(command='/help', description='/help_description'),
    ]

    if user_role == UserRole.ADMIN:
        main_menu_commands.extend((
            BotCommand(command='/ban', description=i18n.get('/ban_description')),
            BotCommand(command='/unban', description=i18n.get('/unban_description')),
            BotCommand(command='/statistics', description=i18n.get('/statistics_description')),
        ))

    return main_menu_commands