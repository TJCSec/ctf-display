from tkinter import *
from datetime import datetime, timedelta
import time
from peewee import *
from database import *

bgc = '#008aff'
solves = {}
unsolved_challenges = []

root = Tk()
offscreen_dest = 900
final_delta = 5
last_solve = -1
solve_id = 0
previous_time = datetime.now()
root.resizable(width=FALSE, height=FALSE)
root.title('TJCTF Solves')
root.configure(background=bgc)
root.geometry('1000x700')
c = Canvas(root, height='700', width='1000', bg=bgc)
c.pack()


def animate():
    global solves
    for s in solves:
        sobj = solves[s]
        if (abs(sobj['dest'] - sobj['y']) < final_delta) and sobj['active']:
            continue
        if abs(offscreen_dest - sobj['y']) < final_delta:
            del solves[s]
            continue
        if sobj['active']:
            d = sobj['dest']
            delta = (d - sobj['y'])/15
        else:
            d = offscreen_dest
            delta = abs(d - sobj['y'] - 20)/15

        sobj['y'] += delta
        c.move(sobj['element'], 0, delta)
        if sobj['box']:
            c.move(sobj['box'], 0, delta)

    root.after(25, animate)

def update_solves():
    global solves, solve_id, previous_time, unsolved_challenges
    index = 0
    for item in solves:
        if solves[item]['firstblood']:
            if solves[item]['periods'] >= 6:
                solves[item]['active'] = False
            else:
                solves[item]['dest'] = (50 + 65*index)
                index += 1
        else:
            solves[item]['active'] = False

        solves[item]['periods'] += 1

    now = datetime.now() - timedelta(seconds=1)
    query = ChallengeSolve.select().where((ChallengeSolve.time > previous_time) & (ChallengeSolve.time < now))
    previous_time = now
    for result in query:
        donotshow = False
        if index == 10:
            donotshow = True
        team_name = result.team.name
        if len(team_name) > 35:
            team_name = team_name[:35] + '...'

        solved_string = "%s by %s" % (result.challenge.name, team_name)
        first_blood = False
        print(result.challenge.id)
        print(unsolved_challenges)
        if result.challenge.id in unsolved_challenges:
            # Make sure they were actually first to solve
            other_solves = result.challenge.solves
            if all([result.time <= s.time for s in other_solves]):
                first_blood = True

        element = c.create_text(500, -200, text=solved_string, font=('Roboto', 35), fill='white')
        dest = -200 if donotshow else (50 + 65*index)

        solves[solve_id] = {'element': element, 'active': True, 'solved_string': solved_string, 'y': -200, 'periods': 0, 'firstblood': first_blood, 'dest': (50 + 65*index), 'box': None}
        if first_blood:
            box = c.create_rectangle(c.bbox(element), fill='#4CAF50')
            c.tag_lower(box, element)
            solves[solve_id]['box'] = box

        solve_id += 1
        index += 1
    
    unsolved_challenges = [res.id for res in Challenge.select().where(~(Challenge.id << ChallengeSolve.select(ChallengeSolve.challenge).where(ChallengeSolve.time < now))).execute()]
    print(unsolved_challenges)
    root.after(5000, update_solves)

update_solves()
animate()
root.mainloop()
