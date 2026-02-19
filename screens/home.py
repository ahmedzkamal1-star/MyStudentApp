# screens/home.py - شاشة الطالب (الإعدادات الكاملة ونظام المواد)
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from utils.arabic_utils import ar
import time

# الألوان
C_BG      = '#0f172a'
C_CARD    = '#1e293b'
C_BLUE    = '#3b82f6'
C_GREEN   = '#22c55e'
C_RED     = '#ef4444'
C_YELLOW  = '#eab308'
C_SUB     = '#94a3b8'

def make_card_bg(widget, color=C_CARD, radius=12):
    with widget.canvas.before:
        clr = Color(*get_color_from_hex(color))
        r = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius)])
    widget.bind(pos=lambda i,v: setattr(r, 'pos', v), size=lambda i,v: setattr(r, 'size', v))
    return clr, r

class SubjectCard(ButtonBehavior, BoxLayout):
    def __init__(self, sub_id, name, doctor, on_click, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None; self.height = dp(80); self.padding = dp(12)
        make_card_bg(self)
        self.add_widget(Label(text=ar(name), font_size=dp(17), bold=True, font_name=App.get_running_app().font_name, halign='right'))
        self.bind(on_release=lambda x: on_click(sub_id, name))

class PDFCard(BoxLayout):
    def __init__(self, pdf_id, pdf_data, student_code, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'; self.size_hint_y = None; self.height = dp(85); self.padding = dp(10)
        make_card_bg(self, '#262f45')
        
        title = pdf_data.get('title', 'ملف')
        approved = student_code in pdf_data.get('approved_students', [])
        pending = student_code in pdf_data.get('pending_download_requests', [])
        
        self.add_widget(Label(text=ar(title), font_name=App.get_running_app().font_name, halign='right'))
        
        btn_box = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(8))
        if approved:
            dl = Button(text=ar('⬇️ تحميل'), font_name=App.get_running_app().font_name, background_color=get_color_from_hex(C_GREEN), background_normal='')
            dl.bind(on_release=lambda x: self._download(pdf_data.get('url','')))
            btn_box.add_widget(dl)
        elif pending:
            btn_box.add_widget(Label(text=ar('⏳ طلبك قيد المراجعة'), font_name=App.get_running_app().font_name, color=get_color_from_hex(C_YELLOW)))
        else:
            req = Button(text=ar('طلب الإذن'), font_name=App.get_running_app().font_name, background_color=get_color_from_hex(C_BLUE), background_normal='')
            req.bind(on_release=lambda x: self._req(pdf_id, student_code, x))
            btn_box.add_widget(req)
        self.add_widget(btn_box)

    def _req(self, pid, code, inst):
        from utils.firebase_manager import FirebaseManager
        FirebaseManager.request_pdf_access(pid, code)
        inst.text = ar('✅ تم الطلب'); inst.disabled = True

    def _download(self, url):
        import webbrowser; webbrowser.open(url)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.current_tab = 'home'
        self.setup_ui()

    def setup_ui(self):
        from kivy.uix.floatlayout import FloatLayout
        self.root = FloatLayout()
        with self.root.canvas.before:
            Color(*get_color_from_hex(C_BG))
            self.bg_rect = RoundedRectangle(pos=self.root.pos, size=self.root.size)
        
        layout = BoxLayout(orientation='vertical')
        
        # Header
        head = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(16), 0])
        self.welcome = Label(text=ar('مراحباً بك'), font_size=dp(18), bold=True, font_name=self.app.font_name, halign='right')
        head.add_widget(self.welcome)
        layout.add_widget(head)

        # Content
        self.scroll = ScrollView(size_hint_y=0.82)
        self.content = BoxLayout(orientation='vertical', size_hint_y=None, padding=dp(15), spacing=dp(12))
        self.content.bind(minimum_height=self.content.setter('height'))
        self.scroll.add_widget(self.content)
        layout.add_widget(self.scroll)

        # Nav
        self.nav = BoxLayout(size_hint_y=None, height=dp(60))
        make_card_bg(self.nav)
        for tab, lbl in [('home','الرئيسية'), ('mats','موادي'), ('settings','الإعدادات')]:
            b = Button(text=ar(lbl), font_name=self.app.font_name, background_normal='', background_color=(0,0,0,0), color=get_color_from_hex(C_SUB))
            b.bind(on_release=lambda x, t=tab: self.switch_tab(t))
            self.nav.add_widget(b)
        layout.add_widget(self.nav)
        
        self.root.add_widget(layout)
        self.add_widget(self.root)

    def on_enter(self):
        if self.app.username: self.welcome.text = ar(f"مرحباً، {self.app.username}")
        self.switch_tab(self.current_tab)

    def switch_tab(self, tab):
        self.current_tab = tab
        self.content.clear_widgets()
        if tab == 'home': self.build_home()
        elif tab == 'mats': self.build_mats()
        elif tab == 'settings': self.build_settings()

    def build_home(self):
        from utils.firebase_manager import FirebaseManager
        self.content.add_widget(Label(text=ar('آخر الإعلانات'), font_size=dp(18), bold=True, font_name=self.app.font_name, halign='right', size_hint_y=None, height=dp(40)))
        anns = FirebaseManager.get_announcements()
        if not anns:
            self.content.add_widget(Label(text=ar('لا توجد منشورات حالياً'), font_name=self.app.font_name, color=get_color_from_hex(C_SUB)))
        for a in anns:
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), padding=dp(12), spacing=dp(5))
            make_card_bg(card)
            card.add_widget(Label(text=ar(f"مدير المنصة - {a['time']}"), font_size=dp(10), color=get_color_from_hex(C_BLUE), halign='right'))
            card.add_widget(Label(text=ar(a['text']), font_size=dp(14), halign='right'))
            self.content.add_widget(card)

    def build_mats(self):
        from utils.firebase_manager import FirebaseManager
        self.content.add_widget(Label(text=ar('المواد الدراسية'), font_size=dp(18), bold=True, font_name=self.app.font_name, halign='right', size_hint_y=None, height=dp(40)))
        subs = FirebaseManager.get_subjects()
        if not subs:
            self.content.add_widget(Label(text=ar('سيتم إضافة المواد قريباً'), font_name=self.app.font_name, color=get_color_from_hex(C_SUB)))
        for sid, sdata in subs.items():
            self.content.add_widget(SubjectCard(sid, sdata['name'], sdata['doctor'], self.show_sub_pdfs))

    def show_sub_pdfs(self, sid, name):
        from utils.firebase_manager import FirebaseManager
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        content.add_widget(Label(text=ar(f"ملفات: {name}"), font_name=self.app.font_name, bold=True))
        scroll = ScrollView(); inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        inner.bind(minimum_height=inner.setter('height')); scroll.add_widget(inner)
        
        subs = FirebaseManager.get_subjects(); pdfs = FirebaseManager.get_pdfs()
        sub_pdfs = subs.get(sid, {}).get('pdfs', [])
        if not sub_pdfs:
            inner.add_widget(Label(text=ar('لا توجد ملفات حالياً'), font_name=self.app.font_name, color=get_color_from_hex(C_SUB)))
        else:
            for pid in sub_pdfs:
                if pid in pdfs: inner.add_widget(PDFCard(pid, pdfs[pid], self.app.user_code))
        
        content.add_widget(scroll)
        popup = Popup(title='', content=content, size_hint=(0.9, 0.8), separator_height=0)
        content.add_widget(Button(text=ar('إغلاق'), size_hint_y=None, height=dp(44), on_release=lambda x: popup.dismiss()))
        popup.open()

    def build_settings(self):
        layout = self.content
        layout.add_widget(Label(text=ar('إعدادات حسابي'), font_size=dp(20), bold=True, font_name=self.app.font_name, halign='right', size_hint_y=None, height=dp(50)))
        
        # معلومات الحساب
        acc = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), padding=dp(12))
        make_card_bg(acc)
        acc.add_widget(Label(text=ar(f"الاسم: {self.app.username}"), font_name=self.app.font_name, halign='right', bold=True))
        acc.add_widget(Label(text=ar(f"كود الطالب: {self.app.user_code}"), font_size=dp(11), color=get_color_from_hex(C_SUB), halign='right'))
        layout.add_widget(acc)

        # تغيير كلمة المرور
        pw_btn = Button(text=ar('تغيير كلمة المرور'), font_name=self.app.font_name, size_hint_y=None, height=dp(50), background_normal='', background_color=get_color_from_hex('#1e293b'), color=get_color_from_hex(C_BLUE))
        pw_btn.bind(on_release=self.show_pw_popup)
        layout.add_widget(pw_btn)

        # الوضع الليلي
        dark_box = BoxLayout(size_hint_y=None, height=dp(50), padding=[dp(15), 0])
        make_card_bg(dark_box)
        dark_box.add_widget(Label(text=ar('الوضع الليلي'), font_name=self.app.font_name, halign='right'))
        dark_box.add_widget(Switch(active=True, size_hint_x=0.25))
        layout.add_widget(dark_box)

        # الدعم الفني
        layout.add_widget(Label(text=ar('الدعم الفني'), font_name=self.app.font_name, color=get_color_from_hex(C_BLUE), halign='right', size_hint_y=None, height=dp(30)))
        sup = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        sup.add_widget(Button(text=ar('واتساب'), font_name=self.app.font_name, background_normal='', background_color=get_color_from_hex(C_GREEN)))
        sup.add_widget(Button(text=ar('اتصال مباشر'), font_name=self.app.font_name, background_normal='', background_color=get_color_from_hex(C_BLUE)))
        layout.add_widget(sup)

        # خروج
        exit_btn = Button(text=ar('تسجيل الخروج'), font_name=self.app.font_name, bold=True, size_hint_y=None, height=dp(55), background_normal='', background_color=get_color_from_hex(C_RED))
        exit_btn.bind(on_release=self.logout)
        layout.add_widget(exit_btn)

    def show_pw_popup(self, *a):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        content.add_widget(Label(text=ar('تغيير كلمة المرور'), font_name=self.app.font_name))
        new_in = TextInput(hint_text=ar('كلمة السر الجديدة'), password=True, font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None)
        content.add_widget(new_in)
        popup = Popup(title='', content=content, size_hint=(0.85, 0.4), separator_height=0)
        def update(x):
            if len(new_in.text) > 3:
                from utils.firebase_manager import FirebaseManager
                FirebaseManager.change_password(self.app.user_code, new_in.text)
                popup.dismiss()
        content.add_widget(Button(text=ar('حفظ'), font_name=self.app.font_name, on_release=update))
        popup.open()

    def logout(self, *a):
        from utils.firebase_manager import FirebaseManager
        FirebaseManager.remove_session(self.app.user_code)
        self.app.user_code = ''; self.app.username = ''
        self.manager.current = 'login'
