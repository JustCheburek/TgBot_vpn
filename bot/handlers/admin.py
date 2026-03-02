"""Admin handlers for VPN Telegram Bot"""

import logging
import asyncio
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import func, desc

from bot.models.database import (
    DatabaseManager,
    User,
    Subscription,
    Payment,
    VPNKey,
)
from bot.config.settings import Config
from bot.utils.helpers import (
    is_admin,
    log_admin_action,
    format_datetime,
    format_date,
    format_time_ago,
    StatsCalculator,
)
from locales.ru import get_message

logger = logging.getLogger(__name__)

# Initialize router
router = Router()


# Admin FSM States
class AdminStates(StatesGroup):
    waiting_broadcast_message = State()


db_manager = DatabaseManager(Config.DATABASE_URL)


@router.message(Command("admin"))
async def admin_panel(message: Message, session) -> None:
    """Show admin panel"""
    user_id = message.from_user.id

    if not is_admin(user_id):
        await message.answer(get_message("admin_not_authorized"))
        return

    try:
        # Get comprehensive statistics
        total_users = session.query(User).count()

        active_subscriptions = (
            session.query(Subscription)
            .filter(
                Subscription.is_active,
                Subscription.end_date > datetime.utcnow(),
            )
            .count()
        )

        # Daily revenue
        today = datetime.utcnow().date()
        daily_revenue_kopecks = (
            session.query(func.sum(Payment.amount))
            .filter(Payment.status == "completed", Payment.completed_at >= today)
            .scalar()
            or 0
        )
        daily_revenue = daily_revenue_kopecks / 100

        # Monthly revenue
        start_of_month = datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        monthly_revenue_kopecks = (
            session.query(func.sum(Payment.amount))
            .filter(
                Payment.status == "completed", Payment.completed_at >= start_of_month
            )
            .scalar()
            or 0
        )
        monthly_revenue = monthly_revenue_kopecks / 100

        # Available VPN keys
        available_keys = session.query(VPNKey).filter(~VPNKey.is_used).count()

        # New users today
        new_users = session.query(User).filter(User.created_at >= today).count()

        admin_text = get_message(
            "admin_panel",
            total_users=total_users,
            active_subscriptions=active_subscriptions,
            daily_revenue=int(daily_revenue),
            monthly_revenue=int(monthly_revenue),
            available_keys=available_keys,
            new_users=new_users,
            last_update=format_datetime(datetime.utcnow()),
        )

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        )
        builder.row(
            InlineKeyboardButton(text="🔑 VPN ключи", callback_data="admin_keys"),
            InlineKeyboardButton(text="💰 Платежи", callback_data="admin_payments"),
        )
        builder.row(
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="📋 Логи", callback_data="admin_logs"),
        )
        builder.row(
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings"),
            InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_refresh"),
        )

        await message.answer(
            text=admin_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )

        log_admin_action(user_id, "accessed_admin_panel")

    except Exception as e:
        logger.error(f"Admin panel error: {e}")
        await message.answer("❌ Ошибка при открытии админ-панели")


@router.callback_query(F.data.startswith("admin_"))
async def admin_callback_handler(
    callback_query: CallbackQuery, session, state: FSMContext
) -> None:
    """Handle admin callback queries"""
    user_id = callback_query.from_user.id
    if not is_admin(user_id):
        await callback_query.answer(
            get_message("admin_not_authorized"), show_alert=True
        )
        return

    action = callback_query.data.replace("admin_", "")

    if action == "refresh":
        await callback_query.answer()
        await admin_panel_refresh(callback_query, session)
    elif action == "users":
        await callback_query.answer()
        await admin_users_list(callback_query, session, state)
    elif action == "stats":
        await callback_query.answer()
        await admin_detailed_stats(callback_query, session)
    elif action == "keys":
        await callback_query.answer()
        await admin_keys_management(callback_query, session)
    elif action == "payments":
        await callback_query.answer()
        await admin_payments_list(callback_query, session)
    elif action == "broadcast":
        await callback_query.answer()
        await admin_broadcast_start(callback_query, session, state)
    elif action == "logs":
        await callback_query.answer()
        await admin_logs_view(callback_query)
    elif action == "settings":
        await callback_query.answer()
        await admin_settings(callback_query)
    elif action == "back":
        await callback_query.answer()
        await admin_back_to_panel(callback_query, session, state)
    elif action.startswith("users_page_"):
        await callback_query.answer()
        page = int(action.replace("users_page_", ""))
        await state.update_data(admin_users_page=page)
        await admin_users_list(callback_query, session, state)


async def admin_panel_refresh(callback_query: CallbackQuery, session) -> None:
    """Refresh admin panel"""
    user_id = callback_query.from_user.id

    try:
        # Get fresh statistics
        total_users = session.query(User).count()
        active_subscriptions = (
            session.query(Subscription)
            .filter(
                Subscription.is_active,
                Subscription.end_date > datetime.utcnow(),
            )
            .count()
        )

        today = datetime.utcnow().date()
        daily_revenue_kopecks = (
            session.query(func.sum(Payment.amount))
            .filter(Payment.status == "completed", Payment.completed_at >= today)
            .scalar()
            or 0
        )
        daily_revenue = daily_revenue_kopecks / 100

        start_of_month = datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        monthly_revenue_kopecks = (
            session.query(func.sum(Payment.amount))
            .filter(
                Payment.status == "completed", Payment.completed_at >= start_of_month
            )
            .scalar()
            or 0
        )
        monthly_revenue = monthly_revenue_kopecks / 100

        available_keys = session.query(VPNKey).filter(~VPNKey.is_used).count()
        new_users = session.query(User).filter(User.created_at >= today).count()

        admin_text = get_message(
            "admin_panel",
            total_users=total_users,
            active_subscriptions=active_subscriptions,
            daily_revenue=int(daily_revenue),
            monthly_revenue=int(monthly_revenue),
            available_keys=available_keys,
            new_users=new_users,
            last_update=format_datetime(datetime.utcnow()),
        )

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
        )
        builder.row(
            InlineKeyboardButton(text="🔑 VPN ключи", callback_data="admin_keys"),
            InlineKeyboardButton(text="💰 Платежи", callback_data="admin_payments"),
        )
        builder.row(
            InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="📋 Логи", callback_data="admin_logs"),
        )
        builder.row(
            InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin_settings"),
            InlineKeyboardButton(text="🔄 Обновлено ✅", callback_data="admin_refresh"),
        )

        await callback_query.message.edit_text(
            text=admin_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )

        log_admin_action(user_id, "refreshed_admin_panel")

    except Exception as e:
        logger.error(f"Admin panel refresh error: {e}")
        await callback_query.message.edit_text("❌ Ошибка при обновлении панели")


async def admin_users_list(
    callback_query: CallbackQuery, session, state: FSMContext
) -> None:
    """Show users list for admin"""
    data = await state.get_data()
    page = data.get("admin_users_page", 0)
    limit = 10
    offset = page * limit

    try:
        users = (
            session.query(User)
            .order_by(desc(User.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        total_users = session.query(User).count()

        users_text = f"👥 Пользователи (стр. {page + 1}):\n\n"

        for user in users:
            status_emoji = "✅" if user.has_active_subscription else "❌"
            last_activity = format_time_ago(user.last_activity)

            users_text += f"{status_emoji} <b>{user.full_name}</b>\n"
            users_text += f"   🆔 ID: <code>{user.telegram_id}</code>\n"
            users_text += f"   👤 @{user.username or 'None'}\n"
            users_text += f"   📅 Регистрация: {format_date(user.created_at)}\n"
            users_text += f"   🕐 Активность: {last_activity}\n"
            users_text += f"   💰 Потрачено: {user.total_spent} ₽\n"
            users_text += f"   🎁 Рефералов: {user.total_referrals}\n\n"

        users_text += f"📊 Всего пользователей: {total_users}"

        builder = InlineKeyboardBuilder()
        nav_btns = []
        if page > 0:
            nav_btns.append(
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=f"admin_users_page_{page - 1}"
                )
            )

        if (page + 1) * limit < total_users:
            nav_btns.append(
                InlineKeyboardButton(
                    text="Вперед ➡️", callback_data=f"admin_users_page_{page + 1}"
                )
            )

        if nav_btns:
            builder.row(*nav_btns)

        builder.row(
            InlineKeyboardButton(
                text="🔍 Поиск пользователя", callback_data="admin_user_search"
            ),
            InlineKeyboardButton(
                text="📊 Статистика", callback_data="admin_user_stats"
            ),
        )
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_back")
        )

        await callback_query.message.edit_text(
            text=users_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in admin_users_list: {e}")
        await callback_query.message.edit_text(
            "❌ Ошибка при получении списка пользователей"
        )


async def admin_detailed_stats(callback_query: CallbackQuery, session) -> None:
    """Show detailed statistics"""
    try:
        stats = StatsCalculator.calculate_daily_stats()

        total_users = session.query(User).count()
        active_users_week = (
            session.query(User)
            .filter(User.last_activity >= datetime.utcnow() - timedelta(days=7))
            .count()
        )
        active_users_month = (
            session.query(User)
            .filter(User.last_activity >= datetime.utcnow() - timedelta(days=30))
            .count()
        )

        subs_by_plan = (
            session.query(Subscription.plan_type, func.count(Subscription.id))
            .filter(
                Subscription.is_active,
                Subscription.end_date > datetime.utcnow(),
            )
            .group_by(Subscription.plan_type)
            .all()
        )

        total_revenue_kopecks = (
            session.query(func.sum(Payment.amount))
            .filter(Payment.status == "completed")
            .scalar()
            or 0
        )
        total_revenue = total_revenue_kopecks / 100

        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_revenue_kopecks = (
            session.query(func.sum(Payment.amount))
            .filter(Payment.status == "completed", Payment.completed_at >= week_ago)
            .scalar()
            or 0
        )
        weekly_revenue = weekly_revenue_kopecks / 100

        stats_text = "📊 <b>Подробная статистика</b>\n\n"
        stats_text += "👥 <b>Пользователи:</b>\n"
        stats_text += f"   • Всего: {total_users}\n"
        stats_text += f"   • Новых сегодня: {stats['new_users']}\n"
        stats_text += f"   • Активных за неделю: {active_users_week}\n"
        stats_text += f"   • Активных за месяц: {active_users_month}\n\n"

        stats_text += "📱 <b>Подписки:</b>\n"
        stats_text += f"   • Активных: {stats['active_subscriptions']}\n"
        for plan_type, count in subs_by_plan:
            plan_name = plan_type.replace("_", " ").title()
            stats_text += f"   • {plan_name}: {count}\n"
        stats_text += "\n"

        stats_text += "💰 <b>Доходы:</b>\n"
        stats_text += f"   • Сегодня: {stats['daily_revenue']:.0f} ₽\n"
        stats_text += f"   • За неделю: {weekly_revenue:.0f} ₽\n"
        stats_text += f"   • Всего: {total_revenue:.0f} ₽\n"
        stats_text += f"   • Платежей сегодня: {stats['successful_payments']}\n\n"

        stats_text += f"🔄 <b>Обновлено:</b> {format_datetime(datetime.utcnow())}"

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="📈 График доходов", callback_data="admin_revenue_chart"
            ),
            InlineKeyboardButton(
                text="👥 Активность пользователей", callback_data="admin_activity_chart"
            ),
        )
        builder.row(
            InlineKeyboardButton(
                text="📊 Экспорт данных", callback_data="admin_export_data"
            ),
            InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_stats"),
        )
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_back")
        )

        await callback_query.message.edit_text(
            text=stats_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )

        log_admin_action(callback_query.from_user.id, "viewed_detailed_stats")
    except Exception as e:
        logger.error(f"Error in admin_detailed_stats: {e}")
        await callback_query.message.edit_text("❌ Ошибка при получении статистики")


async def admin_keys_management(callback_query: CallbackQuery, session) -> None:
    """Manage VPN keys"""
    try:
        total_keys = session.query(VPNKey).count()
        available_keys = session.query(VPNKey).filter(~VPNKey.is_used).count()
        used_keys = total_keys - available_keys

        keys_text = "🔑 <b>Управление VPN ключами</b>\n\n"
        keys_text += "📊 <b>Статистика:</b>\n"
        keys_text += f"   • Всего ключей: {total_keys}\n"
        keys_text += f"   • Доступных: {available_keys}\n"
        keys_text += f"   • Использованных: {used_keys}\n\n"

        if available_keys < 10:
            keys_text += "⚠️ <b>Внимание!</b> Мало доступных ключей!\n\n"

        keys_text += f"🔄 <b>Обновлено:</b> {format_datetime(datetime.utcnow())}"

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="➕ Добавить ключи", callback_data="admin_keys_add"
            ),
            InlineKeyboardButton(
                text="📋 Список ключей", callback_data="admin_keys_list"
            ),
        )
        builder.row(
            InlineKeyboardButton(
                text="🗑️ Очистить использованные", callback_data="admin_keys_cleanup"
            ),
            InlineKeyboardButton(
                text="📊 Статистика по серверам", callback_data="admin_keys_stats"
            ),
        )
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_back")
        )

        await callback_query.message.edit_text(
            text=keys_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in admin_keys_management: {e}")
        await callback_query.message.edit_text("❌ Ошибка при управлении ключами")


async def admin_payments_list(callback_query: CallbackQuery, session) -> None:
    """Show recent payments"""
    try:
        payments = (
            session.query(Payment).order_by(desc(Payment.created_at)).limit(20).all()
        )

        payments_text = "💰 <b>Последние платежи</b>\n\n"
        for payment in payments:
            user = session.query(User).filter_by(id=payment.user_id).first()
            status_emoji = {
                "completed": "✅",
                "pending": "⏳",
                "failed": "❌",
                "cancelled": "🚫",
            }.get(payment.status, "❓")

            payments_text += f"{status_emoji} <b>{payment.amount_rubles:.0f} ₽</b>\n"
            payments_text += f"   👤 {user.full_name if user else 'Unknown'}\n"
            payments_text += f"   📦 {payment.plan_type.replace('_', ' ').title()}\n"
            payments_text += f"   💳 {payment.payment_method.upper()}\n"
            payments_text += f"   📅 {format_datetime(payment.created_at)}\n\n"

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="💰 Статистика доходов", callback_data="admin_revenue_stats"
            ),
            InlineKeyboardButton(
                text="🔍 Поиск платежа", callback_data="admin_payment_search"
            ),
        )
        builder.row(
            InlineKeyboardButton(
                text="📊 По методам оплаты", callback_data="admin_payment_methods"
            ),
            InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_payments"),
        )
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_back")
        )

        await callback_query.message.edit_text(
            text=payments_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in admin_payments_list: {e}")
        await callback_query.message.edit_text(
            "❌ Ошибка при получении списка платежей"
        )


async def admin_broadcast_start(
    callback_query: CallbackQuery, session, state: FSMContext
) -> None:
    """Start broadcast message creation"""
    try:
        total_users = session.query(User).count()
        active_users = (
            session.query(User)
            .filter(User.last_activity >= datetime.utcnow() - timedelta(days=30))
            .count()
        )

        broadcast_text = get_message(
            "broadcast_start", total_users=total_users, active_users=active_users
        )

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_back")
        )

        await callback_query.message.edit_text(
            text=broadcast_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )

        await state.set_state(AdminStates.waiting_broadcast_message)
    except Exception as e:
        logger.error(f"Error in admin_broadcast_start: {e}")
        await callback_query.message.edit_text("❌ Ошибка при запуске рассылки")


@router.message(AdminStates.waiting_broadcast_message, F.text)
async def handle_broadcast_message(
    message: Message, session, state: FSMContext
) -> None:
    """Handle broadcast message from admin"""
    if not is_admin(message.from_user.id):
        return

    broadcast_message = message.text
    await state.update_data(broadcast_message=broadcast_message)

    try:
        total_users = session.query(User).count()

        confirm_text = get_message(
            "broadcast_confirm", recipients=total_users, message=broadcast_message
        )

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="✅ Отправить всем", callback_data="admin_broadcast_confirm"
            ),
            InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back"),
        )

        await message.answer(
            text=confirm_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in handle_broadcast_message: {e}")
        await message.answer("❌ Ошибка при обработке сообщения рассылки")


async def admin_broadcast_confirm(
    callback_query: CallbackQuery, session, state: FSMContext
) -> None:
    """Confirm and execute broadcast"""
    await callback_query.answer("📢 Начинаем рассылку...")

    data = await state.get_data()
    broadcast_message = data.get("broadcast_message")

    if not broadcast_message:
        await callback_query.message.edit_text("❌ Сообщение для рассылки не найдено")
        await state.clear()
        return

    try:
        users = session.query(User).all()
        total_users = len(users)
        sent_count = 0
        failed_count = 0

        await callback_query.message.edit_text(
            f"📢 Рассылка запущена...\n\n"
            f"👥 Всего получателей: {total_users}\n"
            f"✅ Отправлено: 0\n"
            f"❌ Ошибок: 0"
        )

        for i, user in enumerate(users):
            try:
                await callback_query.bot.send_message(
                    chat_id=user.telegram_id, text=broadcast_message, parse_mode="HTML"
                )
                sent_count += 1

                if (i + 1) % 50 == 0:
                    await callback_query.message.edit_text(
                        f"📢 Рассылка в процессе...\n\n"
                        f"👥 Всего получателей: {total_users}\n"
                        f"✅ Отправлено: {sent_count}\n"
                        f"❌ Ошибок: {failed_count}\n"
                        f"📊 Прогресс: {((i + 1) / total_users * 100):.1f}%"
                    )
                await asyncio.sleep(0.1)

            except Exception as e:
                failed_count += 1
                logger.warning(
                    f"Failed to send broadcast to user {user.telegram_id}: {e}"
                )

        success_text = get_message(
            "broadcast_success", sent=sent_count, total=total_users
        )
        if failed_count > 0:
            success_text += f"\n❌ Не удалось отправить: {failed_count}"

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_back")
        )

        await callback_query.message.edit_text(
            text=success_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )

        await state.clear()
    except Exception as e:
        logger.error(f"Error in admin_broadcast_confirm: {e}")
        await callback_query.message.edit_text("❌ Ошибка при выполнении рассылки")


async def admin_logs_view(callback_query: CallbackQuery) -> None:
    """View admin logs"""
    try:
        log_file = f"logs/vpn_bot_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            recent_logs = lines[-20:]

        logs_text = f"📋 <b>Последние логи</b>\n\n<pre>"
        for line in recent_logs:
            if len(line) > 100:
                line = line[:97] + "..."
            logs_text += line
        logs_text += "</pre>"

    except FileNotFoundError:
        logs_text = "📋 <b>Логи</b>\n\n❌ Файл логов не найден"
    except Exception as e:
        logs_text = f"📋 <b>Логи</b>\n\n❌ Ошибка чтения логов: {str(e)}"

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📁 Скачать полный лог", callback_data="admin_download_logs"
        ),
        InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_logs"),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_back")
    )

    await callback_query.message.edit_text(
        text=logs_text, reply_markup=builder.as_markup(), parse_mode="HTML"
    )


async def admin_settings(callback_query: CallbackQuery) -> None:
    """Show admin settings"""
    settings_text = "⚙️ <b>Настройки бота</b>\n\n"
    settings_text += "🤖 <b>Основные:</b>\n"
    settings_text += f"   • Режим отладки: {'✅' if Config.DEBUG else '❌'}\n"
    settings_text += f"   • Уровень логов: {Config.LOG_LEVEL}\n"
    settings_text += f"   • Язык по умолчанию: {Config.DEFAULT_LANGUAGE}\n\n"

    settings_text += "💰 <b>Тарифы:</b>\n"
    settings_text += f"   • 1 месяц: {Config.PLAN_1_MONTH_PRICE} ₽\n"
    settings_text += f"   • 3 месяца: {Config.PLAN_3_MONTH_PRICE} ₽\n"
    settings_text += f"   • 6 месяцев: {Config.PLAN_6_MONTH_PRICE} ₽\n"
    settings_text += f"   • 12 месяцев: {Config.PLAN_12_MONTH_PRICE} ₽\n\n"

    settings_text += "🎁 <b>Реферальная программа:</b>\n"
    settings_text += f"   • Процент бонуса: {Config.REFERRAL_BONUS_PERCENT}%\n"
    settings_text += f"   • Минимум для вывода: {Config.REFERRAL_MIN_PAYOUT} ₽\n"

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="💰 Изменить тарифы", callback_data="admin_edit_prices"
        ),
        InlineKeyboardButton(
            text="🎁 Настроить рефералы", callback_data="admin_edit_referrals"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔧 Системные настройки", callback_data="admin_system_settings"
        ),
        InlineKeyboardButton(
            text="💾 Резервное копирование", callback_data="admin_backup"
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад в админку", callback_data="admin_back")
    )

    await callback_query.message.edit_text(
        text=settings_text, reply_markup=builder.as_markup(), parse_mode="HTML"
    )


async def admin_back_to_panel(
    callback_query: CallbackQuery, session, state: FSMContext
) -> None:
    """Return to admin panel"""
    await state.clear()
    await admin_panel_refresh(callback_query, session)
