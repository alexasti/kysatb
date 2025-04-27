import asyncio
import time
from playwright.async_api import async_playwright

# Твои данные
LOGIN_URL = 'https://opdev.ru/'
TARGET_URL = 'https://opdev.ru/catalog/opticheskie_nablyudatelnye_pribory/pritsely_dnevnye_kollimatornye/pritsely_dnevnye_brite/pritsel_opticheskiy_brite_wa8x_2_16x50_sf_ir/'

USER_LOGIN = '9896600@mail.ru'
USER_PASSWORD = '89111664848'

# Функция для отсчета времени с обновлением в реальном времени
async def countdown_timer(step_name, duration, stop_event):
    start_time = time.time()
    print(step_name)  # Печатаем описание этапа один раз
    while not stop_event.is_set():  # Проверяем, если остановка не активирована
        elapsed_time = time.time() - start_time
        remaining_time = max(0, duration - int(elapsed_time))  # Считаем оставшееся время
        print(f"{remaining_time} секунд осталось", end="\r", flush=True)  # Обновляем только цифры секунд
        if remaining_time <= 0:
            break
        await asyncio.sleep(1)
    print(f"{remaining_time} секунд осталось")  # Завершаем вывод с нулем

async def run():
    start_time = time.time()  # Засекаем время начала выполнения скрипта

    print("Привет! Запускаем парсер через Playwright...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=True если нужно без окна
        page = await browser.new_page()

        # Этап 1: Ожидаем открытия сайта и ждем авторизацию
        stop_event = asyncio.Event()  # Ожидаем события остановки
        timer_task = asyncio.create_task(countdown_timer("Открыли сайт\nЖдем авторизацию...", 30, stop_event))  # Запускаем таймер в фоновом потоке
        await page.goto(LOGIN_URL)  # Основной шаг (переход на сайт)
        stop_event.set()  # Завершаем таймер сразу, когда страница открыта
        await timer_task  # Ждем завершения таймера
        print("Открыли сайт")

        # Этап 2: Вводим логин и пароль
        await page.wait_for_selector('input[name="USER_LOGIN"]')
        await page.wait_for_selector('input[name="USER_PASSWORD"]')
        await page.fill('input[name="USER_LOGIN"]', USER_LOGIN)
        await page.fill('input[name="USER_PASSWORD"]', USER_PASSWORD)
        await page.get_by_role("button", name="Войти").click()

        # Этап 3: Ожидаем успешную авторизацию
        stop_event.clear()  # Сбросим стоп-сигнал для следующего этапа
        timer_task = asyncio.create_task(countdown_timer("Успешно авторизовались!\nОткрываем страницу товара...", 30, stop_event))
        await page.wait_for_load_state('networkidle')
        stop_event.set()  # Завершаем таймер сразу, когда страница загрузилась
        await timer_task
        print("Успешно авторизовались!")

        # Этап 4: Переходим на страницу товара
        await page.goto(TARGET_URL)
        stop_event.clear()
        timer_task = asyncio.create_task(countdown_timer("Страница товара открыта!\nИщем фотографии...", 30, stop_event))
        await page.wait_for_load_state('networkidle')
        stop_event.set()
        await timer_task
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

        # Замеряем общее время выполнения
        total_time = time.time() - start_time
        print(f"\nЗатрачено секунд на выполнение всех этапов: {total_time:.0f} 🙂")

        await browser.close()

# Начинаем выполнение
asyncio.run(run())
