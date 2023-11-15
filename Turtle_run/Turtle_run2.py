# Turtle run
# by ToushifA_1611
# create player and motion

import turtle

speed = 1

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


s.mainloop()