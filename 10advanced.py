import yt_dlp
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
import logging
import json
from typing import Dict, List, Optional, Union
import re
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Advanced YouTube Downloader")
        self.window.geometry("800x600")
        
        # Configuration management
        self.config_file = "config.json"
        self.config = self.load_config()
        
        self.setup_ui()
        self.current_downloads: Dict[str, Dict] = {}
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        return {
            "default_download_path": "downloads",
            "max_concurrent_downloads": 3,
            "preferred_quality": "1080p",
            "auto_create_playlist_folder": True
        }
        
    def save_config(self):
        """Save current configuration to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def setup_ui(self):
        """Setup the main UI components."""
        # URL Input Frame
        url_frame = ttk.LabelFrame(self.window, text="Video URL", padding=10)
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=70)
        url_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        fetch_btn = ttk.Button(url_frame, text="Fetch Info", command=self.fetch_video_info)
        fetch_btn.pack(side=tk.LEFT)
        
        # Video Info Frame
        self.info_frame = ttk.LabelFrame(self.window, text="Video Information", padding=10)
        self.info_frame.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)
        
        # Format Selection
        self.format_tree = ttk.Treeview(self.info_frame, columns=("Resolution", "Extension", "Size"), show="headings")
        self.format_tree.heading("Resolution", text="Resolution")
        self.format_tree.heading("Extension", text="Format")
        self.format_tree.heading("Size", text="Size")
        self.format_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Download Controls
        control_frame = ttk.Frame(self.window)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.download_path_var = tk.StringVar(value=self.config["default_download_path"])
        ttk.Label(control_frame, text="Save to:").pack(side=tk.LEFT)
        ttk.Entry(control_frame, textvariable=self.download_path_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Browse", command=self.browse_download_path).pack(side=tk.LEFT)
        
        # Download Button
        self.download_btn = ttk.Button(self.window, text="Download", command=self.start_download)
        self.download_btn.pack(pady=10)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(self.window, text="Download Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        ttk.Label(progress_frame, textvariable=self.progress_var).pack()

    def progress_hook(self, d: Dict):
        """Enhanced progress hook for downloads."""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            
            progress = float(percent.strip('%')) if percent != 'N/A' else 0
            self.progress_bar['value'] = progress
            
            status = f"Downloading: {percent} at {speed} (ETA: {eta})"
            self.progress_var.set(status)
            self.window.update_idletasks()
            
        elif d['status'] == 'finished':
            self.progress_var.set(f"Download completed: {os.path.basename(d['filename'])}")
            self.progress_bar['value'] = 100
            
    def validate_youtube_url(self, url: str) -> bool:
        """Enhanced URL validation with support for playlists and shorts."""
        try:
            parsed = urlparse(url)
            if parsed.netloc in ['youtube.com', 'www.youtube.com', 'youtu.be', 'm.youtube.com']:
                if parsed.path.startswith('/watch') or parsed.path.startswith('/shorts/'):
                    return True
                if parsed.path.startswith('/playlist'):
                    return True
                if parsed.netloc == 'youtu.be' and len(parsed.path) > 1:
                    return True
            return False
        except Exception:
            return False

    def get_video_info(self, url: str) -> Optional[Dict]:
        """Get video information with enhanced error handling."""
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # For playlist support
            'no_warnings': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info.get('_type') == 'playlist':
                    # Handle playlist differently
                    return self.process_playlist_info(info)
                return info
        except Exception as e:
            logger.error(f"Error fetching video info: {e}")
            messagebox.showerror("Error", f"Could not fetch video information: {str(e)}")
            return None

    def process_playlist_info(self, playlist_info: Dict) -> Dict:
        """Process playlist information."""
        return {
            'title': playlist_info.get('title', 'Unknown Playlist'),
            'is_playlist': True,
            'entries': playlist_info.get('entries', []),
            'playlist_count': playlist_info.get('playlist_count', 0)
        }

    def fetch_video_info(self):
        """Fetch and display video information."""
        url = self.url_var.get().strip()
        if not self.validate_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
            
        self.progress_var.set("Fetching video information...")
        self.window.update_idletasks()
        
        def fetch():
            info = self.get_video_info(url)
            if info:
                self.display_video_info(info)
                
        threading.Thread(target=fetch, daemon=True).start()

    def get_available_formats(self, info: Dict) -> List[Dict]:
        """Get available video formats."""
        formats = []
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                formats.append({
                    'format_id': f['format_id'],
                    'ext': f['ext'],
                    'resolution': f.get('resolution', 'Unknown'),
                    'filesize': f.get('filesize', 0),
                })
        return sorted(formats, key=lambda x: int(x['resolution'].split('x')[1]) if 'x' in x['resolution'] else 0, reverse=True)

    def download_video(self, url: str, resolution: str, download_path: str) -> bool:
        """Download video with specified resolution."""
        ydl_opts = {
            'format': 'best[height<=?720]',  # Default format
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                return True
            except Exception as e:
                logger.error(f"Download error: {e}")
                return False

    def display_playlist_info(self, info: Dict):
        """Display playlist information."""
        self.format_tree.insert('', 'end', values=(
            f"Playlist ({info['playlist_count']} videos)",
            "Various",
            "N/A"
        ))

    def display_video_info(self, info: Dict):
        """Display video information in the UI."""
        # Clear existing items
        for item in self.format_tree.get_children():
            self.format_tree.delete(item)
            
        if info.get('is_playlist'):
            self.display_playlist_info(info)
            return
            
        formats = self.get_available_formats(info)
        for fmt in formats:
            size_mb = fmt['filesize'] / 1_000_000 if fmt['filesize'] else 0
            self.format_tree.insert('', 'end', values=(
                fmt['resolution'],
                fmt['ext'],
                f"{size_mb:.1f} MB"
            ))

    def start_download(self):
        """Initiate the download process."""
        selected_items = self.format_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a format to download")
            return
            
        url = self.url_var.get().strip()
        format_values = self.format_tree.item(selected_items[0])['values']
        
        download_path = self.download_path_var.get()
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
        def download():
            self.download_btn['state'] = 'disabled'
            success = self.download_video(url, format_values[0], download_path)
            self.download_btn['state'] = 'normal'
            
            if success:
                messagebox.showinfo("Success", f"Download completed!\nSaved in: {download_path}")
            else:
                messagebox.showerror("Error", "Download failed")
                
        threading.Thread(target=download, daemon=True).start()

    def browse_download_path(self):
        """Open file dialog to select download directory."""
        path = filedialog.askdirectory(initialdir=self.download_path_var.get())
        if path:
            self.download_path_var.set(path)
            self.config["default_download_path"] = path
            self.save_config()

    def run(self):
        """Start the application."""
        self.window.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()
