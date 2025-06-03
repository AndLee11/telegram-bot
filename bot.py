import subprocess
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Ваш токен от @BotFather
TOKEN = "7618757786:AAGS313s1k5_v257KlqGKBqPSZ27lTE5Z8s"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Получена команда /start")
    await update.message.reply_text("Бот работает! Используйте /photo для съемки или /lamp для управления лампочками:\n/lamp 1 — включить первую лампочку\n/lamp 2 — включить вторую лампочку\n/lamp off — выключить обе.")

async def take_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Получена команда /photo")
    try:
        if os.path.exists("snapshot.jpg"):
            os.remove("snapshot.jpg")
            print("Старая фотография snapshot.jpg удалена")

        os.environ["SDL_VIDEODRIVER"] = "dummy"
        result = subprocess.run(['python3', './camera.py'], capture_output=True, text=True)  # Изменено на camera.py
        print(f"Результат camera.py: {result.stdout}")
        print(f"Ошибки camera.py: {result.stderr}")

        if os.path.exists("snapshot.jpg"):
            print("Файл snapshot.jpg найден, пытаюсь отправить...")
            await update.message.reply_text("Фото успешно сделано! Отправляю...")
            file_size = os.path.getsize("snapshot.jpg") / (1024 * 1024)  # Размер в МБ
            print(f"Размер файла: {file_size:.2f} МБ")
            if file_size > 10:
                await update.message.reply_text("Ошибка: файл слишком большой (>10 МБ)")
                return
            with open("snapshot.jpg", "rb") as photo:
                print("Файл открыт, отправляю в Telegram...")
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
                print("Фото успешно отправлено!")
        else:
            print("Файл snapshot.jpg не найден")
            await update.message.reply_text("Ошибка: файл snapshot.jpg не найден. Вывод скрипта: " + result.stdout + "\nОшибки: " + result.stderr)
    except Exception as e:
        print(f"Ошибка в take_photo: {str(e)}")
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

async def toggle_lamp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Получена команда /lamp")
    try:
        args = context.args
        if not args or len(args) != 1:
            await update.message.reply_text("Укажите параметр: /lamp 1, /lamp 2 или /lamp off")
            return

        command = args[0].lower()
        if command == "1":
            lamp_state = [1, 0]
            response_message = "Включена первая лампочка (1:0)."
        elif command == "2":
            lamp_state = [0, 1]
            response_message = "Включена вторая лампочка (0:1)."
        elif command == "off":
            lamp_state = [0, 0]
            response_message = "Обе лампочки выключены (0:0)."
        else:
            await update.message.reply_text("Неверный параметр. Используйте: /lamp 1, /lamp 2 или /lamp off")
            return

        result = subprocess.run(['node', './index.js', str(lamp_state[0]), str(lamp_state[1])], capture_output=True, text=True)
        print(f"Результат index.js (stdout): {result.stdout}")
        print(f"Ошибки index.js (stderr): {result.stderr}")
        print(f"Код возврата index.js: {result.returncode}")

        if "ok" in result.stdout.lower():
            await update.message.reply_text(response_message)
        else:
            error_message = result.stderr if result.stderr else result.stdout
            await update.message.reply_text(f"Ошибка при управлении лампочками:\nВывод: {result.stdout}\nОшибки: {error_message}")
    except Exception as e:
        print(f"Ошибка в toggle_lamp: {str(e)}")
        await update.message.reply_text(f"Произошла ошибка: {str(e)}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Произошла ошибка: {context.error}")
    if update:
        await update.message.reply_text(f"Произошла ошибка: {context.error}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("photo", take_photo))
    app.add_handler(CommandHandler("lamp", toggle_lamp))
    app.add_error_handler(error_handler)
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
