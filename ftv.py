from bs4 import BeautifulSoup
import requests
from datetime import date
import re

today = date.today()

# SBS ESPN
response = requests.get('http://schedule.sbs.co.kr/index.jsp?pmDiv=tv&pmSubDiv=espn&pmDate={}'.format(str(today).replace('-', '')))
soup = BeautifulSoup(response.text, 'lxml')
table = soup.find('table', summary='TV 주간 편성표').find('tbody')
trs = table.find_all('tr')

for tr in trs:
    start_time = tr.find('th').find('div').text.strip()
    start_time = re.sub(r'(AM|PM)', '', start_time)

    content = tr.find('td').find('div')
    title = content.text.strip()

    if '잉글리시 프리미어리그' not in title:
        continue

    # 중복 제거
    title_list = title.split()
    for t in title_list:
        if title_list.count(t) > 1:
            title_list.remove(t)

    title = ' '.join(title_list)
    is_live = content.find('img', alt='생방송') is not None
    print('channel: sbs espn start: {} {} title: {} is_live: {}'.format(today, start_time, title, is_live))

title_strings = ('프리미어리그', '라리가', '클럽 월드컵', '분데스리가')
# SPOTV, SPOTV2, SPOTV+
for channel in ('spotv', 'spotv2', 'spotvp'):
    for timing in ('morning', 'evening', 'night'):
        url = "http://www.spotv.net/data/json/schedule/daily.json2.asp?y={year}&m={month}&d={day}&dayPart={timing}&ch={channel}".format(
                year=today.year, month=today.month, day=today.day,
                timing=timing, channel=channel
                )
        response = requests.get(url, headers={'X-Requested-With': 'XMLHttpRequest'})
        results = response.json()

        for result in results:
            include_title = False
            for title_string in title_strings:
                if title_string in result['title']:
                    include_title = True
                    break

            if not include_title:
                continue

            # {'kind': 'LIVE', 'sch_date': '2016-12-11', 'sch_min': '50', 'sch_hour': 15, 'title': 'FIFA 클럽 월드컵 2016 전북:클럽 아메리카'}
            print('channel: {} start: {} {}:{} title: {} is_live: {}'.format(channel, result['sch_date'], result['sch_hour'], result['sch_min'], result['title'], result['kind'] == 'LIVE'))
