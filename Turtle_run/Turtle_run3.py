# Turtle run
# by ToushifA_1611
# create food and check boarder collision

import turtle
import math
import random
 
speed=1

#set screen
s=turtle.Screen()
s.bgcolor("black")
s.title("TURTLE-RUN")

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
    
#keyboard binding
s.listen()
s.onkeypress(turnleft,"Left")
s.onkeypress(turnright,"Right")
s.onkeypress(increasespeed,"Up")
s.onkeypress(decreasespeed,"Down")  

#main game loop
while True:
    
    #player move
    player.forward(speed)

    #check boarder collision
    if player.xcor()> 300 or player.xcor()< -300:
        player.right(100)
    if player.ycor()> 300 or player.ycor()< -300:
        player.right(100)


s.mainloop()