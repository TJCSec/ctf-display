from tkinter import *
from datetime import datetime, timedelta
import time
from peewee import *
from database import *
import redis
import json
from config import redis_host

bgc = '#008aff'
teams = {}

r = redis.StrictRedis(host=redis_host)
root = Tk()
offscreen_dest = 1000
final_delta = 1
root.resizable(width=FALSE, height=FALSE)
root.title('TJCTF Scoreboard')
root.configure(background=bgc)
root.geometry('920x800')
c = Canvas(root, height='800', width='920', bg=bgc)
c.pack()


def animate():
    global teams
    for s in teams:
        sobj = teams[s]
        if (abs(sobj['dest'] - sobj['y']) < final_delta) and sobj['active']:
            continue
        if abs(offscreen_dest - sobj['y']) < final_delta:
            del teams[s]
            continue
        if sobj['active']:
            d = sobj['dest']
            delta = (d - sobj['y'])/15
        else:
            d = offscreen_dest
            delta = abs(d - sobj['y'] - 20)/15

        sobj['y'] += delta
        c.move(sobj['element'], 0, delta)

    root.after(25, animate)

def calculate_scores():
    solves = ChallengeSolve.select(ChallengeSolve, Challenge).join(Challenge)
    adjustments = ScoreAdjustment.select()
    teams = Team.select()

    team_solves = {team.id: [] for team in teams}
    team_mapping = {team.id: team for team in teams}
    scores = {team.id: 0 for team in teams}
    for solve in solves:
        scores[solve.team_id] += solve.challenge.points
        team_solves[solve.team_id].append(solve)
    for adjustment in adjustments:
        scores[adjustment.team_id] += adjustment.value

    most_recent_solve = {tid: max([i.time for i in team_solves[tid]]) for tid in team_solves if team_solves[tid]}
    scores = {i: j for i, j in scores.items() if i in most_recent_solve}
    return [(team_mapping[i[0]].eligible, i[0], team_mapping[i[0]].name, team_mapping[i[0]].affiliation, i[1]) for idx, i in enumerate(sorted(scores.items(), key=lambda k: (-k[1], most_recent_solve[k[0]])))]

def update_teams():
    global teams
    index = 0

    i = r.get('scoreboard')
    if i is not None:
        tresults = json.loads(i.decode())
    else:
        tresults = calculate_scores()

    newteams = {}
    tids = []
    for rank,team in enumerate(tresults[:10]):
        tids.append(team[1])
        text = '%02s. %s (%s)' % (rank+1, team[2], team[3])
        if len(text) > 35:
            text = text[:35] + '...'
        existing = False
        for t in teams:
            if teams[t]['tid'] == team[1]:
                c.itemconfig(teams[t]['element'], text=text)
                teams[t]['dest'] = (50 + rank*65)
                newteams[rank] = teams[t]
                existing = True

        if not existing:
            element = c.create_text(10, -200, text=text, font=('Roboto', 35), fill='white', anchor=W)
            newteams[rank+1] = {'tid': team[1], 'element': element, 'active': True, 'y': -200, 'dest': (50 + rank*65)}

    for team in teams:
        if teams[team]['tid'] not in tids:
            teams[team]['active'] = False
            newteams[50 + teams[team]['tid']] = teams[team]

    teams = newteams

    root.after(5000, update_teams)

update_teams()
animate()
root.mainloop()
