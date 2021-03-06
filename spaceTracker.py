import json
import requests
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    Print any errors.
    """
    print(e)

# ########################################################################################################
#                                       getPeopleInfo()
#
# This function first makes a call to an api which returns the names of the astronauts who are currently in
# space. These names are then used to make a call to a wikipedia api to gather the summary description and
# photo. A collection of the astronauts containing their name, craft, background summary, photo, and total
# number of astronauts is returned.
# ########################################################################################################

def getPeopleInfo():
    url = "http://api.open-notify.org/astros.json"
    response = requests.get(url)
    peopleData = json.loads(response.text)
    peopleList = []
    for i in peopleData['people']:
        currentName = i['name'].replace(" ", "%20")

        if currentName == "Richard%20Arnold":
            currentName = "Richard%20R.%20Arnold"

        if currentName == "Sergey%20Prokopyev":
            currentName = "Sergey%20Prokopyev%20(cosmonaut)"

        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + currentName
        response = requests.get(url)
        peopleInfo = json.loads(response.text)
        numOfAstros = len(peopleData['people'])
        if i['craft'] == 'ISS':
            i['craft'] = 'International Space Station'
        astronaut = {'name': i['name'], 'craft': i['craft'], 'info': peopleInfo['extract'],
                     'photo': peopleInfo['originalimage']['source'], "numOfAstros": numOfAstros}

        peopleList.append(astronaut)

    return peopleList


# ########################################################################################################
#                                       getMissionInfo()
#
# This function utilizes a web scraper to collect information on upcoming rocket launches to space.
# The various html elements are selected and parsed so that mission objects can be created and returned.
# The missionList contains the launch date, launch location, mission name, and mission description.
# ########################################################################################################

def getMissionInfo():
    raw_html = simple_get("https://spaceflightnow.com/launch-schedule/")
    html = BeautifulSoup(raw_html, 'html.parser')
    missionList = []
    counter = 0

    # launchList contains the flight window and launch location
    launchList = []
    for i in html.find_all('div', attrs={"class": 'missiondata'}):
        launchTime = i.text
        launchList.append(launchTime)

    # descriptionList contains the mission descriptions
    descriptionList = []
    for i in html.find_all('div', attrs={"class": 'missdescrip'}):
        missiondescription = i.text
        descriptionList.append(missiondescription)

    # the date and mission name are included before the entire row is appended to the missionList
    for i in html.find_all('div', attrs={'class': 'datename'}):
        date = i.find('span', attrs={'class': 'launchdate'})
        mission = i.find('span', attrs={'class': 'mission'})
        row = {
                "date": date.text, "name":mission.text,
                "launchInfo": launchList[int(counter)],
                "description":descriptionList[int(counter)]
            }
        missionList.append(row)
        counter += 1
    return missionList
