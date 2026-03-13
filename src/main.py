# Copyright (C) 2026 Oktapiancaw
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import logging

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.configs import config, project_meta
from src.utils.handler import (
    AMOUNT,
    BILLING,
    CATEGORY,
    DESCRIPTION,
    TYPE,
    add_billing,
    add_category,
    help_command,
    log_amount,
    log_billing,
    log_cancel,
    log_category,
    log_description,
    log_start,
    log_type,
    report_daily,
    report_monthly,
    report_weekly,
    start_command,
)

LOGGER = logging.getLogger(project_meta.name)


def main():
    # Base Commands
    application = Application.builder().token(config.telegram_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))

    # CRUD Commands
    application.add_handler(CommandHandler("addcat", add_category))
    application.add_handler(CommandHandler("addbill", add_billing))

    # Reporting Commands
    application.add_handler(CommandHandler("daily", report_daily))
    application.add_handler(CommandHandler("weekly", report_weekly))
    application.add_handler(CommandHandler("monthly", report_monthly))

    # Transaction Conversation Handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("log", log_start)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, log_amount)],
            TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, log_type)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, log_category)],
            BILLING: [MessageHandler(filters.TEXT & ~filters.COMMAND, log_billing)],
            DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, log_description)
            ],
        },
        fallbacks=[CommandHandler("cancel", log_cancel)],
    )
    application.add_handler(conv_handler)

    # Start polling
    LOGGER.info("Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
