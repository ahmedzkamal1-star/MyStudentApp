# screens/settings.py - Settings screen with theme toggle
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.graphics import Color, RoundedRectangle
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.app import App

class AppSettingRow(BoxLayout):
    """Reusable setting item with label and control"""
    
    def __init__(self, setting_name, setting_icon, control_widget, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = [dp(15), dp(10)]
        self.spacing = dp(15)
        
        # Background
        with self.canvas.before:
            self.bg_color = Color()
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Icon
        self.icon_label = Label(
            text=setting_icon,
            font_size=dp(24),
            size_hint_x=0.15
        )
        
        # Name
        self.name_label = Label(
            text=setting_name,
            font_size=dp(16),
            size_hint_x=0.5,
            halign='left'
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))
        
        # Control (switch, slider, etc)
        control = control_widget
        control.size_hint_x = 0.35
        
        self.add_widget(self.icon_label)
        self.add_widget(self.name_label)
        self.add_widget(control)
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
            
        self.name_label.color = get_color_from_hex(self.app.text_color)
        self.icon_label.color = get_color_from_hex(self.app.primary_color)

class SettingsScreen(Screen):
    """Settings screen with theme toggle and preferences"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the settings screen UI"""
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
            text='Settings',
            font_size=dp(22),
            bold=True,
            size_hint_x=0.85,
            halign='left'
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
        
        # Store items for animation and theme updates
        self.items = []
        
        # Sections
        content.add_widget(self.create_section_title('Appearance'))
        
        dark_mode_switch = Switch(active=(self.app.theme_mode == 'dark'))
        dark_mode_switch.bind(active=self.on_theme_toggle)
        
        theme_item = AppSettingRow(
            setting_name='Dark Mode',
            setting_icon='🌙',
            control_widget=dark_mode_switch
        )
        content.add_widget(theme_item)
        self.items.append(theme_item)
        
        content.add_widget(self.create_section_title('Notifications'))
        
        push_item = AppSettingRow(setting_name='Push Notifications', setting_icon='🔔', control_widget=Switch(active=True))
        content.add_widget(push_item)
        self.items.append(push_item)
        
        email_item = AppSettingRow(setting_name='Email Updates', setting_icon='📧', control_widget=Switch(active=False))
        content.add_widget(email_item)
        self.items.append(email_item)
        
        content.add_widget(self.create_section_title('Preferences'))
        
        lang_btn = Button(text='English', size_hint=(0.35, None), height=dp(40), background_color=get_color_from_hex(self.app.primary_color), color=(1, 1, 1, 1))
        lang_item = AppSettingRow(setting_name='Language', setting_icon='🌐', control_widget=lang_btn)
        content.add_widget(lang_item)
        self.items.append(lang_item)
        
        self.logout_btn = Button(
            text='Log Out',
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=get_color_from_hex('#E74C3C'),
            color=(1, 1, 1, 1)
        )
        self.logout_btn.bind(on_release=self.on_logout)
        content.add_widget(self.logout_btn)
        
        scroll.add_widget(content)
        
        main_layout.add_widget(header)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        self.update_theme()
    
    def create_section_title(self, title):
        """Create a section title widget"""
        lbl = Label(
            text=title,
            font_size=dp(18),
            bold=True,
            color=get_color_from_hex(self.app.primary_color),
            size_hint_y=None,
            height=dp(40),
            halign='left'
        )
        lbl.bind(size=lbl.setter('text_size'))
        return lbl
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_theme(self):
        """Update colors based on theme"""
        self.bg_color.rgba = self.app.get_background_color()
        self.title_label.color = get_color_from_hex(self.app.text_color)
        for item in self.items:
            if hasattr(item, 'update_theme'):
                item.update_theme()

    def animate_enter(self):
        """Animate items when screen enters"""
        for i, item in enumerate(self.items):
            item.opacity = 0
            item.x += dp(50)
            delay = i * 0.05
            anim = Animation(opacity=1, x=item.x - dp(50), duration=0.4, t='out_quad')
            Clock.schedule_once(lambda dt, a=anim, it=item: a.start(it), delay)
    
    def on_theme_toggle(self, switch, value):
        """Handle theme toggle"""
        self.app.toggle_theme()
        
    def on_logout(self, instance):
        """Handle logout"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text='Are you sure you want to log out?'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        cancel_btn = Button(text='Cancel')
        confirm_btn = Button(text='Log Out', background_color=get_color_from_hex('#E74C3C'))
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Logout', content=content, size_hint=(0.8, 0.3))
        cancel_btn.bind(on_release=popup.dismiss)
        confirm_btn.bind(on_release=lambda x: self.confirm_logout(popup))
        
        popup.open()
    
    def confirm_logout(self, popup):
        """Confirm logout and go to splash screen"""
        popup.dismiss()
        self.manager.current = 'splash'
