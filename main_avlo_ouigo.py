from AVLO.main import main_function as main_avlo
from OUIGO.main import main_function as main_ouigo

if __name__ == '__main__':
    cfg_path = r"C:\Users\pablo\ProjectsData\HSTrainWebScraping\configuration_files\main.cfg"
    main_avlo(cfg_path)
    main_ouigo(cfg_path)
