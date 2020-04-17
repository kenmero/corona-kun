"""日本国内の完成者数を取得する"""
# 組み込みモジュール
import re

# サードパーティ
import bs4
import json
import requests


class InfectedPerson(object):
    """日本国内の感染者数を収集する機能を実装
    下記ホームページから都道府県別に収集を行う
    https://www.nippon.com/ja/japan-data/h00663/
    """

    HOME_PAGE = 'https://www.nippon.com/ja/japan-data/h00663/'

    def __init__(self):
        # 都道府県別感染者数格納用変数
        self.ipbp_db = {}
        # 国内感染者数格納用変数
        self.di_db = {}

        # 前日データ
        self.before_ipbp_db = None
        self.before_di_db = None

        # 前日感染者数読み込み
        self.read_today_before()

    def load(self):
        """感染者数確認ホームページ読み込み"""
        # html解析
        self._parse_html()

        # トピック毎にデータを分割
        self._separate_topic()

        # 都道府県別感染者数取得
        self._set_number_of_infected_people_by_prefecture()

        # 国内感染者数取得
        self._set_domestic_infected()

    def searcher(self, keyword=None):
        """検索"""
        hit_data = ''
        if keyword:
            # 読み込み
            self.load()

            # 国内感染者情報確認
            hit_data = self._search_domestic_infected(keyword)
            if not hit_data:
                # 都道府県別感染者数確認
                hit_data = self._search_number_of_infected_people_by_prefecture(keyword)
        return hit_data

    def _search_number_of_infected_people_by_prefecture(self, keyword):
        """都道府県別感染者検索処理"""
        hit_datas = []

        r = re.compile(keyword)
        for prefecture, value in self.ipbp_db.items():

            if keyword == '都道府県':
                is_hit = True
            else:
                m = r.search(prefecture)
                is_hit = True if m else False

            if is_hit:
                copy_value = value.copy()
                title1, number1 = copy_value.popitem()
                title2, number2 = copy_value.popitem()

                diff_number1 = number1 - self.before_ipbp_db[prefecture][title1]
                diff_number2 = number2 - self.before_ipbp_db[prefecture][title2]
                hit_datas.append(f'{prefecture}\n    '
                                 f'{title2}: {number2}人 (前日差分: {diff_number2})\n    '
                                 f'{title1}: {number1}人 (前日差分: {diff_number1})')
        return '\n'.join(hit_datas)

    def _search_domestic_infected(self, keyword):
        """国内感染者検索処理"""
        hit_datas = []

        r = re.compile(keyword)
        for title, number in self.di_db.items():
            if keyword == '国内':
                is_hit = True
            else:
                m = r.search(title)
                is_hit = True if m else False

            if is_hit:
                diff = number - self.before_di_db[title]
                hit_datas.append(f'{title} {number}人 (前日差分: {diff})')
        return '\n'.join(hit_datas)

    def _parse_html(self):
        """html解析"""
        response = requests.get(self.HOME_PAGE)
        self._bs = bs4.BeautifulSoup(response.text, 'html.parser')

    def _separate_topic(self):
        """都道府県別感染者数トピックと国内感染者数トピックでデータを分割"""
        topics = self._bs.find_all('div', class_='scroll')
        self._topic_domestic_infected = topics[0]
        self._topic_infected_persons_by_prefecture = topics[1]

    def _set_number_of_infected_people_by_prefecture(self):
        """都道府県別感染者数取得"""

        tr_tags = self._topic_infected_persons_by_prefecture.find_all('tr')
        for i, tr_tag in enumerate(tr_tags):
            if i == 0:
                continue

            data = tr_tag.text.split('\n')[1:-1]
            data = [d.strip('\u3000') if d.strip('\u3000') else '0' for d in data]
            db = {
                data[0]: {
                    '感染者数': int(data[1]),
                    '死亡者数': int(data[2])
                }
            }
            self.ipbp_db.update(db)

    def _set_domestic_infected(self):
        """国内感染者数取得"""
        tr_tags = self._topic_domestic_infected.find_all('tr')
        for i, tr_tag in enumerate(tr_tags):
            data = tr_tag.text.split('\n')[1:-1]
            data = [d.strip('\u3000') if d.strip('\u3000') else 0 for d in data]

            db = {
                data[0]: int(data[1])
            }

            self.di_db.update(db)

    def write_today_before(self):
        # TODO: 毎日0時に更新
        with open('today_before_di_db.json', 'w', encoding='utf-8') as js:
            json.dump(self.di_db, js, ensure_ascii=False, indent=4)

        with open('today_before_ipbp_db.json', 'w', encoding='utf-8') as js:
            json.dump(self.ipbp_db, js, ensure_ascii=False, indent=4)

    def read_today_before(self):
        with open('today_before_di_db.json', encoding='utf-8') as js:
            self.before_di_db = json.load(js)

        with open('today_before_ipbp_db.json', encoding='utf-8') as js:
            self.before_ipbp_db = json.load(js)


if __name__ == '__main__':
    ip = InfectedPerson()
    hit = ip.searcher('都道府県')
    # ip.write_today_before()
    print(hit)
