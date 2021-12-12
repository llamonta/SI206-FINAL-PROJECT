import html
import sqlite3
import json
from bs4 import BeautifulSoup
from bs4.element import ProcessingInstruction
import requests
import os
#Names: Zack, Toby, Luc

db_name = "FinalProject.db"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+db_name)
cur = conn.cursor()

nbateams = ["hawks", "celtics", "nets", "hornets", "bulls", "cavaliers", "mavericks", "nuggets", 'pistons', 'warriors', 'rockets', 'pacers', 'clippers', 'lakers', 'grizzlies', 'heat', 'bucks', 'timberwolves', 'pelicans', 'knicks', 'thunder', 'magic', 'sixers', 'suns', 'blazers', 'kings', 'spurs', 'raptors', 'jazz', 'wizards']

def getUSNBATeamsAndRecords():
    requestURL = "https://champsorchumps.us/records/most-nba-wins-since-2010"
    list1 = []
    resp = requests.get(requestURL)
    soup = BeautifulSoup(resp.content, 'html.parser')
    teamnames = soup.find_all( 'table', class_ = 'table table-striped table-condensed')
    for var in teamnames:
        y = var.find_all('td')
        for variable in y:
            list1.append(variable.text.strip())
    outputlist = []
    x = 0
    while x < 210:
        outputlist.append(list1[x])
        outputlist.append(list1[x+1])
        outputlist.append(list1[x+3])
        outputlist.append(list1[x+6])
        x = x + 7
    cur.execute("DROP TABLE IF EXISTS TeamWinPct")
    cur.execute("CREATE TABLE TeamWinPct (Rank INTEGER PRIMARY KEY, Team STRING, WinPercentage INTEGER, ChampionshipsWon INTEGER)")
    y = 0
    while y < 119:
        cur.execute('INSERT INTO TeamWinPct (Rank, Team, WinPercentage, ChampionshipsWon) VALUES (?,?,?,?)', (outputlist[y], outputlist[y+1], outputlist[y+2], outputlist[y+3]))
        y = y + 4
    conn.commit()

getUSNBATeamsAndRecords()

def heightandweight():
    abbreviations = []

    x = 0
    placer2 = []
    for teamname in nbateams:
        url= "http://data.nba.net/json/cms/noseason/team/" + teamname +"/roster.json?limit=25"
        request1 = requests.get(url)
        data1 = request1.text
        data1_dict =json.loads(data1) 
        teamabbreviation = data1_dict['sports_content']['roster']['team']['team_abbrev']
        abbreviations.append(teamabbreviation)
        holder = data1_dict['sports_content']['roster']['players']['player']
        y = 0
        placer1 = []
        while y < len(holder):
            L = []
            heightInInches = 12 * int(holder[y]['height_ft']) + int(holder[y]['height_in'])
            L.append(heightInInches)
            weightinLbs = int(holder[y]['weight_lbs'])
            L.append(weightinLbs)
            placer1.append(L)
            y = y + 1
        placer2.append(placer1)
    cur.execute('DROP TABLE IF EXISTS playerPhysicals')
    cur.execute('CREATE TABLE playerPhysicals (Id INTEGER PRIMARY KEY, Team STRING, HeightInInches INTEGER, WeightInLbs INTEGER)')
    k = 1  
    x = 0
    while x < 30:
        z = 0
        while z < len(placer2[x]):

            cur.execute('INSERT INTO playerPhysicals (Id, Team, HeightInInches, WeightInLbs) VALUES (?,?,?,?)', (k , abbreviations[x], placer2[x][z][0], placer2[x][z][1]))
            z += 1
            k += 1
        x += 1
    conn.commit()
heightandweight()
