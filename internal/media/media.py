import os
import random
import pygame

class MediaManager:
    def __init__(self, image_dir, music_dir):
        pygame.mixer.init()
        self.image_dir = image_dir
        self.music_dir = music_dir
        self.images = self.load_images()
        self.current_image_index = 0
        self.load_music()

    def load_images(self):
        images = []
        if os.path.isdir(self.image_dir):
            for file in os.listdir(self.image_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    images.append(os.path.join(self.image_dir, file))
        return images if images else ["assets/images/default.jpg"]

    def load_music(self):
        self.music_files = []
        if os.path.isdir(self.music_dir):
            for file in os.listdir(self.music_dir):
                if file.lower().endswith('.mp3'):
                    self.music_files.append(os.path.join(self.music_dir, file))
        if self.music_files:
            pygame.mixer.music.load(self.music_files[0])
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)

    def get_current_image(self):
        return self.images[self.current_image_index] if self.images else "assets/images/default.jpg"

    def next_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)

    #def play_alarm(self):
        #pygame.mixer.music.load("assets/alarm.mp3")
        #pygame.mixer.music.play(1)

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume / 100.0)

    def toggle_mute(self, is_muted):
        if is_muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(0.5)  # Восстановить громкость