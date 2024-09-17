from functions import *


class Defect:
    def __init__(self, group, defect_code, location, defect_name, quantitative_params,
                 category_B, category_D, category_G, category_R, note, base):
        self.group = group  # Группа
        self.defect_code = defect_code  # Код дефекта по каталогу
        self.location = location  # Место расположения дефекта
        self.defect_name = defect_name  # Название дефекта
        self.quantitative_params = quantitative_params  # Количественные параметры развития
        self.category_B = category_B  # Категория дефекта (Б)
        self.category_D = category_D  # Категория дефекта (Д)
        self.category_G = category_G  # Категория дефекта (Г)
        self.category_R = category_R  # Категория дефекта (Р)
        self.note = note  # Примечание
        self.base = base  # Базовый

    def set_defect(self, group='', code='', loc='', name='', params='', cb='', cd='', cg='', cr='', note=''):
        self.group = group
        self.defect_code = code
        self.location = loc
        self.defect_name = name
        self.quantitative_params = params
        self.category_B = cb
        self.category_D = cd
        self.category_G = cg
        self.category_R = cr
        self.note = note

    def __repr__(self):
        return (f"Defect(group={self.group}, defect_code={self.defect_code}, location={self.location}, defect_name={self.defect_name}, "
                f"quantitative_params={self.quantitative_params}, category_B={self.category_B}, category_D={self.category_D}, "
                f"category_G={self.category_G}, category_R={self.category_R}, note={self.note})")
