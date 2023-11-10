import turtle
 
speed=1

s=turtle.Screen()
s.bgcolor("black")
s.title("TURTLE-RUN")

a=turtle.Turtle()
a.shape("turtle")
a.color("green")
a.speed(0)
a.penup()

b=turtle.Turtle()
b.shape("circle")
b.color("red")
b.speed(0)
b.penup()

pen=turtle.Turtle()
pen.color("yellow")
pen.pensize(5)
pen.penup()
pen.goto(-300,-300)
pen.pendown()
for i in range(4):
    pen.forward(600)
    pen.left(90)
    pen.hideturtle()


def turnleft():
    a.left(30)

def turnright():
    a.right(30)

s.listen()
s.onkeypress(turnleft,"Left")
s.onkeypress(turnright,"Right")   


while True:
    a.forward(speed)
    b.forward(3)
    if a.xcor()> 300 or a.xcor()< -300:
        a.right(100)
    if a.ycor()> 300 or a.ycor()< -300:
        a.right(100)
    if b.xcor()> 290 or b.xcor()< -290:
        b.right(100)
    if b.ycor()> 290 or b.ycor()< -290:
        b.right(100)

s.mainloop()