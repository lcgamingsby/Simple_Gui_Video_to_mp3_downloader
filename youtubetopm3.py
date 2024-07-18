import tkinter as tk
from tkinter import filedialog
from pytube import Playlist
from moviepy.editor import AudioFileClip
import os


def patch_pytube():
    import re
    from pytube import extract
    from pytube.exceptions import RegexMatchError

    def get_throttling_function_name(js):
        function_patterns = [
            r"\b[a-zA-Z]+\b\s*=\s*function\s*\((?:[^()]*)\)\s*{",
            r"\b[a-zA-Z]+\b\s*:\s*function\s*\((?:[^()]*)\)\s*{",
        ]
        for pattern in function_patterns:
            regex = re.compile(pattern)
            match = regex.search(js)
            if match:
                return match.group(1)
        raise RegexMatchError(
            caller="get_throttling_function_name", pattern="multiple"
        )

    extract.get_throttling_function_name = get_throttling_function_name


patch_pytube()


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Downloader")

        self.url_label = tk.Label(root, text="Masukkan URL playlist YouTube:")
        self.url_label.pack()

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()

        self.output_label = tk.Label(root, text="Pilih folder untuk menyimpan file:")
        self.output_label.pack()

        self.output_path = tk.StringVar()
        self.output_entry = tk.Entry(root, textvariable=self.output_path, width=50)
        self.output_entry.pack()

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_folder)
        self.browse_button.pack()

        self.download_button = tk.Button(root, text="Download & Convert", command=self.download_and_convert)
        self.download_button.pack()

        self.finish_button = tk.Button(root, text="Selesai", command=root.quit)
        self.finish_button.pack()

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.output_path.set(folder_path)

    def download_and_convert(self):
        playlist_url = self.url_entry.get()
        output_folder = self.output_path.get()

        playlist = Playlist(playlist_url)
        for video in playlist.videos:
            stream = video.streams.filter(only_audio=True).order_by('abr').desc().first()
            video_filename = stream.default_filename
            stream.download(output_folder)

            video_clip = AudioFileClip(f"{output_folder}/{video_filename}")
            output_mp3_filename = f"{output_folder}/{os.path.splitext(video_filename)[0]}.mp3"
            video_clip.write_audiofile(output_mp3_filename, codec='libmp3lame', bitrate='320k')
            video_clip.close()

            print(f"Video telah diunduh dan dikonversi ke MP3: {output_mp3_filename}")


def main():
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()