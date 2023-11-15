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
pen=turtle.Turtle()
pen.color("brown")
pen.speed(0)
pen.penup()
pen.goto(-20, -50)
pen.pendown()
pen.pensize(3)
pen.hideturtle()
for i in range(4):
    pen.forward(40)
    pen.left(90)
    pen.forward(100)
    pen.left(90)
    
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



#function
def a_animate():

    red.color("red")
    time.sleep(2)
    red.color("grey")

    yellow.color("yellow")
    time.sleep(0.9)
    yellow.color("grey")

    green.color("green")
    time.sleep(2)
    green.color("grey")

#mainloop
while True:
    a_animate()

s.mainloop()