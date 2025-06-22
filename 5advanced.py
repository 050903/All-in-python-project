import turtle as t
from typing import Callable
import random
import colorsys
import math  # Added math import

# Set up the turtle
t.speed(0)  # Fastest speed
t.bgcolor('black')
t.tracer(0, 0)  # Turn off animation to speed up drawing

# Create a list of vibrant colors
def generate_vibrant_colors(num_colors: int) -> list[str]:
    """Generate a list of num_colors evenly distributed vibrant colors."""
    return [
        f"#{int(red * 255):02x}{int(green * 255):02x}{int(blue * 255):02x}"
        for red, green, blue in [colorsys.hsv_to_rgb(i / num_colors, 1.0, 1.0) for i in range(num_colors)]
    ]

# Fixed: Changed generate_colors to generate_vibrant_colors to match function name
COLORS = generate_vibrant_colors(10)

def draw_shape(size: float, sides: int, angle: float) -> None:
    """Draw a shape with the given parameters."""
    for _ in range(sides):
        t.forward(size)
        t.right(360/sides + angle)
        t.speed(random.randint(1,10))  # Random speed for movement variation

def spiral_pattern(shape_func: Callable, iterations: int, shrink_factor: float = 0.97) -> None:
    """Create a spiral pattern using the given shape function."""
    size = 200
    for i in range(iterations):
        t.pencolor(COLORS[i % len(COLORS)])
        t.pensize(i // 20 + 1)  # Gradually increase pen size
        shape_func(size, 90 if i % 2 == 0 else 45)
        size *= shrink_factor
        t.right(10 + i/10)
        t.speed(random.randint(1,10))  # Random speed

        # Update the screen every 5 iterations for smoother animation
        if i % 5 == 0:
            t.update()

def draw_flower(size: float, petals: int) -> None:
    """Draw a flower with the given parameters."""
    angle = 360 / petals
    for _ in range(petals):
        t.circle(size/2, 60)
        t.left(120)
        t.circle(size/2, 60)
        t.left(120 + angle)
        t.speed(random.randint(1,10))  # Random speed for petal drawing

def mandala(iterations: int) -> None:
    """Create a mandala pattern."""
    for i in range(iterations):
        t.pencolor(COLORS[i % len(COLORS)])
        t.circle(100 + i*2, 90)
        t.left(90)
        t.circle(100 + i*2, 90)
        t.left(18)
        t.speed(random.randint(1,10))  # Random speed
        t.update()

# Main animation sequence
t.hideturtle()  # Fixed indentation

# First animation: Square spiral with bounce effect
for i in range(100):
    t.pencolor(COLORS[i % len(COLORS)])
    draw_shape(150 - i + abs(10*math.sin(i/5)), 4, i/10)  # Added bounce with sine
    t.right(i/2)
    if i % 5 == 0:
        t.update()

t.clear()

# Second animation: Mandala with pulsing effect
t.penup()
t.goto(0, 0)
t.pendown()
mandala(50)

t.clear()

# Third animation: Flower pattern with size oscillation
t.penup()
t.goto(0, 0)
t.pendown()
for i in range(12):
    t.pencolor(COLORS[i % len(COLORS)])
    draw_flower(200 - i*10 + 20*math.sin(i), 8)  # Added size oscillation
    t.right(30)
    t.update()

t.clear()

# Final animation: Complex spiral with wave effect
def complex_shape(size: float, angle: float) -> None:
    """Draw a complex shape combining circles and lines with wave motion."""
    t.circle(size/2 + 10*math.sin(angle), 180)  # Added wave motion
    t.right(angle)
    t.forward(size)
    t.right(angle)
    t.speed(random.randint(1,10))  # Random speed

spiral_pattern(complex_shape, 150)

t.done()
