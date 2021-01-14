import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

def main():
    url = os.getenv('URL')
    current_time = datetime.strptime(os.getenv('CURRENT'), "%d.%m.%Y %H:%M")
    twilio = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))

    data = requests.get(url)
    data = BeautifulSoup(data.text, 'html.parser')

    table = data.find(id='eksami_ajad:kategooriaBEksamiAjad_data')
    rows = table.find_all('tr')
    available_times = {}
    for row in rows:
        byroo = row.find('td', {'class': 'eksam-ajad-byroo'}).string
        times = row.find_all('td', {"class": "eksam-ajad-aeg"})
        available_times[byroo] = [time.string for time in times]

    if not os.path.exists('notified.txt'):
        with open('notified.txt', 'w'): pass

    with open('notified.txt', 'r', encoding='utf-8') as my_file:
        already_notified_dates = my_file.read().splitlines()

    to_notify = []
    for byroo, times in available_times.items():
        for time in times:
            date = datetime.strptime(time, "%d.%m.%Y %H:%M")
            notified_txt = f"{byroo}={time}"
            if date < current_time and notified_txt not in already_notified_dates:
                to_notify.append(notified_txt)

                with open('notified.txt', 'a+', encoding='utf-8') as my_file:
                    my_file.writelines([notified_txt + '\n'])
                    my_file.close()

    if to_notify:
        times = ' '.join(to_notify)
        message = twilio.messages \
                    .create(
                        body="Uued sõidueksami ajad: " + times,
                        from_=os.getenv('PHONENR_FROM'),
                        to=os.getenv('PHONENR_TO')
                    )

    sys.exit(0)

if __name__ == '__main__':
    main()
