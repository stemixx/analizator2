"""
Анализатор2 берёт из 1С.xls СНИЛС и Сумма (СНИЛС может повторяться в разных строках) и проверяет,
есть ли такой СНИЛС в all_peoples.csv
Если есть, то в новый файл Для_загрузки_в_ЕГИССО.csv (с заголовком из fieldnames)
помещает совпавшую по СНИЛС строку из all_peoples.csv и заполняет значение amount, равное Сумма
Если нет, то создаёт отдельный файл Не_найдены_в_общей базе.csv (с заголовком из fieldnames) и полями:
FamilyName_recip = Фамилия
Name_recip = Имя
Patronymic_recip = Отчество
SNILS_recip = СНИЛС
amount = Сумма
"""
import csv
import os
import pandas as pd


PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
ALL_PEOPLES = os.path.join(PROJECT_FOLDER, r'all_peoples_22-test.csv')
DATA_1C = os.path.join(PROJECT_FOLDER, r'1C.xls')
SNILS_1C_df = pd.read_excel(DATA_1C, usecols='E,F', dtype=str)  # берём столбцы Е и F (Сумма и СНИЛС)


def multiple_replace(target_str):
    # получаем на входе строку с данными, где символы надо заменить
    replace_values = {' ': '', '-': '', '.': ','}
    for i, j in replace_values.items():
        # меняем символы в target_str на подставляемое из replace_values
        target_str = target_str.replace(i, j)
    return target_str


SNILS_and_amount_all = []
for index, row in SNILS_1C_df.iterrows():
    SNILS_and_amount = {}
    key = multiple_replace(row['СНИЛС'])
    value = multiple_replace(row['Сумма'])
    SNILS_and_amount[key] = value  # {'078-979-023 42': 277.56, '079-003-284 56': 195.0}
    SNILS_and_amount_all.append(SNILS_and_amount)


fieldnames = [
                    'RecType',
                    'assignmentFactUuid',
                    'LMSZID',
                    'categoryID',
                    'ONMSZCode',
                    'LMSZProviderCode',
                    'providerCode',
                    'SNILS_recip',
                    'FamilyName_recip',
                    'Name_recip',
                    'Patronymic_recip',
                    'Gender_recip',
                    'BirthDate_recip',
                    'doctype_recip',
                    'doc_Series_recip',
                    'doc_Number_recip',
                    'doc_IssueDate_recip',
                    'doc_Issuer_recip',
                    'SNILS_reason',
                    'FamilyName_reason',
                    'Name_reason',
                    'Patronymic_reason',
                    'Gender_reason',
                    'BirthDate_reason',
                    'kinshipTypeCode',
                    'doctype_reason',
                    'doc_Series_reason',
                    'doc_Number_reason',
                    'doc_IssueDate_reason',
                    'doc_Issuer_reason',
                    'decision_date',
                    'dateStart',
                    'dateFinish',
                    'usingSign',
                    'criteria',
                    'criteriaCode',
                    'FormCode',
                    'amount',
                    'measuryCode',
                    'monetization',
                    'content',
                    'comment',
                    'equivalentAmount'
                ]


def make_EGISSO_file():
    with open('Для_загрузки_в_ЕГИССО.csv', 'a', newline='') as template:
        writer = csv.writer(template, delimiter=';')
        writer.writerow(fieldnames)
        return None


# make_EGISSO_file()

with open(ALL_PEOPLES) as file:
    count = 0
    reader = csv.reader(file, delimiter=';')
    for dict_ in SNILS_and_amount_all:          # {'07897902342': '198,26'}
        for key, value in dict_.items():        # 07897902342 198,26
            new_iter = list(reader[1::])
            for row in new_iter:       # Fact		b68bdde6-7864-4daa-8aff-bd1da70dd76f	b8c86b2a-b958-49bc-a075-a8730efa9ef4 ...
                print(key)
                print(row[7])
                if str(row[7]) == key:
                    print('YES')
                else:
                    continue
                #     with open('Для_загрузки_в_ЕГИССО.csv', 'a', newline='') as output_file:
                #         writer = csv.writer(output_file, delimiter=';')
                #         writer.writerow(row)
                # else:
                #     print('No')
                #     count += 1
            # continue
# print(count)
        # if row[7] in get_SNILS_set(): # проверяем, есть ли СНИЛС из общей базы в списке СНИЛС на льготу
        #     with open('Для_загрузки_в_ЕГИССО.csv', 'a', newline='') as output_file:
        #         writer = csv.writer(output_file, delimiter=';')
        #         writer.writerow(row)
        #

