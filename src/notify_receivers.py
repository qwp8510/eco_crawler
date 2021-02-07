import logging
from os import path

from utils.config import Config
from utils.apis.api import Api
from crawlers.cathaylife import CathaylifeFundCrawler
from notificaions.line_notify import LineNotification

logger = logging.getLogger(__name__)
CURRENT_PATH = path.dirname(path.abspath(__file__))


class FundTargets():
    _fund_targets = None

    @classmethod
    def data(cls):
        def _get_fund_targets():
            fund_targets = Api(
                host=Config.instance().get('PORTAL_SERVER'),
                target_path='fundTargets/',
                cache_path=Config.instance().get('CACHE_DIR')).get()
            for target in fund_targets:
                yield target.get('code'), target
        if not cls._fund_targets:
            cls._fund_targets = dict(_get_fund_targets())
        return cls._fund_targets


def _get_receivers():
    return Api(
        host=Config.instance().get('PORTAL_SERVER'),
        target_path='receivers/',
        cache_path=Config.instance().get('CACHE_DIR')
    ).get()


def _get_net_worth(url):
    return CathaylifeFundCrawler.instance(url).net_worth


def _get_url(code):
    return FundTargets.data().get(code).get('url')


def gen_receivers_data():
    def update_net_worth():
        for target in receiver.get('targets'):
            target.update({'net_worth': _get_net_worth(_get_url(target.get('code')))})
            yield target

    for receiver in _get_receivers():
        return {
            receiver.get('name'): {
                'line_token': receiver.get('lineToken'),
                'data': list(update_net_worth())
            }}


def notify_receivers(data):
    for name, value in data.items():
        logger.info('notify to {} data: {}'.format(name, str(value.get('data'))))
        LineNotification(value.get('line_token')).notify(
            '{name}: {data}'.format(name=name, data=str(value.get('data'))))


def main():
    Config.set_dir(path.join(CURRENT_PATH, 'config.json'))
    notify_receivers(gen_receivers_data())


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)-15s:%(levelname)s:%(name)s:%(message)s')
    main()
