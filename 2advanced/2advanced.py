import tkinter as tk
from tkinter import filedialog, Scale, Frame, Button, Label
from PIL import Image, ImageTk
import numpy as np

class AsciiArtGenerator(tk.Tk):
    """
    A tkinter GUI application to convert an image into ASCII art.
    """
    def __init__(self):
        super().__init__()
        self.title("ASCII Art Generator")
        self.geometry("800x600")
        self.configure(bg="#2c3e50")

        # --- Member variables ---
        self.image_path = "image_0f733e.jpg" 
        self.original_image = None
        self.ascii_art = ""

        # --- UI Elements ---
        # Frame for controls
        control_frame = Frame(self, bg="#34495e", padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # Resolution slider
        Label(control_frame, text="Resolution (Width):", fg="white", bg="#34495e").pack(side=tk.LEFT, padx=5)
        self.resolution_slider = Scale(control_frame, from_=20, to_=200, orient=tk.HORIZONTAL, length=200, bg="#2c3e50", fg="white", troughcolor="#7f8c8d")
        self.resolution_slider.set(100)
        self.resolution_slider.pack(side=tk.LEFT, padx=5)
        
        # Invert checkbox
        self.invert_var = tk.IntVar()
        invert_check = tk.Checkbutton(control_frame, text="Invert", variable=self.invert_var, bg="#34495e", fg="white", selectcolor="#2c3e50", activebackground="#34495e")
        invert_check.pack(side=tk.LEFT, padx=5)

        # Buttons
        generate_button = Button(control_frame, text="Generate", command=self.generate_and_display_art, bg="#2980b9", fg="white", relief="flat", padx=10)
        generate_button.pack(side=tk.LEFT, padx=5)

        save_button = Button(control_frame, text="Save to .txt", command=self.save_to_file, bg="#27ae60", fg="white", relief="flat", padx=10)
        save_button.pack(side=tk.LEFT, padx=5)

        # Frame for the output
        output_frame = Frame(self, bg="#ecf0f1", padx=10, pady=10)
        output_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Text widget for ASCII art
        self.text_area = tk.Text(output_frame, wrap=tk.WORD, bg="#ecf0f1", fg="#2c3e50", font=("Courier", 8), relief="flat")
        self.text_area.pack(expand=True, fill=tk.BOTH)

        # Initial generation
        self.generate_and_display_art()

    def image_to_ascii(self, width=100, invert=False):
        """
        Converts the loaded image to an ASCII string representation.
        
        Args:
            width (int): The desired width of the ASCII art in characters.
            invert (bool): If True, inverts the brightness mapping.
        """
        try:
            self.original_image = Image.open(self.image_path)
        except FileNotFoundError:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"Error: Image file not found at '{self.image_path}'.\nPlease make sure the image is in the same directory.")
            return

        # --- Image Processing ---
        # Convert to grayscale
        img = self.original_image.convert('L')

        # Resize the image
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width * 0.55) # 0.55 to adjust for character aspect ratio
        img = img.resize((width, new_height))

        # Convert image to numpy array
        img_array = np.array(img)
        
        # Define ASCII characters based on brightness
        # More characters give a more detailed image
        ascii_chars = " .:-=+*#%@"
        if invert:
            ascii_chars = ascii_chars[::-1]

        # Map pixel brightness to ASCII characters
        self.ascii_art = ""
        for row in img_array:
            for pixel_brightness in row:
                # Normalize pixel value to be within the range of ascii_chars
                index = int((pixel_brightness / 255) * (len(ascii_chars) - 1))
                self.ascii_art += ascii_chars[index]
            self.ascii_art += "\n"

    def generate_and_display_art(self):
        """
        Gets parameters from the GUI, generates the ASCII art,
        and displays it in the text area.
        """
        resolution = self.resolution_slider.get()
        invert_colors = self.invert_var.get() == 1
        
        print("\n--- Generating ASCII Art ---")
        print(f"Resolution: {resolution}, Invert: {invert_colors}")

        self.image_to_ascii(width=resolution, invert=invert_colors)

        # Display in terminal
        print("\n--- Console Output ---")
        print(self.ascii_art)
        
        # Display in GUI
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.ascii_art)

    def save_to_file(self):
        """
        Saves the generated ASCII art to a text file.
        """
        if not self.ascii_art:
            print("No ASCII art generated to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save ASCII Art"
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.ascii_art)
                print(f"Successfully saved to {file_path}")
            except Exception as e:
                print(f"Error saving file: {e}")

if __name__ == "__main__":
    app = AsciiArtGenerator()
    app.mainloop()
