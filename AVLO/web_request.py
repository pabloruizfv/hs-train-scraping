from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, \
    NoSuchElementException, UnexpectedAlertPresentException, \
    ElementNotInteractableException, WebDriverException
from common.dates import date_object_to_string_date


def avlo_services_try(origin_station, destination_station, travel_date,
                      output_file, chromedriver_path, avlo_url, headless=True):
    """
    Launches the "avlo_services" function for a specific origin and destination
    pair of stations and for a specific date. If the process raises a
    "TimeoutException" or "NoSuchElementException" type exception, then it
    escapes it and returns False. If the process does complete without errors,
    then True boolean value is returned.
    :param origin_station: (string) origin station to request.
    :param destination_station: (string) destination station to request.
    :param travel_date: (string DD/MM/YYYY) date to request.
    :param output_file: (file object) file to which the output information will
        be written.
    :param chromedriver_path: (string) path to the chromedriver exe file.
    :param avlo_url: (string) URL path to the AVLO website.
    :param headless: (boolean) if False, the browser window will be shown. Set
        as True for speed.
    :return boolean. True if train services have been found. False otherwise.
    """
    try:
        avlo_services(origin_station, destination_station, travel_date,
                      output_file, chromedriver_path, avlo_url,
                      headless=headless)
        return True        
    except (TimeoutException, NoSuchElementException,
            UnexpectedAlertPresentException, ElementNotInteractableException,
            WebDriverException, IndexError) as _error:
        return False


def avlo_services(origin_station, destination_station, travel_date,
                  output_file,  chromedriver_path, avlo_url,
                  loading_wait_seconds=10, headless=True):
    """
    Initialises and executes the Chrome Webdriver. Uses it to retrieve the AVLO
    website. Fills in the required information in the AVLO website for the
    specified origin station, destination station and date. Then loads the
    results page and reads the existing train services for that date, with
    their departure and arrival times and prices. Writes this information to
    an output file and closes the Webdriver.
    :param origin_station: (string) origin station to request.
    :param destination_station: (string) destination station to request.
    :param travel_date: (string DD/MM/YYYY) date to request.
    :param output_file: (file object) file to which the output information will
        be written.
    :param chromedriver_path: (string) path to the chromedriver exe file.
    :param avlo_url: (string) URL path to the AVLO website.
    :param loading_wait_seconds: (float)
    :param headless: (boolean) if False, the browser window will be shown. Set
        as True for speed.
    """
    # Obtain current date and time:
    dt_now = datetime.now()
    search_date = date_object_to_string_date(dt_now)
    search_time = str(dt_now.hour).zfill(2) + ':' + str(dt_now.minute).zfill(2)
    print('{}\tSearching for \"{}\" -> \"{}\" services for date: {} in AVLO'
          .format(datetime.now(), origin_station, destination_station,
                  travel_date))

    # Enter site:
    options = Options()
    if headless:
        options.add_argument("--headless")  # to not see browser window
    driver = webdriver.Chrome(chromedriver_path, options=options)
    driver.get(avlo_url)
    webpage_title = driver.title
    print('{}\tEntered \"{}\" site successfully'.format(datetime.now(),
                                                        webpage_title))

    # Wait for the website to load the origin station field box:
    search = WebDriverWait(driver, loading_wait_seconds).until(
        EC.presence_of_element_located((By.NAME,
                                        "estacionOrigen.descEstacion")))

    # accept all cookies (not strictly necessary, but helps visually when
    # displaying window - not headless):
    if not headless:
        accept_cookies_button = driver.find_element_by_xpath(
            "//button[@id='onetrust-accept-btn-handler']")
        accept_cookies_button.click()

    # Fill in the origin station field box:
    search.send_keys(origin_station)
    time.sleep(1.5)  # wait for the dropdown options to show TODO: esperar hasta que cargue
    search.send_keys(Keys.TAB)
    # by pressing the TAB button, the field autocompletes

    # Search for the destination station field box:
    search = driver.find_element_by_name("estacionDestino.descEstacion")

    # Fill in the destination station field box:
    search.send_keys(destination_station)
    time.sleep(1.5)  # wait for the dropdown options to show
    search.send_keys(Keys.TAB)
    # by pressing the TAB button, the field autocompletes

    # Search for the date field box:
    search = driver.find_element_by_name("estacionOrigen.fecha")
    search.send_keys(travel_date)

    # TODO: buscar forma mas elegante de hacer esto:
    search = driver.find_element_by_class_name("border-color-orange")
    search.send_keys(Keys.TAB)
    search.send_keys(Keys.TAB)
    search.send_keys(Keys.TAB)
    search.send_keys(Keys.TAB)
    search.send_keys(Keys.RETURN)

    print('{}\tFilled in field boxes successfully. Waiting for response...'
          .format(datetime.now()))

    # TODO: cambiar lo de loading_wait_seconds por load como arriba
    time.sleep(loading_wait_seconds)
    search = driver.find_element_by_id("listaTrenesTBody")
    # print( search.text )

    services = driver.find_elements_by_class_name("contHistorial")
    parsed_train_services = []
    for service in services:
        service_info_list = service.text.split('\n')
        if service_info_list == ['']:
            continue
        departure_time = service_info_list[0]
        arrival_time = service_info_list[1]
        price = service_info_list[-1]  # TODO: comprobar que es un precio, bug -> raise Time...Error
        train_service = [origin_station, destination_station, travel_date,
                         departure_time, arrival_time, price, 'AVLO',
                         search_date, search_time]
        parsed_train_services.append(train_service)

    driver.quit()

    if len(parsed_train_services) == 0:
        raise TimeoutException

    for train_service in parsed_train_services:
        output_file.write('|'.join(train_service) + '\n')

    print('{}\t{} train services found ({} - {}, {}) and written in output file'
          .format(datetime.now(), len(parsed_train_services),
                  origin_station, destination_station, travel_date))

