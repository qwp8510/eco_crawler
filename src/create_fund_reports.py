import logging
from os import path
import json
from datetime import datetime, timedelta

from crawlers.cathaylife import CathaylifeFundCrawler

logger = logging.getLogger(__name__)
CURRENT_PATH = path.dirname(path.abspath(__file__))


def read_config():
    with open('./crawlers/config.json', 'r') as js:
        return json.load(js)


def read_user_data():
    with open('./user_data.json', 'r') as js:
        return json.load(js)


def _get_net_worth(url):
    return CathaylifeFundCrawler.instance(url).net_worth


def write_records(records):
    with open('./records.json', 'w') as js:
        json.dump(records, js)


def gen_day_record(fund_total):
    result = {}
    records = []
    for code, data in read_config().items():
        net_worth = _get_net_worth(data.get('url'))
        dividen = (fund_total / float(net_worth)) * data.get('dividenPercentage', 0)
        record = {'code': code,
               'name': data['name'],
               'dividen': dividen,
               'date': datetime.now().strftime('%Y-%m-%d')}
        result[code] = record
        records.append(record)
        logger.info('create record: {}'.format(record))
    write_records({k: v for k, v in sorted(
        result.items(), key=lambda item: item[1]['dividen'], reverse=True)})
    return records


def gen_report():
    user_data = read_user_data()
    total = user_data['num'] * user_data['net_worth']
    return gen_day_record(total)


def main():
    gen_report()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)-15s:%(levelname)s:%(name)s:%(message)s')
    main()
