"""Dash Dash - Main Entry Point"""
import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources.*")
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import sys
from library.config_manager import ConfigManager
from gui.screens.main_menu import MainMenu
from gui.screens.settings_menu import SettingsMenu
from gui.screens.multiplayer_menu import MultiplayerMenu
from gui.screens.game_screen import GameScreen


class Game:
    """Main game application."""
    
    def __init__(self):
        pygame.init()
        self.config = ConfigManager()
        self.screen = pygame.display.set_mode(self.config.resolution)
        pygame.display.set_caption(f"{self.config.get('game.name')} v{self.config.get('game.version')}")
        self.running = True
        self.clock = pygame.time.Clock()
        self.current_screen = None
        self.screens = {}
        
        # Store network client and game state
        self.network_client = None
        self.is_host = False
        
        self._init_screens()
        self._change_screen('main_menu')
    
    def _init_screens(self):
        """Initialize all game screens."""
        main_callbacks = {
            'main_menu': lambda: self._change_screen('main_menu'),
            'singleplayer': self._start_singleplayer,
            'multiplayer': lambda: self._change_screen('multiplayer'),
            'settings': lambda: self._change_screen('settings'),
            'quit': self._quit_game
        }
        
        self.screens['main_menu'] = MainMenu(self.screen, self.config, main_callbacks)
        self.screens['settings'] = SettingsMenu(self.screen, self.config, main_callbacks)
        
        # Multiplayer menu with start_game callback
        multiplayer_callbacks = {
            'main_menu': lambda: self._change_screen('main_menu'),
            'start_game': self._start_multiplayer_game
        }
        self.screens['multiplayer'] = MultiplayerMenu(self.screen, self.config, multiplayer_callbacks)
    
    def _change_screen(self, screen_name):
        """Switch to a different screen."""
        if screen_name not in self.screens:
            print(f"Warning: Screen '{screen_name}' not found!")
            return
        
        if self.current_screen:
            self.current_screen.on_exit()
        
        self.current_screen = self.screens[screen_name]
        self.current_screen.on_enter()
        
        print(f"Switched to screen: {screen_name}")
    
    def _start_singleplayer(self):
        """Start a singleplayer game."""
        print("Starting Singleplayer...")
        print(f"Speed: {self.config.singleplayer_speed}, Username: {self.config.username}")
        # TODO: Implement singleplayer game
    
    def _start_multiplayer_game(self, client, is_host):
        """
        Start multiplayer game.
        
        Args:
            client: NetworkClient instance (already connected)
            is_host: bool, True if hosting
        """
        print(f"Starting multiplayer game (host={is_host})...")
        
        # Store client reference
        self.network_client = client
        self.is_host = is_host
        
        # Create game screen
        game_screen = GameScreen(
            self.screen,
            self.config,
            client,
            is_host,
            lambda: self._exit_multiplayer_game()
        )
        
        # Add to screens and switch to it
        self.screens['game'] = game_screen
        self._change_screen('game')
    
    def _exit_multiplayer_game(self):
        """Exit multiplayer game and return to multiplayer menu."""
        print("Exiting multiplayer game...")
        
        # Remove game screen
        if 'game' in self.screens:
            del self.screens['game']
        
        # Return to multiplayer menu (still connected)
        self._change_screen('multiplayer')
    
    def _quit_game(self):
        """Exit the game."""
        print("Quitting game...")
        self.running = False
    
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.current_screen:
                    self.current_screen.handle_event(event)
            
            if self.current_screen:
                self.current_screen.update(dt)
                self.current_screen.draw()
        
        # Cleanup
        if self.network_client and self.network_client.is_connected():
            self.network_client.disconnect()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
