import time  # Модуль для роботи з часом, використовується для затримок між діями.
import logging  # Модуль для логування (запису повідомлень про виконання програми).
import random  # Модуль для генерації випадкових чисел, використовується для рандомних затримок між діями.
from selenium import webdriver  # Імпортуємо основний модуль Selenium для роботи з браузером.
from selenium.webdriver.chrome.service import \
    Service as ChromiumService  # Імпортуємо сервіс для запуску драйвера для браузера Chrome.
from webdriver_manager.chrome import \
    ChromeDriverManager  # Модуль для автоматичного завантаження та управління драйверами Chrome.
from selenium.webdriver.chrome.options import Options  # Модуль для налаштування опцій браузера Chrome.
from selenium.webdriver.common.keys import \
    Keys  # Модуль для відправки клавіатурних команд (наприклад, натискання Enter).
from webdriver_manager.core.os_manager import \
    ChromeType  # Тип браузера для вказівки, що ми використовуємо Chromium (замість стандартного Chrome).
from selenium.webdriver.common.by import \
    By  # Модуль для пошуку елементів на веб-сторінці за різними параметрами (ID, CSS, XPath тощо).
from selenium.webdriver.support.ui import \
    WebDriverWait  # Модуль для налаштування явних затримок (waits) при пошуку елементів.
from selenium.webdriver.support import \
    expected_conditions as EC  # Модуль для налаштування умов, при яких елементи будуть знайдені чи готові до дій.
from dotenv import load_dotenv  # Модуль для завантаження змінних середовища з файлу .env.
import os  # Модуль для роботи з операційною системою, зокрема для доступу до змінних середовища та файлів.

# Завантажуємо змінні середовища з .env файлу
load_dotenv()

# Налаштування логування
logging.basicConfig(
    filename='out.log',  # Файл, в який будуть записуватись логи.
    level=logging.INFO,
    # Мінімальний рівень логів (INFO означає інформативні повідомлення, включаючи попередження та помилки).
    format='%(asctime)s - %(levelname)s - %(message)s'  # Формат виведення логів (час, рівень логування, повідомлення).
)


# Функція для налаштування драйвера (на моїй системі працює коректно лише з такими налаштуваннями)
def setup_driver():
    logging.info("Запуск Selenium WebDriver...")  # Логування старту запуску драйвера.
    options = Options()  # Створюємо об'єкт для налаштування опцій браузера.
    options.add_argument("--headless")  # Запускаємо браузер без графічного інтерфейсу (фоновий режим).
    options.add_argument("--no-sandbox")  # Відключення пісочниці для безпеки.
    options.add_argument(
        "--disable-dev-shm-usage")  # Відключення використання спільної пам'яті.
    options.add_argument("--remote-debugging-port=9222")  # Відкриваємо порт для віддаленого налагодження.

    # Створюємо об'єкт сервісу для драйвера, вказуючи шлях до інстальованого драйвера.
    service = ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service,
                              options=options)  # Створюємо екземпляр веб-драйвера Chrome з вказаними опціями.

    logging.info("Драйвер запущено.")  # Логування запуску драйвера.
    return driver  # Повертаємо драйвер для подальшого використання.


# Функція для входу в LinkedIn
def login_linkedin(driver, email, password):
    try:
        logging.info("Переходимо на сторінку входу в LinkedIn.")
        driver.get("https://www.linkedin.com/login")  # Відкриваємо сторінку входу в LinkedIn.

        # Знаходимо елементи для введення логіна та пароля.
        email_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")

        logging.info("Вводимо дані для входу.")
        email_input.send_keys(email)  # Вводимо email в поле логіну.
        password_input.send_keys(password)  # Вводимо пароль в поле пароля.

        # Натискаємо клавішу Enter для підтвердження входу.
        password_input.send_keys(Keys.RETURN)

        # Випадкова затримка між діями (для імітації більш природної взаємодії).
        time.sleep(random.uniform(2, 5))  # Чекаємо випадкову кількість секунд від 2 до 5.

        # Перевірка наявності кнопки "Sign in using another account" (якщо є, то натискаємо її).
        try:
            logging.info("Перевіряємо наявність кнопки для входу іншим акаунтом.")
            sign_in_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button.artdeco-list__item.signin-other-account'))
            )
            sign_in_button.click()  # Натискаємо на кнопку для входу іншим акаунтом.
            logging.info("Натиснута кнопка для входу іншим акаунтом.")

            # Випадкова затримка перед повторним введенням даних.
            time.sleep(random.uniform(2, 4))

            # Повторне введення логіна та пароля.
            email_input = driver.find_element(By.ID, "username")
            password_input = driver.find_element(By.ID, "password")
            email_input.send_keys(email)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)  # Натискаємо Enter для підтвердження входу.

            # Випадкова затримка після повторного введення даних.
            time.sleep(random.uniform(2, 5))

        except Exception as e:
            logging.info("Кнопка для входу іншим акаунтом не знайдена.")

        # Перевірка успішності входу.
        if "feed" in driver.current_url:  # Якщо URL містить 'feed', значить вхід успішний.
            logging.info("Вхід до LinkedIn успішний.")
        else:
            logging.error("Вхід до LinkedIn не вдалося виконати.")

    except Exception as e:
        logging.error(f"Помилка при вході в LinkedIn: {e}")  # Логування помилки, якщо щось пішло не так.


# Функція для отримання фотографії профілю
def get_profile_photo(driver):
    try:
        logging.info("Переходимо на сторінку профілю.")
        profile_url = os.getenv("URL")  # Отримуємо URL профілю зі змінного середовища.
        driver.get(profile_url)  # Відкриваємо сторінку профілю.

        # Випадкова затримка перед взаємодією з елементами.
        time.sleep(random.uniform(2, 5))

        # Чекаємо, поки кнопка редагування фотографії стане доступною.
        edit_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.profile-photo-edit__edit-btn'))
        )
        edit_button.click()  # Натискаємо кнопку для редагування фотографії профілю.
        logging.info("Натиснута кнопка для редагування фотографії профілю.")

        # Випадкова затримка перед завантаженням фотографії.
        time.sleep(random.uniform(2, 5))

        # Чекаємо, поки зображення профілю стане доступним.
        photo_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.imgedit-profile-photo-frame-viewer__image-container img'))
        )

        # Отримуємо URL фотографії.
        photo_url = photo_element.get_attribute("src")
        logging.info(f"Фотографія профілю знайдена: {photo_url}")

        return photo_url  # Повертаємо URL фотографії.

    except Exception as e:
        logging.error(
            f"Помилка при отриманні фотографії профілю: {e}")  # Логування помилки, якщо не вдалося отримати фото.
        return None  # Якщо не вдалося отримати фото, повертаємо None.


# Основна логіка
def main():
    driver = setup_driver()  # Ініціалізація драйвера.

    # Отримуємо email та пароль з .env файлу.
    email = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")

    login_linkedin(driver, email, password)  # Викликаємо функцію для входу в LinkedIn.

    # Отримуємо URL фотографії профілю.
    photo_url = get_profile_photo(driver)
    if photo_url:
        print(f"URL фотографії профілю: {photo_url}")
    else:
        logging.error("Не вдалося отримати фотографію профілю.")  # Логування, якщо фото не знайдено.

    # Закриваємо браузер після виконання.
    driver.quit()

if __name__ == "__main__":
    main()  # Запуск основної функції.
