from common.dates import load_dates_inbetween, string_date_to_date_object, \
    date_object_to_string_date
from AVLO.web_request import avlo_services_try
from datetime import datetime
import configparser
from common.existing_output import load_services_to_request
import random
from common.remaining_time import print_remaining_time
from common.write_missing_services import write_missing_services
from os.path import dirname


AVLO_URL = r'https://avlorenfe.com/'


def main_function(config_file_path):
    """
    Main function of the AVLO Web Scraping project. Reads a set of parameters
    from the configuration file, executes the request to the AVLO website
    and writes the resulting information in an output file.
    :param: config_file_path (str): path to the configuration file.
    """
    # Load parameters from configuration file:
    parser = configparser.ConfigParser()
    parser.read(config_file_path)

    station_ods = [od.split('-')
                   for od in parser.get("config", "station_ods").split(',')]
    travel_dates = \
        load_dates_inbetween(*parser.get("config", "travel_dates").split('-'))
    chromedriver_path = parser.get("config", "chromedriver_path")
    output_path = parser.get("config", "output_path")
    show_window = parser.getboolean("config", "show_window")

    # Calculate today's date (DD/MM/YYYY):
    search_date = date_object_to_string_date(datetime.now())

    # make sure that there are not dates to request prior to today:
    assert string_date_to_date_object(travel_dates[0]) >= \
        string_date_to_date_object(search_date), \
        'The specified start date is previous to today\'s date.'

    # Calculate train services to request (set argument repeat_services=False to
    # discard those that already exist in output file for the same search date):
    services_to_request = load_services_to_request(station_ods, travel_dates,
                                                   search_date, output_path)
    initial_remaining_services = len(services_to_request)

    # Open output file
    output_file = open(output_path, 'a')
    start_dt = datetime.now()
    last_services_not_found_count = 0
    while len(services_to_request) > 0:
        s_to_request = random.choice(services_to_request)
        o_station, d_station, t_date, _ = s_to_request
        # Request the train services for a specific origin and destination
        # stations and date:
        services_found = avlo_services_try(o_station, d_station, t_date,
                                           output_file, chromedriver_path,
                                           AVLO_URL, headless=not show_window)

        if services_found:
            services_to_request.remove(s_to_request)
            print_remaining_time(start_dt, initial_remaining_services,
                                 datetime.now(), len(services_to_request))
            last_services_not_found_count = 0
        else:
            last_services_not_found_count += 1

        if last_services_not_found_count > 20:
            print('{}\tNo trains found for the following services: {}'
                  .format(datetime.now(), services_to_request))
            write_missing_services(services_to_request, dirname(output_path))
            break

    output_file.close()
    print('{}\tFinished successfully!'.format(datetime.now()))


if __name__ == '__main__':
    cfg_path = r"C:\Users\pablo\ProjectsData\HSTrainWebScraping\configuration_files\AVLO.cfg"
    main_function(cfg_path)
