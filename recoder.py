# 組み込みモジュール
import time

# サードパーティ
import schedule

# 自作モジュール
from collector import infected_person


def main():
    # 本日の最終感染者数記録
    ip = infected_person.NipponComSite()
    ip.write_today_before()


if __name__ == '__main__':
    schedule.every().day.at('23:59:59').do(main)
    while True:
        schedule.run_pending()
        time.sleep(60)
