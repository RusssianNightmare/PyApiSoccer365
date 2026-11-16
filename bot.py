from telegram.ext import Updater, CommandHandler, ConversationHandler, Filters, MessageHandler
from pytz import timezone
from datetime import time

import jobs
import handlers
import config


def main():
    bot = Updater(config.API_TOKEN_BOT)

    dp = bot.dispatcher
    dp.add_handler(CommandHandler('start', handlers.greet_user))

    conv = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Ближайшая дата матча)$'), handlers.choose_league),
            # MessageHandler(Filters.regex('^(Подписаться на рассылку)$'), handlers.new_func),
        ],
        states={
            'choose_team': [MessageHandler(Filters.text, handlers.choose_team)],
            'show_shedule': [MessageHandler(Filters.text, handlers.show_shedule)],
            # 'new_step': [MessageHandler(Filters.text, handlers.show_shedule)]

        },
        fallbacks=[],
        # MessageHandler(Filters.regex('^(Связаться с админом)$'), handlers.show_error_message),
        # ],
    )
    dp.add_handler(conv)
    sub_conv = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^(Подписаться на рассылку)$'), handlers.start_subscription),
        ],
        states={
            'choose_league_sub': [MessageHandler(Filters.text, handlers.choose_league_sub)],
            'choose_team_sub': [MessageHandler(Filters.text, handlers.choose_team_sub)],
        },
        fallbacks=[],
    )
    dp.add_handler(sub_conv)

    jq = bot.job_queue

    # jq.run_daily(jobs.delete_old_matches, time=time(3, 0, tzinfo=timezone('Europe/Moscow')))
    # создаем задачу на обновление расписания
    jq.run_once(jobs.delete_old_matches, when=1)

    jq.run_daily(
        jobs.update_schedule,
        time=time(3, 0, tzinfo=timezone('Europe/Moscow'))
    )
    jq.run_daily(jobs.send_matches_reminders, time=time(10, 0, tzinfo=timezone('Europe/Moscow')))

    print('бот запущен!')
    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()
