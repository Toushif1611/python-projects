# Traffic light
# by toushifA
# set screen and boarder

import turtle
import time

#set screen
s=turtle.Screen()
s.bgcolor("black")
s.title("traffic-light")
s.setup(width=300, height=300)

#boarder
boarder_pen=turtle.Turtle()
boarder_pen.color("brown")
boarder_pen.speed(0)
boarder_pen.penup()
boarder_pen.goto(-20, -50)
boarder_pen.pendown()
boarder_pen.pensize(3)
boarder_pen.hideturtle()
for i in range(4):
    boarder_pen.forward(40)
    boarder_pen.left(90)
    boarder_pen.forward(100)
    boarder_pen.left(90)


s.mainloop()