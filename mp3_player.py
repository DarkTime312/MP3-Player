from datetime import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog

import customtkinter as ctk
from mutagen.mp3 import MP3
import pygame
import PIL.Image


def _format_seconds(total_seconds: int) -> str:
    """
    Converts a total number of seconds into a formatted string representing minutes and seconds.

    Args:
        total_seconds (int): The total number of seconds to convert.

    Returns:
        str: A string formatted as 'MM:SS' where MM represents minutes and SS represents seconds.

    Example:
        >>> _format_seconds(125)
        '02:05'
    """
    minute, second = divmod(total_seconds, 60)
    total = time(minute=minute, second=second).strftime('%M:%S')
    return total


def volume_func(volume_value: float) -> None:
    """
    Sets the audio playback volume for the music mixer in Pygame.

    Args:
        volume_value (float): The volume level to set, where 0.0 is silent and 1.0 is the maximum loudness.

    Returns:
        None: This function does not return any value.

    Example:
        volume_func(0.5)  # Sets the volume to 50% of the maximum volume.
    """
    pygame.mixer.music.set_volume(volume_value)


# Setting the CustomTkinter appearance
ctk.set_appearance_mode('light')
ctk.set_default_color_theme('dark-blue')

# Initialize Pygame
pygame.mixer.init()


class App(ctk.CTk):
    """Our mp3 player main window"""

    def __init__(self):
        super().__init__()
        self.geometry('550x450')
        self.title('MP3 Player')
        self.song_dictionary = dict()  # A dictionary of 'song title: song path'.

        # Main frame (The one that holds all the pieces).
        self.main_frame = ctk.CTkFrame(self, fg_color='transparent', width=500, height=400)
        self.main_frame.pack_propagate(False)
        self.main_frame.pack(pady=20)

        # Top level frame inside the Main frame (The one that holds Play list and volume bar)
        self.top_frame = TopFrame(self.main_frame, fg_color='transparent')
        self.top_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # The frame that holds all the player buttons and their related functions.
        self.my_buttons = ButtonsFrame(self.main_frame, self, fg_color='transparent')
        self.my_buttons.pack(padx=30, anchor='w', pady=5, expand=True,
                             fill='both')

        # The Song's progress bar.
        self.progress_slide = ctk.CTkSlider(self.main_frame,
                                            orientation='horizontal',
                                            width=350,
                                            from_=0,
                                            command=self.set_progress
                                            )
        self.progress_slide.pack(padx=30, anchor='w', pady=20)

        # Our app's status bar.
        self.status_bar = ttk.Label(self,
                                    text='Time Elapsed:',
                                    anchor='e',
                                    relief='groove',
                                    background='black',
                                    foreground='white',
                                    )
        self.status_bar.place(relx=0, rely=1, anchor='sw', relwidth=1)

        # A class that creates the Menu bar at the top.
        self.menus = Menus(self, self.get_playlist_widget(), self.get_song_dictionary())
        # Bind the mouse wheel events to the increase and decrease functions
        self.bind('<MouseWheel>',
                  lambda event: self.increase_volume(event) if event.delta > 0 else self.decrease_volume(event))

    def increase_volume(self, event):
        # Increase the volume by moving the slider up
        current_value = self.top_frame.volume_slider.get()
        if current_value < 1.0:  # Assuming the maximum value is 100
            self.top_frame.volume_slider.set(current_value + 0.05)

    def decrease_volume(self, event):
        # Decrease the volume by moving the slider down
        current_value = self.top_frame.volume_slider.get()
        if current_value > 0:  # Assuming the minimum value is 0
            self.top_frame.volume_slider.set(current_value - 0.05)

    def get_song_dictionary(self):
        """Returns the song dictionary"""
        return self.song_dictionary

    def get_playlist_widget(self):
        """Returns the reference to our playlist widget"""
        return self.top_frame.get_playlist_widget()

    def set_progress(self, pos: float) -> None:
        """Sets the play position based on changes on slider."""
        pygame.mixer.music.play(start=pos)  # plays the song from new position
        self.my_buttons.seek_position = pos  # saves the seek position inside our buttons class


class Menus(tk.Menu):
    """A class that creates and manages the Menu bar."""

    def __init__(self, parent, playlist_widget, songs_dictionary):
        super().__init__(parent)
        self.play_list_widget = playlist_widget  # A reference to our playlist widget.
        self.songs_dictionary = songs_dictionary  # A reference to our song's dictionary.

        # Adding the menu bar to our main window.
        parent.configure(menu=self)

        # Creating the 'add songs' menu on our menu bar.
        self.add_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(menu=self.add_menu, label='Add songs')

        # adding commands to the 'add songs' menu.
        self.add_menu.add_command(label='Add One song to the playlist',
                                  command=self.add_one_song)
        self.add_menu.add_command(label='Add many songs to the playlist',
                                  command=self.add_multiple_songs)

        # Creating the 'Remove songs' menu on our menu bar.
        self.remove_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(menu=self.remove_menu, label='Remove Songs')

        # adding commands to the 'Remove songs' menu.
        self.remove_menu.add_command(label='Delete a song from playlist',
                                     command=self.delete_one_song)
        self.remove_menu.add_command(label='Delete all songs from playlist',
                                     command=self.delete_all_songs)

    def add_one_song(self):
        """Prompts user to select a single song"""
        song = filedialog.askopenfilename(title='Add song',
                                          filetypes=(('mp3 files', '*.mp3'), ('All files', '*.*'))
                                          )
        self._song_importer(song)  # passes the selected song to the importer function.

    def add_multiple_songs(self):
        """Prompts user to select a various number of songs"""
        songs = filedialog.askopenfilenames(title='Add songs',
                                            filetypes=(('mp3 files', '*.mp3'), ('All files', '*.*')))

        # Iterates the tuple of songs and passes each to our importer function.
        for song in songs:
            self._song_importer(song)

    def _song_importer(self, song: str) -> None:
        """A helper function that adds songs to our playlist and updates the dictionary."""
        song_path = Path(song)
        song_name = song_path.stem  # gets the song's title.

        # checks our dictionary to avoid adding duplicates
        if song_path not in self.songs_dictionary.values():
            self.songs_dictionary[song_name] = song_path  # adds to our dictionary
            self.play_list_widget.insert('end', song_name)  # adds to our playlist widget
            # Serves for display purposes.

    def delete_one_song(self):
        """Removes the selected song from both of our playlist and our dictionary."""
        selected_index = self.play_list_widget.curselection()[0]  # Index of selected song in playlist
        selected_name = self.play_list_widget.get(selected_index)  # Title of selected song in playlist

        # Doing the deletions
        self.play_list_widget.delete(selected_index)
        self.songs_dictionary.pop(selected_name)

    def delete_all_songs(self):
        """Clears our playlist and dictionary."""
        self.play_list_widget.delete(0, 'end')
        self.songs_dictionary.clear()


class TopFrame(ctk.CTkFrame):
    """The frame that contains our playlist widget and volume bar"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # creating our playlist widget
        self.song_list = tk.Listbox(self,
                                    bg='black',
                                    fg='green',
                                    selectbackground='green',
                                    selectforeground='black',
                                    )
        self.song_list.pack(side='left', expand=True, fill='both', padx=20)

        # volume bar's frame
        self.volume_frame = ctk.CTkScrollableFrame(self, label_text='Volume', width=80, fg_color='transparent')
        self.volume_frame._scrollbar.grid_forget()  # hiding the scroll bar of our frame.
        self.volume_frame.pack(side='left')

        # volume slider
        self.volume_slider = ctk.CTkSlider(self.volume_frame,
                                           orientation='vertical',
                                           command=lambda e: volume_func(e)  # calls the function to change audio level
                                           )
        self.volume_slider.set(0.3)  # setting the starting volume
        self.volume_slider.pack()

    def get_playlist_widget(self):
        """Returns the reference to playlist widget"""
        return self.song_list


class ButtonsFrame(ctk.CTkFrame):
    """A frame that contains all our player buttons and their related functions."""

    def __init__(self, parent, main_app: App, **kwargs):
        super().__init__(parent, **kwargs)

        self.id = None
        self.song_path = None
        self.song_name = None
        self.song_index = None
        self.play_list_widget = main_app.get_playlist_widget()  # A reference to our playlist widget.
        self.song_dictionary = main_app.get_song_dictionary()  # A reference to our song dictionary.
        self.main_app = main_app
        self.playing = False  # Music player status
        self.seek_position = 0
        # Binding double click to the playlist widget
        self.play_list_widget.bind('<Double-Button-1>', lambda e: self.play())

        # Back Button
        self.back_button_image = ctk.CTkImage(light_image=PIL.Image.open('assets\\left-arrows.png'), size=(50, 50))
        self.back_button = ctk.CTkButton(self,
                                         image=self.back_button_image,
                                         text='',
                                         width=50,
                                         height=50,
                                         fg_color='transparent',
                                         hover=True,
                                         command=self.back)
        # Forward Button
        self.forward_button_image = ctk.CTkImage(light_image=PIL.Image.open('assets\\next.png'), size=(50, 50))
        self.forward_button = ctk.CTkButton(self,
                                            image=self.forward_button_image,
                                            text='',
                                            width=50,
                                            height=50,
                                            fg_color='transparent',
                                            hover=True,
                                            command=self.next_)
        # Play button
        self.play_button_image = ctk.CTkImage(light_image=PIL.Image.open('assets\\play-button.png'), size=(50, 50))
        self.play_button = ctk.CTkButton(self,
                                         image=self.play_button_image,
                                         text='',
                                         width=50,
                                         height=50,
                                         fg_color='transparent',
                                         hover_color='green',
                                         hover=True,
                                         command=self.play)
        # Pause button
        self.pause_button_image = ctk.CTkImage(light_image=PIL.Image.open('assets\\pause.png'), size=(50, 50))
        self.pause_button = ctk.CTkButton(self,
                                          image=self.pause_button_image,
                                          text='',
                                          width=50,
                                          height=50,
                                          fg_color='transparent',
                                          hover=True,
                                          command=self.pause)
        # Stop button
        self.stop_button_image = ctk.CTkImage(light_image=PIL.Image.open('assets\\stop-button.png'), size=(50, 50))
        self.stop_button = ctk.CTkButton(self,
                                         image=self.stop_button_image,
                                         text='',
                                         width=50,
                                         height=50,
                                         fg_color='transparent',
                                         hover_color='red',
                                         hover=True,
                                         command=self.stop,
                                         )
        self.back_button.grid(row=0, column=0)
        self.forward_button.grid(row=0, column=1)
        self.play_button.grid(row=0, column=2)
        self.pause_button.grid(row=0, column=3)
        self.stop_button.grid(row=0, column=4)

    def play(self):
        """Starts playing music."""
        self.seek_position = 0  # Reset seek position when a new song starts
        self.song_index = self.play_list_widget.curselection()[0]  # gets the index of selected song
        self.song_name = self.play_list_widget.get(self.song_index)  # gets the title of selected song
        self.song_path = self.main_app.get_song_dictionary()[
            self.song_name]  # gets the path to the song on file system from dictionary

        # load and start playing the song
        pygame.mixer.music.load(self.song_path)
        pygame.mixer.music.play()

        self.playing = True  # change the status to True
        self._get_song_duration()

        self.monitor_song_end()

    def stop(self):
        """Stops the playback and resets the position."""
        pygame.mixer.music.stop()
        # clearing the selected song
        self.play_list_widget.selection_clear(self.song_index)
        if self.id:  # If a loop exists
            self.after_cancel(self.id)  # stops the loop
        # clears the text in status bar
        self.main_app.status_bar.config(text='')
        self.main_app.progress_slide.set(0)  # reset the song progress bar

    def pause(self):
        """Pause and unpauses the song."""
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
        else:
            pygame.mixer.music.unpause()
            self.playing = True
            self.update_label()  # start updating the label

    def next_(self):
        """Plays the next song in the playlist."""
        # Deciding if it should go to next song or start from beginning if it reached the end
        new_song_index = self.song_index + 1 if self.song_index < len(self.song_dictionary) - 1 else 0

        self.play_list_widget.selection_set(new_song_index)  # selects the next song
        self.play_list_widget.activate(new_song_index)  # activates the song
        self.play_list_widget.selection_clear(self.song_index)  # unselect the last song
        self.play()  # starts playing

    def back(self):
        """Plays the song before in the playlist."""
        # Deciding if it should go to song before or goes to the end of playlist
        new_song_index = self.song_index - 1 if self.song_index else 'end'

        self.play_list_widget.selection_set(new_song_index)
        self.play_list_widget.activate(new_song_index)
        self.play_list_widget.selection_clear(self.song_index)
        self.play()

    def _get_song_duration(self):
        """Gets the length of the current song"""
        current_song_total_seconds = int(MP3(self.song_path).info.length)
        # formatting the song duration to a human-readable format
        self.current_song_duration_formatted = _format_seconds(current_song_total_seconds)
        # setting the upper edge of our song slider the current song's length
        self.main_app.progress_slide.configure(to=current_song_total_seconds)

        # update the text in status bar
        self.update_label()

    def update_label(self):
        """Updates the info on status bar"""
        if self.playing:  # if any song is playing
            # calculate the current position in the song by considering our seek position
            current_song_position = int(pygame.mixer.music.get_pos() / 1000) + int(self.seek_position)
            # formatting the current song position to a human-readable format
            pos_text = _format_seconds(current_song_position)
            # updating the text
            self.main_app.status_bar.config(
                text=f'Time Elapsed: {pos_text} of {self.current_song_duration_formatted}  ')
            # updating the progress bar position
            self.main_app.progress_slide.set(current_song_position)
            # running the `update_label` again and storing its ID for later use
            self.id = self.after(300, self.update_label)

    def monitor_song_end(self):
        """
        Periodically checks if the song has finished playing. If the song is no longer playing,
        and it was supposed to be playing (i.e., hasn't been paused or stopped manually),
        it calls the stop method to reset the player. This method schedules itself to run
        every 400 milliseconds to continuously monitor the song playback status.
        """

        if not pygame.mixer.music.get_busy() and self.playing:
            self.next_()
        else:
            self.after(400, self.monitor_song_end)


app = App()
app.mainloop()
