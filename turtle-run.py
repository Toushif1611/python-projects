#Turtle run
#by toushifA

import turtle
import math
import random
 
speed=1
score=0

#set screen
s=turtle.Screen()
s.bgcolor("black")
s.title("TURTLE-RUN")
s.tracer(0)

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
pen1.write("score: 0 ", align="left", font=("courier", 24, "normal"))

#boarder
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
    
#key binding
s.listen()
s.onkeypress(turnleft,"Left")
s.onkeypress(turnright,"Right")
s.onkeypress(increasespeed,"Up")
s.onkeypress(decreasespeed,"Down")  

#mainloop
while True:
    s.update()
    
    #player move
    player.forward(speed)

    #boarder collision with player 
    if player.xcor()> 300 or player.xcor()< -300:
        player.right(100)
    if player.ycor()> 300 or player.ycor()< -300:
        player.right(100)

    #collision checking
    if isCollision(player, food):
        food.setposition(random.randint(-290, 290), random.randint(-290, 290))
        score += 1
        pen1.clear()
        pen1.write("score: {}".format(score), align="left", font=("courier", 24, "normal"))


s.mainloop()