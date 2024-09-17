from grading import Grader
import csv


class Socket:
    def __init__(self, grader: Grader):
        self.grader = grader

    def load_file(self, path):
        self.grader.set_defects(path)

    def save_file(self, name):
        with open('../saved/' + name + '.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            for row in self.grader.get_defects():
                csvwriter.writerow(row)
            csvwriter.writerows()


class ConsoleInterface:
    def __init__(self):
        pass

    def start(self) -> None:
        print("Программа для оценивания мостов")
        inp = ''
        loaded = False
        while inp != 'exit':
            inp = input('command: ')
            if inp == 'load' and not loaded:
                file_def = input('укажите название файла дефектов: ')
                file_param = input('укажите название файла параметров сооружения: ')
                zagruzit(file_def, file_param)
                loaded = True
                print('успешно загружено')
            if inp == 'save' and loaded:





c = ConsoleInterface()
c.start()
