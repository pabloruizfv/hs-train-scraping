from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, \
    NoSuchElementException, UnexpectedAlertPresentException, \
    ElementNotInteractableException
import time
from common.dates import date_object_to_string_date


def ouigo_services_try(origin_station, destination_station, travel_date,
                       output_file,  chromedriver_path, ouigo_url,
                       headless=True):
    """
    Launches the "ouigo_services" function for a specific origin and destination
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
    :param ouigo_url: (string) URL path to the OUIGO website.
    :param headless: (boolean) if False, the browser window will be shown. Set
        as True for speed.
    :return boolean. True if train services have been found. False otherwise.
    """
    try:
        ouigo_services(origin_station, destination_station, travel_date,
                       output_file, chromedriver_path, ouigo_url,
                       headless=headless)
        return True

    except (TimeoutException, NoSuchElementException,
            UnexpectedAlertPresentException, ElementNotInteractableException) \
            as _error:
        return False


def ouigo_services(origin_station, destination_station, travel_date,
                   output_file, chromedriver_path, ouigo_url, headless=True):
    """
    Initialises and executes the Chrome Webdriver. Uses it to retrieve the OUIGO
    website. Fills in the required information in the OUIGO website for the
    specified origin station, destination station and date. Then loads the
    results page and reads the existing train services for that date, with
    their departure and arrival times and prices. Writes this information in
    an output file and closes the Webdriver.
    :param origin_station: (string) origin station to request.
    :param destination_station: (string) destination station to request.
    :param travel_date: (string DD/MM/YYYY) date to request.
    :param output_file: (file object) file to which the output information will
        be written.
    :param chromedriver_path: (string) path to the chromedriver exe file.
    :param ouigo_url: (string) URL path to the OUIGO website.
    :param headless: (boolean) if False, the browser window will be shown. Set
        as True for speed.
    """
    # Obtain current date and time:
    dt_now = datetime.now()
    search_date = date_object_to_string_date(dt_now)
    search_time = str(dt_now.hour).zfill(2) + ':' + str(dt_now.minute).zfill(2)
    print('{}\tSearching for \"{}\" -> \"{}\" services for date: {} in OUIGO'
          .format(datetime.now(), origin_station, destination_station,
                  travel_date))

    # Enter site:
    options = Options()
    if headless:
        options.add_argument("--headless")  # to not see browser window
    driver = webdriver.Chrome(chromedriver_path, options=options)
    driver.get(ouigo_url)
    webpage_title = driver.title
    print('{}\tEntered \"{}\" site successfully'.format(datetime.now(),
                                                        webpage_title))

    # accept all cookies (not strictly necessary, but helps visually when
    # displaying window - not headless):
    if not headless:
        accept_cookies_button = driver.find_element_by_xpath(
            "//button[@id='didomi-notice-agree-button']")
        accept_cookies_button.click()

    # FILL IN ORIGIN STATION:

    # 1) find origin station textbox and click on it so that the dropdown menu
    # with the station options is displayed:
    origin_station_textbox = driver.find_element_by_xpath(
        "//span[text()='Elige tu estación de origen ']")
    origin_station_textbox.click()

    # 2) add all the displayed station options to a list:
    origin_station_suggestions = \
        driver.find_elements(By.XPATH, '//li[@class="select2-results__option"]')
    # there is one highlighted station option that needs to be accessed
    # differently. Add it:
    origin_station_suggestions += \
        driver.find_elements(By.XPATH, '//li[@class="select2-results__option' +
                             ' select2-results__option--highlighted"]')

    # 3) iterate over the station options and compare them to the specified
    # origin station (all lowercase):
    origin_station_found = False
    for suggested_origin_station in origin_station_suggestions:
        if origin_station.lower() in suggested_origin_station.text.lower():
            suggested_origin_station.click()
            origin_station_found = True
            break
    # in case the specified origin station is not found in dropdown menu,
    # then raise error:
    if not origin_station_found:
        raise ValueError('Origin station \"{}\" not found in dropdown menu. '
                         .format(origin_station) + 'Available options are: {}'
                         .format(','.join([o.text for o in
                                           origin_station_suggestions])))

    # FILL IN DESTINATION STATION:

    # 1) find destination station textbox and click on it so that the dropdown
    # menu with the station options is displayed:
    destination_station_textbox = driver.find_element_by_xpath(
        "//span[text()='Elige tu estación de destino ']")
    destination_station_textbox.click()

    # 2) add all the displayed station options to a list:
    destination_station_suggestions = \
        driver.find_elements(By.XPATH, '//li[@class="select2-results__option"]')
    # there is one highlighted station option that needs to be accessed
    # differently. Add it:
    destination_station_suggestions += \
        driver.find_elements(By.XPATH, '//li[@class="select2-results__option' +
                             ' select2-results__option--highlighted"]')

    # 3) iterate over the station options and compare them to the specified
    # destination station (all lowercase):
    destination_station_found = False
    for suggested_destin_station in destination_station_suggestions:
        if destination_station.lower() in suggested_destin_station.text.lower():
            suggested_destin_station.click()
            destination_station_found = True
            break
    # in case the specified origin station is not found in dropdown menu,
    # then raise error:
    if not destination_station_found:
        raise ValueError('Destination station \"{}\" not found in dropdown menu'
                         .format(destination_station) +
                         '. Available options are: {}'
                         .format(','.join([d.text for d in
                                           destination_station_suggestions])))

    # FILL IN DATE (only one way date):
    # when loading the page headless, the datebox element is set as "readonly",
    # we need to remove that:
    if headless:
        driver.execute_script('document.getElementById("edit-start-date")' +
                              '.removeAttribute("readonly")')
    # Find date box, clear the predetermined date, and fill in our
    # specified date:
    date_box = driver.find_element_by_xpath("//input[@id='edit-start-date']")
    date_box.clear()
    date_box.send_keys(travel_date)
    # move out of date box and hide small dates window:
    date_box.send_keys(Keys.ESCAPE)

    # CLICK ON SEARCH FOR TRAINS BUTTON:
    search_button = driver.find_element_by_xpath(
        "//button[@id='search_submit']")
    search_button.click()

    print('{}\tFilled in field boxes successfully. Waiting for response...'
          .format(datetime.now()))

    time.sleep(2)

    # Reach information from each train service for this date:
    # departure times:
    departure_times = driver.find_elements_by_xpath(
        "//div[@class='sc-krtoiy Jyeze']")
    # arrival times:
    arrival_times = driver.find_elements_by_xpath(
        "//div[@class='sc-lcwbcE gmUBgo']")
    # prices:
    prices = driver.find_elements_by_xpath(
        "//div[@class='sc-gEUNXV iLVHbv']")

    # make sure the information is consistent. If not, raise exception that
    # makes the process retry:

    if not (len(departure_times) == len(arrival_times) == len(prices)):
        print('{}\tInconsistent results for ({} - {}, {}). Skipped.'
              .format(datetime.now(), origin_station, destination_station,
                      travel_date))
        raise TimeoutException
    elif len(departure_times) == 0:
        print('{}\tNo results found for ({} - {}, {}). Skipped.'
              .format(datetime.now(), origin_station, destination_station,
                      travel_date))
        raise TimeoutException

    parsed_train_services = []
    for trip_index in range(len(departure_times)):
        dep_time = departure_times[trip_index].text
        arr_time = arrival_times[trip_index].text
        price = prices[trip_index].text
        if price.lower().rstrip() == 'tren completo':
            pass
        else:
            try:
                float(price.replace(',', '.').replace('€', ''))
            except ValueError:
                print('{}\t"{}" invalid price value ({} - {}, {}). Skipped.'
                      .format(datetime.now(), price, origin_station,
                              destination_station, travel_date))
                raise TimeoutException
        train_service = [origin_station, destination_station, travel_date,
                         dep_time, arr_time, price, 'OUIGO', search_date,
                         search_time]
        parsed_train_services.append(train_service)

    driver.quit()

    for train_service in parsed_train_services:
        output_file.write('|'.join(train_service) + '\n')

    print('{}\t{} train services found ({} - {}, {}) and written in output file'
          .format(datetime.now(), len(parsed_train_services),
                  origin_station, destination_station, travel_date))
