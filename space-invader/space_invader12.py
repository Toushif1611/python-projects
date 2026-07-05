# Space Invader
# by Toushif1611
# Add level system and restart button

import turtle
import math

# -----------------------
# Screen Setup
# -----------------------
screen = turtle.Screen()
screen.bgcolor("black")
screen.title("Space Invader")
screen.setup(700, 700)
screen.tracer(0)

# -----------------------
# Border
# -----------------------
border = turtle.Turtle()
border.hideturtle()
border.color("white")
border.pensize(3)
border.penup()
border.goto(-300, -300)
border.pendown()
for _ in range(4):
    border.forward(600)
    border.left(90)

# -----------------------
# Score
# -----------------------
score = 0

score_pen = turtle.Turtle()
score_pen.hideturtle()
score_pen.color("white")
score_pen.penup()
score_pen.goto(-290, 280)

def update_score():
    score_pen.clear()
    score_pen.write(f"Score: {score}", font=("Arial", 14, "normal"))

update_score()

# -----------------------
# Player
# -----------------------
player = turtle.Turtle()
player.shape("triangle")
player.color("blue")
player.penup()
player.setheading(90)
player.goto(0, -250)

player_speed = 20

# flags for smooth movement
move_left_pressed = False
move_right_pressed = False

def move_left():
    x = player.xcor() - player_speed
    if x < -280:
        x = -280
    player.setx(x)

def move_right():
    x = player.xcor() + player_speed
    if x > 280:
        x = 280
    player.setx(x)

# handlers for key press/release

def start_move_left():
    global move_left_pressed
    move_left_pressed = True


def stop_move_left():
    global move_left_pressed
    move_left_pressed = False


def start_move_right():
    global move_right_pressed
    move_right_pressed = True


def stop_move_right():
    global move_right_pressed
    move_right_pressed = False


# -----------------------
# Enemies
# -----------------------
number_of_enemies = 30
enemies = []

start_x = -225
start_y = 250
count = 0

# -----------------------
# Level System
# -----------------------
level = 1

level_pen = turtle.Turtle()
level_pen.hideturtle()
level_pen.color("white")
level_pen.penup()
level_pen.goto(200, 280)

def update_level():
    level_pen.clear()
    level_pen.write(f"Level: {level}", font=("Arial", 14, "normal"))

update_level()

# -----------------------
# Reset Enemies Function
# -----------------------
def reset_enemies():
    global enemies, enemy_speed
    
    start_x = -225
    start_y = 250
    count = 0

    for enemy in enemies:
        x = start_x + (50 * count)
        y = start_y
        enemy.goto(x, y)

        count += 1
        if count == 10:
            count = 0
            start_y -= 50

    enemy_speed = 2 + level   # increase difficulty

# -----------------------
# Create Enemies
# -----------------------
enemy_speed = 3

for i in range(number_of_enemies):
    enemy = turtle.Turtle()
    enemy.shape("circle")
    enemy.color("red")
    enemy.penup()
    enemy.speed(0)
    enemies.append(enemy)

# Position them for first level
reset_enemies()

# -----------------------
# (single bullet object removed since we now use multiple bullets)
# -----------------------

# -----------------------
# Multiple Bullets System
# -----------------------
bullets = []
bullet_speed = 20

def fire_bullet():
    bullet = turtle.Turtle()
    bullet.shape("triangle")
    bullet.color("yellow")
    bullet.penup()
    bullet.setheading(90)
    bullet.shapesize(0.5, 0.5)
    bullet.goto(player.xcor(), player.ycor() + 10)
    bullets.append(bullet)

# -----------------------
# Collision Function
# -----------------------
def is_collision(t1, t2):
    distance = math.hypot(t1.xcor() - t2.xcor(),
                          t1.ycor() - t2.ycor())
    return distance < 20

# -----------------------
# Start Screen / Game Over
# -----------------------
game_over = False
game_started = False
game_running = False

game_over_pen = turtle.Turtle()
game_over_pen.hideturtle()
game_over_pen.color("white")
game_over_pen.penup()

title_pen = turtle.Turtle()
title_pen.hideturtle()
title_pen.color("white")
title_pen.penup()

controls_pen = turtle.Turtle()
controls_pen.hideturtle()
controls_pen.color("white")
controls_pen.penup()

restart_button = turtle.Turtle()
quit_button = turtle.Turtle()
home_button = turtle.Turtle()
start_button = turtle.Turtle()
restart_button.hideturtle()
quit_button.hideturtle()
home_button.hideturtle()
start_button.hideturtle()


def draw_button(button_turtle, x, y, width, height, text, fill_color):
    button_turtle.clear()
    button_turtle.penup()
    button_turtle.goto(x - width / 2, y - height / 2)
    button_turtle.color("white", fill_color)
    button_turtle.begin_fill()
    button_turtle.pendown()
    for _ in range(2):
        button_turtle.forward(width)
        button_turtle.left(90)
        button_turtle.forward(height)
        button_turtle.left(90)
    button_turtle.end_fill()
    button_turtle.penup()
    button_turtle.goto(x, y - 8)
    button_turtle.color("white")
    button_turtle.write(text, align="center", font=("Arial", 12, "bold"))
    screen.update()


def show_start_screen():
    title_pen.clear()
    controls_pen.clear()
    start_button.clear()

    title_pen.penup()
    title_pen.goto(0, 90)
    title_pen.write("SPACE INVADER",
                    align="center",
                    font=("Arial", 28, "bold"))

    controls_pen.penup()
    controls_pen.goto(0, -90)
    controls_pen.write("Controls:\nLeft / Right Arrow - Move\nSpace - Shoot",
                       align="center",
                       font=("Arial", 14, "normal"))

    draw_button(start_button, 0, 30, 140, 45, "Play", "blue")
    screen.update()


def hide_start_screen():
    title_pen.clear()
    controls_pen.clear()
    start_button.clear()
    start_button.hideturtle()


def show_game_over():
    game_over_pen.clear()
    game_over_pen.goto(0, 50)
    game_over_pen.write("GAME OVER",
                        align="center",
                        font=("Arial", 24, "bold"))
    draw_button(restart_button, 10, 0, 120, 30, "Restart", "green")
    draw_button(home_button, 10, -50, 120, 30, "Home", "orange")
    draw_button(quit_button, 10, -100, 120, 30, "Quit", "red")


def hide_game_over_buttons():
    restart_button.clear()
    quit_button.clear()
    home_button.clear()
    restart_button.hideturtle()
    quit_button.hideturtle()
    home_button.hideturtle()


def is_button_clicked(x, y, button_x, button_y, width, height):
    return (button_x - width / 2 <= x <= button_x + width / 2 and
            button_y - height / 2 <= y <= button_y + height / 2)


def reset_game_state():
    global enemies, bullets, score, level, game_over, enemy_speed
    global move_left_pressed, move_right_pressed, game_started, game_running

    for bullet in bullets[:]:
        bullet.hideturtle()
    bullets.clear()

    for enemy in enemies:
        enemy.hideturtle()
        enemy.goto(0, 10000)
    enemies.clear()

    for i in range(number_of_enemies):
        enemy = turtle.Turtle()
        enemy.shape("circle")
        enemy.color("red")
        enemy.penup()
        enemy.speed(0)
        enemies.append(enemy)

    score = 0
    level = 1
    update_score()
    update_level()

    enemy_speed = 3
    move_left_pressed = False
    move_right_pressed = False

    player.showturtle()
    player.goto(0, -250)

    reset_enemies()

    for enemy in enemies:
        enemy.showturtle()

    game_over = False
    game_started = True
    game_running = True
    screen.update()


def start_game():
    hide_start_screen()
    reset_game_state()
    game_loop()


def handle_click(x, y):
    global game_over, game_started, game_running

    if not game_started and not game_over:
        if is_button_clicked(x, y, 0, 30, 140, 45):
            start_game()
        return

    if not game_over:
        return

    if is_button_clicked(x, y, 0, 0, 120, 30):
        restart_game()
    elif is_button_clicked(x, y, 0, -50, 120, 30):
        go_home()
    elif is_button_clicked(x, y, 0, -100, 120, 30):
        turtle.bye()


def go_home():
    global game_over, game_started, game_running, enemies, bullets, score, level, enemy_speed
    global move_left_pressed, move_right_pressed

    hide_game_over_buttons()
    game_over_pen.clear()

    for bullet in bullets[:]:
        bullet.hideturtle()
    bullets.clear()

    for enemy in enemies:
        enemy.hideturtle()
        enemy.goto(0, 10000)
    enemies.clear()

    score = 0
    level = 1
    update_score()
    update_level()

    enemy_speed = 3
    move_left_pressed = False
    move_right_pressed = False

    player.showturtle()
    player.goto(0, -250)
    game_over = False
    game_started = False
    game_running = False
    screen.update()
    show_start_screen()


def restart_game():
    hide_game_over_buttons()
    game_over_pen.clear()
    reset_game_state()
    game_loop()

# -----------------------
# Keyboard Bindings (smooth movement)
# -----------------------
screen.listen()
# pressing sets flag, releasing clears it
screen.onkeypress(start_move_left, "Left")
screen.onkeyrelease(stop_move_left, "Left")
screen.onkeypress(start_move_right, "Right")
screen.onkeyrelease(stop_move_right, "Right")
screen.onkeypress(fire_bullet, "space")
screen.onclick(handle_click)

# -----------------------
# Main Game Loop (Smooth)
# -----------------------
def game_loop():
    # bullet_state not used anymore
    global enemy_speed, score, game_over, level, game_running

    if not game_running or not game_started or game_over:
        return

    move_down = False

    # Move player smoothly based on key state
    if move_left_pressed:
        move_left()
    if move_right_pressed:
        move_right()

    # Move enemies
    for enemy in enemies:
        enemy.setx(enemy.xcor() + enemy_speed)

        if enemy.xcor() > 280 or enemy.xcor() < -280:
            move_down = True

    if move_down:
        enemy_speed *= -1
        for enemy in enemies:
            enemy.sety(enemy.ycor() - 40)

    # -----------------------
    # Move Bullets
    # -----------------------
    for bullet in bullets[:]:
        bullet.sety(bullet.ycor() + bullet_speed)

        if bullet.ycor() > 275:
            bullet.hideturtle()
            bullets.remove(bullet)

    # -----------------------
    # Collision Check
    # -----------------------
    alive_enemies = 0

    for enemy in enemies:

        if enemy.ycor() < -240:
            player.hideturtle()
            show_game_over()
            game_over = True
            return

        # Bullet hit
        for bullet in bullets[:]:
            if is_collision(bullet, enemy):

                bullet.hideturtle()
                bullets.remove(bullet)

                enemy.hideturtle()
                enemy.goto(0, 10000)

                score += 10
                update_score()
                break

        if enemy.ycor() < 1000:
            alive_enemies += 1

        if is_collision(player, enemy):
            player.hideturtle()
            show_game_over()
            game_over = True
            return

    # LEVEL COMPLETE
    if alive_enemies == 0:
        level += 1
        update_level()
        reset_enemies()
        # make sure all enemies are visible again
        for e in enemies:
            e.showturtle()

    screen.update()
    if game_running and game_started and not game_over:
        screen.ontimer(game_loop, 16)

# Show start screen first
show_start_screen()
screen.mainloop()