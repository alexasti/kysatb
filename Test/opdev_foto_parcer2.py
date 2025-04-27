import asyncio
import time
from playwright.async_api import async_playwright

# Твои данные
LOGIN_URL = 'https://opdev.ru/'
TARGET_URL = 'https://opdev.ru/catalog/opticheskie_nablyudatelnye_pribory/pritsely_dnevnye_kollimatornye/pritsely_dnevnye_brite/pritsel_opticheskiy_brite_wa8x_2_16x50_sf_ir/'

USER_LOGIN = '9896600@mail.ru'
USER_PASSWORD = '89111664848'

async def run():
    print("Привет! Запускаем парсер через Playwright...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=True если нужно без окна
        page = await browser.new_page()

        # Переходим на главную
        await page.goto(LOGIN_URL)
        print("Открыли сайт")

        # Ждём появления полей
        await page.wait_for_selector('input[name="USER_LOGIN"]')
        await page.wait_for_selector('input[name="USER_PASSWORD"]')

        # Вводим логин и пароль
        await page.fill('input[name="USER_LOGIN"]', USER_LOGIN)
        await page.fill('input[name="USER_PASSWORD"]', USER_PASSWORD)

        # Нажимаем кнопку "Войти"
        await page.get_by_role("button", name="Войти").click()

        # Ждём, когда залогинимся
        await page.wait_for_load_state('networkidle')
        print("Успешно авторизовались!")

        # Теперь переходим на страницу товара
        await page.goto(TARGET_URL, timeout=60000)
        await page.wait_for_load_state('networkidle')
        print("Страница товара открыта!")

        # Ищем все кнопки с картинками
        buttons = await page.query_selector_all('.product-images-thumbs button')

        if not buttons:
            print("Не нашли кнопки с картинками 😢")
        else:
            print(f"Нашли {len(buttons)} изображений:")

            # Сохраняем результаты в список
            image_urls = []
            for button in buttons:
                style = await button.get_attribute('style')
                if style:
                    # Вытащим URL из стиля background-image
                    import re
                    match = re.search(r'url\(["\']?(.*?)["\']?\)', style)
                    if match:
                        relative_url = match.group(1)
                        full_url = 'https://opdev.ru' + relative_url
                        image_urls.append(full_url)
            
            # Сначала выводим список на каждой новой строке
            for url in image_urls:
                print(url)

            # Затем добавляем два разрыва строки и текст "и для переноса в Excel:"
            print("\n\nи для переноса в Excel:")

            # Выводим список с разделителями ", " в одну строку
            print(", ".join(image_urls))

        await browser.close()

asyncio.run(run())