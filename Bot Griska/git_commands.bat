@echo off
echo ========================================
echo  Загрузка бота на GitHub
echo ========================================
echo.

echo ШАГ 1: Инициализация Git...
git init

echo.
echo ШАГ 2: Добавление файлов...
git add .

echo.
echo ШАГ 3: Создание коммита...
git commit -m "Initial commit: College bot"

echo.
echo ШАГ 4: Переименование ветки...
git branch -M main

echo.
echo ========================================
echo  ВАЖНО: Теперь нужно добавить удаленный репозиторий!
echo ========================================
echo.
echo Выполните вручную (замените URL на ваш):
echo git remote add origin https://github.com/ВАШ-USERNAME/college-bot.git
echo git push -u origin main
echo.
pause

