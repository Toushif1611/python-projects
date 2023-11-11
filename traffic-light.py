import turtle
import time

s=turtle.Screen()
s.bgcolor("black")
s.title("traffic-light")
s.setup(width=300, height=300)

a=turtle.Turtle()
a.shape("circle")
a.color("grey")
a.speed(0)
a.penup()
a.goto(0,30)

b=turtle.Turtle()
b.shape("circle")
b.color("grey")
b.speed(0)
b.penup()
b.goto(0,0)

c=turtle.Turtle()
c.shape("circle")
c.color("grey")
c.speed(0)
c.penup()
c.goto(0,-30)

pen=turtle.Turtle()
pen.color("brown")
pen.speed(0)
pen.penup()
pen.goto(-20, -50)
pen.pendown()
pen.pensize(3)
pen.hideturtle()
pen.forward(40)
pen.left(90)
pen.forward(100)
pen.left(90)
pen.forward(40)
pen.left(90)
pen.forward(100)

def a_animate():
    a.color("red")
    time.sleep(2)
    a.color("grey")

    b.color("yellow")
    time.sleep(0.9)
    b.color("grey")

    c.color("green")
    time.sleep(2)
    c.color("grey")

while True:
    a_animate()

s.mainloop()