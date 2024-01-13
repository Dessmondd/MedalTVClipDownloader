import os
import requests
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import customtkinter as ctk
from tkinter.messagebox import showinfo
from tkinter.messagebox import showerror
from packaging.version import parse
import sys
import threading

GITHUB_REPO_URL = "https://api.github.com/repos/Dessmondd/MedalTVClipDownloader/releases/latest"
CURRENT_VERSION = "2.1"  # Just the current version, this will change from time to time, HOPEFULLY LOL


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Clip Downloader :)")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.initUI()

    def initUI(self):
        center_frame = tk.Frame(self.root, bg="#302f2f")
        center_frame.pack(expand=True)

        self.check_version_button = ctk.CTkButton(self.root, text="Check for Updates", command=self.check_for_updates)
        self.check_version_button.pack(pady=5)

        self.url_label = ctk.CTkLabel(center_frame, text="Enter the URL of the clip:")
        self.url_input = ctk.CTkEntry(center_frame)

        self.progress_bar = ttk.Progressbar(center_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(row=2, column=0, columnspan=2, pady=10)

        self.download_button = ctk.CTkButton(center_frame, text="Download Video", command=self.start_download_thread)
        self.download_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.url_label.grid(row=0, column=0, padx=10, pady=5)
        self.url_input.grid(row=0, column=1, padx=10, pady=5)
        self.root.config(bg="#302f2f")

        self.exit_button = ctk.CTkButton(center_frame, text="Exit", command=self.exit_app)
        self.exit_button.grid(row=4, column=0, columnspan=3, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    def start_download_thread(self):
        threading.Thread(target=self.download_video).start()

    def check_for_updates(self):
        try:
            response = requests.get(GITHUB_REPO_URL)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release.get("tag_name")

            if latest_version:
                if parse(latest_version) > parse(CURRENT_VERSION):
                    message = f"A new version ({latest_version}) is available!\nVisit {latest_release['html_url']} for the update."
                    showinfo("Update Available", message)
                else:
                    showinfo("No Updates", "You are using the latest version of the app.")
            else:
                showerror("Error", "Failed to retrieve version information from the GitHub response.")
        except requests.exceptions.RequestException as e:
            showerror("Error", f"Failed to check for updates: {e}")



    def download_video(self):
        url = self.url_input.get().strip()
        if not url:
            print('Invalid URL')
            return
        if 'medal' not in url:
            if '/' not in url:
                url = 'https://medal.tv/clips/' + url
            else:
                print('Invalid URL')
                return

        url = url.replace('?theater=true', '')

        try:
            res = requests.get(url)
            html = res.text
            file_url = html.split('"contentUrl":"')[1].split('","')[0] if '"contentUrl":"' in html else None

            if file_url:
                filename = filedialog.asksaveasfilename(
                    initialfile=os.path.basename("heythisisyourvideohehe"),
                    filetypes=[("Video Files", "*.mp4")],
                    defaultextension=".mp4"
                )

                if not filename:
                    return

                with requests.get(file_url, stream=True) as response:
                    response.raise_for_status()
                    total_length = int(response.headers.get('content-length'))
                    bytes_written = 0

                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
                            if chunk:
                                f.write(chunk)
                                bytes_written += len(chunk)
                                self.update_progress_bar(bytes_written, total_length)

                print(f'\nFile {filename} saved')
                showinfo("Success", f"File {filename} saved")
            else:
                print('Error: Most likely, direct link download does not exist')
        except requests.RequestException as e:
            print(f'Error: {e}')
            showerror("Error", f"Error: {e}")


    def update_progress_bar(self, bytes_written, total_bytes):
        if total_bytes is None:
            return

        done = int(100 * bytes_written / total_bytes)
        self.progress_bar["value"] = done
        self.root.update()

    def exit_app(self):
        self.root.destroy()
        sys.exit()

if __name__ == '__main__':
    root = ctk.CTk()
    window = App(root)
    root.mainloop()
