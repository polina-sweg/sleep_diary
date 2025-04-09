# Sleep Diary
**Sleep Tracker** — это Django-проект для отслеживания времени и качества сна пользователя. 
## Запуск проекта
Все команды необходимо выполнять в командной строке.
### 1. Клонирование репозитория
```bash
git clone https://github.com/polina-sweg/sleep_diary.git
cd sleep_diary 
```


### 2. Создание виртуального окружения
```bash
python -m venv my_venv
source my_venv/bin/activate        # для Linux / macOS
my_venv\Scripts\activate           # для Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Создание .env файла
Cначала необходимо установить PostgreSQL, зарегистрировать там пользователя с `<username>` и паролем `<password>`  и создать базу данных с названием `<db_name>` (в `<...>`) можно указать любое название базы данных/имя пользователя/пароль).
В корневой директории необходимо создать файл `.env` со следующим содержанием:
```env
SECRET_KEY=<твой_секретный_ключ>

DB_NAME=<db_name>
DB_USER=<username>
DB_PASSWORD=<password>
DB_HOST=localhost
DB_PORT=5432
```

### 5. Применение миграций
```bash
python manage.py migrate
```

### 6. Создание супер пользователя
```bash
python manage.py createsuperuser
```

### 7. Запуск сервера
```bash
python manage.py runserver
```

После этого приложение будет доступно по адресу: `http://127.0.0.1:8000`.
