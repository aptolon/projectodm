from defect import Defect
import functions
import csv
import os


class Construction:
    def __init__(self, path_const_params):
        self.defects = []
        self.const_param = self.load_const_params_from_csv(path_const_params)

    def load_const_params_from_csv(self, file_path):
        const_params = {}
        print(os.getcwd())
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                param_name = row['Параметр'].strip()
                param_value = row['Значение'].strip()
                if param_name:
                    const_params[param_name] = param_value
        print(const_params)
        return const_params

    def read_defects_from_csv(self, file_path):
        defects = []
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)  # Пропустить заголовок
            for row in reader:
                defect = Defect(
                    group=row[0],
                    defect_code=row[1],
                    location=row[2],
                    defect_name=row[3],
                    quantitative_params=row[4],
                    category_B=row[5] if row[5] else None,
                    category_D=row[6] if row[6] else None,
                    category_G=row[7] if row[7] else None,
                    category_R=row[8] if row[8] else None,
                    note=row[9] if len(row) > 9 else None,
                    base=row[10] if row[10] else 0
                )
                defects.append(defect)
        return defects

    def print_defects(self, defects):
        for i, defect in enumerate(defects, 1):
            print(f"Дефект {i}:")
            print(f"  Группа: {defect.group}")
            print(f"  Код дефекта: {defect.defect_code}")
            print(f"  Место расположения: {defect.location}")
            print(f"  Название дефекта: {defect.defect_name}")
            print(f"  Количественные параметры: {defect.quantitative_params}")
            print(f"  Категория Б: {defect.category_B}")
            print(f"  Категория Д: {defect.category_D}")
            print(f"  Категория Г: {defect.category_G}")
            print(f"  Категория Р: {defect.category_R}")
            print(f"  Примечание: {defect.note}")
            print()

    def get_defects(self, path):
        self.defects = self.read_defects_from_csv(path)

    def set_defects(self):
        pass

    def sort_defects(self):
        pass

    # Сейчас для разных функций из functions.py своя функция отсюда.
    # Стоит переделать в functions.py более универсальные входные данные, чтобы здесь не было много схожих функций.
    def bd_defect_counter(self) -> dict[str, dict[str, int]]:
        # Создаем словарь для подсчета дефектов каждой подкатегории Б и Д
        b_counts = {'Б1': 0, 'Б2': 0, 'Б3': 0, 'Б4': 0}
        d_counts = {'Д1': 0, 'Д2': 0, 'Д3': 0, 'Д4': 0}

        # Перебираем все дефекты в списке
        for defect in self.defects:
            if defect.category_B:
                b_counts['Б' + defect.category_B] += 1
            if defect.category_D:
                d_counts['Д' + defect.category_D] += 1
        return {'Б': b_counts, 'Д': d_counts}

    def d_defect_counter(self) -> dict[str, int]:
        # Создаем словарь для подсчета дефектов каждой подкатегории Д
        d_counts = {'Д1': 0, 'Д2': 0, 'Д3': 0, 'Д4': 0}

        # Перебираем все дефекты в списке
        for defect in self.defects:
            if defect.category_D:
                d_counts['Д' + defect.category_D] += 1
        return d_counts

    def b_defect_counter(self) -> dict[str, int]:
        # Создаем словарь для подсчета дефектов каждой подкатегории Б
        b_counts = {'Б1': 0, 'Б2': 0, 'Б3': 0, 'Б4': 0}

        # Перебираем все дефекты в списке
        for defect in self.defects:
            if defect.category_B:
                b_counts['Б' + defect.category_B] += 1
        return b_counts

    def main_d_defect_counter(self) -> dict[str, dict[str, int]]:
        # Создаем словарь для подсчета базовых дефектов каждой группы для подкатегории Д
        d_counts = {'Д1': 0, 'Д2': 0, 'Д3': 0, 'Д4': 0}
        group = self.defects[0].group
        counter = {}
        # Перебираем все дефекты в списке
        for defect in self.defects:
            if group != defect.group:
                group = defect.group
                # если все значения нули то не добавляем
                if not all(val == 0 for val in d_counts.values()):
                    counter[group] = d_counts
                d_counts = {'Д1': 0, 'Д2': 0, 'Д3': 0, 'Д4': 0}
            if defect.category_D and defect.base == '1':
                d_counts['Д' + defect.category_D] += 1
        return counter
