"""Label UI Element."""

import pygame


class Label:
    """A non-interactive text label."""
    
    def __init__(self, text, rect, font_size=24):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = pygame.font.SysFont(None, font_size)
    
    def draw(self, surface, theme):
        """Draw the label."""
        # Draw background
        color = theme.get('label_color', (100, 100, 100))
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        
        # Draw text
        text_surf = self.font.render(self.text, True, theme.get('text_color', (255, 255, 255)))
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))
    
    def handle_event(self, event):
        """Labels don't handle events."""
        pass


class Label2:
    """A non-interactive text label."""
    
    def __init__(self, text, rect):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = pygame.font.SysFont(None, 18)
    
    def draw(self, surface, theme):
        """Draw the label."""
        # Draw background
        color = theme.get('label_color', (100, 100, 100))
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
    
        text_surf = self.font.render(
            f"Server: {self.config.server_ip}:{self.config.server_port}",
            True,
            (150, 150, 150)
        )
        surface.blit(text_surf, (10, self.config.resolution[1] - 30))
    
    def handle_event(self, event):
        """Labels don't handle events."""
        pass

