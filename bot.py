import telebot
import os
import subprocess
import ctypes
import urllib.request
import pyautogui
from PIL import Image

# ВСТАВЬ СВОЙ ТОКЕН
TOKEN = "ТВОЙ_ТОКЕН_БОТА"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я твой ПК-ассистент.\n\n"
                          "/screenshot - Скриншот\n"
                          "/cmd [команда] - Выполнить команду\n"
                          "/shutdown - Выключить ПК\n"
                          "/reboot - Перезагрузить ПК\n"
                          "/wallpaper [ссылка] - Сменить обои по ссылке")

@bot.message_handler(commands=['screenshot'])
def screenshot(message):
    try:
        img = pyautogui.screenshot()
        img.save("screen.png")
        with open("screen.png", "rb") as photo:
            bot.send_photo(message.chat.id, photo)
        os.remove("screen.png")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['cmd'])
def cmd(message):
    command = message.text.replace("/cmd ", "")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        bot.reply_to(message, f"Результат:\n{output[:4000]}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    bot.reply_to(message, "Выключаю ПК через 5 секунд...")
    os.system("shutdown /s /t 5")

@bot.message_handler(commands=['reboot'])
def reboot(message):
    bot.reply_to(message, "Перезагружаю ПК через 5 секунд...")
    os.system("shutdown /r /t 5")

@bot.message_handler(commands=['wallpaper'])
def wallpaper(message):
    # Получаем ссылку из сообщения
    url = message.text.replace("/wallpaper ", "").strip()
    if not url.startswith("http"):
        bot.reply_to(message, "Пожалуйста, укажи прямую ссылку на картинку (начинается с http).")
        return
    
    try:
        # Скачиваем картинку
        img_path = os.path.join(os.environ["TEMP"], "wallpaper.jpg")
        urllib.request.urlretrieve(url, img_path)
        
        # Меняем обои на Windows
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, img_path, 3)
        
        bot.reply_to(message, "Обои успешно изменены!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при смене обоев: {e}")

print("Бот запущен...")
bot.infinity_polling()