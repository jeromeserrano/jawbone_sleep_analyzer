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
MOVES_DATA_URL = 'https://jawbone.com/nudge/api/v.1.33/users/@me/moves'

HIGH_STEPS_SCORE = 20000
MEDIUM_STEPS_SCORE = 10000
LOW_STEPS_SCORE = 2000


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
                   "meta":
                   {
                      "user_xid": "6xl39CsoVp2KirfHwVq_Fx",
                      "message": "OK",
                      "code": 200
                      "time": 1386122022
                   },
                   "data":
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
                      "size": 10
                   }
                }

        Throws:
            Exception if an error occured while making the sleep GET request.
        """
        return self._request(token, SLEEP_DATA_URL)

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
        for item in data["data"]["items"]:
            details = item["details"]
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

    def get_moves_data(self, token):
        """ Perform GET request to obtain moves data.

        Returns:
            Returns the list of moves of the current user.
            Example:
                {
                   "meta":
                   {
                      "user_xid": "6xl39CsoVp2KirfHwVq_Fx",
                      "message": "OK",
                      "code": 200
                      "time": 1386122022
                   },
                   "data":
                   {
                      "items":
                      [{
                         "xid": "40F7_htRRnQwoMjIFucJ2g",
                         "title": "16,804 steps",
                         "type": "move",
                         "time_created": 1384963500,
                         "time_updated": 1385049599,
                         "time_completed": 1385099220,
                         "date": 20131121
                         "snapshot_image": "/nudge/image/e/1385107737/40F7_htRRnQwoMjIFucJ2g/grEGutn_XYZ.png"
                         "details":
                         {
                            "distance": 14745,
                            "km": 14.745,
                            "steps": 16804,
                            "active_time": 11927,
                            "longest_active": 2516,
                            "inactive_time": 32760,
                            "longest_idle": 27180,
                            "calories": 1760.30480012,
                            "bmr_day": 1697.47946931,
                            "bmr": 1697.47946931,
                            "bg_calories": 1099.9439497,
                            "wo_calories": 388.506116077,
                            "wo_time": 11484,
                            "wo_active_time": 3902,
                            "wo_count": 2,
                            "wo_longest": 2516,
                            "tz": "America/Los Angeles",
                            "tzs":
                            [
                               [1384963500, "America/Phoenix"],
                               [1385055720, "America/Los_Angeles"]
                            ],
                            "hourly_totals":
                            {
                                "2013112101":
                                {
                                    "distance": 1324,
                                    "calories": 90.0120018125,
                                    "steps": 1603,
                                    "active_time": 793,
                                    "inactive_time": 220,
                                    "longest_active_time": 302,
                                    "longest_idle_time": 780
                                },
                                "2013112101":
                                {
                                    "distance": 626,
                                    "calories": 47.0120018125,
                                    "steps": 455,
                                    "active_time": 246,
                                    "inactive_time": 260,
                                    "longest_active_time": 203,
                                    "longest_idle_time": 650
                                },
                                ... more hours ...
                            }
                         }
                      },
                      {
                      ... more items ....
                      }],
                      "links":
                      {
                         "next": "/nudge/api/v.1.0/users/6xl39CsoVp2KirfHwVq_Fx/moves?page_token=1384390680"
                      },
                      "size": 10
                   }
                }

        Throws:
            Exception if an error occured while making the sleep GET request.
        """
        return self._request(token, MOVES_DATA_URL)

    def display_moves_data(self, data):
        from_date = min([item['time_completed'] for item in data["data"]["items"]])
        to_date = max([item['time_completed'] for item in data["data"]["items"]])

        print ("%s -> %s" %
               (datetime.fromtimestamp(from_date).strftime('%Y-%m-%d'),
                datetime.fromtimestamp(to_date).strftime('%Y-%m-%d')))

        moves_data = []
        line = ""

        for item in data["data"]["items"]:
            steps = item["details"]["steps"]
            if steps > HIGH_STEPS_SCORE:
                line += "|"
            elif steps > MEDIUM_STEPS_SCORE:
                line += ":"
            elif steps > LOW_STEPS_SCORE:
                line += "."
            else:
                line += " "
        print line

    def _request(self, token, url):
        opener = urllib2.build_opener()
        opener.addheaders.append(('x-nudge-token', token))
        resp = opener.open(url)
        data = json.load(resp)
        if 'error' in data:
            raise Exception("Request to %r failed: %r" % (url, data))

        return data
