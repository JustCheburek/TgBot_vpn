"""Russian localization for VPN Bot"""

import json
from pathlib import Path


def _load_messages() -> dict:
    try:
        json_path = Path(__file__).parent / "ru.json"
        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        messages = {}
        for k, v in raw_data.items():
            if isinstance(v, list):
                messages[k] = "\n".join(v)
            else:
                messages[k] = v
        return messages
    except Exception as e:
        print(f"Error loading ru.json: {e}")
        return {}


MESSAGES = _load_messages()
SUBSCRIPTION_PLANS = MESSAGES.get("SUBSCRIPTION_PLANS", {})
PAYMENT_METHODS = MESSAGES.get("PAYMENT_METHODS", {})


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
        except (KeyError, ValueError):
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
