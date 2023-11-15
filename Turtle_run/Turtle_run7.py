# Turtle run
# by ToushifA_1611
# create levels

import turtle
import math
import random
 
speed = 1
score = 0
level = 1

#set screen
s=turtle.Screen()
s.bgcolor("black")
s.title("TURTLE-RUN")
s.tracer(0)

#boarder
boarder_pen = turtle.Turtle()
boarder_pen.color("white")
boarder_pen.pensize(3)
boarder_pen.penup()
boarder_pen.setposition(-300,-300)
boarder_pen.pendown()
for i in range(4):
    boarder_pen.forward(600)
    boarder_pen.left(90)
boarder_pen.hideturtle()

#player
player=turtle.Turtle()
player.shape("turtle")
player.color("green")
player.speed(0)
player.penup()

#food
food=turtle.Turtle()
food.shape("circle")
food.color("red")
food.speed(0)
food.penup()
food.setposition(random.randint(-290, 290), random.randint(-290, 290))

#score
pen1=turtle.Turtle()
pen1.color("white")
pen1.speed(0)
pen1.penup()
pen1.hideturtle()
pen1.goto(-290, 310)
pen1.write("score: 0 level: 1", align="left", font=("courier", 24, "normal"))

#function
def turnleft():
    player.left(30)

def turnright():
    player.right(30)

def increasespeed():
    global speed
    speed+=1

def decreasespeed():
    global speed
    speed-=1

def isCollision(t1, t2):
    d = math.sqrt(math.pow(t1.xcor()-t2.xcor(),2) + math.pow(t1.ycor()-t2.ycor(),2))
    if d <20:
        return True
    else:
        return False
    
#keyboard binding
s.listen()
s.onkeypress(turnleft,"Left")
s.onkeypress(turnright,"Right")
s.onkeypress(increasespeed,"Up")
s.onkeypress(decreasespeed,"Down")  

#main game loop
while True:
    s.update()
    
    #player move
    player.forward(speed)

    #check boarder collision
    if player.xcor()> 300 or player.xcor()< -300:
        player.right(100)
    if player.ycor()> 300 or player.ycor()< -300:
        player.right(100)

    #collision checking
    if isCollision(player, food):
        food.setposition(random.randint(-290, 290), random.randint(-290, 290))
        score += 1
        pen1.clear()
        pen1.write("score: {} level: {}".format(score, level), align="left", font=("courier", 24, "normal"))

    #create levels
    if score >= 9 and score <  19:
        level = 2
        food.forward(1)
        if food.xcor()> 290 or food.xcor()< -290:
            food.right(100)
        if food.ycor()> 290 or food.ycor()< -290:
            food.right(100)
    
    if score >= 19 and score <  29:
        level = 3
        food.forward(2)
        if food.xcor()> 290 or food.xcor()< -290:
            food.right(100)
        if food.ycor()> 290 or food.ycor()< -290:
            food.right(100)

    if score >= 29 and score <  39:
        level = 4
        food.forward(3)
        if food.xcor()> 290 or food.xcor()< -290:
            food.right(100)
        if food.ycor()> 290 or food.ycor()< -290:
            food.right(100)

    if score >= 39 and score <  50:
        level = 5
        food.forward(4)
        if food.xcor()> 290 or food.xcor()< -290:
            food.right(100)
        if food.ycor()> 290 or food.ycor()< -290:
            food.right(100)

    #set wining screen
    if score == 50:
        pen1.goto(0,0)
        pen1.write(" YOU WIN ", align="center", font=("courier", 50, "normal"))
        break



s.mainloop()