import urllib
import urllib2
import json
from datetime import date, datetime, timedelta
from dateutil.rrule import rrule, DAILY

username=''
passwd=''
url = 'https://jawbone.com/user/signin/login'

params = urllib.urlencode({
  'email': username,
  'pwd': passwd,
  'service': 'nudge'
})
resp = urllib2.urlopen(url, params)
data = json.load(resp)   
token = data["token"]

url = 'https://jawbone.com/nudge/api/v.1.33/users/@me/sleeps?limit=200'
opener = urllib2.build_opener()
opener.addheaders.append(('x-nudge-token', token))
resp = opener.open(url)
data = json.load(resp)
sleep_data = []
for i in range(0, len(data["data"]["items"])):
    details = data["data"]["items"][i]["details"]
    asleep_dt = datetime.fromtimestamp(details["asleep_time"])
    awake_dt = datetime.fromtimestamp(details["awake_time"])
    sleep_data.append([asleep_dt, awake_dt])

start = sleep_data[len(sleep_data) - 1][1].replace(hour=17, minute=0, second=0)
start -= timedelta(days=1)

end = sleep_data[0][0].replace(hour=0, minute=0, second=0)
end += timedelta(days=1)

k = len(sleep_data) - 1 
for d in rrule(DAILY, dtstart=start, until=end):
    line = d.strftime("%Y-%m-%d %a") + " "
    start = d
    end = start + timedelta(minutes = 15)
    for i in range(0, 24):
        for j in range(0, 4):
            c = "."
            if (k >= 0):
                sleep = sleep_data[k]
                if (sleep[0] < end and sleep[1] >= start):
                    c = "x"
                    if (end >= sleep[1]):
                        k -= 1
            if (start.hour % 12 == 0 and start.minute == 0):
                line += " "
            line += c
            start += timedelta(minutes = 15)
            end += timedelta(minutes = 15)
    print line
    if (d.weekday() == 6):
        print ""
