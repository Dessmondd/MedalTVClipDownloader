import os
import requests
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import customtkinter as ctk
from tkinter.messagebox import showinfo
from tkinter.messagebox import showerror
from packaging.version import parse

GITHUB_REPO_URL = "URL_REPOSITORY_NOT_YET_FINISHED_SMILEY_FACE"
CURRENT_VERSION = "1.0.0"  # Just the current version, this will change from time to time, HOPEFULLY LOL


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
        self.check_version_button.pack(pady=10)

        self.url_label = ctk.CTkLabel(center_frame, text="Enter the URL of the clip:")
        self.url_input = ctk.CTkEntry(center_frame)

        self.progress_bar = ttk.Progressbar(center_frame, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.grid(row=2, column=0, columnspan=2, pady=10)

        self.download_button = ctk.CTkButton(center_frame, text="Download Video", command=self.download_video)
        self.download_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.url_label.grid(row=0, column=0, padx=10, pady=5)
        self.url_input.grid(row=0, column=1, padx=10, pady=5)
        self.root.config(bg="#302f2f")


    def check_for_updates(self):
        try:
            response = requests.get(GITHUB_REPO_URL + "/releases/latest")
            response_json = response.json()
            print(response.status_code)
            print(response.text)
            response.raise_for_status() 
            latest_version = response_json.get("tag_name")

            if latest_version:
                if parse(latest_version) > parse(CURRENT_VERSION):
                    message = f"A new version ({latest_version}) is available!\nVisit {GITHUB_REPO_URL} for the update."
                    showinfo("Update Available", message)
                else:
                    showinfo("No Updates", "You are using the latest version of the app.")
            else:
                showerror("Error", "Failed to retrieve version information from the GitHub response.")
        except requests.exceptions.RequestException:
            showerror("Error", "Failed to check for updates. Please try again later.")

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
                    initialfile=os.path.basename(file_url),
                    filetypes=[("Video Files", "*.mp4")],
                    defaultextension=".mp4"
                )

                if not filename:
                    return

                self.progress_bar["value"] = 0
                self.progress_bar.grid()

                with open(filename, 'wb') as f:
                    res = requests.get(file_url, stream=True)
                    total_length = res.headers.get('content-length')
                    if total_length is None: 
                        f.write(res.content)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        for data in res.iter_content(chunk_size=4096):
                            dl += len(data)
                            f.write(data)
                            done = int(100 * dl / total_length)
                            self.progress_bar["value"] = done
                            self.root.update()

                print(f'\nFile {filename} saved')
                self.progress_bar.grid_remove()

               
                showinfo("Success", f"File {filename} saved")
            else:
                print('Error: Most likely, direct link download does not exist')
        except:
            print('Error: Clip information is not being fetched properly, probably we are fetching different information..')

if __name__ == '__main__':
    root = ctk.CTk()
    window = App(root)
    root.mainloop()
