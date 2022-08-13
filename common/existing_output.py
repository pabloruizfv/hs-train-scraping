from csv import DictReader
from os.path import exists
from datetime import datetime


def initialize_output_file(output_path):
    """
    Create a new output file and write header.
    :param output_path: (string) path to where the output file will be created.
    """
    output_file = open(output_path, 'w')
    output_file.write('origin_station|destination_station|travel_date|' +
                      'departure_time|arrival_time|price|company|' +
                      'search_date|search_time\n')
    output_file.close()


def discard_existing_services(services_to_request, output_path):
    """
    Discards the train services to request for which there is already existing
    information in the output file (same origin and destination stations, same
    travel date and same search date).
    :param services_to_request: list of tuples [(str, str, str, str)] in which
        each tuple represents a train service to request, and the 4 elements
        of each tuple are the origin station, destination station, travel date
        and search date (all strings, dates in 'DD/MM/YYYY' format).
    :param output_path: (string) path to the existing output file.
    :return: remaining_services_to_request: same as the 'services_to_request'
        argument, but only including those train services to request that are
        not already in the output file.
    """
    existing_requested_services = set()
    for line in DictReader(open(output_path, 'r'), delimiter='|'):
        o_station = line['origin_station']
        d_station = line['destination_station']
        t_date = line['travel_date']
        s_date = line['search_date']
        existing_requested_services.add((o_station, d_station, t_date, s_date))

    remaining_services_to_request = []
    for ser in services_to_request:
        if ser not in existing_requested_services:
            remaining_services_to_request.append(ser)
    return remaining_services_to_request


def load_services_to_request(station_ods, travel_dates, search_date,
                             output_path, repeat_services=True):
    """
    Combines all the origin stations with the destination stations with the
    travel dates, in order to generate all the train services to request.
    Also, reads the output file (if already exists) and discards from the train
    services to request all those for which there already exists information in
    the output file for the same search date, if "repeat_services" is set
    as False.
    :param station_ods: (list of tuples [("","")]): each tuple has 2 string
        elements, the first representing the origin station and the second
        representing the destination station. The name of the stations in
        the webpage's dropdown menu must contain the string by which we refer
        to it in this list.
    :param travel_dates: (list of strings ["DD/MM/YYYY"] list of dates for which
        to request services.
    :param search_date: (string "DD/MM/YYYY") today's date.
    :param output_path: (string) path to the existing output file.
    :param repeat_services: (boolean) If True, all services will be kept. If
        False, then the services which exist in the output file will not be
        searched for again.
    :return: remaining_services_to_request: (list of tuples, each tuple
        containing 4 elements which are strings [(str,str,str,str)]). Contains
        all the origin station, destination station, travel date and search
        date combinations that have been specified, but all the existing ones
        in the output file are not here.
    """
    services_to_request = []

    for o_s, d_s in station_ods:
        for t_d in travel_dates:
            services_to_request.append((o_s, d_s, t_d, search_date))

    print('{}\tTotal specified requests: {}'
          .format(datetime.now(), len(services_to_request)))

    # If some train services already exist in the output file and
    # repeat_services is set as False, skip them:
    if exists(output_path):
        if repeat_services:
            remaining_services_to_request = services_to_request
        else:
            remaining_services_to_request = \
                discard_existing_services(services_to_request, output_path)

    else:
        initialize_output_file(output_path)
        remaining_services_to_request = services_to_request

    print('{}\tSpecified requests pending: {}'
          .format(datetime.now(), len(remaining_services_to_request)))

    return remaining_services_to_request
