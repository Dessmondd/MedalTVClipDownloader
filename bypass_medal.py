import requests
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QLabel, QLineEdit, QVBoxLayout
import tkinter as tk
from tkinter import messagebox

class App(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        url_label = QLabel("Enter the URL of the clip:")
        self.url_input = QLineEdit()
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)
        self.download_button = QPushButton("Download Video")
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button)
        self.setLayout(layout)

    def download_video(self):
        url = self.url_input.text().strip()

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
                filename, _ = QFileDialog.getSaveFileName(self, "Save Video", os.path.basename(file_url), "Video Files (*.mp4)")
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
                            done = int(50 * dl / total_length)
                            print('\r[%s%s]' % ('=' * done, ' ' * (50 - done)), end='', flush=True)

                print(f'\nFile {filename} saved')
                tk.Tk().wm_withdraw() 
                messagebox.showinfo('Download Complete', 'Your video has been downloaded!')
            else:
                print('Error: Most likely, direct link download does not exist')
        except:
            print('Error: Clip information is not being fetch properly, probably we fetching different information..')
            
if __name__ == '__main__':
    app = QApplication([])
    window = App()
    window.show()
    app.exec_()
