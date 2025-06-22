import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image
import time

class DotDrawer:
    def __init__(self, image_path, max_dots=8000):
        self.image_path = image_path
        self.max_dots = max_dots
        self.dots = []
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        
    def detect_face_region(self, img):
        """Detect face region to focus dot placement"""
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(img, 1.1, 4)
        
        if len(faces) > 0:
            # Use the largest detected face
            face = max(faces, key=lambda f: f[2] * f[3])
            return face
        return None
        
    def enhance_facial_features(self, img):
        """Enhance facial features for better dot placement"""
        # Apply Gaussian blur to reduce noise
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img = clahe.apply(img)
        
        # Detect edges to emphasize facial features
        edges = cv2.Canny(img, 50, 150)
        
        # Combine original image with edges
        enhanced = cv2.addWeighted(img, 0.7, edges, 0.3, 0)
        
        return enhanced
        
    def scan_image(self):
        """Scan image and convert to dot coordinates with face detection"""
        # Load image
        original_img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        
        # Detect face region
        face_region = self.detect_face_region(original_img)
        
        # Resize image while maintaining aspect ratio - larger for more detail
        height, width = original_img.shape
        if width > height:
            new_width = 150
            new_height = int(150 * height / width)
        else:
            new_height = 150
            new_width = int(150 * width / height)
            
        img = cv2.resize(original_img, (new_width, new_height))
        
        # Enhance facial features
        img = self.enhance_facial_features(img)
        
        # Create weight map - higher weights for face region but cover entire image
        weight_map = np.ones_like(img, dtype=np.float32) * 0.8  # Base weight for entire image
        if face_region is not None:
            fx, fy, fw, fh = face_region
            # Scale face coordinates to resized image
            fx = int(fx * new_width / width)
            fy = int(fy * new_height / height)
            fw = int(fw * new_width / width)
            fh = int(fh * new_height / height)
            
            # Increase weight in face region but keep background visible
            weight_map[fy:fy+fh, fx:fx+fw] *= 1.5
        
        # Find dot positions with improved logic
        dots = []
        
        # Use different strategies for different intensity levels
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                pixel_value = img[y, x]
                weight = weight_map[y, x]
                
                # Calculate dot probability based on darkness and weight
                darkness = (255 - pixel_value) / 255.0
                probability = darkness * weight
                
                # More comprehensive dot densities for entire image
                if darkness > 0.8:  # Very dark areas (hair, eyebrows, pupils)
                    num_dots = int(probability * 6)
                elif darkness > 0.6:  # Dark areas (shadows, eye lashes)
                    num_dots = int(probability * 4)
                elif darkness > 0.4:  # Medium areas (skin shadows)
                    num_dots = int(probability * 3)
                elif darkness > 0.25:  # Light areas (skin)
                    num_dots = int(probability * 2)
                elif darkness > 0.1:  # Very light areas (highlights)
                    num_dots = int(probability * 1)
                else:  # Background areas
                    num_dots = 1 if np.random.random() < 0.1 else 0  # Sparse dots for background
                
                # Add dots with controlled randomness
                for _ in range(num_dots):
                    if np.random.random() < min(probability, 0.9):  # Higher acceptance rate
                        # Less randomness for more accurate representation
                        dot_x = x + np.random.uniform(-0.15, 0.15)
                        dot_y = y + np.random.uniform(-0.15, 0.15)
                        dot_size = darkness * 0.7 + 0.3  # Size based on darkness
                        dots.append((dot_x, dot_y, darkness, dot_size))
        
        # Sort dots by importance (darkness and face region priority)
        def get_dot_priority(dot):
            base_priority = dot[2]  # darkness
            if face_region is not None:
                fx, fy, fw, fh = face_region
                dot_x_orig = dot[0] * width / new_width
                dot_y_orig = dot[1] * height / new_height
                if fx <= dot_x_orig <= fx + fw and fy <= dot_y_orig <= fy + fh:
                    return base_priority * 2.0  # Higher priority for face region
            return base_priority
            
        dots.sort(key=get_dot_priority, reverse=True)
        
        self.dots = dots[:self.max_dots]
        self.img_width = new_width
        self.img_height = new_height
        print(f"Generated {len(self.dots)} dots from image")
        if face_region is not None:
            print(f"Face detected and prioritized in dot placement")
        
    def animate_drawing(self):
        """Animate the dot drawing process"""
        margin = 5
        self.ax.set_xlim(-margin, self.img_width + margin)
        self.ax.set_ylim(-margin, self.img_height + margin)
        self.ax.set_aspect('equal')
        self.ax.invert_yaxis()  # Flip Y axis to match image orientation
        self.ax.set_facecolor('white')
        self.ax.set_title('Animated Face Dot Drawing', fontsize=16)
        self.ax.axis('off')  # Remove axes for cleaner look
        
        # Animation function
        def animate(frame):
            if frame < len(self.dots):
                # Draw dots progressively in batches for smoother animation
                batch_size = max(1, len(self.dots) // 200)  # Draw multiple dots per frame
                dots_to_draw = min((frame + 1) * batch_size, len(self.dots))
                
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
                self.ax.set_title(f'Face Drawing Progress: {dots_to_draw}/{len(self.dots)} dots', fontsize=14)
                self.ax.axis('off')
                
                # Draw dots with varying sizes and colors based on intensity
                sizes = [size * 30 + 2 for size in dot_sizes]  # Scale dot sizes
                colors = [plt.cm.gray(1 - intensity) for intensity in intensities]  # Grayscale colors
                
                self.ax.scatter(x_coords, y_coords, s=sizes, c=colors, alpha=0.8, edgecolors='none')
                
        # Create animation with appropriate timing
        total_frames = max(200, len(self.dots) // max(1, len(self.dots) // 200))
        interval = max(20, 4000 // total_frames)  # Adjust speed
        
        anim = animation.FuncAnimation(
            self.fig, animate, frames=total_frames, 
            interval=interval, repeat=False, blit=False
        )
        
        plt.tight_layout()
        plt.show()
        
        return anim

def main():
    # Path to the image
    image_path = r"d:\Documents-D\VS Code\Python\python project\2advanced\elonmusk.jpg"
    
    print("Starting dot drawing process...")
    print("1. Scanning image...")
    
    # Create drawer instance with many more dots for full picture detail
    drawer = DotDrawer(image_path, max_dots=6000)
    
    # Scan the image
    drawer.scan_image()
    
    print("2. Starting animated drawing...")
    print("Close the window when animation completes.")
    
    # Animate the drawing
    anim = drawer.animate_drawing()

if __name__ == "__main__":
    main()