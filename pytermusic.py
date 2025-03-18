import os
from app.application import MP3Player
import time
import curses
import mutagen
from mutagen.mp3 import MP3
import pygame
import random

def format_time(seconds):
    """Format seconds into mm:ss format"""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

def main(stdscr):
    curses.curs_set(0)  # Hide cursor

    # Color variables
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)

    green = curses.color_pair(1)
    cyan = curses.color_pair(2)
    yellow = curses.color_pair(3)
    blue = curses.color_pair(4)
    red = curses.color_pair(5)

    # Optimizations
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
    info_height = height - 23
    info_width = 60
    list_width = width - record_width - info_width
    queue_height = height - info_height
    
    # Create windows
    record_win = curses.newwin(record_height, record_width, 1, 2)
    info_win = curses.newwin(info_height, info_width, 2, record_width + 4)
    queue_win = curses.newwin(queue_height - 4, info_width + record_width + 2, info_height + 2, 2)
    list_win = curses.newwin(height - 4, list_width - 8, 2, record_width + info_width + 6)
    
    # Current selected song in the list
    selected_index = 0
    list_offset = 0
    max_list_display = height - 6

    # Current selected song in queue
    q_selected_index = 0   
    q_list_offset = 0
    q_max_list_display = queue_height - 6

    current_volume = player.current_volume
    volume_up = player.volume_up()
    volume_down = player.volume_down()

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
        
        # Exception if file does not have mp3 tags
        try:
            current_song = player.get_current_song_info()
            info_win.addstr(2, 2, f"{str(current_song["title"])[2:-2]}", curses.A_BOLD)
            info_win.addstr(4, 2, f"Ablum: {str(current_song["album"])[2:-2]}", yellow)
            info_win.addstr(5, 2, f"Artist: {str(current_song["artist"])[2:-2]}", yellow)
        except KeyError:
            current_song = player.get_default_current_song_info()
            info_win.addstr(2, 2, f"{str(current_song)}", curses.A_BOLD)
            info_win.addstr(4, 2, f"Ablum: N/A", yellow)
            info_win.addstr(5, 2, f"Artist: N/A", yellow)

        if player.is_playing:
            info_win.addstr(7, 2, status, green)
        elif player.paused:
            info_win.addstr(7, 2, status, yellow)
        else:
            info_win.addstr(7, 2, status, red)
 
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

        # Volume
        info_win.addstr(13, 2, f"Volume: {current_volume}%", cyan)
        
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
            try:
                song_name = mutagen.File(player.songs[idx], easy=True)
                song_name = str(song_name["title"])[2:-2]
            except KeyError:
                song_name = os.path.basename(player.songs[idx])
                song_name = song_name.strip(".mp3")
                song_name = song_name[:45]
            
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

        # Draw Queue
        queue_win.clear()
        queue_win.box()
        queue_win.addstr(0, 2, f"Queue ({len(player.queue)})", curses.A_BOLD)

        # Calculate queue display
        if q_selected_index >= q_list_offset + q_max_list_display:
            q_list_offset = q_selected_index - q_max_list_display + 1
        elif q_selected_index < q_list_offset:
            q_list_offset = q_selected_index

        # Display queue
        for i in range(min(q_max_list_display, len(player.queue) - q_list_offset)):
            q_idx = i + q_list_offset
            q_current_idx = player.queue[q_idx]

            try:
                song_name = mutagen.File(player.songs[q_current_idx], easy=True)
                song_name = str(song_name["title"])[2:-2]
            except KeyError:
                song_name = os.path.basename(player.songs[q_current_idx])
                song_name = song_name.strip(".mp3")

            # Allow selection in edit mode
            if command_mode == False:
                
                # Highlight queue song if selected
                if q_current_idx == player.current_song_index and q_idx == q_selected_index:
                    queue_win.addstr(i + 1, 2, f"> {song_name}", curses.color_pair(1) | curses.A_BOLD)
                elif q_current_idx == player.current_song_index:
                    queue_win.addstr(i + 1, 2, f"* {song_name}", curses.color_pair(1))
                elif q_idx == q_selected_index:
                    queue_win.addstr(i + 1, 2, f"> {song_name}", curses.A_BOLD)
                else: queue_win.addstr(i + 1, 2, f"{q_idx+1}. {song_name}")

            else:
                queue_win.addstr(i + 1, 2, f"{q_idx+1}. {song_name}")

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
            elif key == ord('l'):
                player.volume_up()
                current_volume = player.current_volume
            elif key == ord('h'):
                player.volume_down()
                current_volume = player.current_volume
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
            elif key == ord('c'):
                player.queue.clear()
            elif key == ord('i'):
                command_mode = False
            elif key == ord('?'):
                # Display help
                help_win = curses.newwin(20, 50, height // 2 - 8, width // 2 - 25)
                help_win.clear()
                help_win.box()
                help_win.addstr(0, 20, "HELP", curses.A_BOLD)
                
                help_lines = [
                    "j/k         - Move down/up",
                    "g/G         - Go to first/last song",
                    "Enter/Space - Play selected",
                    "p           - Pause/Resume",
                    "s           - Stop playback",
                    "n           - Next song",
                    "b           - Previous song",
                    "shift + s   - Shuffle song list",
                    "1           - Sort song list",
                    "c           - Clear queue",
                    "i           - Enter queue edit mode",
                    " While in edit mode ",
                    "r           - Remove selected song from queue",
                    "q           - Quit program",
                    "?           - Show this help"
                ]
                
                for i, line in enumerate(help_lines):
                    help_win.addstr(i + 2, 2, line)
                    
                help_win.addstr(17, 2, "Press any key to close")
                help_win.refresh()
                help_win.getch()
        else:  # queue edit mode
            if key == 27:  # ESC key
                command_mode = True
            elif key == ord('q'):
                running = False
            elif key == ord('j'):
                q_selected_index = min(q_selected_index + 1, len(player.queue) - 1)
            elif key == ord('k'):
                q_selected_index = max(q_selected_index - 1, 0)
            elif key == ord('\n') or key == ord(' '):
                player.current_song_index = player.queue[q_selected_index]
                player.play()
            elif key == ord('r'):
                player.queue.pop(q_selected_index)
            elif key == ord('c'):
                player.queue.clear()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    # Display info for window size error
    except curses.error as e:
        print("\nTerminal is too small\n")
        print("Try launching again in a larger window size\n")
    finally:
        # Clean up pygame
        pygame.mixer.quit()
        print("Pytermusic closed.")
