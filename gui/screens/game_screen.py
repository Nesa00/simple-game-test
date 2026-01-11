"""
Game Screen
The actual gameplay screen where players move around.
"""

import pygame
from gui.screens.base_screen import BaseScreen


class GameScreen(BaseScreen):
    """Main game screen with multiplayer support."""
    
    PLAYER_SIZE = 40
    PLAYER_SPEED = 5
    
    def __init__(self, screen, config, client, is_host, back_callback):
        """
        Initialize game screen.
        
        Args:
            screen: pygame display surface
            config: ConfigManager instance
            client: NetworkClient instance
            is_host: bool, True if this player is hosting
            back_callback: Function to call when exiting
        """
        super().__init__(screen, config)
        self.client = client
        self.is_host = is_host
        self.back_callback = back_callback
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 36, bold=True)
    
    def handle_event(self, event):
        """Handle input events."""
        super().handle_event(event)
        
        # ESC to exit game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._exit_game()
    
    def update(self, dt):
        """Update game logic."""
        super().update(dt)
        
        # Check if still connected
        if not self.client.is_connected():
            print("Connection lost during game!")
            self._exit_game()
            return
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        input_state = {
            "w": keys[pygame.K_w],
            "s": keys[pygame.K_s],
            "a": keys[pygame.K_a],
            "d": keys[pygame.K_d],
        }
        
        # Send input to server
        self.client.send_input(input_state)
    
    def draw(self):
        """Draw the game."""
        # Fill background
        self.screen.fill((30, 30, 30))
        
        # Get all players from server
        players = self.client.get_players()
        
        # Draw all players
        for player_id, player_data in players.items():
            x = player_data.get("x", 0)
            y = player_data.get("y", 0)
            name = player_data.get("name", f"Player{player_id}")
            
            # Determine color (own player is blue, others are orange)
            is_self = (name == self.config.username)
            color = (0, 200, 255) if is_self else (200, 100, 50)
            
            # Draw player rectangle
            pygame.draw.rect(
                self.screen,
                color,
                (x, y, self.PLAYER_SIZE, self.PLAYER_SIZE)
            )
            
            # Draw player name above rectangle
            name_surface = self.font.render(name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(
                center=(x + self.PLAYER_SIZE // 2, y - 10)
            )
            self.screen.blit(name_surface, name_rect)
        
        # Draw UI overlay
        self._draw_ui(players)
        
        pygame.display.flip()
    
    def _draw_ui(self, players):
        """Draw UI elements on top of game."""
        # Draw title
        role_text = "HOST" if self.is_host else "CLIENT"
        title = self.title_font.render(f"DASH DASH - {role_text}", True, (255, 255, 255))
        self.screen.blit(title, (10, 10))
        
        # Draw player count
        count_text = self.font.render(
            f"Players: {len(players)}",
            True,
            (200, 200, 200)
        )
        self.screen.blit(count_text, (10, 50))
        
        # Draw controls hint
        controls_text = self.font.render(
            "Controls: WASD to move | ESC to exit",
            True,
            (150, 150, 150)
        )
        controls_rect = controls_text.get_rect(
            centerx=self.config.resolution[0] // 2,
            bottom=self.config.resolution[1] - 10
        )
        self.screen.blit(controls_text, controls_rect)
    
    def _exit_game(self):
        """Exit the game and return to menu."""
        print("Exiting game...")
        
        # Note: We don't disconnect here, just go back to multiplayer menu
        # The multiplayer menu will handle disconnection if needed
        
        if self.back_callback:
            self.back_callback()
    
    def on_exit(self):
        """Called when leaving this screen."""
        print("Game screen exited")
