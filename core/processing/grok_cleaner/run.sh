#!/bin/bash
# Запуск Grok Batch Cleaner
# Использование: bash run.sh  или двойной клик

cd "$(dirname "$0")"

# Проверяем Python
if ! command -v python3 &>/dev/null; then
  echo "Python3 не найден. Установите Python с python.org"
  exit 1
fi

# Устанавливаем зависимости (один раз)
python3 -m pip install -r requirements.txt -q

# Запускаем приложение
python3 app.py
