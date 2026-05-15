# This is a simple Pygame program that creates a window and allows the user to close it.
#pygame initialization
import pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("My Game")

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
# Quit Pygame
pygame.quit()