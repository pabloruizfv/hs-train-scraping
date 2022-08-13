
def print_remaining_time(start_datetime, total_num_processes,
                         current_datetime, remaining_num_processes):
    """
    This function estimates the remaining time for a series of processes
    based on the time that some part of the processes have taken already.
    :param start_datetime: (datetime object) datetime of the moment right
        before starting the first process.
    :param total_num_processes: (integer) number of total processes to launch
    :param current_datetime: (datetime object) datetime of the moment when the
        current last process has been finished.
    :param remaining_num_processes: (integer) number of processes that have been
        launched already
    """
    if remaining_num_processes == total_num_processes:
        return None
    elapsed_minutes = (current_datetime - start_datetime).total_seconds() / 60.
    minutes_per_successful_search = \
        elapsed_minutes / (total_num_processes - remaining_num_processes)
    remaining_time = minutes_per_successful_search * remaining_num_processes
    print('{}\tRemaining time: {} min ({} processes)'
          .format(current_datetime,
                  int(remaining_time) + 1,
                  remaining_num_processes))
