# Space Invader
# by ToushfA_1611
#add player

import turtle

#set screen
s = turtle.Screen()
s.bgcolor("black")
s.title("Space Invader")

#boarder
boarder_pen = turtle.Turtle()
boarder_pen.color("white")
boarder_pen.speed(0)
boarder_pen.penup()
boarder_pen.setposition(-300,-300)
boarder_pen.pendown()
boarder_pen.pensize(3)
for i in range(4):
    boarder_pen.fd(600)
    boarder_pen.lt(90)
boarder_pen.hideturtle()

#player
player = turtle.Turtle()
player.shape("triangle")
player.color("blue")
player.penup()
player.speed(0)
player.setposition(0,-250)
player.setheading(90)

playerspeed =15

#function
def move_left():
    x = player.xcor()
    x -= playerspeed
    if  x < -280:
        x = -280
    player.setx(x)

def move_right():
    x = player.xcor()
    x += playerspeed
    if  x > 280:
        x = 280
    player.setx(x)


s.listen()
s.onkeypress(move_left,"Left")
s.onkeypress(move_right,"Right")

s.mainloop()