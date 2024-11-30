# Convert.io - Универсальный конвертер медиафайлов

Convert.io - это веб-приложение на Flask для конвертации видео и аудио файлов с интуитивно понятным интерфейсом.

![Convert.io Screenshot](convertio.png)
## Возможности

- Конвертация видео файлов (MKV, AVI, MOV, WMV, FLV, WEBM, MP4)
- Конвертация аудио файлов (MP3, WAV, OGG, M4A, FLAC)
- Drag-and-drop загрузка файлов
- Отслеживание прогресса конвертации в реальном времени
- Информация о размере и типе файла
- Адаптивный дизайн
- Поддержка файлов до 1GB

## Требования

- Python 3.8+
- FFmpeg
- Зависимости из requirements.txt

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/convert.io.git
cd convert.io
```

2. Установите FFmpeg:
- Windows: Скачайте с [официального сайта](https://ffmpeg.org/download.html) и добавьте в PATH
- Linux: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`

3. Установите Python зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

1. Запустите Flask приложение:
```bash
python app.py
```

2. Откройте браузер и перейдите по адресу: http://localhost:5000

## Использование

1. Перетащите файл в область загрузки или нажмите кнопку "Выбрать файл"
2. Выберите желаемый формат конвертации из доступных
3. Нажмите "Конвертировать"
4. Дождитесь завершения конвертации
5. Скачайте готовый файл

## Структура проекта

```
convert.io/
├── app.py              # Основной файл приложения
├── requirements.txt    # Python зависимости
├── README.md          # Документация
├── static/            # Статические файлы
├── templates/         # HTML шаблоны
│   └── index.html    
└── uploads/           # Временная папка для загрузок
```

## Разработка

Для добавления новых форматов или функций:

1. Добавьте новый формат в `SUPPORTED_FORMATS` в `app.py`
2. При необходимости добавьте специфичные параметры кодирования в функцию `convert_media`
3. Обновите тесты
4. Создайте Pull Request

## Лицензия

MIT License - см. [LICENSE](LICENSE) файл.

## Автор

Zaruber+AI - [GitHub](https://github.com/Zaruber)
