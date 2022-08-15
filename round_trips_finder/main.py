import configparser
from common.dates import load_dates_inbetween, add_days_to_date
from csv import DictReader


def load_trains(input_path, origin_station, destination_station, travel_dates):
    """
    Given an origin station, a destination station and a set of travel dates,
    this function loads the train services that match these characteristics
    from an input file, skipping those with non-numerical price values.
    :param input_path: (str) path to the input file.
    :param origin_station: (str)
    :param destination_station: (str)
    :param travel_dates: ([str,str,str,...]) DD/MM/YYYY
    :return trains: ({str->[((str,str),float,str,str)]}) dictionary relating
        each travel date (string DD/MM/YYYY) to a list in which each element is
        a tuple representing a train service departing that date. The elements
        of each tuple are:
        1) Another tuple, of two elements, with the departure and arrival times.
        2) A float value indicating the train price.
        3) A string indicating the operator of this train.
        4) A string indicating the departure date of the train (DD/MM/YYYY).
    """
    trains = {}

    for line in DictReader(open(input_path, 'r'), delimiter='|'):

        # Discard trains that do not match the specified conditions:
        if line['origin_station'] != origin_station:
            continue
        if line['destination_station'] != destination_station:
            continue
        travel_date = line['travel_date']
        if travel_date not in travel_dates:
            continue

        # Load price as float. If not numerical value, skip:
        try:
            price = float(line['price'].replace(',', '.').replace('€', ''))
        except ValueError:
            continue

        # Add train information to trains dictionary
        if travel_date not in trains:
            trains[travel_date] = []
        train_times = (line['departure_time'], line['arrival_time'])
        trains[travel_date].append((train_times, price,
                                    line['company'], travel_date))

    return trains


def possible_train_combinations(available_go_trains, available_return_trains,
                                travel_dates, trip_days):
    """
    Selects the possible combinations between go trains and return trains, where
    both trains must be during the travel dates, and there must be a number
    of days between the go train and the return train that is included in the
    trip_days list.
    :param available_go_trains: ({str->[((str,str),float,str,str)]}) dictionary
        relating each travel date (string DD/MM/YYYY) to a list in which each
        element is a tuple representing a GO train service departing that date.
        The elements of each tuple are:
        1) Another tuple, of two elements, with the departure and arrival times.
        2) A float value indicating the train price.
        3) A string indicating the operator of this train.
        4) A string indicating the departure date of the train (DD/MM/YYYY).
    :param available_return_trains: ({str->[((str,str),float,str,str)]}) same
        to available_go_trains, but containing return trains instead.
    :param travel_dates: ([str,str,str,...]) DD/MM/YYYY
    :param trip_days: ([int])
    :return combinations: {(go_train, return_train): float} relates each pair
        of possible go and return trains with the total price of both.
    """
    # Extract possible go-return train combinations between available go trains
    # and available return trains:
    combinations = {}

    # for each possible go date:
    for go_date in travel_dates:
        if go_date not in available_go_trains:  # avoid KeyError
            continue
        # reach potential trains for go date:
        go_trains = available_go_trains[go_date]

        # for each value of trip number of days, obtain a return date:
        for t_day in trip_days:
            return_date = add_days_to_date(go_date, t_day)

            # if the return date is outside travel dates or there are no train
            # services that date, skip:
            if return_date not in travel_dates:
                continue
            if return_date not in available_return_trains:  # avoid KeyError
                continue

            # reach potential trains for return date:
            return_trains = available_return_trains[return_date]

            # now we have a set of go dates and a set of return dates,
            # iterate over them to generate all combinations:
            for go_train in go_trains:
                for return_train in return_trains:
                    total_price = go_train[1] + return_train[1]
                    combinations[(go_train, return_train)] = total_price

    return combinations


def select_cheapest(combinations, min_i):
    """
    Select the cheapest N combinations, where N = min_i, and all those
    combinations at least as cheap as those N cheapest.
    :param combinations: {(go_train, return_train): float} relates each pair
        of possible go and return trains with the total price of both.
    :param min_i: (int) minimum number of combinations to return.
    :return cheapest_combinations: same data structure as combinations argument,
        but keeping only the cheapest options.
    """
    cheapest_combinations = {}
    max_price = float('inf')
    i = 0
    for combi, price in sorted(combinations.items(), key=lambda item: item[1]):

        if i == min_i:
            max_price = price

        if price > max_price:
            break

        cheapest_combinations[combi] = price

    return cheapest_combinations


def main_function(config_file_path):
    """
    Main function of the round trips finder module. Reads a set of parameters
    from the configuration file, reads the existing train services from an
    input file, and selects the cheapest round trips.
    :param config_file_path: (string) path to the configuration file.
    """
    # Load parameters from configuration file:
    parser = configparser.ConfigParser()
    parser.read(config_file_path)

    origin_station = parser.get("config", "origin_station")
    destination_station = parser.get("config", "destination_station")
    trip_days = [int(d) for d in parser.get("config", "trip_days").split(',')]
    travel_dates = \
        load_dates_inbetween(*parser.get("config",
                                         "travel_date_boundaries").split('-'))
    train_services_info_file_path = \
        parser.get("config", "train_services_info_file_path")
    output_path = parser.get("config", "output_path")

    # Load available "go" trains within the specified travel dates:
    available_go_trains = \
        load_trains(train_services_info_file_path,
                    origin_station, destination_station, travel_dates)

    # Load available "return" trains within the specified travel dates:
    available_return_trains = \
        load_trains(train_services_info_file_path,
                    destination_station, origin_station, travel_dates)

    # Extract possible go-return train combinations between available go trains
    # and available return trains:
    combinations = possible_train_combinations(available_go_trains,
                                               available_return_trains,
                                               travel_dates, trip_days)

    # Filter only cheapest combinations:
    cheapest_combinations = select_cheapest(combinations, 50)

    # Write the cheapest combinations in output file:
    i = 0
    with open(output_path,'w') as output_file:
        for combi, price in cheapest_combinations.items():

            output_file.write('{}|{}€|'.format(i, price) +
                              '{}|{}€|{}|{}|{}|'
                              .format(combi[0][2], combi[0][1],
                                      combi[0][0][0], combi[0][3],
                                      origin_station) +
                              '{}|{}|'
                              .format(combi[0][0][1], destination_station) +
                              '|{}|{}€|{}|{}|{}\n'
                              .format(combi[1][2], combi[1][1],
                                      combi[1][0][0], combi[1][3],
                                      destination_station))

            i += 1


if __name__ == '__main__':
    cfg_path = r"C:\Users\pablo\ProjectsData\HSTrainWebScraping\configuration_files\round_trip_finder.cfg"
    main_function(cfg_path)
