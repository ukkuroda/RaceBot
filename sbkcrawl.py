import discord
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pytz


#url = 'https://www.worldsbk.com/en/event/NED/2023'
url = 'https://www.worldsbk.com/en/event/CAT/2023'
#url = 'https://www.worldsbk.com/en/event/ITA/2023'
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')
rounds = ['AUS','MAN', 'NED', 'CAT', 'ITA', 'GBR', 'ITA1', 'CZE', 'FRA',  'ARA', 'POR', 'ARG']



links = []
for link in soup.find_all('a'):
    links.append(link.get('href'))


tokyo_tz= pytz.timezone('Asia/Tokyo')

dates = {'day_0':"Friday", 'day_1':"Saturday", 'day_2':"Sunday"}

for dayIndex, eventTitle in dates.items():
    eventDate=''
    eventtext=''
    day = soup.find('div', id=dayIndex)
    for times in day.find_all('div', class_='timeIso'):
        #print(times.find(attrs={'data_ini':True})['data_ini'])
        if eventDate=='' :
            eventDate=datetime.strptime(times.find(attrs={'data_ini':True})['data_ini'], '%Y-%m-%dT%H:%M:%S%z').astimezone(tokyo_tz).strftime('%Y-%m-%d %H:%M:%S')
        eventtext=eventtext+datetime.strptime(times.find(attrs={'data_ini':True})['data_ini'], '%Y-%m-%dT%H:%M:%S%z').astimezone(tokyo_tz).strftime('%H:%M')
        eventtext=eventtext+'-'
        if times.find(attrs={'data_end':True})['data_end'] :
            eventtext=eventtext+datetime.strptime(times.find(attrs={'data_end':True})['data_end'], '%Y-%m-%dT%H:%M:%S%z').astimezone(tokyo_tz).strftime('%H:%M')
        eventtext=eventtext+'  '
        if times.select('div.cat-session')[0].contents[0] :
            eventtext=eventtext+(times.select('div.cat-session')[0].contents[0])
        eventtext=eventtext+'\r\n'

    
    print(eventTitle)
    print(eventDate)
    print(eventtext)

    print()
