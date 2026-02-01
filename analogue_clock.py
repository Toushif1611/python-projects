import turtle
import time

s=turtle.Screen()
s.bgcolor("black")
s.setup(width=600, height=600)
s.title("simple Analog clock")

a=turtle.Turtle()
a.hideturtle()
a.speed(0)
a.pensize(3)

def draw_clock(h, m, s, a):
    a.up()
    a.goto(0, 210)
    a.setheading(180)
    a.color("green")
    a.pendown()
    a.circle(210)
    a.penup()
    a.goto(0, 0)
    a.setheading(90)
    for _ in range(12):
        a.fd(190)
        a.pendown()
        a.fd(20)
        a.penup()
        a.goto(0, 0)
        a.rt(30) 
    a.penup()
    a.goto(0,0)
    a.color("white")
    a.setheading(90)
    angle = (h / 12) * 360
    a.rt(angle)
    a.pendown()
    a.fd(100)
    a.penup()
    a.goto(0,0)
    a.color("blue")
    a.setheading(90)
    angle = (m / 60) * 360
    a.rt(angle)
    a.pendown()
    a.fd(180)
    a.penup()
    a.goto(0,0)
    a.color("gold")
    a.setheading(90)
    angle = (s / 60) * 360
    a.rt(angle)
    a.pendown()
    a.fd(50)


while True:
    h = int(time.strftime("%I"))
    m = int(time.strftime("%M"))
    s = int(time.strftime("%S"))
    draw_clock(h, m, s, a)
    time.sleep(1)
    a.clear()


s.mainloop()