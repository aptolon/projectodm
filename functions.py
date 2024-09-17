import pandas
import pandas as pd
import numpy as np


def load_category(p_road_category: str, p_tabl9: str):
    road_category = pd.read_csv(p_road_category, delimiter=';')
    tabl9 = pd.read_csv(p_tabl9, delimiter=';')
    return road_category, tabl9


def load_kdi(path: str):
    # Kdi_tabl.csv
    kdi_table = pd.read_csv(path, delimiter=';')
    return kdi_table


def load_kb(path: str):
    # Kb_tabl.csv
    kb_table = pd.read_csv(path, delimiter=';')
    return kb_table


def between_array(array: list, num: int | float) -> tuple[int, int]:
    array.sort()
    if num <= min(array):
        return min(array), min(array)
    elif num >= max(array):
        return max(array), max(array)

    for i in range(1, len(array)):
        if num == array[i]:
            return num, num
        elif num < array[i]:
            return array[i-1], array[i]


def get_max_safe_speed(tabl9, n_ch, width, length):
    n_ch = int(n_ch) / 24       # перевод из авт/сут в авт/час
    width = float(width)
    length = float(length)
    if n_ch > 1200:
        n_ch = 1200
    try:
        if length < 50:
            k = 1.1
        elif length > 150:
            k = 0.85
        else:
            k = 1
        # print(f"n_ch = {n_ch}, width = {width}, length = {length}")
        size = [float(s) for s in tabl9.columns.tolist()[1:]]
        n_ch_tabl = tabl9['Nч'].tolist()

        x1, x2 = between_array(size, width)
        y1, y2 = between_array(n_ch_tabl, n_ch)
        column1, column2 = tabl9[str(x1)].tolist(), tabl9[str(x2)].tolist()     # столбец
        num_of_y1, num_of_y2 = n_ch_tabl.index(y1), n_ch_tabl.index(y2)         # номер строки

        z11, z12 = column1[num_of_y1], column2[num_of_y1]
        z21, z22 = column1[num_of_y2], column2[num_of_y2]

        inter1 = np.interp(float(width), [x1, x2], [z11, z12])
        inter2 = np.interp(float(width), [x1, x2], [z21, z22])
        interpolate = np.interp(float(width), [y1, y2], [inter1, inter2])

        # print(f"x1, x2 = {x1, x2};\ny1, y2 = {y1, y2};\nz11, z12 = {z11, z12};\nz21, z22 = {z21, z22};")
        # print(f"interpolate = {interpolate}")

        safe_speed = interpolate * k
        # print(f"safe_speed = {safe_speed}")
        return safe_speed
    except IndexError:
        print("index")
        return None
    except KeyError:
        print("key")
        return None


def get_calculated_speed(road_category, category, speed_type):
    try:
        value = road_category.loc[road_category['Категория дороги'] == category, speed_type].values[0]
        return value
    except IndexError:
        return None


# Определение параметра дефектности по безопасности мостового сооружения по критерию габарита (K.3.2)
# Где таблицы, там пути.
# (Таблица road_category, Таблица tabl9, значение n_ch(1200 например), габариты ("Г-"9 например), категория дороги
# (II например), столбец в таблице road_category(Основная;Пересеченная;Горная))
def calculate_kv_on_size(p_road_category, p_tabl9, n_ch, width, category, speed_type, length):
    road_category, tabl9 = load_category(p_road_category, p_tabl9)
    V = get_max_safe_speed(tabl9, n_ch, width, length)
    Vp = get_calculated_speed(road_category, category, speed_type)
    Kv = V / Vp
    return Kv


# К.3.2 Определение параметра дефектности по безопасности мостового сооружения

# Нахождение B_b_base
def base_security_setting_value(defect_counts: dict[str, int]) -> int:

    counter = 0
    i = 0
    for value in defect_counts.values():
        i += 1
        if value != 0:
            counter = i

    base_value = 6 - counter
    return base_value


# Нахождение коэффициентов гамма
def defect_impact_indicator(defect_type: str, defect_counts: dict[str, int]) -> dict:
    alpha = {
        'Б': {'Б1': 0.01, 'Б2': 0.03, 'Б3': 0.1, 'Б4': 0.3},
        'Д': {'Д1': 0.01, 'Д2': 0.03, 'Д3': 0.1, 'Д4': 0.3}
    }

    if defect_type not in alpha:
        raise ValueError(f"Неизвестный тип дефекта: {defect_type}")

    temp_dict = {}
    total_dict = {}

    for key, value in defect_counts.items():
        if key in alpha[defect_type] and defect_counts[key] != 0:
            temp_dict[key] = alpha[defect_type][key]

    summ_values = sum(temp_dict.values())

    for key, value in temp_dict.items():
        total_dict[key] = value / summ_values

    return total_dict


# Нахождение B_Base
def calculate_safety_parameter(defect_type: str, defect_counts: dict[str, int]) -> float:
    B_b_base = base_security_setting_value(defect_counts)
    gamma_j = defect_impact_indicator(defect_type, defect_counts)

    if sum(defect_counts.values()) == 0:
        B_b = 5
        return B_b
    else:
        summ = 0

        for key, value in defect_counts.items():
            if defect_counts[key] != 0:
                summ += (1 - (1 / ((defect_counts[key] / 5) + 1))) * gamma_j[key]

        B_b = B_b_base - summ

        return B_b


def find_kb(Kv: float, B_b: float, path_kb: str):

    data = load_kb(path_kb)

    if Kv >= 1:
        k_res = 5
    elif 0.9 <= Kv < 1:
        k_res = 4
    elif 0.7 <= Kv < 0.9:
        k_res = 3
    elif 0.25 <= Kv < 0.7:
        k_res = 2
    elif 0 < Kv < 0.25:
        k_res = 1
    else:
        k_res = 0

    if B_b == 5:
        b_res = 5
    elif 4 < B_b < 5:
        b_res = 4
    elif 3 < B_b <= 4:
        b_res = 3
    elif 2 < B_b <= 3:
        b_res = 2
    elif 1 < B_b <= 2:
        b_res = 1
    else:
        b_res = 0

    kdi_row = data[data['Значение показателя'] == min(k_res, b_res)]

    return (int(kdi_row.iloc[0]['Значение показателя']),
            kdi_row.iloc[0]['Характеристика'])


# Оценка технического состояния мостового сооружения по безотказности (грузоподъемности) (К.5)
def find_K_g(normAK: str, normNK: str, Kak: float, Knk: float, Ket: float, Kp: float=1) -> int:
    # А11, Н11
    # А14, Н14
    # А8, НГ-60
    # А11, НК-80
    # Н-30, НК-80
    # Н-10, НГ-60
    # Н-18, НК-80
    # Н-13, НГ-60
    # Н-13 или Н-10, НГ-60 или НГ-30
    # Н-10, Т-60/5 или Т-30/4
    # Н-13 или Т-60
    # Н-10, Т-25 или Т-60
    norm5new = [['14', '14'], ['А14', 'Н14']]                   # после 2011 года
    norm5 = [['11', '11'], ['А11', 'Н11']]                      # до 2011 года
    norm4new = [['Н-30', 'НК-80']]                              # после 2011 года
    norm4 = [['А11', 'НК-80'], ['11', '11']]                    # до 2011 (1984) года
    norm3new = [['Н-18', 'НК-80'], ['Н-30', 'НК-80']]           # после 2011 (1984) года
    norm3 = [['А11', 'Н11'], ['11', '11'], ['А11', 'НК-80']]    # до 2011 года

    K_g = 0
    if Ket < 12:
        K_g = 0
    elif Knk < 6.6 or (Kak < 6.6 and Kp < 1) or (12 <= Ket <= 18 and Kp > 1):
        K_g = 1
    elif (Kak >= 14 and Knk >= 14 and [normAK, normNK] in norm5new) or \
            (Kak >= 11 and Knk >= 11 and [normAK, normNK] in norm5):
        K_g = 5
    elif (11 <= Kak <= 14) or (11 <= Knk <= 14) and (([normAK, normNK] in norm4new) or ([normAK, normNK] in norm4)):
        K_g = 4
    elif (Knk < 11 or Kak < 11) and Ket > 30 and (([normAK, normNK] in norm3new) or ([normAK, normNK] in norm3)):
        K_g = 3
    elif (6.6 <= Kak <= 11 and Kp < 1) or (18 < Ket <= 30 and Kp > 1) and \
            (([normAK, normNK] in norm3new) or ([normAK, normNK] in norm3)):
        K_g = 2
    return K_g


# K.6.2
def find_kdi(Bdi: float, kdi_df: pandas.DataFrame):
    if Bdi == 5:
        kdi_row = kdi_df[kdi_df['Kdi'] == 5]
    elif 5 > Bdi > 4:
        kdi_row = kdi_df[kdi_df['Kdi'] == 4]
    elif 4 >= Bdi > 3:
        kdi_row = kdi_df[kdi_df['Kdi'] == 3]
    elif 3 >= Bdi > 2:
        kdi_row = kdi_df[kdi_df['Kdi'] == 2]
    elif 2 >= Bdi > 1:
        kdi_row = kdi_df[kdi_df['Kdi'] == 1]
    elif 1 >= Bdi >= 0:
        kdi_row = kdi_df[kdi_df['Kdi'] == 0]
    else:
        return None, "Не найдено подходящее значение Kdi для данного Bdi"

    return int(kdi_row.iloc[0]['Kdi']), kdi_row.iloc[0]['Характеристика']


def find_list_kdi(defect_counts: dict[str, dict[str, int]], path_kdi: str):
    data = load_kdi(path_kdi)
    list_kdi = []
    for group in defect_counts:
        bd = calculate_safety_parameter('Д', defect_counts[group])
        kd, characteristic = find_kdi(bd, data)
        list_kdi.append(kd)
    return list_kdi


def find_min_kdi(list_kdi_values: list) -> int:

    min_value = min(list_kdi_values)

    return min_value


def find_avg_kdi(list_kdi_values: list) -> float:

    avg_value = sum(list_kdi_values) / len(list_kdi_values)

    return avg_value


def find_total_kd(list_kdi_values: list) -> float:

    min_value = find_min_kdi(list_kdi_values)
    avg_value = find_avg_kdi(list_kdi_values)
    total_value = 0.5 * (avg_value + min_value)

    return total_value


# К.8.1
def gen_defectiveness_param_of_bridge(defect_counts: dict[str, dict[str, int]], K_g: int) -> float:
    B_b = calculate_safety_parameter('Б', defect_counts['Б'])
    # K_g = K_g
    B_d = calculate_safety_parameter('Д', defect_counts['Д'])
    min_value = min(B_b, K_g, B_d)

    total_value = 0.5 * ((B_b + K_g + B_d) / 3 + min_value)

    return total_value


# K.8.2
def general_indicator_of_technical_condition_bridge(Kv: float, B_b: float, list_kdi_values: list,
                                                    K_g: int, path_kb: str) -> float:
    K_b, characteristic = find_kb(Kv, B_b, path_kb)  # characteristic не используется. Нужна, чтобы распаковать Tuple
    # K_g = K_g
    K_d = find_total_kd(list_kdi_values)        # список из таблицы 6.2; Kd по долговечности, мб не только основные
    min_value = min(K_b, K_g, K_d)

    total_value = 0.5 * ((K_b + K_g + K_d) / 3 + min_value)

    return total_value
