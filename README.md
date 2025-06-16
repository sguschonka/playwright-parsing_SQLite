# playwright-parsing_SQLite

playwright на данный момент мой фаворит
он поддерживает асинхронность, удобен и понятен.
его метод locator очень похож на querySelector из js и его одного может быть достаточно для веб-скреёпинга
а вот SQLite параша лучше интегрировать сразу в хорошие базы данных PostreSQL или MongoDB ну на крайний случай MySQL который хуево работает на виндовс и никогда в жизни ты его не удалишь
или в эксель его хватит сполна и он более понятен и работать с ним приятнее и менее геморрно

Ты прислал два файла: `db.py` и `parser.py`, и базу данных `books.db`. Вот подробное объяснение кода, как для учебного пособия.

---

## 🔹 1. `db.py` — Работа с базой данных SQLite

Этот файл создаёт базу данных `books.db`, если её ещё нет, и таблицу `books`.

### Структура таблицы

```sql
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price TEXT,
    status TEXT,
    link TEXT UNIQUE
)
```

* `id`: автоинкрементируемый первичный ключ.
* `title`: название книги.
* `price`: цена.
* `status`: наличие ("In stock", "Out of stock").
* `link`: уникальная ссылка на книгу (ключ `UNIQUE` предотвращает дублирование).

### Функция вставки книги

```python
def insert_book(book: dict):
    cursor.execute("""
        INSERT OR IGNORE INTO books (title, price, status, link)
        VALUES (?, ?, ?, ?)
    """, (
        book['title'],
        book['price'],
        book['status'],
        book['link']
    ))
    connection.commit()
```

* Используется `INSERT OR IGNORE`, чтобы избежать ошибок при повторной вставке книги с той же ссылкой.
* `connection.commit()` сохраняет изменения в БД.

### Для проверки

Если запустить `db.py` напрямую:

```python
if __name__ == "__main__":
    insert_book({
        'title': 'Тестовая книга',
        'price': '£0.00',
        'status': 'In stock',
        'link': 'https://books.toscrape.com/catalogue/test-book'
    })
```

Будет добавлена одна тестовая книга.

---

## 🔹 2. `parser.py` — Асинхронный парсер на Playwright + SQLite

Это основной скрипт, который:

* обходит сайт [https://books.toscrape.com](https://books.toscrape.com);
* собирает данные о книгах;
* записывает их в SQLite через `insert_book`.

### Внешние зависимости

```python
from playwright.async_api import async_playwright
import asyncio
from datetime import datetime
from db import insert_book
import sqlite3
```

---

### Главная функция `parse()`

Асинхронная функция для парсинга сайта.

```python
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto('https://books.toscrape.com/')
```

* `async_playwright` — запускаем асинхронно Playwright.
* `headless=True` — без отображения браузера.
* Загружаем главную страницу сайта с книгами.

---

### Цикл пагинации и сбора данных

```python
while True:
    book_content = page.locator('article.product_pod')
    count = await book_content.count()
```

* `article.product_pod` — блок с книгой.
* Считаем, сколько книг на странице.

---

### Цикл по каждой книге

```python
for e in range(count):
    book_name = await book_content.nth(e).locator('h3 > a').get_attribute('title')
    book_price = await book_content.nth(e).locator('div.product_price > p.price_color').text_content()
    book_status = await book_content.nth(e).locator('p.instock.availability').inner_text()
    book_link = await book_content.nth(e).locator('h3 > a').get_attribute('href')
```

* Извлекаем:

  * `title` — из атрибута `title` ссылки.
  * `price` — текст из блока `.price_color`.
  * `status` — текст о наличии.
  * `link` — относительная ссылка на книгу.

Добавляем к ссылке префикс `https://books.toscrape.com/catalogue/`.

---

### Запись в БД

```python
insert_book({
    'title': book_name,
    'price': book_price,
    'status': book_status,
    'link': 'https://books.toscrape.com/catalogue/' + book_link,
})
```

---

### Переход на следующую страницу

```python
if await page.locator('li.next a').count() > 0:
    await page.locator('li.next a').click()
else:
    break
```

Если есть кнопка «Next» — кликаем. Иначе выходим из цикла.

---

### После сбора

```python
connection = sqlite3.connect('books.db')
cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM books")
total = cursor.fetchone()[0]
print(f'Всего уникальных книг в базе: {total}')
connection.close()
```

* Подключаемся к БД.
* Считаем количество книг.
* Выводим итог.

---

### Запуск скрипта

```python
if __name__ == '__main__':
    asyncio.run(main())
```

---

## 📌 Краткое резюме

| Компонент     | Назначение                                              |
| ------------- | ------------------------------------------------------- |
| `playwright`  | Асинхронный браузер для парсинга динамических страниц.  |
| `sqlite3`     | Простая локальная база данных.                          |
| `insert_book` | Вставляет книгу, избегая дубликатов.                    |
| `parser.py`   | Обходит все страницы сайта, сохраняет уникальные книги. |

---

