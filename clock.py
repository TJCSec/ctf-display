from tkinter import *
from datetime import datetime

bgc = '#008aff'
begin = datetime(2016,3,13,0,31)
end = datetime(2016,3,16,1,30)

def update_text():
    delta = begin - datetime.now()
    if delta.days < 0:
        delta = end - datetime.now()

    if delta.seconds > 60:
        s = '%02d:%02d:%02d' % ((delta.days*24 + delta.seconds//3600), (delta.seconds//60)%60, delta.seconds%60)
    else:
        s = '%d seconds' % delta.seconds
    txt.set(s)
    root.after(500, update_text)

root = Tk()
root.resizable(width=FALSE, height=FALSE)
root.title('Countdown Timer')
root.configure(background=bgc)
root.geometry('1920x400')
txt = StringVar()
w = Label(root, bg=bgc, textvariable=txt, font=("Roboto", 240), fg='white')
w.pack()
update_text()
root.mainloop()
