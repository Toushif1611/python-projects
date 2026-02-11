# Turtle run
# by Toushif_1611
# create screen and boarder

import turtle
 
#set screen
s = turtle.Screen()
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


s.mainloop()