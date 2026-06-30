# ✍️ MiniBlog

[![Maintainability](https://qlty.sh/gh/sigmachyo322/projects/miniblog/maintainability.svg)](https://qlty.sh/gh/sigmachyo322/projects/miniblog)

Минималистичный блог на Flask с авторизацией, CRUD-статьями и чистым интерфейсом.

![Демонстрация](/home/sigma/College-coding/miniblog/demo.gif)

## Стек

| Слой | Технология |
|------|-----------|
| Backend | Python 3.11, Flask 3.0 |
| ORM | Flask-SQLAlchemy |
| База данных | SQLite (dev) |
| Frontend | HTML5, CSS (без фреймворков) |
| Деплой | Render.com |

## Функциональность

- Регистрация и авторизация пользователей
- Публикация, редактирование и удаление статей
- Лента всех статей на главной
- Личный кабинет «Мои статьи»

## Запуск локально

```bash
git clone https://github.com/YOUR_USERNAME/miniblog.git
cd miniblog
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Открыть: http://127.0.0.1:5000

## Тестовые данные

| Поле | Значение |
|------|----------|
| login | admin |
| password | admin123 |

## Деплой

🔗 https://ztsche.pythonanywhere.com/

## Лицензия

MIT
