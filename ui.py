# import gi
# gi.require_version("Gtk", "3.0")
# from gi.repository import Gtk, GObject
# import pygst
# pygst.require("0.10")
# import gst

# class MusicPlayer(Gtk.Window):
#     def __init__(self):
#         super().__init__(title="Music Player")
#         self.set_default_size(400, 200)

#         # Layout
#         self.grid = Gtk.Grid()
#         self.add(self.grid)

#         # Player setup
#         self.player = gst.element_factory_make("playbin", "player")
        
#         # File Chooser Button
#         self.file_chooser = Gtk.FileChooserButton(title="Select a Music File", action=Gtk.FileChooserAction.OPEN)
#         self.file_chooser.connect("file-set", self.on_file_selected)
#         self.grid.attach(self.file_chooser, 0, 0, 3, 1)

#         # Play Button
#         self.play_button = Gtk.Button(label="Play")
#         self.play_button.connect("clicked", self.on_play_clicked)
#         self.grid.attach(self.play_button, 0, 1, 1, 1)

#         # Pause Button
#         self.pause_button = Gtk.Button(label="Pause")
#         self.pause_button.connect("clicked", self.on_pause_clicked)
#         self.grid.attach(self.pause_button, 1, 1, 1, 1)

#         # Progress Bar
#         self.progress_bar = Gtk.ProgressBar()
#         self.grid.attach(self.progress_bar, 0, 2, 3, 1)

#         # Timer for progress bar
#         GObject.timeout_add(500, self.update_progress)

#     def on_file_selected(self, widget):
#         filepath = self.file_chooser.get_filename()
#         if filepath:
#             self.player.set_property("uri", f"file://{filepath}")

#     def on_play_clicked(self, widget):
#         self.player.set_state(gst.STATE_PLAYING)

#     def on_pause_clicked(self, widget):
#         self.player.set_state(gst.STATE_PAUSED)

#     def update_progress(self):
#         # Update the progress bar
#         position, duration = self.get_track_position()
#         if duration > 0:
#             self.progress_bar.set_fraction(position / duration)
#         return True

#     def get_track_position(self):
#         # Get current track position and duration
#         try:
#             position, _ = self.player.query_position(gst.Format.TIME)
#             duration, _ = self.player.query_duration(gst.Format.TIME)
#             return position / gst.SECOND, duration / gst.SECOND
#         except Exception:
#             return 0, 0


# if __name__ == "__main__":
#     app = MusicPlayer()
#     app.connect("destroy", Gtk.main_quit)
#     app.show_all()
#     Gtk.main()
