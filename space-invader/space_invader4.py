# Space Invader
# by ToushfA_1611
# create the enemy and move left/right/down

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

#enemy
enemy = turtle.Turtle()
enemy.color("red")
enemy.shape("circle")
enemy.penup()
enemy.speed(0)
enemy.setposition(-200, 250)

enemyspeed = 2

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

#keyboard binding
s.listen()
s.onkeypress(move_left,"Left")
s.onkeypress(move_right,"Right")

#main game loop
while True:
    
    #move the enemy
    x = enemy.xcor()
    x += enemyspeed
    enemy.setx(x)
    
    #move the enemy back and down
    if enemy.xcor() > 280:
        y = enemy.ycor()
        y -=40
        enemyspeed *= -1
        enemy.sety(y)
    
    if enemy.xcor() < -280:
        y = enemy.ycor()
        y -=40
        enemyspeed *= -1
        enemy.sety(y)


s.mainloop()