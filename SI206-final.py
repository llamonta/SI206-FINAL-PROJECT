import html
import sqlite3
import json
from bs4 import BeautifulSoup
from bs4.element import ProcessingInstruction
import requests
import os
import re
#Names: Zack, Toby, Luc

db_name = "FinalProject.db"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+db_name)
cur = conn.cursor()

nbateams = ["hawks", "celtics", "nets", "hornets", "bulls", "cavaliers", "mavericks", "nuggets", 'pistons', 'warriors', 'rockets', 'pacers', 'clippers', 'lakers', 'grizzlies', 'heat', 'bucks', 'timberwolves', 'pelicans', 'knicks', 'thunder', 'magic', 'sixers', 'suns', 'blazers', 'kings', 'spurs', 'raptors', 'jazz', 'wizards']

def getUSNBATeamsAndRecords():
    requestURL = "https://www.espn.com/nba/standings/_/season/2016/group/league"
    resp = requests.get(requestURL)
    soup = BeautifulSoup(resp.content, 'html.parser')
    team_names = soup.findAll('a', class_ = 'AnchorLink')
    team_names = [names.getText() for names in team_names[30:121]]
    team_names = [names for names in team_names if len(names) <= 4 and len(names) >= 2]
    #href = /nba/team/_/name/gs/golden-state-warriors (not sure if we'll need it but good to have regardless)
    winning_pct = soup.findAll('span', class_ = 'stat-cell')
    winning_pct = [pct.getText() for pct in winning_pct]
    reg_ex = re.compile('\.\d{3}')
    winning_pct = [pct for pct in winning_pct if bool(re.match(reg_ex, pct))]
    cur.execute("DROP TABLE IF EXISTS TeamWinPct_15_16")
    cur.execute("CREATE TABLE TeamWinPct_15_16 (Team STRING PRIMARY KEY, WinPercentage FLOAT)")
    for i in range(30):
        cur.execute('INSERT INTO TeamWinPct_15_16 (Team, WinPercentage) VALUES (?,?)', (team_names[i], winning_pct[i]))
        i += 1
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

def shootingefficiency():
    url= " http://stats.nba.com/js/data/sportvu/2015/shootingData.json?limit=25"
    request1 = requests.get(url)
    data1 = request1.text
    data1_dict =json.loads(data1) 
    x = 0
    holder = data1_dict['resultSets'][0]['rowSet']
    cur.execute('DROP TABLE IF EXISTS Shoot')
    cur.execute('CREATE TABLE Shoot (Rank INTEGER PRIMARY KEY, playerId INTEGER,Team STRING, EffFgPct INTEGER)')
    k = 0
    while x < len(holder):
        cur.execute('INSERT INTO Shoot (Rank, playerId, Team, EffFgPct) VALUES(?,?,?,?)', (k, holder[x][0], holder[x][4], holder[x][20]))
        x += 1
        k += 1
    conn.commit()

shootingefficiency()

def catchAndShoot():
    url = "http://stats.nba.com/js/data/sportvu/2015/catchShootData.json"
    request1 = requests.get(url)
    data1 = request1.text
    data1_dict =json.loads(data1) 
    holder = data1_dict['resultSets'][0]['rowSet']
    cur.execute('DROP TABLE IF EXISTS Catch')
    cur.execute('CREATE TABLE Catch (Rank INTEGER PRIMARY KEY, playerIndex INTEGER, Team STRING, CandSPct INTEGER)')
    x = 0
    k = 0
    while x < len(holder):
        cur.execute('INSERT INTO Catch (Rank, playerIndex, Team, CandSPct) VALUES(?,?,?,?)', (k,holder[x][0], holder[x][4], holder[x][10]))
        x += 1
        k += 1
    conn.commit()
catchAndShoot()

def joinAverageReupload():
    cur.execute('SELECT Shoot.Team, Shoot.EffFgPct, Catch.CandSPct FROM SHOOT JOIN CATCH WHERE SHOOT.playerId = CATCH.playerIndex')
    list1 = []
    for row in cur:
        list1.append(row)
    dict1 = {}
    countedCentries = {}
    countedteamabb = []
    for data in list1:
        if data[1] == None:
            continue
        if data[0] == "Total":
            continue
        if data[0] in countedCentries:
            countedCentries[data[0]] += 1
        else:
            countedCentries[data[0]] = 1
        if data[0] in countedteamabb:
            continue
        elif data[0] not in countedteamabb:
            countedteamabb.append(data[0])
        
        
    for data in list1:
        if data[1] == None:
                continue
        elif data[0] == "Total":
            continue
        if data[0] in dict1:
            hold = data[1]
            teamabb = data[0]
            current = dict1[teamabb]
            dict1[teamabb] = hold + current
        else:
            dict1[data[0]] = data[1]
    countedEentries = {}
    for data in list1:
        if data[2] == None:
            continue
        if data[0] == "Total":
            continue
        if data[0] in countedEentries:
            countedEentries[data[0]] += 1
        else:
            countedEentries[data[0]] = 1
    dict2 = {}
    for data in list1:
        if data[2] == None:
                continue
        elif data[0] == "Total":
            continue
        if data[0] in dict1:
            hold = data[2]
            teamabb = data[0]
            current = dict1[teamabb]
            dict2[teamabb] = hold + current
        else:
            dict2[data[0]] = data[2]
    cur.execute('DROP TABLE IF EXISTS Effavg')
    cur.execute('CREATE TABLE Effavg (Team STRING PRIMARY KEY, Average INTEGER)')

    for abb in countedteamabb:
        average = dict1[abb] / countedEentries[abb]
        cur.execute('INSERT INTO Effavg (Team, Average) VALUES (?,?)', (abb, average))

    cur.execute('DROP TABLE IF EXISTS CandSavg')
    cur.execute('CREATE TABLE CandSavg (Team STRING PRIMARY KEY, Average INTEGER)')

    for abb in countedteamabb:
        average = dict2[abb] / countedCentries[abb]
        cur.execute('INSERT INTO CandSavg (Team, Average) VALUES (?,?)', (abb, average))
    conn.commit()
    
joinAverageReupload()
