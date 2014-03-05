"""
Usage example:

    jawbone = JawboneSleepAnalyzer()
    token = jawbone.login()
    sleep_data = jawbone.get_sleep_data(token)
    jawbone.display_sleep_data(sleep_data)
"""


import urllib
import urllib2
import json
from datetime import date, datetime, timedelta
from dateutil.rrule import rrule, DAILY

USERNAME = ''
PASSWORD = ''
LOGIN_URL = 'https://jawbone.com/user/signin/login'
SLEEP_DATA_URL = 'https://jawbone.com/nudge/api/v.1.33/users/@me/sleeps'


class JawboneSleepAnalyzer():

    def login(self):
        """ Perform login action.

        Returns:
            A string representing an access token that can be used for further
            Jawbone API requests.

        Throws:
            Exception if an error occured while making the login request.
        """
        params = urllib.urlencode({
          'email': USERNAME,
          'pwd': PASSWORD,
          'service': 'nudge'
        })
        resp = urllib2.urlopen(LOGIN_URL, params)
        data = json.load(resp)
        if 'error' in data:
            raise Exception("Login failed: %r" % data)

        return data.get("token")

    def get_sleep_data(self, token):
        """ Perform GET request to obtain sleep data.

        Returns:
            Returns the list of sleeps of the current user.
            Example:
                {
                   “meta”:
                   {
                      “user_xid”: “6xl39CsoVp2KirfHwVq_Fx”,
                      “message”: “OK”,
                      “code”: 200
                      "time": 1386122022
                   },
                   “data”:
                   {
                      "items":
                      [{
                         "xid": "40F7_htRRnQ6_IpPSk0pow",
                         "title": "for 6h 46m",
                         "sub_type": 0,
                         "time_created": 1384963500,
                         "time_completed": 1385099220,
                         "date": 20131121,
                         "place_lat": "37.451572",
                         "place_lon": "-122.184435",
                         "place_acc": 10,
                         "place_name": "My House",
                         "snapshot_image": "/nudge/image/e/1385066264/40F7_htRRnQ6_IpPSk0pow/grEGutn_3mE.png"
                         "details":
                         {
                            "smart_alarm_fire": 1385049600,
                            "awake_time": 1385049573,
                            "asleep_time": 1385023259,
                            "awakenings": 2
                            "rem": 0
                            "light": 8340,
                            "deep": 16044,
                            "awake": 3516,
                            "duration": 27900,
                            "quality": 75
                            "tz": "America/Los_Angeles"
                         }
                      },
                      {
                      ... more items ....
                      }],
                      "links":
                      {
                         "next": "/nudge/api/v.1.0/users/6xl39CsoVp2KirfHwVq_Fx/sleeps?page_token=1384390680"
                      },
                      “size”: 10
                   }
                }

        Throws:
            Exception if an error occured while making the sleep GET request.
        """
        opener = urllib2.build_opener()
        opener.addheaders.append(('x-nudge-token', token))
        resp = opener.open(SLEEP_DATA_URL)
        data = json.load(resp)
        if 'error' in data:
            raise Exception("Request to %r failed: %r" % (SLEEP_DATA_URL, data))

        return data

    def display_sleep_data(self, data):
        """ Display sleep data from Jawbone API.

        Example:
            2014-01-27 Mon ............................ .....xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx..xxxxxxxx.. ....................
            2014-01-28 Tue ............................ ........xxx.....xxxxxxxxxxxxxxxxxxxx............ ....................
            2014-01-29 Wed ............................ .......xxxxxxxxxxxxxxxxxxxxxxxxxxxxx............ ....................

        Each line represents a 24h interval starting at 17h00, each '.' (awake)
        or 'x' (asleep) represents a 15 min interval. For clarity purposes,
        a white space has been introduced at midnight and noon.
        """
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
