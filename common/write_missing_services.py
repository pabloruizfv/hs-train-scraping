from os.path import join


def write_missing_services(missing_services, operator, output_dir):
    """
    Write a list of missing train services in an output file.
    :param missing_services: ([(str,str,str,str)]): list of tuples, each of
        the tuples representing a missing train service. Each tuple, or train
        service, contains 4 string elements. The first 3 elements shall be
        origin station, destination station, and travel date, in that order.
    :param operator: (str): train operator name.
    :param output_dir: (str) path to the directory under which the output
        'missing_services.txt' file will be generated.
    """
    output_path = join(output_dir, 'missing_services.txt')
    with open(output_path, 'w') as output_file:
        output_file.write(
            'origin_station|destination_station|operator|travel_date\n')
        for o_station, d_station, t_date, _ in missing_services:
            output_file.write('{}|{}|{}|{}\n'.format(o_station, d_station,
                                                     operator, t_date))
