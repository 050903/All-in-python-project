import yt_dlp
import os
import sys

def progress_hook(d):
    """Progress hook for yt-dlp downloads."""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        print(f"\rDownloading: {percent} at {speed}", end='', flush=True)
    elif d['status'] == 'finished':
        print(f"\nDownload completed: {d['filename']}")

def get_video_info(url):
    """Get video information without downloading."""
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None

def get_available_formats(info):
    """Get available video formats."""
    formats = []
    for f in info.get('formats', []):
        if f.get('vcodec') != 'none' and f.get('acodec') != 'none':  # Has both video and audio
            formats.append({
                'format_id': f['format_id'],
                'ext': f['ext'],
                'resolution': f.get('resolution', 'Unknown'),
                'filesize': f.get('filesize', 0),
                'format_note': f.get('format_note', '')
            })
    return sorted(formats, key=lambda x: int(x['resolution'].split('x')[1]) if 'x' in x['resolution'] else 0, reverse=True)

def download_video(url, format_id, download_path):
    """Download video with specified format."""
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False

def validate_youtube_url(url):
    """Validate if the URL is a valid YouTube URL."""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
    return any(domain in url.lower() for domain in youtube_domains)

def main():
    """Main function."""
    print("Python YouTube Video Downloader (yt-dlp)")
    print("=" * 40)
    
    while True:
        url = input("\nEnter YouTube video URL (or 'quit' to exit): ").strip()
        
        if url.lower() == 'quit':
            print("Goodbye!")
            sys.exit(0)
            
        if not validate_youtube_url(url):
            print("[ERROR] Invalid YouTube URL.")
            continue
            
        print("\nFetching video information...")
        info = get_video_info(url)
        
        if not info:
            print("[ERROR] Could not fetch video information.")
            continue
            
        print(f"Title: {info.get('title', 'Unknown')}")
        print(f"Duration: {info.get('duration', 0) // 60}:{info.get('duration', 0) % 60:02d}")
        print(f"Views: {info.get('view_count', 0):,}")
        
        formats = get_available_formats(info)
        if not formats:
            print("[ERROR] No suitable formats found.")
            continue
            
        print("\nAvailable formats:")
        for i, fmt in enumerate(formats[:10]):  # Show top 10 formats
            size_mb = fmt['filesize'] / 1_000_000 if fmt['filesize'] else 0
            print(f"  {i + 1}: {fmt['resolution']} ({fmt['ext']}) - {size_mb:.1f} MB")
            
        while True:
            try:
                choice = input("\nSelect format (number): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(formats):
                    selected_format = formats[int(choice) - 1]
                    break
                print("[ERROR] Invalid choice.")
            except (ValueError, IndexError):
                print("[ERROR] Invalid input.")
                
        # Create downloads folder
        download_path = "downloads"
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
        print(f"\nStarting download...")
        success = download_video(url, selected_format['format_id'], download_path)
        
        if success:
            print(f"File saved in: {os.path.abspath(download_path)}")
            restart = input("\nDownload another video? (y/n): ").strip().lower()
            if restart != 'y':
                break
        else:
            print("[ERROR] Download failed.")

if __name__ == "__main__":
    main()