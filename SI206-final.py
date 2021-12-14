import html
import sqlite3
import json
from bs4 import BeautifulSoup
from bs4.element import ProcessingInstruction
import requests
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import csv
#Names: Zack, Toby, Luc


#create SQL link
db_name = "FinalProject.db"
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path+'/'+db_name)
cur = conn.cursor()

#create CSV object
f = open('finalprojectdata.csv', 'w')
writer = csv.writer(f)
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
    cur.execute("CREATE TABLE IF NOT EXISTS TeamWinPct_15_16 (Team STRING PRIMARY KEY, WinPercentage FLOAT)")
    for i in range(30):
        cur.execute('INSERT OR IGNORE INTO TeamWinPct_15_16 (Team, WinPercentage) VALUES (?,?)', (team_names[i], winning_pct[i]))
        i += 1
    conn.commit()
getUSNBATeamsAndRecords()

def heightandweight():
    abbreviations = []
    x = 0
    placer2 = []
    for teamname in nbateams:
        url= "http://data.nba.net/json/cms/noseason/team/" + teamname +"/roster.json?limit=20"
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
    cur.execute('CREATE TABLE IF NOT EXISTS playerPhysicals (Id INTEGER PRIMARY KEY, Team STRING, HeightInInches INTEGER, WeightInLbs INTEGER)')
    cur.execute('SELECT COUNT(*) FROM playerPhysicals')
    currentrowcount = cur.fetchone()[0]
    targetrowcount = currentrowcount + 25
    x = currentrowcount
    rank = 1
    placer3 = []
    z = 0
    for z in range(0,len(placer2)):
        y = 0
        while y < len(placer2[z]):
            hold = []
            hold.append(abbreviations[z])
            hold.append(placer2[z][y][0])
            hold.append(placer2[z][y][1])
            placer3.append(hold)
            y += 1
        z += 1    
    if currentrowcount <= 450:
        while x  < targetrowcount:

                cur.execute('INSERT OR IGNORE INTO playerPhysicals (Id, Team, HeightInInches, WeightInLbs) VALUES (?,?,?,?)', (x , placer3[x][0], placer3[x][1], placer3[x][2]))
                x = x + 1
    conn.commit()

heightandweight()

def avgheight():
    cur.execute('SELECT Team, HeightInInches FROM playerPhysicals')
    list1 = []
    for row in cur:
        list1.append(row)
    countedHentries = {}
    for row in list1:
        if row[0] in countedHentries:
            countedHentries[row[0]] += 1
        else:
            countedHentries[row[0]] = 1
    dict2 = {}
    teamabbs = []
    for data in list1:
        if data[0] in dict2:
            hold = data[1]
            teamabb = data[0]
            current = dict2[teamabb]
            dict2[teamabb] = hold + current
        else:
            dict2[data[0]] = data[1]
            teamabbs.append(data[0])
    cur.execute('SELECT COUNT(*) FROM playerPhysicals')
    rowcount = cur.fetchone()[0]        
    if rowcount >= 450:
        cur.execute('CREATE TABLE IF NOT EXISTS avgHeightOfTeam (Team STRING PRIMARY KEY, AvgHeight INTEGER)')
        for abb in teamabbs:
            teamaverage = dict2[abb] / countedHentries[abb]
            cur.execute('INSERT OR IGNORE INTO avgHeightofTeam (Team, AvgHeight) VALUES (?,?)', (abb, teamaverage))
    conn.commit()



avgheight()

def avgweight():
    cur.execute('SELECT team, WeightInLbs FROM playerPhysicals')
    list2 = []
    for row in cur:
        list2.append(row)
    countedWentries = {}
    for row in list2:
        if row[0] in countedWentries:
            countedWentries[row[0]] += 1
        else:
            countedWentries[row[0]] = 1
    dict2 = {}
    teamabbs = []
    for data in list2:
        if data[0] in dict2:
            hold = data[1]
            teamabb = data[0]
            current = dict2[teamabb]
            dict2[teamabb] = hold + current
        else:
            dict2[data[0]] = data[1]
            teamabbs.append(data[0])
    cur.execute('SELECT COUNT(*) FROM playerPhysicals')
    currentrowcount = cur.fetchone()[0]        
    if currentrowcount >= 450:
        cur.execute('CREATE TABLE IF NOT EXISTS avgWeightOfTeam (Team STRING PRIMARY KEY, AvgWeight INTEGER)')
        for abb in teamabbs:
            teamaverage = dict2[abb] / countedWentries[abb]
            cur.execute('INSERT OR IGNORE INTO avgWeightofTeam (Team, AvgWeight) VALUES (?,?)', (abb, teamaverage))
avgweight()
def shootingefficiency():
    url= " http://stats.nba.com/js/data/sportvu/2015/shootingData.json?limit=20"
    request1 = requests.get(url)
    data1 = request1.text
    data1_dict =json.loads(data1) 
    x = 0
    holder = data1_dict['resultSets'][0]['rowSet']
    cur.execute('CREATE TABLE IF NOT EXISTS Shoot (tableindex INTEGER PRIMARY KEY, playerId INTEGER,Team STRING, EffFgPct INTEGER)')
    cur.execute('SELECT COUNT(*) FROM Shoot')
    currentrowcount = cur.fetchone()[0]
    targetrowcount = currentrowcount + 25
    x = currentrowcount
    rank = 1
    if currentrowcount <= 325:
        while x  < targetrowcount:
            cur.execute('INSERT OR IGNORE INTO Shoot (tableindex, playerId, Team, EffFgPct) VALUES(?,?,?,?)', (x, holder[x][0], holder[x][4], holder[x][20]))
            x = x + 1
    conn.commit()
shootingefficiency()

def catchAndShoot():
    url = "http://stats.nba.com/js/data/sportvu/2015/catchShootData.json?limit=20"
    request1 = requests.get(url)
    data1 = request1.text
    data1_dict =json.loads(data1) 
    holder = data1_dict['resultSets'][0]['rowSet']
    cur.execute('CREATE TABLE IF NOT EXISTS CandS (tableindex INTEGER PRIMARY KEY, playerId INTEGER,Team STRING, CandSPct INTEGER)')
    cur.execute('SELECT COUNT(*) FROM CandS')
    currentrowcount = cur.fetchone()[0]
    targetrowcount = currentrowcount + 25
    x = currentrowcount
    if currentrowcount <= 325:
        while x  < targetrowcount:
            cur.execute('INSERT OR IGNORE INTO CandS (tableindex, playerId, Team, CandSPct) VALUES(?,?,?,?)', (x, holder[x][0], holder[x][4], holder[x][10]))
            x = x + 1
    conn.commit()
catchAndShoot()

def joinAverageReupload():
    cur.execute('SELECT Shoot.Team, Shoot.EffFgPct, CandS.CandSPct FROM SHOOT JOIN CandS WHERE SHOOT.playerId = CandS.playerId')
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
    cur.execute('SELECT COUNT(*) FROM CandS')
    currentrowcount = cur.fetchone()[0]
    targetrowcount = currentrowcount + 25
    x = currentrowcount
    if currentrowcount == 350:
        cur.execute('CREATE TABLE IF NOT EXISTS Effavg (Team STRING PRIMARY KEY, AverageEffPct INTEGER)')
        for abb in countedteamabb:
            average = dict1[abb] / countedEentries[abb]
            cur.execute('INSERT OR IGNORE INTO Effavg (Team, AverageEffPct) VALUES (?,?)', (abb, average))

        cur.execute('CREATE TABLE IF NOT EXISTS CandSavg (Team STRING PRIMARY KEY, AverageCandSpct INTEGER)')

        for abb in countedteamabb:
            average = dict2[abb] / countedCentries[abb]
            cur.execute('INSERT OR IGNORE INTO CandSavg (Team, AverageCandSpct) VALUES (?,?)', (abb, average))
    conn.commit()



def graphandwriteheightandwinpercentage():
    cur.execute("SELECT avgHeightOfTeam.Team, avgHeightOfTeam.AvgHeight, TeamWinPct_15_16.WinPercentage  FROM avgHeightOfTeam, TeamWinPCt_15_16 WHERE avgHeightOfTeam.Team = TeamWinPct_15_16.Team")
    list1 = []
    for row in cur:
        list1.append(row)
    labels = []
    height = []
    winpct = []
    for val in list1:
        labels.append(val[0])
        height.append(val[1])
        winpct.append(val[2])
    
    #graphing
    plt.scatter(winpct, height)
    plt.ylabel('Average Height')
    plt.xlabel('Win Percentage')
    plt.title('Height per Win Percentage')
    plt.show()
    
    #writingtoCSV
    header = ['Team', 'Team Average Height', "Team Win Percentage"]
    writer.writerow(header)
    for row in list1:
        writer.writerow(row)
    writer.writerow(['End Study of Average Height'])


def graphandwriteweightandwinpercentage():
    cur.execute("SELECT avgWeightOfTeam.Team, avgWeightOfTeam.AvgWeight, TeamWinPct_15_16.WinPercentage  FROM avgWeightOfTeam, TeamWinPCt_15_16 WHERE avgWeightOfTeam.Team = TeamWinPct_15_16.Team")
    list1 = []
    for row in cur:
        list1.append(row)
    sortedlist1 = sorted(list1,key = lambda list1: list1[1], reverse = True)
    labels = []
    weight = []
    winpct = []
    for val in sortedlist1:
        labels.append(val[0])
        weight.append(val[1])
        winpct.append(val[2])


    #graphing
    plt.scatter(winpct, weight, color = 'red')
    plt.ylabel('Average weight')
    plt.xlabel('Win Percentage')
    plt.title('Weight per Win Percentage')
    plt.show()

    #writingtoCsv
    header = ['Team', 'Team Average Weight', "Team Win Percentage"]
    writer.writerow(header)
    for row in sortedlist1:
        writer.writerow(row)
    writer.writerow(['End Study of Average Weight'])

def graphandwriteCandSshootingpercentage():
    cur.execute("SELECT CandSavg.Team, CandSavg.AverageCandSpct, TeamWinPct_15_16.WinPercentage FROM CandSavg, TeamWinPct_15_16 WHERE CandSavg.Team = TeamWinPct_15_16.Team")
    list1 = []
    for row in cur:
        list1.append(row)
    labels = []
    effavgs = []
    winpct = []
    sortedlist1 = sorted(list1,key = lambda list1: list1[1], reverse = True)
    for val in sortedlist1:
        labels.append(val[0])
        effavgs.append(val[1])
        winpct.append(val[2])
    #graphing
    x = np.arange(len(labels))
    width = 0.5
    fig, ax = plt.subplots()
    bar1 = ax.bar(x - width/2, effavgs, width, label = 'Catch and Shoot Avg')
    bar2 = ax.bar(x + width/2, winpct, width, label = 'Win Percentage')
    ax.set_ylabel('Percentage')
    ax.set_title('Catch and Shoot Average and Win Percentage per Team')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    plt.show()
    #writingtoCsv
    header = ['Team', 'Team Average Catch and Shoot % ', "Team Win Percentage"]
    writer.writerow(header)
    for row in sortedlist1:
        writer.writerow(row)
    writer.writerow(['End Study of Catch and Shoot %'])

def graphandwriteefficientshootingpercentage():
    cur.execute("SELECT Effavg.Team, Effavg.AverageEffPct, TeamWinPct_15_16.WinPercentage FROM Effavg, TeamWinPct_15_16 WHERE Effavg.Team = TeamWinPct_15_16.Team")
    list1 = []
    for row in cur:
        list1.append(row)
    sortedlist1 = sorted(list1,key = lambda list1: list1[1], reverse = True)
    labels = []
    effavgs = []
    winpct = []
    for val in list1:
        labels.append(val[0])
        effavgs.append(val[1])
        winpct.append(val[2])
    x = np.arange(len(labels))
    width = 0.5
    fig, ax = plt.subplots()
    bar1 = ax.bar(x - width/2, effavgs, width, label = 'Efficient Shot Average')
    bar2 = ax.bar(x + width/2, winpct, width, label = 'Win Percentage')
    ax.set_ylabel('Percentage')
    ax.set_title('Efficient Shooting Average and Win Percentage per Team')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    plt.show()
    header = ['Team', 'Team Average Efficient Shot % ', "Team Win Percentage"]
    writer.writerow(header)
    for row in sortedlist1:
        writer.writerow(row)
    writer.writerow(['End Study of Efficient Shot %'])




cur.execute('SELECT COUNT(*) FROM playerPhysicals')
currentrowcount = cur.fetchone()[0]        
if currentrowcount >= 450:
    graphandwriteheightandwinpercentage()
    graphandwriteweightandwinpercentage()
    graphandwriteCandSshootingpercentage()
    graphandwriteefficientshootingpercentage()


joinAverageReupload()
f.close()
