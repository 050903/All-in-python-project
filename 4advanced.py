import turtle
import colorsys
import random
import math
import time
from typing import Tuple, List
from dataclasses import dataclass, asdict
import argparse
import logging
import sys

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ElonMuskSuperTurtle")

# --- Config Dataclass ---
@dataclass
class PatternConfig:
    repetitions: int = 16
    shapes_per_loop: int = 18
    hue_increment: float = 0.005
    initial_radius: int = 150
    radius_decrement: int = 6
    small_circle_radius: int = 40
    small_circle_extent: int = 24
    bg_color: str = "black"
    draw_speed: int = 0
    pen_width: int = 2
    screen_width: int = 800
    screen_height: int = 600
    num_turtles: int = 1
    spiral_mode: bool = False
    pulsing_effect: bool = False
    save_image: bool = False
    headless: bool = False


def hsv_to_rgb_tuple(h: float, s: float = 1, v: float = 1) -> Tuple[float, float, float]:
    """
    Convert HSV color to RGB tuple (0-1 floats).
    """
    return colorsys.hsv_to_rgb(h, s, v)


def create_multi_turtle_pattern(config: PatternConfig, turtles: List[turtle.Turtle], screen: turtle.Screen) -> None:
    """Draw pattern with multiple synchronized turtles."""
    h_values = [i * (1.0 / config.num_turtles) for i in range(config.num_turtles)]
    total_shapes = config.repetitions * config.shapes_per_loop
    
    for i in range(config.repetitions):
        for j in range(config.shapes_per_loop):
            for idx, t in enumerate(turtles):
                # Unique color for each turtle
                rgb = hsv_to_rgb_tuple(h_values[idx])
                rgb_255 = tuple(int(c * 255) for c in rgb)
                t.pencolor(rgb_255)
                
                # Pulsing effect
                if config.pulsing_effect:
                    pulse = 1 + 0.3 * math.sin(time.time() * 5 + idx)
                    t.pensize(max(1, int(config.pen_width * pulse)))
                
                # Draw pattern with offset
                radius = max(10, config.initial_radius - j * config.radius_decrement)
                if config.spiral_mode:
                    t.right(90 + idx * 15)  # Offset angles for spiral
                else:
                    t.right(90)
                
                t.circle(radius, 90)
                t.left(90)
                t.circle(radius, 90)
                t.right(180)
                t.circle(config.small_circle_radius, config.small_circle_extent)
                
                h_values[idx] += config.hue_increment
                if h_values[idx] > 1.0:
                    h_values[idx] = 0.0
            
            if (i * config.shapes_per_loop + j) % 25 == 0:
                screen.update()
                logger.info(f"Progress: {((i * config.shapes_per_loop + j) / total_shapes * 100):.1f}%")


def draw_advanced_pattern(config: PatternConfig) -> None:
    """
    Draw an advanced colorful pattern using turtle graphics.
    Args:
        config: PatternConfig object with all drawing parameters.
    """
    logger.info(f"Starting pattern drawing with config: {asdict(config)}")
    try:
        screen = turtle.Screen()
        screen.setup(config.screen_width, config.screen_height)
        screen.bgcolor(config.bg_color)
        screen.colormode(255)
        screen.tracer(0)
        screen.title("Elon Musk SuperTurtle - Press SPACE for random colors, S to save")
        
        # Create multiple turtles
        turtles = []
        for i in range(config.num_turtles):
            t = turtle.Turtle()
            t.hideturtle()
            t.speed(0)
            t.pensize(config.pen_width)
            # Position turtles in a circle for multi-turtle mode
            if config.num_turtles > 1:
                angle = (360 / config.num_turtles) * i
                x = 50 * math.cos(math.radians(angle))
                y = 50 * math.sin(math.radians(angle))
                t.goto(x, y)
            else:
                t.goto(0, 0)
            turtles.append(t)
        
        # Set up keyboard controls
        def randomize_colors():
            for t in turtles:
                r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                t.pencolor(r, g, b)
            screen.update()
        
        def save_drawing():
            if config.save_image:
                filename = f"turtle_art_{int(time.time())}.eps"
                screen.getcanvas().postscript(file=filename)
                logger.info(f"Drawing saved as {filename}")
        
        screen.onkey(randomize_colors, "space")
        screen.onkey(save_drawing, "s")
        screen.listen()
        
        # Draw the pattern
        if config.num_turtles > 1:
            create_multi_turtle_pattern(config, turtles, screen)
        else:
            # Single turtle mode (original pattern)
            t = turtles[0]
            h = 0.0
            total_shapes = config.repetitions * config.shapes_per_loop
            
            for i in range(config.repetitions):
                for j in range(config.shapes_per_loop):
                    rgb = hsv_to_rgb_tuple(h)
                    rgb_255 = tuple(int(c * 255) for c in rgb)
                    t.pencolor(rgb_255)
                    
                    if config.pulsing_effect:
                        pulse = 1 + 0.5 * math.sin(time.time() * 3)
                        t.pensize(max(1, int(config.pen_width * pulse)))
                    
                    h += config.hue_increment
                    if h > 1.0:
                        h = 0.0
                    
                    radius = max(10, config.initial_radius - j * config.radius_decrement)
                    if config.spiral_mode:
                        t.right(90 + i * 2)  # Gradual spiral effect
                    else:
                        t.right(90)
                    
                    t.circle(radius, 90)
                    t.left(90)
                    t.circle(radius, 90)
                    t.right(180)
                    t.circle(config.small_circle_radius, config.small_circle_extent)
                    
                    if (i * config.shapes_per_loop + j) % 50 == 0:
                        screen.update()
                        logger.info(f"Progress: {((i * config.shapes_per_loop + j) / total_shapes * 100):.1f}%")
        
        screen.update()
        logger.info("Pattern drawing complete. Controls: SPACE=random colors, S=save")
        
    except turtle.Terminator:
        logger.info("Drawing terminated by user.")
    except Exception as e:
        logger.exception(f"Error during drawing: {e}")
        raise


def parse_args() -> PatternConfig:
    """
    Parse command-line arguments for batch/supercomputer automation.
    """
    parser = argparse.ArgumentParser(description="Elon Musk SuperTurtle Pattern Generator")
    parser.add_argument('--repetitions', type=int, default=16)
    parser.add_argument('--shapes_per_loop', type=int, default=18)
    parser.add_argument('--hue_increment', type=float, default=0.005)
    parser.add_argument('--initial_radius', type=int, default=150)
    parser.add_argument('--radius_decrement', type=int, default=6)
    parser.add_argument('--small_circle_radius', type=int, default=40)
    parser.add_argument('--small_circle_extent', type=int, default=24)
    parser.add_argument('--bg_color', type=str, default="black")
    parser.add_argument('--draw_speed', type=int, default=0)
    parser.add_argument('--pen_width', type=int, default=2)
    parser.add_argument('--screen_width', type=int, default=800)
    parser.add_argument('--screen_height', type=int, default=600)
    parser.add_argument('--num_turtles', type=int, default=1, help='Number of turtles (1-5)')
    parser.add_argument('--spiral_mode', action='store_true', help='Enable spiral drawing mode')
    parser.add_argument('--pulsing_effect', action='store_true', help='Enable pulsing pen width')
    parser.add_argument('--save_image', action='store_true', help='Enable image saving with S key')
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()
    return PatternConfig(**vars(args))


def main() -> None:
    """
    Entry point for the advanced turtle drawing application.
    """
    config = parse_args()
    if config.headless:
        logger.warning("Headless mode is not yet implemented. GUI required for drawing.")
        sys.exit(1)
    
    # Validate config
    if config.num_turtles > 5:
        logger.warning("Too many turtles! Limiting to 5.")
        config.num_turtles = 5
    
    try:
        draw_advanced_pattern(config)
        logger.info("Interactive mode: SPACE=random colors, S=save, Click=close")
        turtle.exitonclick()
    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    except Exception as e:
        logger.error(f"Program failed: {e}")
        sys.exit(1)
    finally:
        try:
            turtle.bye()
        except:
            pass


if __name__ == "__main__":
    main()
