import math
from construction import Construction
from functions import *
import configparser


class Grader:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.paths = config['paths']

        self.construction: Construction = Construction(self.paths['const_params'])
        self.construction.get_defects(self.paths['defects'])

    def get_grade(self):
        Kv = calculate_kv_on_size(self.paths['road_category'], self.paths['tabl9'],
                          self.construction.const_param['Интенсивность'],
                          self.construction.const_param['Габариты'],
                          self.construction.const_param['Категория дороги'],
                          self.construction.const_param['Тип дороги'],
                          self.construction.const_param['длина'])    # (3.1)
        # print(f"\nKv = {Kv} (0.5)\n")
        Bb = calculate_safety_parameter('Б', self.construction.bd_defect_counter()['Б'])  # (3.2)  вызывается в 8
        # print(f"\nBb = {Bb} (2.86)\n")
        Kb, characteristic = find_kb(Kv, Bb, self.paths['kb_tabl'])        # (3.3) можно вызвать в 8
        # print(f"\nKb = {Kb} (2)\n")
        # Kpch, Ktr = 2, 3      (4) может и не надо
        Kg = find_K_g(self.construction.const_param['Нормативные нагрузки 1'],
                      self.construction.const_param['Нормативные нагрузки 2'],
                      float(self.construction.const_param['К ак']),
                      float(self.construction.const_param['К нк']),
                      float(self.construction.const_param['К эт']),
                      float(self.construction.const_param['К п']))       # (5) вызывается в 8
        # print(f"\nKg = {Kg} (1)\n")
        Bd = calculate_safety_parameter('Д', self.construction.bd_defect_counter()['Д'])  # (6.4) можно вызвать в 8
        Bd_baz = math.ceil(Bd)      # (6.4) округление в большую сторону
        # K = 3                 (7) ремонтопригодность
        # для Kob вместо Kv, Bb можно сразу Kb передавать
        Kdi = find_list_kdi(self.construction.main_d_defect_counter(), self.paths['kdi_tabl'])
        Bob = gen_defectiveness_param_of_bridge(self.construction.bd_defect_counter(), Kg)          # (8)
        # print(f"\nBob = {Bob} (1.52; 2.19)\n")
        Kob = general_indicator_of_technical_condition_bridge(Kv, Bb, Kdi, Kg, self.paths['kb_tabl'])
        # print(f"\nKob = {Kob} (1.41; 2.08)\n")
        print(f"\nKv = {Kv}\nBb = {Bb}\nKb = {Kb}\nKg = {Kg}\nBob = {Bob}\nKob = {Kob}\n")

    def set_defects(self, path):
        self.construction.read_defects_from_csv(path)


# g = Grader()
# g.get_grade()
