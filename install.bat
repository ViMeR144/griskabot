@echo off
echo Установка библиотек для бота...
python -m pip install aiogram==3.4.1
python -m pip install python-dotenv==1.0.0
python -m pip install aiohttp==3.9.1
echo.
echo Установка завершена!
echo Теперь можно запустить бота: python bot.py
pause

