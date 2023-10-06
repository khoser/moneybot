import os
import pandas
import sys
# from uuid import uuid4 as guid
import PocketClass
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

ids = [int(os.environ.get('ID_KTU')), int(os.environ.get('ID_ERO'))]
pcs = PocketClass.Pockets('MyPythonMoney.db')
URL = os.environ.get('URL')
LOGIN = os.environ.get('LOGIN')
PASS = os.environ.get('PASS')
pcs.set_settings(URL, LOGIN, PASS)


def define_item(param):
    # todo определить статью по комментарию
    return 'Прочие расходы'


def out(main_data):
    pocket = 'Ziraat TRY'  # pcs.pockets[-5]
    item = define_item(main_data['Explanation'])
    date = datetime.strptime(main_data['Date'], '%d.%m.%Y')
    sum = - float(main_data['Transaction Amount'].replace(',', ''))
    # print(type(sum), sum)
    pcs.action_out(pocket=pocket, item=item, summ=sum, amount=0, comment=main_data['Explanation'], date=date)
    return main_data


def main(filename):
    pcs.get_data()

    df = pandas.read_csv(filename)
    tasks = [row for _, row in df.iterrows()]

    n = 0
    with ThreadPoolExecutor(max_workers=4) as executor:
        result = executor.map(out, tasks)
        for r in result:
            n = n + 1
            print(str(n) + " " + str(r))

    pcs.post_data()

if __name__ == '__main__':
    main(sys.argv[1])
