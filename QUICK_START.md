# 🚀 Быстрый запуск VPN Telegram Bot

## ⚡ За 5 минут до запуска

### 1️⃣ Установите зависимости
```bash
pip install .
```

### 2️⃣ Настройте конфигурацию
```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте .env файл
nano .env
```

**Обязательно настройте:**
- `BOT_TOKEN` - получите у @BotFather
- `ADMIN_IDS` - ваш Telegram ID

### 3️⃣ Запустите бота
```bash
python main.py
```

## ❓ Частые проблемы

### Ошибка "ModuleNotFoundError: No module named 'telegram'"
**Решение:** Установите зависимости
```bash
pip install .
```

### Ошибка "BOT_TOKEN is required"
**Решение:** 
1. Создайте бота у @BotFather в Telegram
2. Скопируйте токен в файл `.env`

### Ошибка "At least one ADMIN_ID is required"
**Решение:**
1. Узнайте свой Telegram ID (@userinfobot)
2. Добавьте в `.env`: `ADMIN_IDS=ваш_id`

## 📞 Поддержка

Если что-то не работает:
1. Запустите `python test_setup.py` для диагностики
2. Проверьте файл `.env`
3. Убедитесь, что Python версии 3.8+

---

**🎯 После запуска бот будет доступен в Telegram и готов к работе!**