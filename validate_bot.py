#!/usr/bin/env python3
"""
Simple validation test for core functionality without external dependencies
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_localization():
    """Test localization"""
    print("🌐 Testing localization...")

    try:
        from locales.ru import get_message

        # Test message retrieval
        welcome_msg = get_message("welcome")
        assert "Добро пожаловать" in welcome_msg
        print("  ✅ Welcome message loaded correctly")

        # Test message formatting
        plan_msg = get_message(
            "plan_template",
            emoji="🥉",
            name="Тест план",
            popular_badge="",
            price=299,
            price_per_month=299,
            duration=30,
            description="Тестовое описание",
            savings="",
        )
        assert "Тест план" in plan_msg
        assert "299" in plan_msg
        print("  ✅ Message formatting works correctly")

        # Test all key messages exist
        key_messages = [
            "welcome",
            "help",
            "payment_success",
            "profile_info",
            "admin_panel",
        ]
        for key in key_messages:
            msg = get_message(key)
            assert len(msg) > 0
        print("  ✅ All key messages present")

        print("✅ Localization test passed")
        return True
    except Exception as e:
        import traceback

        print(f"❌ Localization test failed: {e}")
        traceback.print_exc()
        return False


def test_project_structure():
    """Test project structure"""
    print("📁 Testing project structure...")

    try:
        # Check if all required directories exist
        required_dirs = [
            "bot",
            "bot/handlers",
            "bot/models",
            "bot/utils",
            "bot/config",
            "locales",
        ]

        for dir_name in required_dirs:
            dir_path = os.path.join(".", dir_name)
            assert os.path.exists(dir_path), f"Directory {dir_name} missing"
        print("  ✅ All required directories exist")

        # Check if all required files exist
        required_files = [
            "bot/__init__.py",
            "bot/main.py",
            "bot/handlers/main.py",
            "bot/handlers/admin.py",
            "bot/models/database.py",
            "bot/utils/helpers.py",
            "bot/config/settings.py",
            "locales/ru.py",
            "requirements.txt",
            ".env.example",
            ".gitignore",
        ]

        for file_name in required_files:
            file_path = os.path.join(".", file_name)
            assert os.path.exists(file_path), f"File {file_name} missing"
        print("  ✅ All required files exist")

        print("✅ Project structure test passed")
        return True
    except Exception as e:
        print(f"❌ Project structure test failed: {e}")
        return False


def test_configuration_logic():
    """Test configuration logic without external dependencies"""
    print("🔧 Testing configuration logic...")

    try:
        # Test without loading external dependencies
        config_content = open("bot/config/settings.py", "r", encoding="utf-8").read()

        # Check if all required configuration options are present
        required_configs = [
            "BOT_TOKEN",
            "ADMIN_IDS",
            "DATABASE_URL",
            "SUBSCRIPTION_PLANS",
            "PLAN_1_MONTH_PRICE",
            "PLAN_3_MONTH_PRICE",
        ]

        for config in required_configs:
            assert config in config_content, f"Configuration {config} missing"
        print("  ✅ All required configurations present")

        # Check subscription plans structure
        assert "SUBSCRIPTION_PLANS = {" in config_content
        assert "'1_month':" in config_content
        assert "'3_months':" in config_content
        assert "'6_months':" in config_content
        assert "'12_months':" in config_content
        print("  ✅ Subscription plans properly configured")

        print("✅ Configuration logic test passed")
        return True
    except Exception as e:
        print(f"❌ Configuration logic test failed: {e}")
        return False


def test_database_models_structure():
    """Test database models structure"""
    print("🗄️ Testing database models structure...")

    try:
        # Read and analyze database models file
        models_content = open("bot/models/database.py", "r", encoding="utf-8").read()

        # Check if all required models are present
        required_models = [
            "class User(",
            "class Subscription(",
            "class Payment(",
            "class VPNKey(",
            "class AdminLog(",
            "DatabaseManager:",
        ]

        for model in required_models:
            assert model in models_content, f"Model {model} missing"
        print("  ✅ All required database models present")

        # Check for essential fields
        essential_fields = [
            "telegram_id",
            "username",
            "first_name",
            "referral_code",
            "plan_type",
            "start_date",
            "end_date",
            "amount",
            "payment_method",
            "status",
        ]

        for field in essential_fields:
            assert field in models_content, f"Essential field {field} missing"
        print("  ✅ All essential database fields present")

        print("✅ Database models structure test passed")
        return True
    except Exception as e:
        print(f"❌ Database models structure test failed: {e}")
        return False


def test_handlers_structure():
    """Test handlers structure"""
    print("🎮 Testing handlers structure...")

    try:
        # Test main handlers
        main_handlers_content = open(
            "bot/handlers/main.py", "r", encoding="utf-8"
        ).read()

        required_elements = [
            "router = Router()",
            "class PurchaseStates(StatesGroup):",
            "async def start_command(",
            "async def show_plans(",
            "async def select_payment_method(",
            "async def process_payment(",
            "async def verify_payment(",
            "async def show_profile(",
            "async def show_referral_info(",
        ]

        for element in required_elements:
            assert element in main_handlers_content, (
                f"Required element {element} missing in main.py"
            )
        print("  ✅ All main router and handlers present")

        # Test admin handlers
        admin_handlers_content = open(
            "bot/handlers/admin.py", "r", encoding="utf-8"
        ).read()

        admin_required_elements = [
            "router = Router()",
            "class AdminStates(StatesGroup):",
            "async def admin_panel(",
            "async def admin_users_list(",
            "async def admin_detailed_stats(",
            "async def admin_broadcast_start(",
        ]

        for element in admin_required_elements:
            assert element in admin_handlers_content, (
                f"Required element {element} missing in admin.py"
            )
        print("  ✅ All admin router and handlers present")

        print("✅ Handlers structure test passed")
        return True
    except Exception as e:
        print(f"❌ Handlers structure test failed: {e}")
        return False


def test_bot_main_structure():
    """Test main bot file structure"""
    print("🤖 Testing main bot structure...")

    try:
        main_content = open("bot/main.py", "r", encoding="utf-8").read()

        # Check for essential components
        essential_components = [
            "async def main() -> None:",
            "bot = Bot(token=Config.BOT_TOKEN)",
            "dp = Dispatcher(storage=storage)",
            "dp.include_router(admin_router)",
            "dp.include_router(main_router)",
            "await dp.start_polling(bot)",
        ]

        for component in essential_components:
            assert component in main_content, f"Component {component} missing"
        print("  ✅ All essential bot components present")

        print("✅ Main bot structure test passed")
        return True
    except Exception as e:
        print(f"❌ Main bot structure test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting VPN Bot structure and logic validation...\n")

    tests = [
        test_project_structure,
        test_localization,
        test_configuration_logic,
        test_database_models_structure,
        test_handlers_structure,
        test_bot_main_structure,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Validation Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All validations passed! Bot structure is correct and ready.")
        print("💡 To run the bot:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Configure .env file with your bot token")
        print("   3. Run: python bot/main.py")
        return True
    else:
        print("❌ Some validations failed. Please check the code structure.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
