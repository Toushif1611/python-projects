# Space Invader
# by ToushfA_1611
#set screen and boarder

import turtle

#set screen
s = turtle.Screen()
s.bgcolor("black")
s.title("Space Invader")

#boarder
boarder_pen = turtle.Turtle()
boarder_pen.color("white")
boarder_pen.penup()
boarder_pen.goto(-300,-300)
boarder_pen.pendown()
for i in range(4):
    boarder_pen.fd(600)
    boarder_pen.lt(90)
boarder_pen.hideturtle()




s.mainloop()