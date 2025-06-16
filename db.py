import sqlite3

connection = sqlite3.connect('books.db')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price TEXT,
    status TEXT,
    link TEXT UNIQUE
)
""")


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


if __name__ == "__main__":
    insert_book({
        'title': 'Тестовая книга',
        'price': '£0.00',
        'status': 'In stock',
        'link': 'https://books.toscrape.com/catalogue/test-book'
    })
    print("Книга добавлена в базу.")
