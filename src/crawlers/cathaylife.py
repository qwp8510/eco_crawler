import requests
import logging
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


class CathaylifeFundCrawler():
    def __init__(self, url):
        self._url = url
        self._page_html = None

    @classmethod
    def instance(cls, url):
        return cls(url)

    @property
    def page_html(self):
        if not self._page_html:
            try:
                result = requests.get(self._url)
                self._page_html = BeautifulSoup(result.text, 'html.parser')
            except requests.exceptions.HTTPError as err:
                logger.error('set_page fail with {}'.format(err))
            except Exception as err:
                logger.error('set_page fail with {}'.format(err))
        return self._page_html

    def find_html_element(self, html, element, filter_parameter):
        try:
            return html.find_all(element, filter_parameter)
        except AttributeError as err:
            logger.error('find_html_element fail with AttributeError: {}'.format(err))
            return []
        except Exception as err:
            logger.error('find_html_element fail with Exception: {}'.format(err))
            return []

    @property
    def table_html(self):
        class_name = 'table table-striped table-bordered reversion-xs page-break-inside-avoid'
        result = self.find_html_element(self.page_html, 'table', {'class': class_name})
        if len(result) == 1:
            return result[0]
        else:
            logger.error(
                'get table by its class name, but got uncorrected number :{}'.format(result))

    @property
    def page_table_fields(self):
        filter_field = ['淨值日期']
        for element in self.find_html_element(self.table_html, 'th', {}):
            if element.text in filter_field:
                continue
            yield element.text

    @property
    def page_table_values(self):    
        for element in self.find_html_element(
            self.table_html, 'td', {'class': 'text-right'}):
            yield element.text

    @property
    def net_worth_field_idx(self):
        net_worth_field = '最新淨值'
        try:
            idx = list(self.page_table_fields).index(net_worth_field)
            return idx
        except ValueError:
            logger.error('{} is not in the list {}'.format(
                net_worth_field, list(self.page_table_fields)))
        except Exception as err:
            logger.error('net_worth_field_idx fail with {}'.format(err))

    @property
    def net_worth(self):
        net_worth = 'unfind net worth'
        try:
            net_worth = list(self.page_table_values)[self.net_worth_field_idx]
        except IndexError:
            logger.error('list: {} index {} out of range'.format(self.page_table_values, idx))
        except Exception as err:
            logger.error('net_worth fail with {}'.format(err))
        finally:
            return net_worth

def main():
    crawler = CathaylifeFundCrawler.instance(
        'https://fund.cathaylife.com.tw/w/wb/wb01.djhtm?a=alb58-abu033')
    logger.info(crawler.net_worth)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)-15s:%(levelname)s:%(name)s:%(message)s')
    main()
