from playwright.async_api import async_playwright
import asyncio
from datetime import datetime
from db import insert_book
import sqlite3


filename = f"результаты_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"


async def parse():
    data = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://books.toscrape.com/')
        while True:
            book_content = page.locator('article.product_pod')
            count = await book_content.count()
            for e in range(count):
                book_name = await book_content.nth(e).locator('h3 > a').get_attribute('title')
                book_price = await book_content.nth(e).locator('div.product_price > p.price_color').text_content()
                book_status = await book_content.nth(e).locator('p.instock.availability').inner_text()
                book_link = await book_content.nth(e).locator('h3 > a').get_attribute('href')
                insert_book({
                    'title': book_name,
                    'price': book_price,
                    'status': book_status,
                    'link': 'https://books.toscrape.com/catalogue/' + book_link,
                })
            if await page.locator('li.next a').count() > 0:
                await page.locator('li.next a').click()
            else:
                break
    connection = sqlite3.connect('books.db')
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    total = cursor.fetchone()[0]
    print(f'Всего уникальных книг в базе: {total}')
    connection.close()
    await browser.close()


async def main():
    await parse()


if __name__ == '__main__':
    asyncio.run(main())
