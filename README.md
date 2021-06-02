# Impftermin Berlin Bot

A simple script for getting a COVID-19 vaccination appointment ("Impftermin") in Berlin.
The bot will open a browser windows with Doctolib and will play a sound as soon as an time slot is available so you can continue booking the slot.

![Example](https://github.com/malteos/covid-vaccination-appointment/raw/master/demo.gif)

### Requirements
- Python 3.6+
- Firefox
- Selenium + Webdriver

### Installation

- Selenium https://selenium-python.readthedocs.io/installation.html
- Python packages `pip install -r requirements.txt`


### Run
```bash
# Open a Firefox window and play a sound when an appointment was found
python bot.py

# Close with CRTL+C or STRG+C
```

You can enable email notification by setting the following environment variables: `SENDER_EMAIL, RECEIVER_EMAIL, SMTP_SERVER, SMTP_PORT, SMTP_LOGIN, SMTP_PASSWORD`

## License

MIT
