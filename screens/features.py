# screens/features.py - Features screen with interactive elements
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from utils.arabic_utils import ar

class FeatureDetailCard(BoxLayout):
    """Detailed feature card with progress or interactive elements"""
    
    def __init__(self, title, description, icon, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(200)
        self.padding = dp(15)
        self.spacing = dp(10)
        
        # Background
        with self.canvas.before:
            self.bg_color = Color()
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Header with icon and title
        header = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        self.icon_label = Label(text=ar(icon), font_size=dp(30), size_hint_x=0.2, font_name=self.app.font_name)
        self.title_label = Label(
            text=ar(title),
            font_size=dp(18),
            bold=True,
            size_hint_x=0.8,
            halign='right',
            font_name=self.app.font_name
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        header.add_widget(self.icon_label)
        header.add_widget(self.title_label)
        
        # Description
        self.desc_label = Label(
            text=ar(description),
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40),
            halign='right',
            font_name=self.app.font_name
        )
        self.desc_label.bind(size=self.desc_label.setter('text_size'))
        
        # Progress bar (example interactive element)
        progress_layout = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(10))
        self.usage_label = Label(text=ar('الاستخدام:'), size_hint_x=0.3, font_name=self.app.font_name)
        progress = ProgressBar(value=75, size_hint_x=0.7, max=100)
        progress_layout.add_widget(self.usage_label)
        progress_layout.add_widget(progress)
        
        # Action button
        self.action_btn = Button(
            text=ar('معرفة المزيد'),
            size_hint_y=None,
            height=dp(40),
            font_name=self.app.font_name,
            background_normal='',
            background_color=get_color_from_hex(self.app.primary_color),
            color=(1, 1, 1, 1)
        )
        
        self.add_widget(header)
        self.add_widget(self.desc_label)
        self.add_widget(progress_layout)
        self.add_widget(self.action_btn)
        self.update_theme()
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_theme(self):
        """Update colors based on theme"""
        if self.app.theme_mode == 'dark':
            self.bg_color.rgba = get_color_from_hex('#25263F')
        else:
            self.bg_color.rgba = get_color_from_hex('#FFFFFF')
            
        text_color = get_color_from_hex(self.app.text_color)
        sec_text = get_color_from_hex(self.app.secondary_text)
        
        self.title_label.color = text_color
        self.desc_label.color = sec_text
        self.usage_label.color = sec_text
        self.icon_label.color = get_color_from_hex(self.app.primary_color)
        self.action_btn.background_color = get_color_from_hex(self.app.primary_color)

class FeaturesScreen(Screen):
    """Features screen with detailed cards"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the features screen UI"""
        from kivy.uix.floatlayout import FloatLayout
        main_layout = FloatLayout()
        
        # Background
        with main_layout.canvas.before:
            self.bg_color = Color()
            self.rect = RoundedRectangle(pos=main_layout.pos, size=main_layout.size)
            
        main_layout.bind(pos=self.update_rect, size=self.update_rect)
        
        # Header
        header = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=[dp(20), dp(15)],
            pos_hint={'top': 1}
        )
        
        back_btn = Button(
            text='←',
            font_size=dp(30),
            size_hint_x=0.15,
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex(self.app.primary_color)
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))
        
        self.title_label = Label(
            text=ar('مميزات المنصة'),
            font_size=dp(22),
            bold=True,
            size_hint_x=0.85,
            halign='right',
            font_name=self.app.font_name
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        
        header.add_widget(back_btn)
        header.add_widget(self.title_label)
        
        # Scrollable content
        scroll = ScrollView(
            size_hint=(1, 0.9),
            pos_hint={'top': 0.9},
            bar_width=dp(5),
            bar_color=get_color_from_hex(self.app.primary_color)
        )
        
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(20), dp(10)],
            spacing=dp(15)
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Add detailed feature cards
        features = [
            {'title': 'Analytics Dashboard', 'desc': 'Real-time insights and data visualization with custom reports', 'icon': '📊'},
            {'title': 'AI Assistant', 'desc': 'Smart suggestions and automated workflows powered by AI', 'icon': '🤖'},
            {'title': 'Cloud Storage', 'desc': 'Secure cloud backup with 100GB of free space', 'icon': '☁️'},
            {'title': 'Advanced Security', 'desc': 'End-to-end encryption and biometric authentication', 'icon': '🔒'},
            {'title': 'Team Collaboration', 'desc': 'Real-time collaboration tools for teams', 'icon': '👥'},
            {'title': 'Mobile Sync', 'desc': 'Seamless sync across all your devices', 'icon': '📱'},
        ]
        
        self.cards = []
        for feature in features:
            card = FeatureDetailCard(
                title=feature['title'],
                description=feature['desc'],
                icon=feature['icon']
            )
            content.add_widget(card)
            self.cards.append(card)
        
        scroll.add_widget(content)
        
        main_layout.add_widget(header)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        self.update_theme()

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_theme(self):
        """Update colors based on theme"""
        # Background
        self.bg_color.rgba = self.app.get_background_color()
        # Text
        self.title_label.color = get_color_from_hex(self.app.text_color)
        # Cards handle their own theme if complex, but here we can force refresh
        for card in self.cards:
            if hasattr(card, 'update_theme'):
                card.update_theme()

    def animate_enter(self):
        """Animate cards when screen enters"""
        for i, card in enumerate(self.cards):
            card.opacity = 0
            card.y -= dp(20)
            delay = i * 0.05
            anim = Animation(opacity=1, y=card.y + dp(20), duration=0.4, t='out_quad')
            Clock.schedule_once(lambda dt, a=anim, c=card: a.start(c), delay)
