# Traffic light
# by toushifA
# create lights 

import turtle
import time

#set screen
s=turtle.Screen()
s.bgcolor("black")
s.title("traffic-light")
s.setup(width=600, height=600)

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

#Red lights
red=turtle.Turtle()
red.shape("circle")
red.color("grey")
red.speed(0)
red.penup()
red.goto(0,30)

#yellow lights
yellow=turtle.Turtle()
yellow.shape("circle")
yellow.color("grey")
yellow.speed(0)
yellow.penup()
yellow.goto(0,0)

#green lights
green=turtle.Turtle()
green.shape("circle")
green.color("grey")
green.speed(0)
green.penup()
green.goto(0,-30)



s.mainloop()