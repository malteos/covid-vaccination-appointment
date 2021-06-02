import logging
import os
import random
import smtplib
import ssl
import time

import beepy
from selenium.common.exceptions import NoSuchElementException
from seleniumwire import webdriver

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

requests_logger = logging.getLogger('seleniumwire')
requests_logger.setLevel(logging.ERROR)

DELAY = max(int(os.environ.get('DELAY', 1)), 1)  # at least = 1
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900

# Email notifications
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')
SMTP_SERVER = os.environ.get('SMTP_SERVER')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 1))
SMTP_LOGIN = os.environ.get('SMTP_LOGIN')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0'
START_URL = 'https://www.doctolib.de/institut/berlin/ciz-berlin-berlin?pid=practice-158431'  # Arena Berlin

def send_mail():
    if SENDER_EMAIL and RECEIVER_EMAIL and SMTP_SERVER and SMTP_LOGIN and SMTP_PORT and SMTP_PASSWORD:
        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            # server.ehlo()  # Can be omitted
            # server.starttls(context=context)
            # server.ehlo()  # Can be omitted
            server.login(SMTP_LOGIN, SMTP_PASSWORD)
            message = """\
            Subject: New slot found
        
            Have a look at your browser!."""

            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)
    else:
        logger.info('No email credentials provided')


cookies_selector = '#didomi-notice-agree-button'
practice_selector = '.dl-profile-card .dl-chip-large a'

# button.dl-button-small-primary
availabilities_selector = '.dl-desktop-availabilities-overlay .availabilities-message button'

slot_selector = '.dl-desktop-availabilities-days .availabilities-slots .availabilities-slot'  # click first
# e.g., aria-label="Mo., 7. Juni, 09:50"

confirm_selector = '.dl-appointment-rule .dl-button-check-inner'  # click on last

# Prepare browser
options = webdriver.FirefoxOptions()
options.add_argument(f"user-agent={USER_AGENT}")

driver = webdriver.Firefox(firefox_options=options)
driver.set_window_position(0, 0)
driver.set_window_size(SCREEN_WIDTH, SCREEN_HEIGHT)

driver.implicitly_wait(60)  # the implicit wait is set for the life of the WebDriver object

logger.info('Open start url')
driver.get(START_URL)

# play sound as test
beepy.beep(sound="ready")

logger.info('Click on cookie banner')
driver.find_element_by_css_selector(cookies_selector).click()

clicks = 0

while True:
    practices = driver.find_elements_by_css_selector(practice_selector)
    # logger.info(f'Practices found: {len(practices)}')

    if len(practices) < 1:
        logger.error('No practices available')
        break

    # TODO not random
    practice = random.choice(practices)

    logger.info(f'Click #{clicks} on {practice.text}')
    practice.click()

    time.sleep(DELAY * 1)

    # Next availabilities ...
    try:
        availabilities = driver.find_element_by_css_selector(availabilities_selector)
        availabilities.click()
        logger.info(f'Click on {availabilities.text}')
        time.sleep(1)
    except NoSuchElementException:
        logger.info('No other availabilities')
        pass

    # Slots already visible?
    slots = driver.find_elements_by_css_selector(slot_selector)

    if len(slots) > 0:
        slot = slots[0]  # first available slot
        logger.info(f'Click on slot: {slot.text}')
        slot.click()
        time.sleep(DELAY * 1)
        beepy.beep(sound="ready")

        # Second slot
        second_slots = driver.find_elements_by_css_selector(slot_selector)
        if len(second_slots) > 0:
            second_slot = second_slots[0]  # first available slot
            logger.info(f'Click on second_slot: {second_slot.text}')
            second_slot.click()
            time.sleep(1 * DELAY)

            # alert email!
            for i in range(3):
                #print('\a')  # play beep when run in terminal
                beepy.beep(sound="success")
            send_mail()

            logger.info('stop - bot will not click again. now it is your turn!')
            break

    # sleep before click again
    logger.info('No slot found.. sleep and click again...')
    time.sleep(3)

    clicks += 1

logger.info('done')
