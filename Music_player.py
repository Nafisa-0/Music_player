import os
import pygame
import tkinter
os.environ['TCL_LIBRARY'] = "C:/Program Files/Python313/tcl/tcl8.6"
os.environ['TK_LIBRARY'] = "C:/Program Files/Python313/tcl/tk8.6"
import customtkinter as ctk
from tkinter import filedialog
from mutagen.mp3 import MP3

# Initialize Pygame Mixer
pygame.mixer.init()

class MusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Music Player")
        self.geometry("800x600")
        self.configure(bg="#1e1e1e")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Playlist and Current Song
        self.playlist = []  # Contains dicts: {"path": song_path, "length": song_length}
        self.current_song_index = -1
        self.is_playing = False
        self.is_dragging = False

        # Default Music Folder Path
        self.music_folder = r"C:/Users/USER/OneDrive/Desktop/Python/Music"

        # Create UI
        self.create_ui()

        # Load music from the default folder
        self.load_music_from_folder()

    def create_ui(self):
        # Title Label
        self.title_label = ctk.CTkLabel(
            self, text="Music Player",
            font=("Helvetica Neue", 26, "bold"),
            text_color="#1DB954"
        )
        self.title_label.pack(pady=30)

        # Playlist Box
        self.playlist_box = ctk.CTkTextbox(self, 
                                           width=500, 
                                           height=200, 
                                           font=("Helvetica", 16), 
                                           fg_color="#1e1e1e",
                                           text_color="white",
                                           cursor="arrow",
                                           border_width=1,
                                           border_spacing=2,
                                           border_color="green",
                                           corner_radius=10)
        self.playlist_box.pack(pady=10)

        # Bind click event to the playlist_box to play the selected song
        self.playlist_box.bind("<ButtonRelease-1>", self.on_playlist_click)

        # Control Buttons Frame
        control_frame = ctk.CTkFrame(self, bg_color="#1e1e1e", corner_radius=15)
        control_frame.pack(pady=(25, 0))

        # Control Buttons
        self.previous_btn = ctk.CTkButton(control_frame, text="⏮", font=("Helvetica", 40), command=self.previous_song, width=60, fg_color="#1e1e1e", hover_color="#1DB954", corner_radius=10, text_color="white")
        self.previous_btn.grid(row=0, column=0, padx=5)

        self.play_btn = ctk.CTkButton(control_frame, text="▶",font=("Helvetica", 40), command=self.toggle_play_pause, width=50, height=50, fg_color="#1e1e1e", hover_color="#1DB954", corner_radius=10, text_color="white")
        self.play_btn.grid(row=0, column=1, padx=2, pady=2)

        self.next_btn = ctk.CTkButton(control_frame, text="⏭", font=("Helvetica", 40), command=self.next_song, width=60, fg_color="#1e1e1e", hover_color="#1DB954", corner_radius=10, text_color="white")
        self.next_btn.grid(row=0, column=2, padx=5)
        
        # Add Back 5s and Forward 5s Buttons
        self.back_5s_btn = ctk.CTkButton(control_frame, text="⏪5s", command=self.skip_backward_5s, width=100,  fg_color="#1e1e1e", hover_color="#1DB954", corner_radius=10, text_color="white")
        self.back_5s_btn.grid(row=1, column=0, padx=5)
    
        self.forward_5s_btn = ctk.CTkButton(control_frame, text="⏩5s", command=self.skip_forward_5s, width=100,  fg_color="#1e1e1e", hover_color="#1DB954", corner_radius=10, text_color="white")
        self.forward_5s_btn.grid(row=1, column=2, padx=5)
        
        self.progress_bar_frame = ctk.CTkFrame(self, fg_color="#202020", width=500, height=50, corner_radius=8)
        self.progress_bar_frame.pack(pady=10, padx=20)
    
        
        # Progress Bar with drag event to skip music
        self.progress_bar = ctk.CTkSlider(self.progress_bar_frame,
                                          from_=0,
                                          to=1,
                                          width=480,
                                          height=4,
                                          button_color="#1DB954",
                                          button_hover_color="#1ED760",
                                          progress_color="#1DB954",
                                          fg_color="#282c34",
                                          command=self.on_progress_bar_drag)
        self.progress_bar.grid(row=0, column=0, pady=10)
        
        # self.progress_bar.configure(command=self.on_progress_bar_drag)
        
        self.progress_bar.bind("<ButtonRelease-1>", self.on_progress_bar_release)
        self.progress_bar.bind("<B1-Motion>", self.on_progress_bar_drag)
        # Time Labels
        self.current_time_label = ctk.CTkLabel(self.progress_bar_frame,
                                               text="0:00",
                                               font=("Helvetica", 12),
                                               text_color="white")
        self.current_time_label.grid(row=1, column=0, sticky="w", padx=10)

        self.total_time_label = ctk.CTkLabel(self.progress_bar_frame,
                                             text="0:00",
                                             font=("Helvetica", 12),
                                             text_color="white")
        self.total_time_label.grid(row=1, column=1, sticky="e", padx=10)


        # Volume Control
        self.volume_label = ctk.CTkLabel(
            self, text="Volume 🔊", font=("Helvetica", 16), text_color="white"
        )
        self.volume_label.pack(pady=5)
        
        self.volume_slider = ctk.CTkSlider(
            self, from_=0, to=1, command=self.set_volume, width=500, fg_color="#282c34", button_color="#1DB954", button_hover_color="#1ED760"
        )
        self.volume_slider.pack(pady=5)
        self.volume_slider.set(0.5)
        
        self.tooltip_label = ctk.CTkLabel(
            self,
            text="0:00",
            font=("Helvetica", 10),
            text_color="white",
            fg_color="#333333",
            corner_radius=5,
        )
        self.tooltip_label.place_forget()  # Hide initially
        
        # Show tooltip on drag
        def show_tooltip(event):
            x_offset = self.progress_bar.winfo_rootx() + event.x
            self.tooltip_label.place(x=x_offset, y=self.progress_bar.winfo_rooty() - 20)
            new_time = self.progress_bar.get() * self.playlist[self.current_song_index]["length"]
            self.tooltip_label.configure(text=self.format_time(new_time))
        self.progress_bar.bind("<B1-Motion>", show_tooltip)
        self.progress_bar.bind("<ButtonRelease-1>", lambda e: self.tooltip_label.place_forget())  # Hide on release


    def load_music(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        if files:
            for file in files:
                try:
                    audio = MP3(file)
                    self.playlist.append({"path": file, "length": audio.info.length})
                except Exception as e:
                    print(f"Error loading {file}: {e}")
            self.update_playlist_box()

    def load_music_from_folder(self):
        if os.path.exists(self.music_folder):
            for file in os.listdir(self.music_folder):
                if file.endswith((".mp3", ".wav", ".ogg")):
                    full_path = os.path.join(self.music_folder, file)
                    try:
                        audio = MP3(full_path)
                        self.playlist.append({"path": full_path, "length": audio.info.length})
                    except Exception as e:
                        print(f"Error loading {file}: {e}")
            self.update_playlist_box()

    def update_playlist_box(self):
        self.playlist_box.delete("1.0", "end")
        for index, song in enumerate(self.playlist, start=1):
            self.playlist_box.insert("end", f"{index}. {os.path.basename(song['path'])}\n")

    def toggle_play_pause(self):
        """Toggle play/pause functionality."""
        if self.current_song_index == -1:
            return  # No song selected
    
        if self.is_playing:
            # Pause the song
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_btn.configure(text="▶️")
        else:
            # Resume or start the song
            if pygame.mixer.music.get_pos() > 0:
                # Resume if already started
                pygame.mixer.music.unpause()
            else:
                # Start from the beginning
                song_path = self.playlist[self.current_song_index]["path"]
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
            self.is_playing = True
            self.play_btn.configure(text="⏸️")
            self.update_progress_bar()


    def play_music(self):
        if self.current_song_index != -1:
            song_data = self.playlist[self.current_song_index]
            song_path = song_data["path"]
            try:
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.is_playing = True
                self.play_btn.configure(text="⏸️")
                self.total_time_label.configure(text=self.format_time(song_data["length"]))
                self.update_progress_bar(song_data["length"])
            except pygame.error as e:
                print(f"Error playing song: {e}")

    def previous_song(self):
        if self.current_song_index > 0:
            self.current_song_index -= 1
            self.play_music()

    def next_song(self):
        if self.current_song_index < len(self.playlist) - 1:
            self.current_song_index += 1
            self.play_music()

    def on_playlist_click(self, event):
        try:
            index = self.playlist_box.index("@%s,%s" % (event.x, event.y))
            line_index = int(index.split(".")[0]) - 1
            self.current_song_index = line_index
            self.play_music()
        except Exception as e:
            print(f"Error selecting song: {e}")

    def update_progress_bar(self):
        """Continuously update the progress bar and time labels."""
        if self.current_song_index != -1 and not self.is_dragging:
            # Get the current time from the mixer
            current_time = pygame.mixer.music.get_pos() / 1000
            song_length = self.playlist[self.current_song_index]["length"]
    
            # Update progress bar and time labels
            if current_time < song_length:
                self.current_time_label.configure(text=self.format_time(current_time))
                self.progress_bar.set(current_time / song_length)
                self.after(500, self.update_progress_bar)  # Check every 500ms
            else:
                # End of song
                self.progress_bar.set(1)
                self.current_time_label.configure(text=self.format_time(song_length))
                self.is_playing = False
                self.play_btn.configure(text="▶️")


    def on_progress_bar_drag(self, value):
        """Update progress bar dynamically as it's being dragged."""
        if self.current_song_index != -1:
            self.is_dragging = True
            # Calculate the new time in the song based on slider value
            song_length = self.playlist[self.current_song_index]["length"]
            dragged_time = value * song_length
            self.current_time_label.configure(text=self.format_time(dragged_time))
    
    def on_progress_bar_release(self, event=None):
        """Skip to the part of the song after dragging."""
        if self.current_song_index != -1:
            self.is_dragging = False
            # Get the new time from the progress bar
            value = self.progress_bar.get()
            song_length = self.playlist[self.current_song_index]["length"]
            new_time = value * song_length
    
            # Update Pygame mixer to play from the new position
            pygame.mixer.music.set_pos(new_time)
    
            # Update UI to reflect the new time
            self.current_time_label.configure(text=self.format_time(new_time))
            # self.progress_bar.set(value)
            self.update_progress_bar()

        
    def skip_backward_5s(self):
        """Skip backward 5 seconds."""
        if self.current_song_index != -1:
            current_time = pygame.mixer.music.get_pos() / 1000
            new_time = max(0, current_time - 5)  # Ensure no negative time
            pygame.mixer.music.set_pos(new_time)
            self.progress_bar.set(new_time / self.playlist[self.current_song_index]["length"])
            self.current_time_label.configure(text=self.format_time(new_time))
            self.update_progress_bar()

    def skip_forward_5s(self):
        """Skip forward 5 seconds."""
        if self.current_song_index != -1:
            song_length = self.playlist[self.current_song_index]["length"]
            current_time = pygame.mixer.music.get_pos() / 1000
            new_time = min(song_length, current_time + 5)  # Ensure no overflow beyond song length
            pygame.mixer.music.set_pos(new_time)
            self.progress_bar.set(new_time / song_length)
            self.current_time_label.configure(text=self.format_time(new_time))
            self.update_progress_bar()

    def set_volume(self, value):
        pygame.mixer.music.set_volume(float(value))
        volume = float(value)

        # Update the volume emoji based on the level
        if volume == 0:
            emoji = "🔇"
        elif volume <= 0.3:
            emoji = "🔈"
        elif volume <= 0.7:
            emoji = "🔉"
        else:
            emoji = "🔊"

        self.volume_label.configure(text=f"Volume {emoji}")

    @staticmethod
    def format_time(seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02}"

if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()