"""Russian localization for VPN Bot"""

MESSAGES = {
    # Welcome and basic messages
    "welcome": (
        "🎉 Добро пожаловать в <b>Макс Спид VPN</b>!\n\n"
        "🚀 Самый дешёвый и надежный VPN для русскоязычной аудитории!\n\n"
        "🔒 Наши преимущества:\n"
        "• 🇷🇺 Ловим даже на парковке\n"
        "• ⚡ Высокая скорость до 1 Гбит/с\n"
        "• 🌍 Серверы в 3 странах\n"
        "• 🔐 Военное шифрование AES-256\n"
        "• 📱 Поддержка всех устройств\n"
        "• 🛡️ Защита от утечек DNS\n"
        "• 🎯 Обход любых блокировок\n"
        "• 💬 Техподдержка 24/7\n\n"
         "🎁 Специальные цены для СВОих!\n\n"
        "Выберите действие:"
    ),
    "welcome_back": (
        "👋 <b>С возвращением, {name}!</b>\n\n"
        #"🔥 Что нового:\n"
        #"• Добавлены новые серверы в Европе\n"
        #"• Улучшена скорость соединения\n"
        #"• Обновлена реферальная программа\n\n"
        "Выберите действие:"
    ),
    "help": (
        "📖 <b>Помощь по использованию бота:</b>\n\n"
        "🛒 Покупка speed:\n"
        "• Выберите время для передачи Государственной тайны\n"
        "• Оплатите удобным способом\n"
        "• Получите конфигурацию автоматически\n"
        "• Откройте ссылку и получите подробный чертеж орешника\n\n"
        #"📱 Настройка:\n"
        #"• Скачайте приложение WireGuard\n"
        #"• Отсканируйте QR-код или импортируйте файл\n"
        #"• Наслаждайтесь безопасным интернетом!\n\n"
        "🎁 Реферальная программа:\n"
        "• Приглашайте друзей по своей ссылке\n"
        "• Получайте 10% с каждой их покупки\n"
        "• Выводите заработанные деньги\n\n"
        "💬 Поддержка работает круглосуточно!"
    ),
    # Subscription plans
    "plans_header": "🎯 Выберите свой идеальный план:\n\n",
    "plan_template": (
        "{emoji} {name} {popular_badge}\n"
        "💰 {price} ₽ ({price_per_month} ₽/мес)\n"
        "⏰ {duration} дней\n"
        "📝 {description}\n"
        "💎 {savings}\n\n"
    ),
    "popular_badge": "🔥 ПОПУЛЯРНЫЙ",
    "best_deal_badge": "💎 ЛУЧШЕЕ ПРЕДЛОЖЕНИЕ",
    "choose_plan": "👆 Выборите плана захвата Польши:",
    # Payment
    "payment_methods": (
        '💳 Способы оплаты для плана "{plan_name}":\n\n'
        "💰 Сумма к оплате: {amount} ₽\n"
        "⏰ Срок действия: {duration} дней\n\n"
        "Выберите удобный способ оплаты:"
    ),
    "payment_created": (
        "✅ Счет успешно создан!\n\n"
        "📦 План: {plan_name}\n"
        "💰 Сумма: {amount} ₽\n"
        "🔗 Ссылка: {payment_url}\n\n"
        "⏰ Счет действителен 15 минут\n"
        "🎯 После оплаты VPN активируется мгновенно!\n\n"
        "💡 Совет: сохраните эту ссылку, чтобы не потерять"
    ),
    "payment_success": (
        "🎉 Поздравляем! Оплата прошла успешно!\n\n"
        "✅ СВОя VPN подписка активирована\n"
        "📦 План: {plan_name}\n"
        "📅 Действует до: {end_date}\n"
        "🌍 Сервер: {server_location}\n\n"
        "📱 Ваша инъекция speed vpn готова к использованию!"
    ),
    "payment_failed": (
        "❌ Ошибка при обработке платежа\n\n"
        "Возможные причины:\n"
        "• Недостаточно дозы на счете\n"
        "• Истек срок действия карты\n"
        "• Технические проблемы\n\n"
        "• Был обнаружен иноагент\n"
        "• Вы не облизали Байкал\n"
        "💬 Обратитесь в РКН или попробуйте другой способ передачи ГосТайны"
    ),
    "payment_pending": (
        "⏳ Ожидаем поступления ссылки в Сибирь...\n\n"
        "💰 Сумма: {amount} ₽\n"
        "🔗 Ссылка: {payment_url}\n\n"
        "⏰ Осталось времени: {time_left} мин\n\n"
        "🔄 Проверить статус платежа"
    ),
    # Profile
    "profile_info": (
        "👤 Личное дело\n\n"
        "🆔 Досье: {user_id}\n"
        "👤 {full_name}\n"
        "📅 Со СВОими: {created_at}\n"
        "💰 Потрачено всего: {total_spent} ₽\n\n"
        "📱 Текущая подписка:\n"
        "{subscription_info}\n\n"
        "🎁 Путевка в Сибирь для друга: <code>{referral_code}</code>"
    ),
    "subscription_active": (
        "✅ АКТИВНА\n"
        "📦 План: {plan_name}\n"
        "📅 До: {end_date}\n"
        "⏰ Осталось: {time_remaining}\n"
        "🌍 Сервер: {server_location}"
    ),
    "subscription_inactive": "❌ Подписка не активна\n\n🛒 Купите VPN для защиты своего интернета!",
    "subscription_expired": (
        "⏰ Подписка истекла {days_ago} дней назад\n\n"
        "🔄 Продлите подписку со скидкой 20%!"
    ),
    # VPN Configuration
    "vpn_config_info": (
        "📱 Инструкция по подключению:\n\n"
        "1️⃣ Скачайте приложение WireGuard:\n"
        "• Android: Google Play\n"
        "• iOS: App Store\n"
        "• Windows/Mac: wireguard.com\n\n"
        "2️⃣ Добавьте конфигурацию:\n"
        "• Нажмите '+' в приложении\n"
        "• Выберите 'Создать из QR-кода'\n"
        "• Отсканируйте QR-код ниже\n\n"
        "3️⃣ Подключитесь и наслаждайтесь!"
    ),
    "config_download": "📁 Скачать файл конфигурации",
    "config_qr": "📱 QR-код для быстрой настройки:",
    # Referral system
    "referral_info": (
        "🎁 Реферальная программа\n\n"
        "💰 Ваша статистика:\n"
        "👥 Приглашено друзей: {referral_count}\n"
        "💵 Заработано: {earned_amount} ₽\n"
        "💳 Доступно к выводу: {available_balance} ₽\n\n"
        "🔗 Ваша реферальная ссылка:\n"
        "<code>{referral_link}</code>\n\n"
        "💡 Условия программы:\n"
        "• 10% с каждой покупки друга\n"
        "• Минимальная сумма вывода: {min_payout} ₽\n"
        "• Вывод на карту или кошелек\n\n"
        "📢 Поделитесь ссылкой в соцсетях!"
    ),
    "referral_bonus": (
        "🎉 Поздравляем!\n\n"
        "💰 Вы получили {amount} ₽ за приглашение друга!\n"
        "👤 Пользователь: {friend_name}\n\n"
        "💳 Баланс пополнен автоматически"
    ),
    "referral_payout_request": (
        "💳 Заявка на вывод средств\n\n"
        "💰 Сумма: {amount} ₽\n"
        "📝 Укажите реквизиты для выплаты:\n"
        "(номер карты, кошелек и т.д.)"
    ),
    # Support
    "support_info": (
        "💬 <b>Техническая поддержка</b>\n\n"
        #"🕐 Работаем круглосуточно, без выходных\n"
        #"⚡ Среднее время ответа: 5 минут\n\n"
        "📱 Telegram: @{support_username} (отвечает человек)\n"
        #"• Email: support@vpnbot.ru\n"
        #"• Чат в боте (кнопка ниже)\n\n"
        #"🆘 Частые проблемы:\n"
        #"• Не подключается VPN\n"
        #"• Медленная скорость\n"
        #"• Проблемы с оплатой\n"
        #"• Настройка на устройствах\n\n"
        "📝 Опишите проблему подробно для быстрого решения!"
    ),
    "support_chat": "💬 Написать в поддержку",
    "support_faq": "❓ Часто задаваемые вопросы",
    # Admin messages
    "admin_panel": (
        "🔧 Панель администратора\n\n"
        "📊 Статистика:\n"
        "👥 Всего пользователей: {total_users}\n"
        "✅ Активных подписок: {active_subscriptions}\n"
        "💰 Доходы сегодня: {daily_revenue} ₽\n"
        "💵 Доходы за месяц: {monthly_revenue} ₽\n"
        "🔑 Доступных ключей: {available_keys}\n"
        "🆕 Новых пользователей: {new_users}\n\n"
        "⏰ Последнее обновление: {last_update}"
    ),
    "admin_not_authorized": "❌ Доступ запрещен. У вас нет прав администратора.",
    "admin_users_list": "👥 Управление пользователями",
    "admin_keys_management": "🔑 Управление VPN ключами",
    "admin_broadcast": "📢 Массовая рассылка",
    "admin_stats": "📊 Подробная статистика",
    # Broadcast
    "broadcast_start": (
        "📢 Массовая рассылка\n\n"
        "👥 Всего пользователей: {total_users}\n"
        "✅ Активных: {active_users}\n\n"
        "📝 Отправьте сообщение для рассылки:"
    ),
    "broadcast_confirm": (
        "📢 Подтвердите рассылку\n\n"
        "👥 Получателей: {recipients}\n"
        "📝 Сообщение:\n\n{message}\n\n"
        "⚠️ Отправить всем пользователям?"
    ),
    "broadcast_success": "✅ Рассылка завершена! Отправлено {sent} сообщений из {total}.",
    # Errors and warnings
    "error_general": "❌ Что-то пошло не так. Попробуйте позже или обратитесь в поддержку.",
    "error_no_subscription": "❌ У вас нет активной подписки. Купите VPN для продолжения.",
    "error_payment_timeout": "⏰ Время оплаты истекло. Создайте новый счет для покупки.",
    "error_insufficient_keys": "❌ Временно нет доступных VPN ключей. Обратитесь в поддержку.",
    "error_invalid_plan": "❌ Неверный тарифный план. Выберите план из списка.",
    "error_payment_failed": "❌ Ошибка создания платежа. Попробуйте другой способ оплаты.",
    "warning_subscription_expires": (
        "⚠️ Внимание!\n\n"
        "Ваша подписка истекает через {days} дней.\n"
        "Продлите сейчас со скидкой 15%!"
    ),
    # Success messages
    "success_config_sent": "✅ Конфигурация отправлена! Проверьте файл и QR-код выше.",
    "success_subscription_extended": "✅ Подписка успешно продлена до {end_date}!",
    "success_referral_registered": "✅ Новый реферал зарегистрирован! Вы получите бонус после его первой покупки.",
    # Buttons
    "btn_buy_vpn": "🛒 Купить VPN",
    "btn_my_profile": "👤 Мой профиль",
    "btn_help": "❓ Помощь",
    "btn_support": "💬 Поддержка",
    "btn_referral": "🎁 Рефералы",
    "btn_config": "📱 Моя конфигурация",
    # Plan buttons with dynamic pricing
    "btn_plan_1_month": "🥉 1 месяц - {price} ₽",
    "btn_plan_3_months": "🥈 3 месяца - {price} ₽ 🔥",
    "btn_plan_6_months": "🥇 6 месяцев - {price} ₽ 💎",
    "btn_plan_12_months": "💰 1 год - {price} ₽ 👑",
    # Payment buttons
    "btn_yoomoney": "💳 ЮMoney (карты, кошельки)",
    "btn_qiwi": "🥝 QIWI (кошелек, карты)",
    "btn_crypto": "₿ Криптовалюты (BTC, ETH, USDT)",
    "btn_check_payment": "🔄 Проверить платеж",
    "btn_new_payment": "💳 Создать новый счет",
    # Navigation buttons
    "btn_back": "⬅️ Назад",
    "btn_main_menu": "🏠 Главное меню",
    "btn_cancel": "❌ Отмена",
    "btn_confirm": "✅ Подтвердить",
    "btn_download": "📁 Скачать",
    "btn_share": "📤 Поделиться",
    # Admin buttons
    "btn_admin_users": "👥 Пользователи",
    "btn_admin_keys": "🔑 VPN ключи",
    "btn_admin_stats": "📊 Статистика",
    "btn_admin_broadcast": "📢 Рассылка",
    "btn_admin_settings": "⚙️ Настройки",
    "btn_admin_logs": "📋 Логи",
    # Time periods
    "today": "сегодня",
    "yesterday": "вчера",
    "this_week": "на этой неделе",
    "this_month": "в этом месяце",
    "days_ago": "{days} дней назад",
    "hours_ago": "{hours} часов назад",
    "minutes_ago": "{minutes} минут назад",
}


IMAGES = {
    # Keys should match MESSAGES keys where an image is desired
    # "welcome": "https://cdn-icons-png.flaticon.com/512/3799/3799863.png",  # Example welcome image
    # "profile_info": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",  # Example profile image
    # "help": "https://cdn-icons-png.flaticon.com/512/471/471664.png",  # Example help image
    # "support_info": "https://cdn-icons-png.flaticon.com/512/1067/1067566.png",  # Example support image
}


def get_image(key: str) -> str | None:
    """Get localized image URL/FileID for message key"""
    return IMAGES.get(key)


def get_message(key: str, **kwargs) -> str:
    """Get localized message with formatting"""
    message = MESSAGES.get(key, f"❌ Сообщение не найдено: {key}")
    if kwargs:
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError) as e:
            # Return message without formatting if there's an error
            return message
    return message


def format_price_per_month(total_price: int, months: int) -> str:
    """Format price per month"""
    try:
        price_per_month = total_price / months
        return f"{price_per_month:.0f}"
    except (ZeroDivisionError, TypeError):
        return "0"


def format_savings(plan_price: int, base_month_price: int, months: int) -> str:
    """Calculate and format savings"""
    try:
        full_price = base_month_price * months
        savings = full_price - plan_price
        if savings > 0:
            return f"Экономия {savings} ₽!"
        return "Базовая цена"
    except (TypeError, ValueError):
        return "Базовая цена"
