# main.py - Main application entry point
import os
os.environ['KIVY_NO_ARGS'] = '1'  # Disable argument parsing for cleaner startup

from kivy.config import Config
Config.set('kivy', 'window_icon', '')  # Remove default icon
Config.set('graphics', 'width', '400')  # Set default window size for testing
Config.set('graphics', 'height', '700')
Config.set('graphics', 'resizable', False)  # Fixed size for mobile feel

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.utils import get_color_from_hex, platform
from kivy.core.text import LabelBase

try:
    from kivymd.theming import ThemeManager
    HAS_KIVYMD = True
except ImportError:
    HAS_KIVYMD = False
import random

# Enable Content Protection (Prevent Screenshots) on Android
if platform == 'android':
    try:
        from android.runnable import run_on_ui_thread
        from jnius import autoclass
        
        @run_on_ui_thread
        def set_flag_secure():
            WindowManager = autoclass('android.view.WindowManager$LayoutParams')
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            window = activity.getWindow()
            window.addFlags(WindowManager.FLAG_SECURE)
            print("Android: FLAG_SECURE activated (Screenshots disabled)")
            
        set_flag_secure()
    except Exception as e:
        print(f"Android Secure Flag Error: {e}")

# Register custom fonts (Arabic support)
try:
    from kivy.core.text import LabelBase
    import os
    # استخدام خط يدعم العربية من النظام لضمان التوافق
    arial_path = "C:\\Windows\\Fonts\\arial.ttf"
    if os.path.exists(arial_path):
        LabelBase.register(name='ArabicFont', fn_regular=arial_path)
    else:
        # إذا لم يوجد، نعتمد على الخط الافتراضي مع التنبيه
        print("Warning: arial.ttf not found")
except Exception as e:
    print(f"Font registration failed: {e}")

from kivy.lang import Builder
from utils.arabic_utils import ar

# Import screens
# ...
from screens.splash import SplashScreen
from screens.login import LoginScreen
from screens.register import RegisterScreen
from screens.home import HomeScreen
from screens.admin import AdminScreen
from screens.features import FeaturesScreen
from screens.settings import SettingsScreen

# Load styles
try:
    Builder.load_file('assets/styles.kv')
except Exception as e:
    print(f"Error loading styles: {e}")

class MainApp(App):
    """Main application class with theme management"""
    
    theme_mode = StringProperty('light')  # 'light' or 'dark'
    primary_color = StringProperty('#3b82f6')  # match student system blue
    accent_color = StringProperty('#00B894')  # Mint green
    text_color = StringProperty('#2D3436') # Default dark text
    secondary_text = StringProperty('#636E72') # Subtitle color
    font_name = StringProperty('ArabicFont') # الخط الداعم للعربية
    
    # User properties
    user_role = StringProperty('guest') # guest, admin, student
    user_code = StringProperty('')
    username = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if HAS_KIVYMD:
            self.theme_manager = ThemeManager()
        self.title = 'MyStudent'
        self.icon = 'assets/icon.png'
        # self.register_fonts() # تم التسجيل في الأعلى
        self.load_theme_preference()
        
    def register_fonts(self):
        """Register custom fonts if files exist"""
        try:
            import os
            from kivy.core.text import LabelBase
            
            # Check if font files exist
            reg_path = os.path.join('assets', 'fonts', 'Poppins-Regular.ttf')
            bold_path = os.path.join('assets', 'fonts', 'Poppins-Bold.ttf')
            
            if os.path.exists(reg_path):
                LabelBase.register(name='Poppins',
                                 fn_regular=reg_path,
                                 fn_bold=bold_path if os.path.exists(bold_path) else reg_path)
                self.font_name = 'Poppins'
                print("Registered Poppins font")
            else:
                print("Poppins font not found, falling back to Roboto")
        except Exception as e:
            print(f"Font registration failed: {e}")
            
    def build(self):
        """Build the application"""
        # Update colors based on loaded theme
        self.update_theme_colors()
        
        # Set window background color
        Window.clearcolor = self.get_background_color()
        
        # Create screen manager with fade transition
        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))
        
        # Add screens
        self.sm.add_widget(SplashScreen(name='splash'))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(AdminScreen(name='admin'))
        self.sm.add_widget(FeaturesScreen(name='features'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        
        # ─── المزامنة السحابية عند البدء ───
        from utils.firebase_manager import FirebaseManager
        FirebaseManager.sync_data()
        
        # Bind to screen changes for animations
        self.sm.bind(current=self.on_screen_change)
        
        return self.sm
    
    def on_screen_change(self, instance, screen_name):
        """Handle screen change animations"""
        if screen_name in ['home', 'features', 'settings', 'admin']:
            # Trigger screen animations when it becomes current
            screen = self.sm.get_screen(screen_name)
            if hasattr(screen, 'animate_enter'):
                Clock.schedule_once(lambda dt: screen.animate_enter(), 0.1)
    
    def get_background_color(self):
        """Get background color based on theme"""
        if self.theme_mode == 'dark':
            return get_color_from_hex('#0f172a')  # Sync with new C_BG
        else:
            return get_color_from_hex('#F5F6FA')  # Light gray
            
    def update_theme_colors(self):
        """Update logic colors based on theme mode"""
        if self.theme_mode == 'dark':
            self.text_color = '#FFFFFF'
            self.secondary_text = '#94a3b8'
        else:
            self.text_color = '#2D3436'
            self.secondary_text = '#636E72'
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.theme_mode = 'dark' if self.theme_mode == 'light' else 'light'
        self.update_theme_colors()
        
        # Update window background with animation
        new_color = self.get_background_color()
        anim = Animation(clearcolor=new_color, duration=0.3)
        anim.start(Window)
        
        # Force update all screens
        for screen in self.sm.screens:
            if hasattr(screen, 'update_theme'):
                screen.update_theme()
        
        # Save preference
        self.save_theme_preference()
    
    def save_theme_preference(self):
        """Save theme preference (could use json file)"""
        try:
            with open('theme_pref.txt', 'w') as f:
                f.write(self.theme_mode)
        except:
            pass
    
    def load_theme_preference(self):
        """Load saved theme preference"""
        try:
            with open('theme_pref.txt', 'r') as f:
                self.theme_mode = f.read().strip()
        except:
            pass

if __name__ == '__main__':
    MainApp().run()
