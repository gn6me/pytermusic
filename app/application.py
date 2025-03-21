import os
import random
import glob
import mutagen
from mutagen.mp3 import MP3
import pygame

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
        self.volume = 0.5
        pygame.mixer.music.set_volume(self.volume)
        self.current_volume = str(int(self.volume * 100))
        
    def scan_songs(self):
        """Scan the music directory for MP3 files"""
        self.songs = glob.glob(os.path.join(self.music_dir, "**/*.mp3"))
        self.songs.sort()

    def shuffle(self):
        """Shuffle song list"""
        random.shuffle(self.songs)
        pygame.mixer.music.load(self.songs[self.current_song_index])
        pygame.mixer.music.play()
        self.song_length = MP3(self.songs[self.current_song_index]).info.length
        self.is_playing = True
        if self.is_playing:
            self.song_position = pygame.mixer.music.get_pos() / 1000
            
    def addsong(self, song_index):
        """Add selected song to queue"""
        if 0 <= song_index < len(self.songs):
            self.queue.append(song_index)
            return True
        return False

    def sort(self):
        """Sort song list window"""
        self.songs.sort()

    def play(self):
        """Start playing the current song"""
        if not self.songs:
            return
        
        # Unpause function
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.is_playing = True
        else:
            pygame.mixer.music.load(self.songs[self.current_song_index])

            # Only pass is song has mp3 tags
            try:
                # Grab song info for notification daemon
                self.songtitle = mutagen.File(self.songs[self.current_song_index], easy=True)
                self.songartist = str(self.songtitle["artist"])[2:-2]
                self.songtitle = str(self.songtitle["title"])[2:-2]
                os.system(f'notify-send "󰎇 Now Playing:" "{self.songtitle} \n by {self.songartist}" -t 2000')
            except KeyError:
                pass

            # Play song
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
            
        self.songtitle = mutagen.File(self.songs[self.current_song_index], easy=True)
        
        return self.songtitle
    
    def get_default_current_song_info(self):
        """Get current song info if there are no tags"""
        self.songtitle = os.path.basename(self.songs[self.current_song_index])
        self.songtitle = self.songtitle.strip(".mp3")
        
        return self.songtitle

        
    def update_position(self):
        """Update the current song position"""
        if self.is_playing:
            self.song_position = pygame.mixer.music.get_pos() / 1000
            
            # Check if song ended
            if not pygame.mixer.music.get_busy() and self.is_playing:
                self.next_song()

    def get_volume(self):
        return self.current_volume

    def volume_up(self):
        if self.volume < 1.0:
            self.volume += 0.05
            pygame.mixer.music.set_volume(self.volume)
            self.current_volume = str(int(self.volume * 100))

    def volume_down(self):
        if self.volume > 0.05:
            self.volume -= 0.05
            pygame.mixer.music.set_volume(self.volume)
            self.current_volume = str(int(self.volume * 100))
                
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
            "⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⠈⠉⠑⠒⠒⠒⠂⠐⠒⠒⠒⠉⠁⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀⡀",
            "..............................................."
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
