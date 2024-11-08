import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    filename='out.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Функція для налаштування драйвера
def setup_driver():
    logging.info("Запуск Selenium WebDriver...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")

    service = ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=options)

    logging.info("Драйвер запущено.")
    return driver

# Функція для входу в LinkedIn
def login_linkedin(driver, email, password):
    try:
        logging.info("Переходимо на сторінку входу в LinkedIn.")
        driver.get("https://www.linkedin.com/login")

        # Знаходимо елементи для введення логіна та пароля.
        email_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")

        logging.info("Вводимо дані для входу.")
        email_input.send_keys(email)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        time.sleep(random.uniform(2, 5))

        # Перевірка на CAPTCHA
        if check_captcha(driver):
            logging.error("CAPTCHA виявлено! Вхід не вдалося виконати.")
            return False

        # Перевірка наявності кнопки для входу іншим акаунтом
        try:
            logging.info("Перевіряємо наявність кнопки для входу іншим акаунтом.")
            sign_in_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button.artdeco-list__item.signin-other-account'))
            )
            sign_in_button.click()
            logging.info("Натиснута кнопка для входу іншим акаунтом.")
            time.sleep(random.uniform(2, 4))

            email_input = driver.find_element(By.ID, "username")
            password_input = driver.find_element(By.ID, "password")
            email_input.send_keys(email)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(random.uniform(2, 5))

            # Додаткова перевірка на CAPTCHA після повторного входу
            if check_captcha(driver):
                logging.error("CAPTCHA виявлено після повторного входу! Вхід не вдалося виконати.")
                return False

        except Exception as e:
            logging.info("Кнопка для входу іншим акаунтом не знайдена.")

        # Перевірка успішності входу
        if "feed" in driver.current_url:
            logging.info("Вхід до LinkedIn успішний.")
            return True
        else:
            logging.error("Вхід до LinkedIn не вдалося виконати.")
            return False

    except Exception as e:
        logging.error(f"Помилка при вході в LinkedIn: {e}")
        return False

# Функція для перевірки на CAPTCHA
def check_captcha(driver):
    try:
        # Перевірка на наявність елемента, пов'язаного з CAPTCHA (можливо, текст "I’m not a robot" або форма CAPTCHA)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'I’m not a robot')]"))
        )
        logging.warning("CAPTCHA виявлено!")
        return True
    except:
        return False

# Функція для отримання фотографії профілю
def get_profile_photo(driver):
    try:
        logging.info("Переходимо на сторінку профілю.")
        profile_url = os.getenv("URL")
        driver.get(profile_url)
        time.sleep(random.uniform(2, 5))

        # Перевірка на CAPTCHA при переході на сторінку профілю
        if check_captcha(driver):
            logging.error("CAPTCHA виявлено при завантаженні профілю. Операцію скасовано.")
            return None

        edit_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.profile-photo-edit__edit-btn'))
        )
        edit_button.click()
        logging.info("Натиснута кнопка для редагування фотографії профілю.")
        time.sleep(random.uniform(2, 5))

        photo_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.imgedit-profile-photo-frame-viewer__image-container img'))
        )
        photo_url = photo_element.get_attribute("src")
        logging.info(f"Фотографія профілю знайдена: {photo_url}")

        return photo_url

    except Exception as e:
        logging.error(f"Помилка при отриманні фотографії профілю: {e}")
        return None

# Основна логіка
def main():
    driver = setup_driver()

    email = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")

    if login_linkedin(driver, email, password):
        photo_url = get_profile_photo(driver)
        if photo_url:
            print(f"URL фотографії профілю: {photo_url}")
        else:
            logging.error("Не вдалося отримати фотографію профілю.")
    else:
        logging.error("Не вдалося виконати вхід через CAPTCHA.")

    driver.quit()

if __name__ == "__main__":
    main()
