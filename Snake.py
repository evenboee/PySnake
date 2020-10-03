import getopt
import math
import os
import random
import sys
from screeninfo import get_monitors

# os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame import mixer


# Representing an element with x and y coordinate
class Pos:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def dist(self, other):
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


# Pick new random location for food. Finds a position that is not in the tail
def pick_spot():
    global w, h, tail
    p = None
    while p is None:
        p = Pos(random.randint(0, w - 1), random.randint(0, h - 1))
        for e in tail:
            if p.dist(e) < 1:
                p = None
                break
    return p


def print_help():
    print("\n--help\n        To get help\n" +
          "--width, -w\n        To set width of game in blocks\n\n" +
          "--height, -h\n        To set height of game in blocks\n\n" +
          "--fps, -f\n        To set framerate\n\n" +
          "--scale, -s\n        To set the scale of a block in pixels\n\n" +
          "--no-image, -i\n        Do not load images\n\n" +
          "--no-sound, -n\n        Do not load sounds\n"
          )


def main(argv):
    global w, h, fps, scl, loadImage, playSound
    try:
        opts, args = getopt.getopt(argv, "w:h:f:s:ni",
                                   ["width=", "height=", "help", "fps=", "scale=", "no-image", "no-sound"])
    except getopt.GetoptError:
        print("Command line argument exception\n    --help to list commands")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "--help":
            print_help()
            sys.exit()
        elif opt in ("-h", "--height"):
            try:
                h = int(arg)
            except ValueError:
                print("Could not set height")
        elif opt in ("-w", "--width"):
            try:
                w = int(arg)
            except ValueError:
                print("Could not set width")
        elif opt in ("-f", "--fps"):
            try:
                fps = int(arg)
            except ValueError:
                print("Could not set fps")
        elif opt in ("-s", "--scale"):
            try:
                scl = int(arg)
            except ValueError:
                print("Could not set scale")
        elif opt in ("-n", "--no-sound"):
            playSound = False
        elif opt in ("-i", "--no-image"):
            loadImage = False
        else:
            print(f"Option << {opt} >> not recognised")
            print_help()


monitor1 = get_monitors()[0]
# Game variables
scl = 25
fps = 10
w = h = 18
keyQueue = []
loadImage = True
playSound = True

if __name__ == "__main__":
    main(sys.argv[1:])

# Player variables
s = Pos(1)
tail = [Pos()]
direction = Pos(1)
food = pick_spot()

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % ((monitor1.width - (w * scl)) / 2, (monitor1.height - (h * scl)) / 2)

# Initializing pygame
pygame.init()

# Initializing the text module and setting font
pygame.font.init()
font = pygame.font.SysFont('Areal', 2 * scl)

# Create screen
screen = pygame.display.set_mode((w * scl, h * scl))

# Setting refresh rate
clock = pygame.time.Clock()

# Setting title
pygame.display.set_caption("Snake")

# Setting icon
try:
    icon = pygame.image.load('images/snake.png')  # where url is url of image
    pygame.display.set_icon(icon)
except FileNotFoundError:
    print("Could not load image << snake.png >>")

# Loading sound
hit = None
if playSound:
    try:
        hit = pygame.mixer.Sound('music/hit.wav')
    except FileNotFoundError:
        print("Could not load << hit.wav >>")

apple = None
if loadImage:
    try:
        apple = pygame.image.load('images/apple.png')
        apple = pygame.transform.scale(apple, (scl, scl))
    except Exception:
        print("Could not load image << apple.png >>")

# Game loop
running = True
while running:
    dt = clock.tick(fps)

    # Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                keyQueue.append(Pos(-1, 0))
            elif event.key == pygame.K_UP:
                keyQueue.append(Pos(0, -1))
            elif event.key == pygame.K_RIGHT:
                keyQueue.append(Pos(1, 0))
            elif event.key == pygame.K_DOWN:
                keyQueue.append(Pos(0, 1))

    # Direction update
    if len(keyQueue) > 0:
        nDir = keyQueue[0]
        if direction.x != -nDir.x and direction.y != -nDir.y:
            direction = nDir  # Sets direction to the first element in the queue
        keyQueue.pop(0)  # Removes the element from the queue

    # Adding last position of head to tail
    tail.append(Pos(s.x, s.y))

    # Updating position of head
    s.x += direction.x
    s.y += direction.y

    # If overlapping with food: Pick new spot for food. Else: remove least recently added element of tail
    if s.dist(food) < 1:
        food = pick_spot()
        if hit is not None and playSound:
            hit.play()
    else:
        tail.pop(0)

    # If out of bounds
    if s.x > w - 1 or s.x < 0 or s.y > h - 1 or s.y < 0:
        running = False
        continue
    # If crashing into itself
    for t in tail:
        if s.dist(t) < 1:
            running = False
            continue

    # Drawing background
    screen.fill((51, 51, 51))

    # Draw snake
    pygame.draw.rect(screen, (200, 200, 200), (s.x * scl + 1, s.y * scl + 1, scl - 2, scl - 2))
    for t in tail:
        pygame.draw.rect(screen, (255, 255, 255), (t.x * scl + 1, t.y * scl + 1, scl - 2, scl - 2))

    # Drawing apple
    if apple is not None:
        screen.blit(apple, (food.x * scl, food.y * scl))
    else:
        pygame.draw.rect(screen, (0, 255, 0), (food.x * scl, food.y * scl, scl, scl))

    # Displaying score
    textSurface = font.render(str(len(tail) - 1), True, (255, 255, 255))
    screen.blit(textSurface, (scl // 2, scl // 2))

    # Updating screen
    pygame.display.update()

print(f"Final score: {len(tail) - 1}")
