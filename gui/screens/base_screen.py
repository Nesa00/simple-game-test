"""Base Screen Class."""

import pygame


class BaseScreen:
    """Base class for all game screens/menus."""
    
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.buttons = []
        self.inputs = []
        self.labels = []
    
    def add_button(self, button):
        """Add a button to this screen."""
        self.buttons.append(button)
    
    def add_input(self, input_field):
        """Add an input field to this screen."""
        self.inputs.append(input_field)
    
    def add_label(self, label):
        """Add a label to this screen."""
        self.labels.append(label)
    
    def handle_event(self, event):
        """Handle input events."""
        for button in self.buttons:
            button.handle_event(event)
        for input_field in self.inputs:
            input_field.handle_event(event)
        for label in self.labels:
            label.handle_event(event)
    
    def update(self, dt):
        """Update screen logic."""
        for input_field in self.inputs:
            input_field.update(dt)
    
    def draw(self):
        """Draw the screen."""
        self.screen.fill(self.config.bg_color)
        
        theme = {
            'button_color': self.config.button_color,
            'button_hover': self.config.button_hover,
            'text_color': self.config.text_color,
            'input_border': self.config.input_border,
            'input_active': self.config.input_active,
            'label_color': self.config.label_color,
            'button_disabled': self.config.button_disabled
        }
        
        for label in self.labels:
            label.draw(self.screen, theme)
        for button in self.buttons:
            button.draw(self.screen, theme)
        for input_field in self.inputs:
            input_field.draw(self.screen, theme)
        
        # pygame.display.flip()
    
    def on_enter(self):
        """Called when entering this screen."""
        pass
    
    def on_exit(self):
        """Called when leaving this screen."""
        pass
