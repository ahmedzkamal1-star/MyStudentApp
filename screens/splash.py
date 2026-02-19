# screens/splash.py - Splash screen with animations
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
import math

class AnimatedLogo(Image):
    """Custom animated logo with rotation and scaling"""
    angle = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animate()
    
    def animate(self):
        """Create smooth rotation animation"""
        anim = Animation(angle=360, duration=2, t='in_out_quad')
        anim += Animation(angle=0, duration=0)  # Reset without animation
        anim.repeat = True
        anim.start(self)

class SplashScreen(Screen):
    """Beautiful splash screen with animations"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_dots = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the splash screen UI"""
        layout = FloatLayout()
        
        # Create animated logo (you can replace with your actual logo)
        logo = AnimatedLogo(
            source='assets/logo.png' if self.has_logo() else '',
            size_hint=(0.3, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.6}
        )
        
        # If no logo file, create a text logo
        if not self.has_logo():
            from kivy.uix.label import Label
            logo = Label(
                text='🚀',
                font_size=dp(80),
                color=get_color_from_hex('#6C5CE7'),
                size_hint=(None, None),
                size=(dp(100), dp(100)),
                pos_hint={'center_x': 0.5, 'center_y': 0.6}
            )
        
        # App name with fade-in
        app_name = Label(
            text='My Mobile App',
            font_size=dp(28),
            bold=True,
            color=get_color_from_hex('#2D3436'),
            size_hint=(None, None),
            size=(dp(300), dp(50)),
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            opacity=0
        )
        
        # Loading text with animated dots
        self.loading_text = Label(
            text='Loading',
            font_size=dp(16),
            color=get_color_from_hex('#636E72'),
            size_hint=(None, None),
            size=(dp(200), dp(30)),
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
            opacity=0
        )
        
        # Version number
        version = Label(
            text='v1.0.0',
            font_size=dp(12),
            color=get_color_from_hex('#B2BEC3'),
            size_hint=(None, None),
            size=(dp(100), dp(20)),
            pos_hint={'center_x': 0.5, 'center_y': 0.1}
        )
        
        layout.add_widget(logo)
        layout.add_widget(app_name)
        layout.add_widget(self.loading_text)
        layout.add_widget(version)
        
        self.add_widget(layout)
        
        # Store references for animations
        self.logo = logo
        self.app_name = app_name
    
    def on_enter(self):
        """Called when screen enters"""
        self.start_animations()
    
    def start_animations(self):
        """Start all splash screen animations"""
        # Logo scale/size animation
        if self.logo.size_hint == [None, None] or self.logo.size_hint == (None, None):
            # Animate size if size_hint is disabled (for text logo)
            current_size = self.logo.size
            target_size = (current_size[0] * 1.2, current_size[1] * 1.2)
            anim = Animation(size=target_size, duration=0.5, t='out_elastic')
            anim += Animation(size=current_size, duration=0.5, t='out_elastic')
            anim.start(self.logo)
        else:
            # Animate size_hint if active (for image logo)
            anim = Animation(size_hint=(0.35, 0.35), duration=0.5, t='out_elastic')
            anim += Animation(size_hint=(0.3, 0.3), duration=0.5, t='out_elastic')
            anim.start(self.logo)
        
        # App name fade in with bounce
        anim = Animation(opacity=1, duration=0.8, t='out_quad')
        anim.start(self.app_name)
        
        # Loading text fade in
        anim = Animation(opacity=1, duration=0.5)
        anim.start(self.loading_text)
        
        # Start loading animation
        Clock.schedule_interval(self.update_loading_text, 0.5)
        
        # Schedule transition to home screen
        Clock.schedule_once(lambda dt: self.go_to_home(), 3)
    
    def update_loading_text(self, dt):
        """Update loading dots animation"""
        self.loading_dots = (self.loading_dots + 1) % 4
        dots = '.' * self.loading_dots
        self.loading_text.text = f'Loading{dots}'
    
    def go_to_home(self):
        """Transition to home screen"""
        # Fade out current screen
        anim = Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda *x: setattr(self.manager, 'current', 'home'))
        anim.start(self)
    
    def has_logo(self):
        """Check if logo file exists"""
        import os
        return os.path.exists('assets/logo.png')
