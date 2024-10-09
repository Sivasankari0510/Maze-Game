import pygame
import random
import time
import heapq

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 800
screen_height = 600
maze_width = 600
maze_height = 600
info_panel_width = 200
info_panel_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("AI Maze Game")

# Colors
BACKGROUND_COLOR = (173, 216, 230)  # Light blue
MAZE_LINE_COLOR = (255, 99, 71)  # Tomato red
INFO_PANEL_BG = (60, 60, 60)  # Dark gray
INFO_TEXT_COLOR = (255, 255, 255)  # White
BUTTON_COLOR = (0, 128, 0)  # Green
BUTTON_TEXT_COLOR = (255, 255, 255)  # White
HOVER_COLOR = (34, 139, 34)  # Darker green when hovering

# Load images
player_img = pygame.image.load("0.png")
food_img = pygame.image.load("food.png")

# Scale images
player_img = pygame.transform.scale(player_img, (32, 32))
food_img = pygame.transform.scale(food_img, (32, 32))

# Set up the clock for a decent frame rate
clock = pygame.time.Clock()

# Font for score, time, and buttons
font = pygame.font.SysFont("Arial", 40)
button_font = pygame.font.SysFont("Arial", 30)

# Player variables
player_speed = 5
player_rect = player_img.get_rect(topleft=(50, 50))

# Food class
class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = food_img
        self.rect = self.image.get_rect(topleft=(x, y))

# Create food items in random locations
def create_food():
    food_list = []
    for i in range(3):
        x = random.randint(50, maze_width - 50)
        y = random.randint(50, maze_height - 50)
        food_list.append(Food(x, y))
    return food_list

# Create random food
food_list = create_food()

# A* Algorithm Implementation
def a_star(start, goal, grid):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Right, Left, Down, Up
    rows, cols = len(grid), len(grid[0])
    
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    open_list = []
    heapq.heappush(open_list, (0 + heuristic(start, goal), 0, start))
    
    came_from = {}
    cost_so_far = {}
    
    came_from[start] = None
    cost_so_far[start] = 0
    
    while open_list:
        _, current_cost, current = heapq.heappop(open_list)
        
        if current == goal:
            break
        
        for direction in directions:
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and grid[neighbor[0]][neighbor[1]] != 1:
                new_cost = cost_so_far[current] + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + heuristic(goal, neighbor)
                    heapq.heappush(open_list, (priority, new_cost, neighbor))
                    came_from[neighbor] = current
    
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    
    return path

# Create grid representation
def create_grid():
    rows = maze_height // 40
    cols = maze_width // 40
    grid = [[0] * cols for _ in range(rows)]
    return grid

# AI movement logic using A* pathfinding
def ai_move():
    if food_list:
        food = food_list[0]  # Choose the first food item (can be improved to choose the nearest)
        food_x, food_y = food.rect.centerx // 40, food.rect.centery // 40  # Convert to grid coordinates
        player_x, player_y = player_rect.centerx // 40, player_rect.centery // 40  # Convert to grid coordinates
        
        # Create grid representation
        grid = create_grid()
        
        # Perform A* pathfinding
        path = a_star((player_x, player_y), (food_x, food_y), grid)
        
        if path:
            next_step = path[1]  # Get the next step in the path
            next_x, next_y = next_step
            move_x = (next_x - player_x) * 40
            move_y = (next_y - player_y) * 40
            
            # Check for collisions before moving
            if not is_collide(move_x, move_y):
                player_rect.move_ip(move_x, move_y)

# Maze boundaries and collision detection
def is_collide(move_x, move_y):
    future_rect = player_rect.move(move_x, move_y)
    if future_rect.left < 0 or future_rect.right > maze_width or future_rect.top < 0 or future_rect.bottom > maze_height:
        return True
    return False

# Draw maze with vibrant grid lines
def draw_maze():
    screen.fill(BACKGROUND_COLOR)  # Background color
    for x in range(0, maze_width, 40):
        pygame.draw.line(screen, MAZE_LINE_COLOR, (x, 0), (x, maze_height), 5)
    for y in range(0, maze_height, 40):
        pygame.draw.line(screen, MAZE_LINE_COLOR, (0, y), (maze_width, y), 5)

# Draw info panel with contrasting background
def draw_info_panel(time_left, score):
    pygame.draw.rect(screen, INFO_PANEL_BG, (maze_width, 0, info_panel_width, info_panel_height))
    time_text = font.render(f"TIME: {time_left}", True, INFO_TEXT_COLOR)
    score_text = font.render(f"Score: {score}", True, INFO_TEXT_COLOR)
    screen.blit(time_text, (maze_width + 20, 50))
    screen.blit(score_text, (maze_width + 20, 150))

# Draw buttons
def draw_button(text, x, y, width, height, active):
    color = HOVER_COLOR if active else BUTTON_COLOR
    pygame.draw.rect(screen, color, (x, y, width, height))
    text_surface = button_font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surface, text_rect)

# Check if the mouse is over the button
def is_mouse_over_button(mouse_pos, x, y, width, height):
    return x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

# Reset game state (new paths, new food positions)
def reset_game():
    global player_rect, food_list, start_time
    player_rect.topleft = (50, 50)
    food_list = create_food()  # Create new food positions
    start_time = time.time()  # Reset start time

# Main game loop
def main():
    score = 0
    time_limit = 60
    start_time = None

    running = True
    game_active = False  # Game is not active until 'Start' is clicked

    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_maze()

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Check for quit events and button clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if is_mouse_over_button(mouse_pos, 620, 400, 150, 50):  # Start button
                    game_active = True
                    reset_game()
                elif is_mouse_over_button(mouse_pos, 620, 460, 150, 50):  # End button
                    running = False

        if game_active:
            # Time management
            if start_time is None:  # Set the start time only when the game begins
                start_time = time.time()

            elapsed_time = time.time() - start_time
            time_left = max(0, int(time_limit - elapsed_time))

            # AI moves
            ai_move()

            # Draw player
            screen.blit(player_img, player_rect)

            # Draw food
            for food in food_list:
                screen.blit(food.image, food.rect)

            # Check for food collision
            for food in food_list[:]:
                if player_rect.colliderect(food.rect):
                    food_list.remove(food)
                    score += 10

            # Draw info panel
            draw_info_panel(time_left, score)

            # End game when time is up or all food is collected
            if time_left <= 0 or not food_list:
                game_active = False
                start_time = None  # Reset the timer when the game ends

        # Draw buttons below the score
        draw_button("Start", 620, 400, 150, 50, is_mouse_over_button(mouse_pos, 620, 400, 150, 50))
        draw_button("End", 620, 460, 150, 50, is_mouse_over_button(mouse_pos, 620, 460, 150, 50))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
