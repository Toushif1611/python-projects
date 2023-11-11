#Turtle run
#by toushifA

import turtle
 
speed=1

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

    #food move
    food.forward(3)

    #boarder collision with player 
    if player.xcor()> 300 or player.xcor()< -300:
        player.right(100)
    if player.ycor()> 300 or player.ycor()< -300:
        player.right(100)

    #boarder collision with player  
    if food.xcor()> 290 or food.xcor()< -290:
        food.right(100)
    if food.ycor()> 290 or food.ycor()< -290:
        food.right(100)

s.mainloop()