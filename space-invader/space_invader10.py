# Space Invader
# by ToushfA_1611
# multiple invader in multiple row

import turtle
import math 

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

#set the score 
score = 0

#draw the score
pen1=turtle.Turtle()
pen1.color("white")
pen1.speed(0)
pen1.penup()
pen1.hideturtle()
pen1.goto(-290, 280)
pen1.write("score: 0", align="left", font=("Arial", 14, "normal"))

#player
player = turtle.Turtle()
player.shape("triangle")
player.color("blue")
player.penup()
player.speed(0)
player.setposition(0,-250)
player.setheading(90)

playerspeed =15

enemyspeed = 2

#choose a number of enemy
number_of_enemies = 30
#
enemies = []

#add enemies to the list 
for i in range(number_of_enemies):
    enemies.append(turtle.Turtle())

enemy_start_x = -225
enemy_start_y = 250
enemy_number = 0

for enemy in enemies:
    enemy.color("red")
    enemy.shape("circle")
    enemy.penup()
    enemy.speed(0)
    x = enemy_start_x + (50 * enemy_number)
    y = enemy_start_y
    enemy.setposition(x, y)
    #
    enemy_number +=1
    if enemy_number == 10:
        enemy_start_y -=50
        enemy_number = 0


enemyspeed = 2


#create the player's bullet
bullet = turtle.Turtle()
bullet.color("yellow")
bullet.shape("triangle")
bullet.penup()
bullet.speed(0)
bullet.setheading(90)
bullet.shapesize(0.5, 0.5)
bullet.hideturtle()

bulletspeed = 20

#define bullet state
#ready - ready to fire
#fire - bullet is firing
bulletstate = "ready"

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

def fire_bullet():
    #declare bulletstate as a global if it needs changed
    global bulletstate
    if bulletstate == "ready":
        bulletstate = "fire"
        #move the bullet to the just above the player
        x = player.xcor()
        y = player.ycor() + 10
        bullet.setposition(x, y)
        bullet.showturtle()

def isCollision(t1, t2):
    d = math.sqrt(math.pow(t1.xcor()-t2.xcor(),2) + math.pow(t1.ycor()-t2.ycor(),2))
    if d <20:
        return True
    else:
        return False

#keyboard binding
s.listen()
s.onkeypress(move_left,"Left")
s.onkeypress(move_right,"Right")
s.onkeypress(fire_bullet,"space")

#main game loop
while True:

    for enemy in enemies: 
        #move the enemy
        x = enemy.xcor()
        x += enemyspeed
        enemy.setx(x)
        
        #move the enemy back and down
        if enemy.xcor() > 280:
            #move all enemies down
            for e in enemies:  
                y = e.ycor()
                y -=40
                e.sety(y) 
            #change enemy direction
            enemyspeed *= -1
        
        if enemy.xcor() < -280:
            #move all enemies down
            for e in enemies:
                y = e.ycor()
                y -=40
                e.sety(y)
            #change enemy direction
            enemyspeed *= -1
   
        #check for a collision
        if isCollision(bullet, enemy):
            #reset the bullet
            bullet.hideturtle()
            bulletstate = "ready"  
            bullet.setposition(0, -400)
            #reset the enemy
            enemy.setposition(0, 10000)
            #update the score
            score += 10
            pen1.clear()
            pen1.write("score: {}".format(score), align="left", font=("Arial", 14, "normal"))


        if isCollision(player, enemy):
            player.hideturtle()
            enemy.hideturtle()
            print ("game over")
            break

    #move the bullet 
    y =bullet.ycor()
    y += bulletspeed
    bullet.sety(y)

    #check to see if the bullet has gone to the top
    if bullet.ycor() > 275:
        bullet.hideturtle()
        bulletstate = "ready"



s.mainloop()