import sys
import os
import csv
import pandas as pd
import configparser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QAction, QLabel, QLineEdit,
    QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFormLayout, QStackedWidget,
    QListWidget, QGridLayout, QMessageBox,QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt
from grading import Grader

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project_dir = None
        config = configparser.ConfigParser()
        self.config_file = 'config.ini'
        self.configparser_file = config.read('config.ini')
        self.paths = config['paths']
        self.defects_df = pd.DataFrame(columns=[
            'Группа', 'Код дефекта по каталогу', 'Место расположения дефекта', 'Название дефекта',
            'Количественные параметры развития', 'Категории дефекта (Б)', 'Категории дефекта (Д)',
            'Категории дефекта (Г)', 'Категории дефекта (Р)', 'Примечание'
        ])
        self.catalog_defects_df = self.load_catalog_defects()  # Load defects from the external file
        self.initUI()

    def load_catalog_defects(self):
        catalog_defects_path = self.paths['catalog']
        if os.path.exists(catalog_defects_path):
            return pd.read_csv(catalog_defects_path, sep=';')
        else:
            QMessageBox.warning(self, 'Ошибка', f'Файл дефектов по пути {catalog_defects_path} не найден.')
            return pd.DataFrame(columns=self.defect_fields)


    def initUI(self):
        self.setWindowTitle('Проект Моста')
        self.setGeometry(0, 0, 1000, 1000)  # Увеличить ширину окна для дополнительных списков

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.default_widget = QLabel('Выберите проект для начала работы', alignment=Qt.AlignCenter)
        self.central_widget.addWidget(self.default_widget)

        self.bridge_params_widget = QWidget()
        self.bridge_params_layout = QVBoxLayout()
        self.bridge_params_form = QFormLayout()
        self.inputs = {}

        self.params = {
            'Тип дороги': ['Основная', 'Пересеченная', 'Горная'],
            'Категория дороги': ['IA', 'IБ', 'IB', 'II', 'III', 'IV', 'V'],
            'Габариты': '',
            'Интенсивность': '',
            'Г': '',
            'Т1': '',
            'Т2': '',
            'длина': '',
            'отверстие': '',
            'Средний продольный уклон': '',
            'Ширина проезжей части': '',
            'К ак':'',
            'К нк':'',
            'К эт':'',
            'К п':'',
            'Нормативные нагрузки 1':['14','11','Н-30','А11','А14','Н-18','Н-13'],
            'Нормативные нагрузки 2':['14','11','НК-80','Н11','Н14','НГ-60'],
            
        }

        for param in self.params:
            if param in ['Тип дороги', 'Категория дороги','Нормативные нагрузки 1','Нормативные нагрузки 2']:
                self.inputs[param] = QComboBox()
                self.inputs[param].addItems(self.params[param])
            else:
                self.inputs[param] = QLineEdit()

            self.bridge_params_form.addRow(QLabel(param), self.inputs[param])

        self.bridge_params_layout.addLayout(self.bridge_params_form)

        save_button = QPushButton('Сохранить', self)
        save_button.clicked.connect(self.save_params)
        self.bridge_params_layout.addWidget(save_button)

        self.bridge_params_widget.setLayout(self.bridge_params_layout)
        self.central_widget.addWidget(self.bridge_params_widget)

        self.defects_widget = QWidget()
        self.defects_layout = QVBoxLayout(self.defects_widget)

        self.defects_list_layout = QHBoxLayout()
        self.defects_list_layout2 = QHBoxLayout()

        # Существующие списки
        self.left_list_label = QLabel('Дефекты моста  ')
        self.groups_listbox = QListWidget()
        self.groups_listbox.currentItemChanged.connect(self.on_group_select1)
        self.defects_listbox = QListWidget()
        self.defects_listbox.currentItemChanged.connect(self.on_defect_select1)

        # Новые списки
        self.right_list_label = QLabel('Каталог дефектов')
        self.groups_listbox2 = QListWidget()
        self.groups_listbox2.currentItemChanged.connect(self.on_group_select2)
        self.defects_listbox2 = QListWidget()
        self.defects_listbox2.currentItemChanged.connect(self.on_defect_select2)

        self.defects_list_layout.addWidget(self.left_list_label)
        self.defects_list_layout.addWidget(self.groups_listbox)
        self.defects_list_layout.addWidget(self.defects_listbox)
        
        self.defects_list_layout2.addWidget(self.right_list_label)
        self.defects_list_layout2.addWidget(self.groups_listbox2)  # Добавляем новый список групп
        self.defects_list_layout2.addWidget(self.defects_listbox2)  # Добавляем новый список дефектов

        self.defects_layout.addLayout(self.defects_list_layout)
        

        self.defect_details_layout = QGridLayout()
        self.defect_fields = [
            'Группа', 'Код дефекта по каталогу', 'Место расположения дефекта', 'Название дефекта',
            'Количественные параметры развития', 'Категории дефекта (Б)', 'Категории дефекта (Д)',
            'Категории дефекта (Г)', 'Категории дефекта (Р)', 'Примечание', 'Базовый'
        ]
        self.defect_entries = {}

        for i, field in enumerate(self.defect_fields):
            label = QLabel(field)
            if field == 'Базовый':
                entry = QCheckBox()
            else:
                entry = QLineEdit()
            self.defect_details_layout.addWidget(label, i, 0)
            self.defect_details_layout.addWidget(entry, i, 1)
            self.defect_entries[field] = entry


        self.defects_layout.addLayout(self.defect_details_layout)
        
        self.defects_action_layout = QHBoxLayout()

        edit_defect_button = QPushButton('Редактировать выбраный дефект', self)
        edit_defect_button.clicked.connect(self.edit_defect)
        self.defects_action_layout.addWidget(edit_defect_button)
        
        add_defect_button = QPushButton('Добавить новый дефект', self)
        add_defect_button.clicked.connect(self.add_defect)
        self.defects_action_layout.addWidget(add_defect_button)

        delete_defect_button = QPushButton('Удалить выбраный дефект', self)
        delete_defect_button.clicked.connect(self.delete_defect)
        self.defects_action_layout.addWidget(delete_defect_button)
        
        clear_defect_button = QPushButton('Очистить поля', self)
        clear_defect_button.clicked.connect(self.clear_defect_fields)
        self.defects_action_layout.addWidget(clear_defect_button)
        
        calculate_result_button = QPushButton('Рассчитать результат', self)
        calculate_result_button.clicked.connect(self.calculate_result)
        self.defects_action_layout.addWidget(calculate_result_button)


        self.defects_layout.addLayout(self.defects_action_layout)
        self.defects_layout.addLayout(self.defects_list_layout2)
        self.central_widget.addWidget(self.defects_widget)

        menubar = self.menuBar()
        statusbar = self.statusBar()

        project_menu = menubar.addMenu('Проект')
        bridge_params_menu = menubar.addMenu('Параметры моста')
        defects_menu = menubar.addMenu('Дефекты')

        open_project_action = QAction('Открыть проект', self)
        open_project_action.triggered.connect(self.open_project)
        project_menu.addAction(open_project_action)

        create_project_action = QAction('Создать проект', self)
        create_project_action.triggered.connect(self.create_project)
        project_menu.addAction(create_project_action)

        bridge_params_action = QAction('Параметры моста', self)
        bridge_params_action.triggered.connect(self.show_bridge_params)
        bridge_params_menu.addAction(bridge_params_action)

        defects_action = QAction('Дефекты', self)
        defects_action.triggered.connect(self.show_defects)
        defects_menu.addAction(defects_action)

        self.project_label = QLabel('Проект не выбран')
        statusbar.addPermanentWidget(self.project_label)

    def open_project(self):
        project_dir = QFileDialog.getExistingDirectory(self, 'Выбрать папку с проектом')
        if project_dir:
            self.project_dir = project_dir
            self.project_label.setText(f'Проект: {os.path.basename(project_dir)}')
            self.update_config_paths(project_dir)

            const_params_path = os.path.join(project_dir, 'const_params.csv')
            defects_path = os.path.join(project_dir, 'defects.csv')

            # Создание файлов, если они не существуют
            self.create_file_if_not_exists(const_params_path, ['Параметр', 'Значение'])
            self.create_file_if_not_exists(defects_path, self.defect_fields)

            QMessageBox.information(self, 'Проект открыт', f'Путь к файлам:\n{const_params_path}\n{defects_path}')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Папка с проектом не выбрана.')

    def create_project(self):
        project_dir = QFileDialog.getExistingDirectory(self, 'Выбрать папку для нового проекта')
        if project_dir:
            self.project_dir = project_dir
            self.project_label.setText(f'Проект: {os.path.basename(project_dir)}')
            self.update_config_paths(project_dir)

            const_params_path = os.path.join(project_dir, 'const_params.csv')
            defects_path = os.path.join(project_dir, 'defects.csv')

            # Создание файлов, если они не существуют
            self.create_file_if_not_exists(const_params_path, ['Параметр', 'Значение'])
            self.create_file_if_not_exists(defects_path, self.defect_fields)

            QMessageBox.information(self, 'Проект создан', f'Проект создан по пути:\n{project_dir}')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Папка для нового проекта не выбрана.')

    def create_file_if_not_exists(self, file_path, headers):
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(headers)

    def update_config_paths(self, project_dir):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)

        if 'paths' not in config:
            config['paths'] = {}

        config['paths']['const_params'] = os.path.join(project_dir, 'const_params.csv')
        config['paths']['defects'] = os.path.join(project_dir, 'defects.csv')

        with open(self.config_file, 'w', encoding='utf-8') as file:
            config.write(file)

    def show_bridge_params(self):
        if not self.project_dir:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите проект.')
            return

        self.load_params()
        self.central_widget.setCurrentWidget(self.bridge_params_widget)

    def show_defects(self):
        if not self.project_dir:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите проект.')
            return

        self.load_defects()
        self.central_widget.setCurrentWidget(self.defects_widget)

    def load_params(self):
        const_params_path = os.path.join(self.project_dir, 'const_params.csv')
        if os.path.exists(const_params_path):
            with open(const_params_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                params = {row[0]: row[1] for row in reader if len(row) == 2}

            for param in self.params:
                if param in params:
                    if isinstance(self.inputs[param], QComboBox):
                        index = self.inputs[param].findText(params[param])
                        if index != -1:
                            self.inputs[param].setCurrentIndex(index)
                    else:
                        self.inputs[param].setText(params[param])
                else:
                    if isinstance(self.inputs[param], QComboBox):
                        self.inputs[param].setCurrentIndex(0)  # Set default index for combo box
                    else:
                        self.inputs[param].clear()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Файл параметров моста не найден.')


    def save_params(self):
        const_params_path = os.path.join(self.project_dir, 'const_params.csv')
        with open(const_params_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Параметр', 'Значение'])
            for param in self.params:
                if isinstance(self.inputs[param], QComboBox):
                    value = self.inputs[param].currentText()
                else:
                    value = self.inputs[param].text()
                self.params[param] = value
                writer.writerow([param, value])

        QMessageBox.information(self, 'Сохранено', 'Параметры моста сохранены успешно.')


    def load_defects(self):
        defects_path = os.path.join(self.project_dir, 'defects.csv')
        if os.path.exists(defects_path):
            self.defects_df = pd.read_csv(defects_path, sep=';')
            self.update_groups_list()  # Обновляем список групп
            self.on_group_select1()  # Обновляем дефекты для первой группы
        else:
            self.defects_df = pd.DataFrame(columns=self.defect_fields)
            QMessageBox.warning(self, 'Ошибка', 'Файл дефектов не найден.')

    def update_groups_list(self):
        # Получение уникальных групп и добавление "(Все дефекты)"
        self.groups = ['(Все дефекты)'] + sorted(self.defects_df['Группа'].dropna().unique().tolist())
        self.groups_listbox.clear()
        self.groups_listbox2.clear()

        # Добавление групп в QListWidget
        for group in self.groups:
            self.groups_listbox.addItem(group)
        
        catalog_groups = ['(Все дефекты)'] + sorted(self.catalog_defects_df['Группа'].dropna().unique().tolist())
        for group in catalog_groups:
            self.groups_listbox2.addItem(group)

        # Установка первой группы в качестве выбранной и обновление списка дефектов
        if self.groups_listbox.count() > 0:
            self.groups_listbox.setCurrentRow(0)  # Убедиться, что первая группа выбрана
            self.on_group_select1()  # Обновить список дефектов для выбранной группы в первом списке

        if self.groups_listbox2.count() > 0:
            self.groups_listbox2.setCurrentRow(0)  # Убедиться, что первая группа выбрана
            self.on_group_select2()  # Обновить список дефектов для выбранной группы во втором списке

    def on_group_select1(self):
        selected_item = self.groups_listbox.currentItem()
        if selected_item is None:
            return
        selected_group = selected_item.text()
        if selected_group == '(Все дефекты)':
            defects = self.defects_df
        else:
            defects = self.defects_df[self.defects_df['Группа'] == selected_group]

        self.defects_listbox.clear()

        for index, row in defects.iterrows():
            defect_name = f"{row['Название дефекта']} ({row['Код дефекта по каталогу']}) [{index + 1}]"
            self.defects_listbox.addItem(defect_name)

        self.clear_defect_fields()  # Clear defect fields when changing groups

    def on_defect_select1(self):
        selected_item = self.defects_listbox.currentItem()
        if selected_item:
            selected_defect = selected_item.text()
            defect_number = int(selected_defect.split('[')[-1].strip(']')) - 1

            if 0 <= defect_number < len(self.defects_df):
                defect = self.defects_df.iloc[defect_number]

                for field in self.defect_fields:
                    value = defect[field]
                    if field == 'Базовый':
                        self.defect_entries[field].setChecked(value == 1)
                    else:
                        self.defect_entries[field].setText(str(value))
            else:
                QMessageBox.warning(self, 'Ошибка', 'Выбранный дефект недоступен.')
        else:
            self.clear_defect_fields()

    def on_defect_select2(self):
        selected_item = self.defects_listbox2.currentItem()
        if selected_item:
            selected_defect = selected_item.text()
            defect_number = int(selected_defect.split('[')[-1].strip(']')) - 1

            if 0 <= defect_number < len(self.catalog_defects_df):
                defect = self.catalog_defects_df.iloc[defect_number]

                for field in self.defect_fields:
                    try:
                        if field == 'Базовый':
                            self.defect_entries[field].setChecked(str(defect[field]) == '1')
                        else:
                            self.defect_entries[field].setText(str(defect[field]))
                    except KeyError as e:
                        QMessageBox.warning(self, 'Ошибка', f'Ошибка при доступе к полю {field}:\n{str(e)}')
                        self.clear_defect_fields()
                        return
            else:
                QMessageBox.warning(self, 'Ошибка', 'Выбранный дефект недоступен.')
                self.clear_defect_fields()
        else:
            self.clear_defect_fields()


    def on_group_select2(self):
        selected_item = self.groups_listbox2.currentItem()
        if selected_item is None:
            return
        selected_group = selected_item.text()
        if selected_group == '(Все дефекты)':
            defects = self.catalog_defects_df
        else:
            defects = self.catalog_defects_df[self.catalog_defects_df['Группа'] == selected_group]

        self.defects_listbox2.clear()

        for index, row in defects.iterrows():
            defect_name = f"{row['Название дефекта']} ({row['Код дефекта по каталогу']}) [{index + 1}]"
            self.defects_listbox2.addItem(defect_name)




    def add_defect(self):
        new_defect = {field: (self.defect_entries[field].isChecked() if field == 'Базовый' else self.defect_entries[field].text()) for field in self.defect_fields}

        if not new_defect['Код дефекта по каталогу']:
            QMessageBox.warning(self, 'Ошибка', 'Необходимо заполнить код дефекта по каталогу.')
            return

        if not new_defect['Название дефекта']:
            QMessageBox.warning(self, 'Ошибка', 'Необходимо заполнить название дефекта.')
            return

        if new_defect['Группа'] and new_defect['Группа'] not in self.groups:
            self.groups.append(new_defect['Группа'])
            self.update_groups_list()

        new_defect['Базовый'] = 1 if new_defect['Базовый'] else 0

        new_defect_df = pd.DataFrame([new_defect], columns=self.defect_fields)
        self.defects_df = pd.concat([self.defects_df, new_defect_df], ignore_index=True)
        self.on_group_select1()  # Обновляем список дефектов для первой группы
        self.on_group_select2()  # Обновляем список дефектов для второй группы
        self.save_defects()
        self.clear_defect_fields()



    def delete_defect(self):
        selected_item = self.defects_listbox.currentItem()
        if selected_item:
            selected_defect = selected_item.text()
            defect_number = int(selected_defect.split('[')[-1].strip(']')) - 1

            if 0 <= defect_number < len(self.defects_df):
                self.defects_df = self.defects_df.drop(self.defects_df.index[defect_number]).reset_index(drop=True)
                self.save_defects()

                selected_group = self.groups_listbox.currentItem().text()
                if selected_group != '(Все дефекты)' and self.defects_df[self.defects_df['Группа'] == selected_group].empty:
                    self.groups.remove(selected_group)
                    self.update_groups_list()

                self.on_group_select1()  # Обновляем список дефектов для первой группы
                self.on_group_select2()  # Обновляем список дефектов для второй группы
                QMessageBox.information(self, 'Успех', 'Дефект удален успешно')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Выбранный дефект недоступен.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите дефект для удаления.')

        self.update_groups_list()

    def save_defects(self):
        defects_path = os.path.join(self.project_dir, 'defects.csv')
        self.defects_df.to_csv(defects_path, sep=';', index=False)
        QMessageBox.information(self, 'Сохранено', 'Файл дефектов сохранен успешно.')

    def clear_defect_fields(self):
        for field in self.defect_fields:
            if field == 'Базовый':
                self.defect_entries[field].setChecked(False)
            else:
                self.defect_entries[field].clear()

    
    def edit_defect(self):
        selected_item = self.defects_listbox.currentItem()
        if selected_item:
            selected_defect = selected_item.text()
            defect_number = int(selected_defect.split('[')[-1].strip(']')) - 1

            if 0 <= defect_number < len(self.defects_df):
                for field in self.defect_fields:
                    if field == 'Базовый':
                        self.defects_df.at[defect_number, field] = '1' if self.defect_entries[field].isChecked() else '0'
                    else:
                        self.defects_df.at[defect_number, field] = self.defect_entries[field].text()

                self.save_defects()
                self.on_group_select1()  # Обновляем список дефектов для первой группы
                self.on_group_select2()  # Обновляем список дефектов для второй группы
                QMessageBox.information(self, 'Успех', 'Дефект обновлен успешно.')
            else:
                QMessageBox.warning(self, 'Ошибка', 'Выбранный дефект недоступен.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Сначала выберите дефект для редактирования.')
            
    def calculate_result(self):
        g = Grader()
        g.get_grade()


        
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
