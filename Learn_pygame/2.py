# This code creates a simple Pygame window where you can move a red rectangle using the arrow keys. 
# The rectangle will move smoothly across the screen, and the game will close when you click the close button.

#pygame initialization
import pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("My Game")

x = 50
y = 50
width = 40
height = 60

vel = 5

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
    if keys[pygame.K_LEFT]:
        x -= vel
    if keys[pygame.K_RIGHT]:
        x += vel
    if keys[pygame.K_UP]:
        y -= vel
    if keys[pygame.K_DOWN]:
        y += vel

    # Fill the screen with white
    screen.fill((0, 0, 0))
    
    # Draw a red rectangle at the new position
    pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height))
    pygame.display.update()

# Quit Pygame
pygame.quit()