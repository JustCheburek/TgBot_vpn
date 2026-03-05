"""Main handlers for VPN Telegram Bot"""

import logging
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    BufferedInputFile,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.models.database import DatabaseManager, User, Subscription, Payment
from bot.config.settings import Config
from locales.ru import (
    get_message,
    get_image,
    format_price_per_month,
    format_savings,
    SUBSCRIPTION_PLANS,
    PAYMENT_METHODS,
)
from bot.utils.helpers import (
    generate_referral_code,
    format_date,
    calculate_end_date,
    generate_vpn_config,
    create_qr_code,
    get_server_flag,
    create_referral_link,
    get_random_server_location,
    generate_config_filename,
    calculate_referral_bonus,
)
from bot.utils.payments import payment_manager, PaymentError

logger = logging.getLogger(__name__)

# Initialize router
router = Router()


# FSM States
class PurchaseStates(StatesGroup):
    selecting_plan = State()
    selecting_payment_method = State()
    waiting_payment = State()


# Initialize database
db_manager = DatabaseManager(Config.DATABASE_URL)
db_manager.create_tables()


def get_or_create_user(telegram_user, session=None) -> User:
    """Get or create user in database"""
    own_session = False
    if session is None:
        session = db_manager.get_session()
        own_session = True

    try:
        user = session.query(User).filter_by(telegram_id=telegram_user.id).first()

        if not user:
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                language_code=telegram_user.language_code or "ru",
                referral_code=generate_referral_code(),
                is_admin=telegram_user.id in Config.ADMIN_IDS,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"New user created: {user.telegram_id}")

        # Update user activity
        user.last_activity = datetime.utcnow()
        session.commit()

        return user
    finally:
        if own_session:
            session.close()


@router.message(Command("start"))
async def start_command(message: Message, session, command: Command = None) -> None:
    """Handle /start command"""
    user = get_or_create_user(message.from_user, session)

    # Handle referral code from deep link
    if command and command.args:
        referral_code = command.args
        if user.referrer_id is None:
            try:
                referrer = (
                    session.query(User).filter_by(referral_code=referral_code).first()
                )
                if referrer and referrer.telegram_id != user.telegram_id:
                    user.referrer_id = referrer.id
                    referrer.total_referrals += 1
                    session.commit()
                    logger.info(
                        f"User {user.telegram_id} referred by {referrer.telegram_id}"
                    )

                    # Send notification to referrer (using bot instance from message)
                    try:
                        await message.bot.send_message(
                            chat_id=referrer.telegram_id,
                            text=get_message("success_referral_registered"),
                        )
                    except Exception as e:
                        logger.warning(f"Failed to notify referrer: {e}")
            except Exception as e:
                logger.error(f"Referral processing error: {e}")

    # Check if returning user
    is_returning = user.created_at < datetime.utcnow() - timedelta(hours=1)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_message("btn_buy_vpn"), callback_data="buy_vpn")
    )
    builder.row(
        InlineKeyboardButton(
            text=get_message("btn_my_profile"), callback_data="profile"
        )
    )

    # Add config button if user has active subscription
    if user.has_active_subscription:
        builder.row(
            InlineKeyboardButton(
                text=get_message("btn_config"), callback_data="my_config"
            )
        )

    builder.row(
        InlineKeyboardButton(text=get_message("btn_help"), callback_data="help"),
        InlineKeyboardButton(text=get_message("btn_support"), callback_data="support"),
    )
    builder.row(
        InlineKeyboardButton(text=get_message("btn_referral"), callback_data="referral")
    )

    if is_returning:
        message_text = get_message("welcome_back", name=user.first_name or "друг")
        message_key = "welcome_back"
    else:
        message_text = get_message("welcome")
        message_key = "welcome"

    image_url = get_image(message_key) or get_image("welcome")

    if image_url:
        await message.answer_photo(
            photo=image_url,
            caption=message_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
        )


async def show_main_menu(
    callback_query: CallbackQuery, session, state: FSMContext = None
):
    """Return to main menu"""
    await callback_query.answer()
    if state:
        await state.clear()

    user = get_or_create_user(callback_query.from_user, session)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_message("btn_buy_vpn"), callback_data="buy_vpn")
    )
    builder.row(
        InlineKeyboardButton(
            text=get_message("btn_my_profile"), callback_data="profile"
        )
    )

    if user.has_active_subscription:
        builder.row(
            InlineKeyboardButton(
                text=get_message("btn_config"), callback_data="my_config"
            )
        )

    builder.row(
        InlineKeyboardButton(text=get_message("btn_help"), callback_data="help"),
        InlineKeyboardButton(text=get_message("btn_support"), callback_data="support"),
    )
    builder.row(
        InlineKeyboardButton(text=get_message("btn_referral"), callback_data="referral")
    )

    message_text = get_message("welcome_back", name=user.first_name or "друг")
    image_url = get_image("welcome_back") or get_image("welcome")

    # If the current message has a photo, we can try to edit its caption or send a new one
    if callback_query.message.photo:
        if image_url:
            # We can't easily change the photo URL in edit_media without complex setup,
            # so we just update caption if it's the same "type" of message
            await callback_query.message.edit_caption(
                caption=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
        else:
            # If no photo needed, delete old and send new text
            await callback_query.message.delete()
            await callback_query.message.answer(
                text=message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
            )
    else:
        # If it was a text message
        if image_url:
            await callback_query.message.delete()
            await callback_query.message.answer_photo(
                photo=image_url,
                caption=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
        else:
            await callback_query.message.edit_text(
                text=message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
            )


@router.callback_query(F.data == "buy_vpn")
async def show_plans(callback_query: CallbackQuery, session, state: FSMContext) -> None:
    """Show subscription plans"""
    await callback_query.answer()

    # Reset FSM state if we were in a conversation
    await state.clear()
    await state.set_state(PurchaseStates.selecting_plan)

    message_text = get_message("plans_header") + "\n\n"

    # Add each plan info with enhanced formatting
    base_month_price = SUBSCRIPTION_PLANS["1_month"]["price"]

    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        months = plan["duration_days"] // 30
        price_per_month = format_price_per_month(plan["price"], months)
        savings = format_savings(plan["price"], base_month_price, months)
        popular_badge = get_message("popular_badge") if plan.get("popular") else ""

        message_text += get_message(
            "plan_template",
            emoji=plan["emoji"],
            name=plan["name"],
            popular_badge=popular_badge,
            price=plan["price"],
            price_per_month=price_per_month,
            duration=plan["duration_days"],
            description=plan["description"],
            savings=savings,
        )

    message_text += "\n\n" + get_message("choose_plan")

    builder = InlineKeyboardBuilder()
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        btn_text = get_message(f"btn_plan_{plan_id}", price=plan["price"])
        builder.row(
            InlineKeyboardButton(text=btn_text, callback_data=f"plan_{plan_id}")
        )

    builder.row(
        InlineKeyboardButton(text=get_message("btn_back"), callback_data="main_menu")
    )

    try:
        if callback_query.message.photo:
            await callback_query.message.delete()
            await callback_query.message.answer(
                text=message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
            )
        else:
            await callback_query.message.edit_text(
                text=message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
            )
    except Exception as e:
        if "message is not modified" not in str(e):
            logger.error(f"Error showing plans: {e}")


@router.callback_query(F.data.startswith("plan_"), PurchaseStates.selecting_plan)
async def select_payment_method(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    """Handle plan selection and show payment methods"""
    await callback_query.answer()

    plan_type = callback_query.data.replace("plan_", "")
    await state.update_data(selected_plan=plan_type)

    plan = SUBSCRIPTION_PLANS.get(plan_type)
    if not plan:
        await callback_query.message.edit_text("❌ Неверный план")
        await state.clear()
        return

    # Get available payment methods
    available_methods = payment_manager.get_available_methods()

    builder = InlineKeyboardBuilder()
    for method in available_methods:
        method_info = PAYMENT_METHODS[method]
        builder.row(
            InlineKeyboardButton(
                text=f"{method_info['emoji']} {method_info['name']}",
                callback_data=f"pay_{method}",
            )
        )

    builder.row(
        InlineKeyboardButton(text=get_message("btn_back"), callback_data="buy_vpn")
    )

    await state.set_state(PurchaseStates.selecting_payment_method)

    await callback_query.message.edit_text(
        text=get_message(
            "payment_methods",
            plan_name=plan["name"],
            amount=plan["price"],
            duration=plan["duration_days"],
        ),
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(
    F.data.startswith("pay_"), PurchaseStates.selecting_payment_method
)
async def process_payment(
    callback_query: CallbackQuery, session, state: FSMContext
) -> None:
    """Process payment"""
    await callback_query.answer("💳 Создаем счет для оплаты...")

    payment_method = callback_query.data.replace("pay_", "")
    data = await state.get_data()
    plan_type = data.get("selected_plan")

    if not plan_type:
        await callback_query.message.edit_text("❌ Ошибка: план не выбран")
        await state.clear()
        return

    plan = SUBSCRIPTION_PLANS[plan_type]
    user = get_or_create_user(callback_query.from_user, session)

    # Create payment record
    try:
        payment = Payment(
            user_id=user.id,
            amount=plan["price"] * 100,  # Convert to kopecks
            plan_type=plan_type,
            payment_method=payment_method,
            expires_at=datetime.utcnow() + timedelta(minutes=15),
        )
        session.add(payment)
        session.commit()
        session.refresh(payment)

        # Create payment with provider
        try:
            payment_data = payment_manager.create_payment(
                method=payment_method,
                amount=payment.amount,
                order_id=f"vpn_{payment.id}",
                description=f"VPN подписка {plan['name']}",
            )

            # Update payment with external data
            payment.payment_id = payment_data["payment_id"]
            payment.payment_url = payment_data["payment_url"]
            session.commit()

        except PaymentError as e:
            logger.error(f"Payment creation error: {e}")
            await callback_query.message.edit_text(f"❌ {str(e)}")
            await state.clear()
            return

        # Store payment info for verification
        await state.update_data(payment_id=payment.id)
        await state.set_state(PurchaseStates.waiting_payment)

        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="🔄 Проверить платеж", callback_data=f"verify_payment_{payment.id}"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="💳 Новый счет", callback_data=f"plan_{plan_type}"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text=get_message("btn_main_menu"), callback_data="main_menu"
            )
        )

        await callback_query.message.edit_text(
            text=get_message(
                "payment_created",
                plan_name=plan["name"],
                amount=plan["price"],
                payment_url=payment_data["payment_url"],
            ),
            reply_markup=builder.as_markup(),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    except Exception as e:
        logger.error(f"Payment creation error: {e}")
        await callback_query.message.edit_text(get_message("error_general"))
        await state.clear()


@router.callback_query(
    F.data.startswith("verify_payment_"), PurchaseStates.waiting_payment
)
async def verify_payment(
    callback_query: CallbackQuery, session, state: FSMContext
) -> None:
    """Verify and complete payment"""
    await callback_query.answer("🔄 Проверяем статус платежа...")

    payment_id = int(callback_query.data.replace("verify_payment_", ""))

    try:
        payment = session.query(Payment).filter_by(id=payment_id).first()
        if not payment:
            await callback_query.message.edit_text("❌ Платеж не найден")
            await state.clear()
            return

        # Check if payment expired
        if payment.is_expired:
            await callback_query.message.edit_text(get_message("error_payment_timeout"))
            await state.clear()
            return

        # Verify payment with provider
        payment_status = payment_manager.check_payment(
            payment.payment_method, payment.payment_id
        )

        if payment_status == "completed":
            # Payment successful - create subscription
            payment.status = "completed"
            payment.completed_at = datetime.utcnow()

            # Get user and update stats
            user = session.query(User).filter_by(id=payment.user_id).first()
            user.total_spent += payment.amount_rubles

            # Deactivate old subscriptions
            old_subs = (
                session.query(Subscription)
                .filter_by(user_id=payment.user_id, is_active=True)
                .all()
            )
            for sub in old_subs:
                sub.is_active = False

            # Create VPN subscription
            server_location = get_random_server_location()
            subscription = Subscription(
                user_id=payment.user_id,
                plan_type=payment.plan_type,
                end_date=calculate_end_date(payment.plan_type),
                vpn_config=generate_vpn_config(user.telegram_id, server_location),
                config_name=f"VPN_{SUBSCRIPTION_PLANS[payment.plan_type]['name']}",
                server_location=server_location,
            )
            session.add(subscription)

            # Process referral bonus
            if user.referrer_id:
                referrer = session.query(User).filter_by(id=user.referrer_id).first()
                if referrer:
                    bonus = calculate_referral_bonus(payment.amount)
                    referrer.referral_balance += bonus / 100  # Convert to rubles
                    session.commit()

                    # Notify referrer
                    try:
                        await callback_query.bot.send_message(
                            chat_id=referrer.telegram_id,
                            text=get_message(
                                "referral_bonus",
                                amount=bonus / 100,
                                friend_name=user.full_name,
                            ),
                        )
                    except Exception as e:
                        logger.warning(f"Failed to notify referrer about bonus: {e}")

            session.commit()

            # Send success message
            plan = SUBSCRIPTION_PLANS[payment.plan_type]
            success_message = get_message(
                "payment_success",
                plan_name=plan["name"],
                end_date=format_date(subscription.end_date),
                server_location=f"{get_server_flag(server_location)} {server_location}",
            )

            await callback_query.message.edit_text(success_message, parse_mode="HTML")

            # Send VPN config as file
            config_filename = generate_config_filename(
                user.telegram_id, payment.plan_type
            )
            config_file_data = subscription.vpn_config.encode("utf-8")
            document = BufferedInputFile(config_file_data, filename=config_filename)

            await callback_query.message.answer_document(
                document=document,
                caption=get_message("vpn_config_info"),
                parse_mode="HTML",
            )

            # Generate and send QR code
            qr_buffer = create_qr_code(subscription.vpn_config)
            photo = BufferedInputFile(qr_buffer.getvalue(), filename="qr_code.png")
            await callback_query.message.answer_photo(
                photo=photo, caption=get_message("config_qr"), parse_mode="HTML"
            )

            # Send main menu and clear state
            await state.clear()
            await show_main_menu_internal(callback_query.message, user)

        elif payment_status == "failed":
            payment.status = "failed"
            session.commit()
            await callback_query.message.edit_text(
                get_message("payment_failed"), parse_mode="HTML"
            )
            await state.clear()

        else:  # pending or unknown
            time_left = int(
                (payment.expires_at - datetime.utcnow()).total_seconds() / 60
            )
            if time_left > 0:
                builder = InlineKeyboardBuilder()
                builder.row(
                    InlineKeyboardButton(
                        text="🔄 Проверить еще раз",
                        callback_data=f"verify_payment_{payment.id}",
                    )
                )
                builder.row(
                    InlineKeyboardButton(
                        text=get_message("btn_main_menu"), callback_data="main_menu"
                    )
                )

                await callback_query.message.edit_text(
                    text=get_message(
                        "payment_pending",
                        amount=payment.amount_rubles,
                        payment_url=payment.payment_url,
                        time_left=time_left,
                    ),
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML",
                )
            else:
                await callback_query.message.edit_text(
                    get_message("error_payment_timeout")
                )
                await state.clear()

    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        await callback_query.message.edit_text(get_message("error_general"))
        await state.clear()


@router.callback_query(F.data == "main_menu")
async def main_menu_handler(
    callback_query: CallbackQuery, session, state: FSMContext
) -> None:
    """Handle main menu button"""
    await show_main_menu(callback_query, session, state)


@router.callback_query(F.data == "profile")
async def show_profile(callback_query: CallbackQuery, session) -> None:
    """Show user profile"""
    await callback_query.answer()

    user = get_or_create_user(callback_query.from_user, session)

    # Get subscription info
    if user.has_active_subscription:
        sub = user.active_subscription
        plan = SUBSCRIPTION_PLANS[sub.plan_type]
        subscription_info = get_message(
            "subscription_active",
            plan_name=plan["name"],
            end_date=format_date(sub.end_date),
            time_remaining=sub.time_remaining_text,
            server_location=f"{get_server_flag(sub.server_location)} {sub.server_location}",
        )
    else:
        subscription_info = get_message("subscription_inactive")

    builder = InlineKeyboardBuilder()
    if user.has_active_subscription:
        builder.row(
            InlineKeyboardButton(text="📱 Моя конфигурация", callback_data="my_config")
        )

    builder.row(
        InlineKeyboardButton(text="🔄 Продлить подписку", callback_data="buy_vpn")
    )
    builder.row(
        InlineKeyboardButton(
            text=get_message("btn_main_menu"), callback_data="main_menu"
        )
    )

    image_url = get_image("profile_info")
    message_text = get_message(
        "profile_info",
        user_id=user.telegram_id,
        full_name=user.full_name,
        created_at=format_date(user.created_at),
        total_spent=user.total_spent,
        subscription_info=subscription_info,
        referral_code=user.referral_code,
    )

    if image_url:
        if callback_query.message.photo:
            await callback_query.message.edit_caption(
                caption=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
        else:
            await callback_query.message.delete()
            await callback_query.message.answer_photo(
                photo=image_url,
                caption=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
    else:
        if callback_query.message.photo:
            await callback_query.message.delete()
            await callback_query.message.answer(
                text=message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
            )
        else:
            await callback_query.message.edit_text(
                text=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )


@router.callback_query(F.data == "my_config")
async def show_my_config(callback_query: CallbackQuery, session) -> None:
    """Show user's VPN configuration"""
    await callback_query.answer()

    user = get_or_create_user(callback_query.from_user, session)

    if not user.has_active_subscription:
        await callback_query.message.edit_text(get_message("error_no_subscription"))
        return

    subscription = user.active_subscription

    # Send config info
    await callback_query.message.edit_text(
        text=get_message("vpn_config_info"), parse_mode="HTML"
    )

    # Send config file
    config_filename = generate_config_filename(user.telegram_id, subscription.plan_type)
    config_file_data = subscription.vpn_config.encode("utf-8")
    document = BufferedInputFile(config_file_data, filename=config_filename)

    await callback_query.message.answer_document(
        document=document,
        caption=f"📱 Конфигурация VPN\n🌍 Сервер: {get_server_flag(subscription.server_location)} {subscription.server_location}",
        parse_mode="HTML",
    )

    # Send QR code
    qr_buffer = create_qr_code(subscription.vpn_config)
    photo = BufferedInputFile(qr_buffer.getvalue(), filename="qr_code.png")
    await callback_query.message.answer_photo(
        photo=photo, caption=get_message("config_qr"), parse_mode="HTML"
    )


@router.callback_query(F.data == "referral")
async def show_referral_info(callback_query: CallbackQuery, session) -> None:
    """Show referral program info"""
    await callback_query.answer()

    user = get_or_create_user(callback_query.from_user, session)

    # Get bot username for referral link
    bot_info = await callback_query.bot.get_me()
    referral_link = create_referral_link(user.referral_code, bot_info.username)

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📤 Поделиться ссылкой",
            url=f"https://t.me/share/url?url={referral_link}",
        )
    )

    # Add payout button if has enough balance
    if user.referral_balance >= Config.REFERRAL_MIN_PAYOUT:
        builder.row(
            InlineKeyboardButton(
                text="💳 Вывести средства", callback_data="request_payout"
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=get_message("btn_main_menu"), callback_data="main_menu"
        )
    )

    await callback_query.message.edit_text(
        text=get_message(
            "referral_info",
            referral_count=user.total_referrals,
            earned_amount=user.referral_balance,
            available_balance=user.referral_balance,
            referral_link=referral_link,
            min_payout=Config.REFERRAL_MIN_PAYOUT,
        ),
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "help")
async def show_help(callback_query: CallbackQuery) -> None:
    """Show help information"""
    await callback_query.answer()

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_message("btn_support"), callback_data="support")
    )
    builder.row(
        InlineKeyboardButton(
            text=get_message("btn_main_menu"), callback_data="main_menu"
        )
    )

    image_url = get_image("help")
    message_text = get_message("help")

    if image_url:
        if callback_query.message.photo:
            await callback_query.message.edit_caption(
                caption=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
        else:
            await callback_query.message.delete()
            await callback_query.message.answer_photo(
                photo=image_url,
                caption=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
    else:
        if callback_query.message.photo:
            await callback_query.message.delete()
            await callback_query.message.answer(
                text=message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
            )
        else:
            await callback_query.message.edit_text(
                text=message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
            )


@router.callback_query(F.data == "support")
async def show_support(callback_query: CallbackQuery) -> None:
    """Show support information"""
    await callback_query.answer()

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="💬 Написать в поддержку",
            url=f"https://t.me/{Config.SUPPORT_USERNAME}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_message("btn_main_menu"), callback_data="main_menu"
        )
    )

    image_url = get_image("support_info")
    message_text = get_message("support_info", support_username=Config.SUPPORT_USERNAME)

    if image_url:
        if callback_query.message.photo:
            await callback_query.message.edit_caption(
                caption=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
        else:
            await callback_query.message.delete()
            await callback_query.message.answer_photo(
                photo=image_url,
                caption=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )
    else:
        if callback_query.message.photo:
            await callback_query.message.delete()
            await callback_query.message.answer(
                text=message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
            )
        else:
            await callback_query.message.edit_text(
                text=message_text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
            )


async def show_main_menu_internal(message: Message, user: User) -> None:
    """Internal helper to show main menu"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_message("btn_buy_vpn"), callback_data="buy_vpn")
    )
    builder.row(
        InlineKeyboardButton(
            text=get_message("btn_my_profile"), callback_data="profile"
        )
    )

    if user.has_active_subscription:
        builder.row(
            InlineKeyboardButton(
                text=get_message("btn_config"), callback_data="my_config"
            )
        )

    builder.row(
        InlineKeyboardButton(text=get_message("btn_help"), callback_data="help"),
        InlineKeyboardButton(text=get_message("btn_support"), callback_data="support"),
    )
    builder.row(
        InlineKeyboardButton(text=get_message("btn_referral"), callback_data="referral")
    )

    message_text = get_message("welcome_back", name=user.first_name or "друг")

    await message.answer(
        text=message_text, reply_markup=builder.as_markup(), parse_mode="HTML"
    )


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext) -> None:
    """Cancel current operation"""
    await state.clear()
    await message.answer("❌ Операция отменена")
