#pygame initialization
import pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("My Game")

#Stats
x = 50
y = 325
width = 64
height = 64
vel = 10
is_jump = False
jump_count = 10
left = False
right = False
walk_count = 0

def redraw_game_window():
    global walk_count
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height))
    pygame.display.update()

# Main game loop
running = True
while running:
    # This will slow down the loop to make the movement smoother
    pygame.time.delay(100)

    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and x > vel:
        x -= vel
        left = True
        right = False
    else:
        left = False
    if keys[pygame.K_RIGHT] and x < 500 - width - vel:
        x += vel
    #jumping
    if not(is_jump): #if the character is not currently jumping, allow the player to initiate a jump
        if keys[pygame.K_SPACE]:
            is_jump = True
    else: #if the character is currently jumping, we need to handle the jump mechanics
        if jump_count >= -10: #the jump will continue until the jump_count variable reaches -10, which represents the peak of the jump and the beginning of the descent
            neg = 1 #this variable is used to determine whether the character is going up or down during the jump
            if jump_count < 0: #if the jump_count is negative, it means the character is descending, so we set neg to -1 to reverse the direction of the jump
                neg = -1
            y -= (jump_count ** 2) * 0.5 * neg #this formula creates a parabolic jump arc by using the square of the jump_count variable, which gives us a smooth and natural-looking jump. The neg variable is used to reverse the direction of the jump when the character is descending.
            jump_count -= 1
        else: #once the jump is complete, we reset the jump variables to allow for another jump in the future
            is_jump = False
            jump_count = 10    
    
    redraw_game_window()

# Quit Pygame
pygame.quit()