import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class SimpleDotDrawer:
    def __init__(self, image_path, max_dots=10000):
        self.image_path = image_path
        self.max_dots = max_dots
        self.dots = []
        self.fig, self.ax = plt.subplots(figsize=(14, 12))
        
    def scan_image(self):
        """Scan entire image and create comprehensive dot representation"""
        # Load and process image
        img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        
        # Resize to reasonable size while maintaining aspect ratio
        height, width = img.shape
        max_size = 200
        if width > height:
            new_width = max_size
            new_height = int(max_size * height / width)
        else:
            new_height = max_size
            new_width = int(max_size * width / height)
            
        img = cv2.resize(img, (new_width, new_height))
        
        # Apply slight blur to reduce noise
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        # Enhance contrast
        img = cv2.equalizeHist(img)
        
        print(f"Processing image of size: {new_width}x{new_height}")
        
        # Generate dots for entire image
        dots = []
        
        # Sample every pixel but with varying density
        for y in range(0, new_height, 1):
            for x in range(0, new_width, 1):
                pixel_value = img[y, x]
                darkness = (255 - pixel_value) / 255.0
                
                # Calculate number of dots based on darkness
                base_dots = 1
                if darkness > 0.9:      # Very dark - many dots
                    num_dots = 8
                elif darkness > 0.7:    # Dark
                    num_dots = 6
                elif darkness > 0.5:    # Medium dark
                    num_dots = 4
                elif darkness > 0.3:    # Medium
                    num_dots = 3
                elif darkness > 0.15:   # Light
                    num_dots = 2
                elif darkness > 0.05:   # Very light
                    num_dots = 1
                else:                   # Almost white
                    num_dots = 1 if np.random.random() < 0.2 else 0
                
                # Add dots with small random offset
                for _ in range(num_dots):
                    if np.random.random() < 0.8:  # 80% chance to place dot
                        dot_x = x + np.random.uniform(-0.3, 0.3)
                        dot_y = y + np.random.uniform(-0.3, 0.3)
                        dot_size = max(0.1, darkness * 0.9 + 0.1)
                        dots.append((dot_x, dot_y, darkness, dot_size))
        
        # Shuffle dots for more natural drawing animation
        np.random.shuffle(dots)
        
        # Limit to max_dots
        self.dots = dots[:self.max_dots]
        self.img_width = new_width
        self.img_height = new_height
        
        print(f"Generated {len(self.dots)} dots covering the entire image")
        
    def animate_drawing(self):
        """Animate the dot drawing process"""
        margin = 10
        self.ax.set_xlim(-margin, self.img_width + margin)
        self.ax.set_ylim(-margin, self.img_height + margin)
        self.ax.set_aspect('equal')
        self.ax.invert_yaxis()
        self.ax.set_facecolor('white')
        self.ax.set_title('Complete Image Dot Drawing Animation', fontsize=16)
        self.ax.axis('off')
        
        def animate(frame):
            # Draw more dots per frame for faster animation
            dots_per_frame = max(10, len(self.dots) // 300)
            dots_to_draw = min((frame + 1) * dots_per_frame, len(self.dots))
            
            if dots_to_draw > 0:
                current_dots = self.dots[:dots_to_draw]
                x_coords = [dot[0] for dot in current_dots]
                y_coords = [dot[1] for dot in current_dots]
                intensities = [dot[2] for dot in current_dots]
                dot_sizes = [dot[3] for dot in current_dots]
                
                self.ax.clear()
                self.ax.set_xlim(-margin, self.img_width + margin)
                self.ax.set_ylim(-margin, self.img_height + margin)
                self.ax.set_aspect('equal')
                self.ax.invert_yaxis()
                self.ax.set_facecolor('white')
                self.ax.set_title(f'Drawing: {dots_to_draw}/{len(self.dots)} dots ({dots_to_draw/len(self.dots)*100:.1f}%)', fontsize=14)
                self.ax.axis('off')
                
                # Draw dots with varying sizes and opacity
                sizes = [size * 25 + 1 for size in dot_sizes]
                colors = ['black'] * len(current_dots)
                alphas = [min(0.9, intensity + 0.3) for intensity in intensities]
                
                # Create scatter plot with alpha values
                for i in range(len(x_coords)):
                    self.ax.scatter(x_coords[i], y_coords[i], s=sizes[i], 
                                  c=colors[i], alpha=alphas[i], edgecolors='none')
        
        # Calculate animation parameters
        total_frames = max(100, len(self.dots) // max(10, len(self.dots) // 300))
        interval = max(30, 5000 // total_frames)
        
        print(f"Starting animation with {total_frames} frames, {interval}ms interval")
        
        anim = animation.FuncAnimation(
            self.fig, animate, frames=total_frames,
            interval=interval, repeat=False, blit=False
        )
        
        plt.tight_layout()
        plt.show()
        return anim

def main():
    image_path = r"d:\Documents-D\VS Code\Python\python project\2advanced\elonmusk.jpg"
    
    print("Starting comprehensive dot drawing...")
    print("1. Scanning entire image...")
    
    # Create drawer with many dots
    drawer = SimpleDotDrawer(image_path, max_dots=8000)
    
    # Process image
    drawer.scan_image()
    
    print("2. Starting animation...")
    print("Close window when complete.")
    
    # Animate
    anim = drawer.animate_drawing()

if __name__ == "__main__":
    main()