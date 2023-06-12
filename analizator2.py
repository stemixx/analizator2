"""
Программа Анализатор2 составлеяет файл в формате ЕГИССО с назначенными льготами родителям
для последующей загрузки в систему.
Анализатор2 берёт из 1С.xls СНИЛС получателя (родителя) и Сумма
(СНИЛС может повторяться в разных строках) и проверяет, есть ли такой СНИЛС в общая_база.csv
Если есть, то в новый файл Для_загрузки_в_ЕГИССО.csv (с заголовком из fieldnames)
помещает совпавшую по СНИЛС строку из общая_база.csv и заполняет значение amount, равное Сумма
Если нет, то создаёт отдельный файл Не_найдены_в_общей базе.csv (с заголовком из fieldnames) и полями для
последующей ручной корректировки
"""
import csv
import os
import pandas as pd
import datetime


COMMON_BASE = 'общая_база.csv'
DATA_1C = '1C.xls'
# берём из файла 1С.xls столбцы ФИО родителя, СНИЛС родителя, Дата назначения, Сумма
SNILS_1C_DF = pd.read_excel(DATA_1C, usecols='C,F,G,H', dtype=str)

# шапка таблицы для ЕГИССО
FILE_ROW = {
            'RecType': 'Fact',
            'assignmentFactUuid': '',
            'LMSZID': 'b68bdde6-7864-4daa-8aff-bd1da70dd76f',
            'categoryID': 'b8c86b2a-b958-49bc-a075-a8730efa9ef4',
            'ONMSZCode': 'A068.000001',
            'LMSZProviderCode': '',
            'providerCode': '',
            'SNILS_recip': '',
            'FamilyName_recip': '',
            'Name_recip': '',
            'Patronymic_recip': '',
            'Gender_recip': '',
            'BirthDate_recip': '',
            'doctype_recip': '',
            'doc_Series_recip': '',
            'doc_Number_recip': '',
            'doc_IssueDate_recip': '',
            'doc_Issuer_recip': '',
            'SNILS_reason': '',
            'FamilyName_reason': '',
            'Name_reason': '',
            'Patronymic_reason': '',
            'Gender_reason': '',
            'BirthDate_reason': '',
            'kinshipTypeCode': '',
            'doctype_reason': '',
            'doc_Series_reason': '',
            'doc_Number_reason': '',
            'doc_IssueDate_reason': '',
            'doc_Issuer_reason': '',
            'decision_date': '',
            'dateStart': 'ЧЧ.ММ.ГГГГ',
            'dateFinish': 'ЧЧ.ММ.ГГГГ',
            'usingSign': 'Нет',
            'criteria': '',
            'criteriaCode': '',
            'FormCode': '01',
            'amount': '',
            'measuryCode': '01',
            'monetization': 'Нет',
            'content': '',
            'comment': '',
            'equivalentAmount': ''
        }


def multiple_replace(target_str):
    """
    Получаем на входе строку с данными, где символы надо заменить
    """

    replace_values = {' ': '', '-': '', '.': ','}
    for i, j in replace_values.items():
        # меняем символы в target_str на подставляемое из replace_values
        target_str = target_str.replace(i, j)
    return target_str


def make_templates_files(fieldnames):
    """
    Cоздаём 2 файла с шапками из FILE_ROW
    """

    with open('Для_загрузки_в_ЕГИССО.csv', 'a', newline='') as template:
        writer = csv.writer(template, delimiter=';')
        writer.writerow(fieldnames)
    with open('Не_найдены_в_общей базе.csv', 'a', newline='') as template:
        writer = csv.writer(template, delimiter=';')
        writer.writerow(fieldnames)
        return None


def delete_file():
    """
    Проверяем есть ли в каталоге файлы "Для_загрузки_в_ЕГИССО.csv" и "Не_найдены_в_общей базе.csv".
    При наличии удаляем их из каталога
    """

    file_install_egisso = 'Для_загрузки_в_ЕГИССО.csv'
    file_not_found_egisso = 'Не_найдены_в_общей базе.csv'
    if os.path.isfile(file_install_egisso) is True:
        os.remove(file_install_egisso)
    if os.path.isfile(file_not_found_egisso) is True:
        os.remove(file_not_found_egisso)
    pass


def delete_duplicated():
    """
    Удаляем дубли в файле "общая_база.csv"
    """

    emp = pd.read_csv(COMMON_BASE, sep=';', encoding='cp1251', dtype=str)
    emp.head()
    emp.columns
    emp[emp.duplicated(['SNILS_recip'])]
    result = emp.drop_duplicates(subset='SNILS_recip', keep='first')
    result.to_csv(COMMON_BASE, sep=';', encoding='cp1251', index=False)
    pass


def date_start_finish():
    """
    Получаем дату первого и последнего дня предыдущего месяца
    """
    today = datetime.date.today()
    first_day_of_month = datetime.date(today.year, today.month, 1)
    prev_month_last_day = first_day_of_month - datetime.timedelta(days=1)
    prev_month_first_day = datetime.date(prev_month_last_day.year, prev_month_last_day.month, 1)
    return prev_month_first_day.strftime('%d.%m.%Y'), prev_month_last_day.strftime('%d.%m.%Y')


def formatted_date_str(date_from_1C):
    """
    Преобразуем дату из 1С к нормальному виду
    """
    try:
        datetime_obj = datetime.datetime.strptime(date_from_1C, '%Y-%m-%d %H:%M:%S')
        formatted_date_str = datetime_obj.strftime('%d.%m.%Y')
    except ValueError:
        return date_from_1C
    return formatted_date_str


def main():
    """
    Проверяем на совпадение СНИЛС в файлах "1С.xls" и "Общая_база.csv".
    Если найден СНИЛС в файле "Общая_база.csv", то обновляем данные строки в файле "Для_загрузки_в_ЕГИССО.csv",
    иначе записываем данные в файл "Не_найдены_в_общей базе.csv"
    """

    delete_file()
    fieldnames = list(FILE_ROW.keys())
    make_templates_files(fieldnames)
    delete_duplicated()


    # открываем общую базу и ищем СНИЛС (row[7]) из data_list
    with open(COMMON_BASE) as file:
        reader = csv.reader(file, delimiter=';')
        file_all_peoples = list(reader)[1::]
        with open('Для_загрузки_в_ЕГИССО.csv', 'a', newline='') as new_egisso:
            writer_new_egisso_file = csv.DictWriter(new_egisso, fieldnames=fieldnames, delimiter=';')
            with open('Не_найдены_в_общей базе.csv', 'a', newline='') as not_found:
                writer_not_found_file = csv.DictWriter(not_found, fieldnames=fieldnames, delimiter=';')

                for data in SNILS_1C_DF.iterrows():
                    # создаём списки с получателями льгот за отчётный период
                    data_list = [
                        str(data[1][0]).split(' '),    # ФИО
                        multiple_replace(data[1][1]),  # СНИЛС
                        formatted_date_str(data[1][2]),# Дата назначения
                        # data[1][2],
                        date_start_finish()[0],        # Дата старта
                        date_start_finish()[1],        # Дата окончания
                        multiple_replace(data[1][3]),  # Сумма
                    ]
                    people_found = False
                    for row in file_all_peoples:
                        if data_list[1] == row[7]:
                            # если СНИЛС нашли, записываем в новый файл для ЕГИССО
                            FILE_ROW['SNILS_recip'] = row[7]
                            FILE_ROW['FamilyName_recip'] = row[8]
                            FILE_ROW['Name_recip'] = row[9]
                            FILE_ROW['Patronymic_recip'] = row[10]
                            FILE_ROW['Gender_recip'] = row[11]
                            FILE_ROW['BirthDate_recip'] = row[12]
                            FILE_ROW['doctype_recip'] = row[13]
                            FILE_ROW['doc_Series_recip'] = row[14]
                            FILE_ROW['doc_Number_recip'] = row[15]
                            FILE_ROW['doc_IssueDate_recip'] = row[16]
                            FILE_ROW['doc_Issuer_recip'] = row[17]
                            FILE_ROW['decision_date'] = data_list[2]
                            FILE_ROW['dateStart'] = data_list[3]
                            FILE_ROW['dateFinish'] = data_list[4]
                            FILE_ROW['amount'] = data_list[5]
                            writer_new_egisso_file.writerow(FILE_ROW)
                            people_found = True
                            break

                    if people_found is False:
                        # если не нашли, то записываем в новый файл для ручного ввода
                        FILE_ROW['SNILS_recip'] = str(data_list[1])
                        FILE_ROW['FamilyName_recip'] = data_list[0][0]
                        FILE_ROW['Name_recip'] = data_list[0][1]
                        if len(data_list[0]) > 3:
                            FILE_ROW['Patronymic_recip'] = data_list[0][2] + ' ' + data_list[0][3]
                        else:
                            FILE_ROW['Patronymic_recip'] = data_list[0][2]
                        FILE_ROW['Gender_recip'] = 'М или Ж'
                        FILE_ROW['BirthDate_recip'] = 'ЧЧ.ММ.ГГГГ'
                        FILE_ROW['doctype_recip'] = '03'
                        FILE_ROW['doc_Series_recip'] = 'ХХХХ'
                        FILE_ROW['doc_Number_recip'] = 'ХХХХХХ'
                        FILE_ROW['doc_IssueDate_recip'] = 'ЧЧ.ММ.ГГГГ'
                        FILE_ROW['doc_Issuer_recip'] = 'строка кем выдан паспорт - в произвольном виде'
                        FILE_ROW['decision_date'] = data_list[2]
                        FILE_ROW['dateStart'] = data_list[3]
                        FILE_ROW['dateFinish'] = data_list[4]
                        FILE_ROW['amount'] = data_list[5]
                        writer_not_found_file.writerow(FILE_ROW)


if __name__ == '__main__':
    main()

