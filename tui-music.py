import os
import subprocess
import fnmatch
import time
import threading
import curses
import glob
import mutagen
from mutagen.mp3 import MP3
import pygame
import random

class MP3Player:
    def __init__(self, music_dir):
        self.music_dir = music_dir
        self.songs = []
        self.queue = []
        self.current_song_index = 0
        self.queue_index = 0
        self.is_playing = False
        self.paused = False
        self.scan_songs()
        pygame.mixer.init()
        self.record_frames = self.create_record_frames()
        self.current_frame = 0
        self.song_position = 0
        self.song_length = 0
        
    def scan_songs(self):
        """Scan the music directory for MP3 files"""
        self.songs = glob.glob(os.path.join(self.music_dir, "**/*.mp3"))
        self.songs.sort()

    def shuffle(self):
        random.shuffle(self.songs)
        pygame.mixer.music.load(self.songs[self.current_song_index])
        pygame.mixer.music.play()
        self.song_length = MP3(self.songs[self.current_song_index]).info.length
        self.is_playing = True
        if self.is_playing:
            self.song_position = pygame.mixer.music.get_pos() / 1000
            
            # Check if song ended
            if not pygame.mixer.music.get_busy() and self.is_playing:
                self.stop()
                self.current_song_index = (self.current_song_index + 1) % len(self.songs)
                self.play()

    def addsong(self, song_index):
        if 0 <= song_index < len(self.songs):
            self.queue.append(song_index)
            return True
        return False

    def sort(self):
        self.songs.sort()

    def play(self):
        """Start playing the current song"""
        if not self.songs:
            return
        
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        pygame.mixer.music.load(self.songs[self.current_song_index])
        self.songtitle = mutagen.File(self.songs[self.current_song_index], easy=True)
        self.songartist = str(self.songtitle["artist"])[2:-2]
        self.songtitle = str(self.songtitle["title"])[2:-2]
        os.system(f'notify-send "󰎇 Now Playing:" "{self.songtitle} \n by {self.songartist}" -t 2000')
        pygame.mixer.music.play()
        self.song_length = MP3(self.songs[self.current_song_index]).info.length
            
        self.is_playing = True
        
    def pause(self):
        """Pause the current song"""
        if self.is_playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.is_playing = False
        elif self.paused:
            self.play()
            
    def stop(self):
        """Stop the current song"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.paused = False
        
    def next_song(self):
        """Play the next song"""
        if not self.songs:
            return
        self.stop()
        if self.queue:
            self.current_song_index = self.queue.pop(0)
        else:
            self.current_song_index = (self.current_song_index + 1) % len(self.songs)
        self.play()
        
    def prev_song(self):
        """Play the previous song"""
        if not self.songs:
            return
            
        self.stop()
        self.current_song_index = (self.current_song_index - 1) % len(self.songs)
        self.play()
        
    def get_current_song_info(self):
        """Get the current song filename"""
        if not self.songs:
            return "No songs available"
            
        #return os.path.basename(self.songs[self.current_song_index])
        self.songtitle = mutagen.File(self.songs[self.current_song_index], easy=True)
        return self.songtitle
        
    def update_position(self):
        """Update the current song position"""
        if self.is_playing:
            self.song_position = pygame.mixer.music.get_pos() / 1000
            
            # Check if song ended
            if not pygame.mixer.music.get_busy() and self.is_playing:
                self.next_song()
                
    def create_record_frames(self):
        """Create frames for the spinning record animation"""
        frames = []
        
        # Frame 1
        frames.append([
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣀⣀⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣠⣴⢶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣦⣤⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣠⡴⠞⠋⠁⡀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⢀⣴⠞⠁⡀⡀⡀⢀⣀⠤⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⣴⠟⠁⡀⡀⡀⡠⠖⠉⡀⠄⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⢠⠞⠁⡀⡀⢀⡴⠋⡀⡀⡀⡀⡀⣄⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⣰⠏⡀⡀⡀⣠⠊⡀⡀⡀⡀⢀⡴⠞⠿⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡀⡀⡀⡀⡀",
            "⡀⡀⡀⢠⠏⡀⡀⡀⡼⠁⡀⡀⡀⢀⡴⠋⢀⡀⢚⣽⣿⣿⡿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⢀⡀⡀⡀",
            "⡀⡀⢀⣿⣄⣄⡀⣼⠁⡀⡀⢠⣠⡟⡀⡀⢫⣶⠟⠉⡀⡀⡀⡀⡀⡀⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⣿⡄⡀⡀",
            "⡀⡀⢸⣿⣿⣿⣿⣿⣾⣶⣦⣴⣏⣻⣾⣴⡟⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⣰⣿⣧⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⣼⣿⣿⣿⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣿⣿⣿⣿⣿⣿⣿⡟⢁⣾⣿⣿⣿⣿⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣿⣿⣿⣿⣿⣿⠟⢀⣾⣿⣿⣿⣿⣿⡀⡀",
            "⡀⡀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣰⣿⢿⣿⠿⠋⡀⡀⢿⣿⣿⣿⣿⣿⡿⡀⡀",
            "⡀⡀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣠⣾⡿⠁⠉⠙⡀⡀⡀⡀⠉⠙⠛⠻⠿⢿⠇⡀⡀",
            "⡀⡀⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣄⣀⣀⣀⣤⣴⣾⠟⠉⠛⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣏⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡐⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡩⡐⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠈⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⡀⡀⡀⡀⡀⡀⡀⢀⠔⠁⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⡀⡀⡀⡀⢀⠠⠂⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠉⠛⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣀⠠⠔⠊⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⠉⠙⠛⠛⠛⠛⠛⠛⠛⠛⠉⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀"
        ])
        
        # Frame 2
        frames.append([
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣀⣀⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣠⣴⠶⠒⠛⠉⠉⠉⠉⠉⠉⠉⠙⠓⠲⠦⣤⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣠⣴⡞⠉⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣿⣿⣶⣄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⢀⣴⣾⣿⣿⣿⣄⡀⣀⡤⠖⠂⡀⡀⠈⠁⡀⡀⡀⡀⠐⡀⢀⣾⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⣴⣿⣿⣿⣿⣿⣿⣿⣏⡀⠠⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠂⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⣄⣂⡤⠤⠒⠒⠒⠂⢠⠔⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣝⣟⡀⡀⡀⡤⡀⢀⣬⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡀⡀⡀⡀⡀",
            "⡀⡀⡀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⡾⠿⢶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⢀⡀⡀⡀",
            "⡀⡀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠉⡀⡀⡀⡀⡀⡀⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⣿⡄⡀⡀",
            "⡀⡀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⣰⣿⣧⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⣼⣿⣿⣿⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢹⣿⣿⣿⣿⣿⣿⡟⢁⣾⣿⣿⣿⣿⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣿⣿⣿⣿⣿⣿⠟⢠⣾⣿⣿⣿⣿⣿⡀⡀",
            "⡀⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣰⣿⣿⣿⣿⠋⠈⡀⣿⣿⣿⣿⣿⣿⣿⡀⡀",
            "⡀⡀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣠⣾⣿⣿⣿⡿⠁⡀⡀⣰⣿⣿⣿⣿⣿⣿⡇⡀⡀",
            "⡀⡀⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣄⣀⣀⣀⣤⣴⣾⣿⣿⣿⣿⣿⣷⣄⣀⣾⣿⣿⣿⣿⣿⣿⡿⡀⡀⡀",
            "⡀⡀⡀⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⠭⠉⢹⡋⠉⠭⢿⡻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⡀⡀⡀",
            "⡀⡀⡀⡀⡀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢵⣳⡀⡀⡀⡀⡀⡀⢚⡫⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⠈⠁⡀⡀⡀⡀⡀⡀⡀⡀⢀⠈⠿⣿⣿⣿⣿⣿⣿⣿⣿⠏⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣀⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠹⣿⣿⣿⣿⣿⠟⠁⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠙⠿⣿⣿⣿⡿⡀⡀⠈⠉⠐⠒⠂⡀⡀⠒⠒⡀⡀⡀⡀⡀⡀⠙⣿⠿⠋⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠉⠻⠤⣀⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣀⠤⠔⠊⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⠉⠑⠒⠒⠒⠂⠐⠒⠒⠒⠉⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀"
        ])
        
        # Frame 3
        frames.append([
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣀⣀⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣠⣴⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠓⠲⠦⣤⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⡀⡀⡀⡀⠈⠙⠲⢄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠐⠠⡀⡀⡀⡀⡀⡀⠙⠢⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⠢⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣯⠔⠢⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡟⠃⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⢿⣿⣿⣭⡁⢠⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣀⡀⢀⡀⡀⡀",
            "⡀⡀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠉⡀⡀⡀⡀⡀⡀⠈⠙⠻⣷⣄⠠⣀⣶⡀⢂⣀⣤⣤⣶⣿⣿⡀⣸⡄⡀⡀",
            "⡀⡀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⢻⣷⣿⣶⣿⣿⣿⣿⣿⣿⡿⠃⣰⣿⣧⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⣼⣿⣿⣿⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢹⣿⣿⣿⣿⣿⣿⡟⢁⣾⣿⣿⣿⣿⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣾⣿⣿⣿⣿⣿⠟⢠⣾⣿⣿⣿⣿⣿⡀⡀",
            "⡀⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣰⣿⣿⣿⣿⠋⡀⡀⣿⣿⣿⣿⣿⣿⣿⡀⡀",
            "⡀⡀⠸⣿⣿⣿⣿⣿⣿⣿⠿⠟⢿⣭⡿⠏⠻⣦⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣠⣾⣿⣿⣿⡿⠁⡀⡀⣰⣿⣿⣿⣿⣿⣿⡇⡀⡀",
            "⡀⡀⡀⢻⡿⠿⠛⠛⣇⡀⠠⡀⠃⠻⣄⡀⠐⣝⠛⢶⣤⣄⣀⣀⣀⣤⣴⣾⣿⣿⣿⣿⣿⣷⣄⣀⣾⣿⣿⣿⣿⣿⣿⡿⡀⡀⡀",
            "⡀⡀⡀⡀⢣⡀⡀⡀⠘⢧⡀⡀⡀⡀⠈⠳⣄⡀⡀⢰⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⡀⡀⡀",
            "⡀⡀⡀⡀⡀⠳⡀⡀⡀⡀⠳⣄⡀⡀⡀⡀⡀⠙⠲⣿⣩⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⠙⢆⡀⡀⡀⠈⠳⢄⡀⡀⡀⡀⠐⡀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⠑⢄⡀⡀⡀⡀⠉⠒⢤⣀⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠙⠦⣀⡀⡀⡀⡀⡀⠈⢩⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠋⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠉⠲⠤⣄⡀⡀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠋⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⠉⠙⠛⠛⠛⠛⠛⠛⠛⠛⠉⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀"
        ])
        
        # Frame 4
        frames.append([
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣀⣀⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣠⣴⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣦⣤⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠋⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⢀⡟⠛⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠉⡀⡀⡀⡀⡀⡀⠈⠙⠻⣿⣿⣿⣿⢟⡁⡀⡀⡀⡀⡀⡀⡀⡀⠈⠄⡀⡀",
            "⡀⡀⢸⠁⡀⡀⢸⠇⠙⠛⠿⢿⣿⣿⣿⣿⡟⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⢿⣿⠻⠋⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡟⡀⡀⡀⢿⡀⡀⡀⠂⣾⡾⣽⣿⡿⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣿⣇⢁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡇⡀⡀⡀⡇⡀⡀⡀⡀⡿⡀⠉⢸⡇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢹⣟⠈⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡇⡀⡀⡀⢰⡀⡀⡀⡀⣿⡀⠲⠸⣇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣾⣿⣰⣄⡤⢀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⢳⡀⡀⡀⢸⡀⡀⡀⡀⢸⡀⡀⣄⣿⡄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣰⣿⣿⣿⣶⠃⡀⡀⡀⡀⡀⡀⡀⡀⠘⡀⡀",
            "⡀⡀⠸⡄⡀⡀⡀⣧⡀⡀⡀⢀⢷⡶⣻⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣀⣼⣿⣿⣿⡿⠁⡀⡀⣰⣷⣦⣤⣀⡀⡀⠃⡀⡀",
            "⡀⡀⡀⢳⡀⡀⡀⠘⣆⡀⡀⢀⣴⣿⣿⣿⣿⣿⣿⣶⣤⣄⣀⣀⣀⣤⣴⣾⣿⣿⣿⣿⣿⣷⣄⣀⣾⣿⣿⣿⣿⣿⣿⡟⡀⡀⡀",
            "⡀⡀⡀⡀⢳⡀⡀⡀⠘⣧⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⡀⡀⡀",
            "⡀⡀⡀⡀⡀⠳⣄⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠁⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠙⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠋⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠙⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠋⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⠉⠙⠛⠛⠛⠛⠛⠛⠛⠛⠉⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀"
        ])
        
        # Frame 5
        frames.append([
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣀⣀⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣠⣴⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣦⣤⣀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣠⡴⢾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⢀⣴⠞⠉⡀⡀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡴⠋⡀⡀⡀⢀⣠⠞⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⢠⠞⠁⡀⡀⢀⡴⠋⡀⠂⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⣰⠏⡀⡀⡀⣠⠊⡀⡀⡀⡀⢲⣴⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡀⡀⡀⡀⡀",
            "⡀⡀⡀⢠⠃⡀⡀⡀⡼⠁⡀⡀⡀⢀⡴⠋⢉⣿⣿⣿⣿⣿⡿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⢀⡀⡀⡀",
            "⡀⡀⢀⡟⡀⡀⡀⣼⡀⡀⡀⡀⢠⠟⡀⣀⢀⣾⠟⠉⡀⡀⡀⡀⡀⡀⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⣿⡄⡀⡀",
            "⡀⡀⢸⠁⡀⡀⢸⠇⢀⡀⢀⢠⡏⡀⠈⢱⡟⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⣰⣿⣧⡀⡀",
            "⡀⡀⣿⣤⣤⣀⣼⣀⣀⣀⣈⣾⣛⣾⣦⡿⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⣼⣿⣿⣿⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢹⣿⣿⣿⣿⣿⣿⡟⢁⣾⣿⣿⣿⣿⡀⡀",
            "⡀⡀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣾⣿⣿⣿⠻⠿⠏⡀⠾⠿⠿⢿⣿⣿⡀⡀",
            "⡀⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⣰⣿⠃⠋⠙⠃⡀⡀⢀⡀⡀⡀⡀⡀⠈⡀⡀",
            "⡀⡀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⢀⣼⡟⠣⠆⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠇⡀⡀",
            "⡀⡀⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣄⣀⣀⣀⣤⣴⣾⣿⣯⡄⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠿⠂⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠈⢀⡀⡀⡀⡀⡀⡀⡀⡀⡐⠁⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⡀⡀⡀⡀⡀⡀⡀⡀⠌⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⡀⡀⡀⡀⣀⠔⠁⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⢀⠠⠊⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠙⠻⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠋⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⠉⠙⠛⠛⠛⠛⠛⠛⠛⠛⠉⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀"
        ])
        
        return frames
        
    def get_current_record_frame(self):
        """Get the current frame of the spinning record"""
        if self.is_playing:
            self.current_frame = (self.current_frame + 1) % len(self.record_frames)
            return self.record_frames[self.current_frame]
        else:
            return self.record_frames[0]

def format_time(seconds):
    """Format seconds into mm:ss format"""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Current song
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Playing status
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Record

    stdscr.nodelay(1)

    curses.cbreak

    # Turn on virtual screen
    stdscr.idlok(1)
    stdscr.scrollok(1)
    stdscr.leaveok(1)

    if hasattr(curses, 'use_default_colors'):
        curses.use_default_colors()


    
    # Get music directory from environment or use default
    music_dir = os.environ.get("MUSIC_DIR", os.path.expanduser("~/Music"))
    player = MP3Player(music_dir)
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Calculate window sizes and positions
    record_width = 48
    record_height = 26
    info_height = height - 32
    info_width = 80
    list_width = width - record_width - info_width
    queue_height = height - info_height
    
    # Create windows
    record_win = curses.newwin(record_height, record_width, 2, 2)
    info_win = curses.newwin(height - 32, info_width, 2, record_width + 4)
    queue_win = curses.newwin(queue_height - 2, info_width, info_height + 2, record_width + 4)
    list_win = curses.newwin(height - 4, list_width, 2, record_width + info_width + 6)
    
    # Current selected song in the list
    selected_index = 0
    qselected_index = 0
    list_offset = 0
    qlist_offset = 0
    max_list_display = height - 6
    qmax_list_display = queue_height - 6
    
    # Input mode
    command_mode = True
    
    # Main loop
    running = True
    while running:
        stdscr.addstr(0, 0, "MP3 Player - Press ? for help", curses.A_BOLD)
        
        # Update song position
        player.update_position()
        
        # Draw record
        record_win.clear()
        record_frame = player.get_current_record_frame()
        record_height, record_width = record_win.getmaxyx()
        for i, line in enumerate(record_frame):
            if i + 1 < record_height:
                display_line = line[:record_width-2]
                record_win.addstr(i + 1, 1, line, curses.color_pair(3))
            
        # Draw info
        info_win.clear()
        info_win.box()
        info_win.addstr(0, 2, "Now Playing:", curses.A_BOLD)
        
        current_song = player.get_current_song_info()
        status = "PLAYING" if player.is_playing else "PAUSED" if player.paused else "STOPPED"
        
        info_win.addstr(3, 2, f"Title: {str(current_song["title"])[2:-2]}", curses.color_pair(1))
        info_win.addstr(4, 2, f"Ablum: {str(current_song["album"])[2:-2]}", curses.color_pair(1))
        info_win.addstr(5, 2, f"Artist: {str(current_song["artist"])[2:-2]}", curses.color_pair(1))
        info_win.addstr(7, 2, f"Status: {status}", curses.color_pair(2))
        
        # Show position/duration
        if player.is_playing or player.paused:
            position_str = f"{format_time(player.song_position)} / {format_time(player.song_length)}"
            info_win.addstr(9, 2, position_str)
            
            # Progress bar
            progress_width = info_width - 8
            if player.song_length > 0:
                progress = int((player.song_position / player.song_length) * progress_width)
                progress_bar = "#" * progress + "-" * (progress_width - progress)
                info_win.addstr(11, 2, f"[{progress_bar}]")

        # Draw Queue
        queue_win.clear()
        queue_win.box()
        queue_win.addstr(0, 2, f"Queue ({len(player.queue)})", curses.A_BOLD)

        for i in range(min(qmax_list_display, len(player.queue) - qlist_offset)):
            if i >= len(player.queue):
                break
            qidx = i + qlist_offset
            qcurrent_idx = player.queue[i]
            song_name = mutagen.File(player.songs[qcurrent_idx], easy=True)
            song_name = str(song_name["title"])[2:-2]

            if command_mode == False:
                if qselected_index >= qlist_offset + qmax_list_display:
                    qlist_offset = qselected_index - qmax_list_display + 1
                elif qselected_index < qlist_offset:
                    qlist_offset = qselected_index
                if qidx == player.current_song_index and qidx == qselected_index:
                    queue_win.addstr(2 + i, 2, f"> {song_name}", curses.color_pair(1) | curses.A_BOLD)
                elif qidx == player.current_song_index:
                    queue_win.addstr(2 + i, 2, f"* {song_name}", curses.color_pair(1))
                elif qidx == qselected_index:
                    queue_win.addstr(2 + i, 2, f"> {song_name}", curses.A_BOLD)
                else: queue_win.addstr(2 + i, 2, f"{i+1}. {song_name}")
            else:
                queue_win.addstr(2 + i, 2, f"{i+1}. {song_name}")
        
        # Draw song list
        list_win.clear()
        list_win.box()
        list_win.addstr(0, 2, f"Songs ({len(player.songs)})", curses.A_BOLD)
        
        # Calculate which songs to display
        if selected_index >= list_offset + max_list_display:
            list_offset = selected_index - max_list_display + 1
        elif selected_index < list_offset:
            list_offset = selected_index
            
        # Display songs
        for i in range(min(max_list_display, len(player.songs) - list_offset)):
            idx = i + list_offset
            song_name = mutagen.File(player.songs[idx], easy=True)
            song_name = str(song_name["title"])[2:-2]
            
            if command_mode == True:
                # Highlight if current song or selected
                if idx == player.current_song_index and idx == selected_index:
                    list_win.addstr(i + 1, 2, f"> {song_name}", curses.color_pair(1) | curses.A_BOLD)
                elif idx == player.current_song_index:
                    list_win.addstr(i + 1, 2, f"* {song_name}", curses.color_pair(1))
                elif idx == selected_index:
                    list_win.addstr(i + 1, 2, f"> {song_name}", curses.A_BOLD)
                else:
                    list_win.addstr(i + 1, 2, f"  {song_name}")
            else:
                list_win.addstr(i + 1, 2, f"  {song_name}")

        mode_text = "NORMAL" if command_mode else "INSERT"
        stdscr.addstr(height - 1, 0, f" {mode_text} ", curses.A_REVERSE)

                
        # Refresh windows
        stdscr.noutrefresh()
        record_win.noutrefresh()
        info_win.noutrefresh()
        list_win.noutrefresh()
        queue_win.noutrefresh()

        curses.doupdate()
        
        # Handle input
        stdscr.timeout(200)  # Timeout for animation
        try:
            key = stdscr.getch()
        except:
            continue
            
        if key == -1:
            continue  # Timeout, just update the screen
            
        if command_mode:
            if key == ord('q'):
                running = False
            elif key == ord('j'):
                selected_index = min(selected_index + 1, len(player.songs) - 1)
            elif key == ord('k'):
                selected_index = max(selected_index - 1, 0)
            elif key == ord('g'):
                selected_index = 0
            elif key == ord('G'):
                selected_index = len(player.songs) - 1
            elif key == ord('\n') or key == ord(' '):
                player.current_song_index = selected_index
                player.play()
            elif key == ord('p'):
                player.pause()
            elif key == ord('s'):
                player.stop()
            elif key == ord('S'):
                player.shuffle()
            elif key == ord('n'):
                player.next_song()
                selected_index = player.current_song_index
            elif key == ord('b'):
                player.prev_song()
                selected_index = player.current_song_index
            elif key == ord('1'):
                player.sort()
            elif key == ord('a'):
                player.addsong(selected_index)
            elif key == ord('i'):
                command_mode = False
            elif key == ord('?'):
                # Display help
                help_win = curses.newwin(15, 50, height // 2 - 8, width // 2 - 25)
                help_win.clear()
                help_win.box()
                help_win.addstr(0, 20, "HELP", curses.A_BOLD)
                
                help_lines = [
                    "j/k   - Move down/up",
                    "g/G   - Go to first/last song",
                    "Enter/Space - Play selected",
                    "p     - Pause/Resume",
                    "s     - Stop playback",
                    "n     - Next song",
                    "b     - Previous song",
                    "i     - Enter queue edit mode",
                    "q     - Quit program",
                    "?     - Show this help"
                ]
                
                for i, line in enumerate(help_lines):
                    help_win.addstr(i + 2, 2, line)
                    
                help_win.addstr(13, 2, "Press any key to close")
                help_win.refresh()
                help_win.getch()
        else:  # queue edit mode
            if key == 27:  # ESC key
                command_mode = True
            elif key == ord('q'):
                running = False
            elif key == ord('j'):
                qselected_index = min(qselected_index + 1, len(player.queue) - 1)
            elif key == ord('k'):
                qselected_index = max(qselected_index - 1, 0)
            elif key == ord('\n') or key == ord(' '):
                player.current_song_index = qselected_index
                player.play()
            elif key == ord('r'):
                player.queue.pop(qselected_index)



if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up pygame
        pygame.mixer.quit()
        print("MP3 Player closed.")
