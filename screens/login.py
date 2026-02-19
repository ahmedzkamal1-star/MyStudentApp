# screens/login.py - شاشة تسجيل الدخول مع دعم الجلسات والتسجيل الجديد
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.app import App
from utils.firebase_manager import FirebaseManager
from utils.arabic_utils import ar


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_ui()

    def setup_ui(self):
        from kivy.uix.floatlayout import FloatLayout
        main = FloatLayout()

        # خلفية داكنة
        with main.canvas.before:
            Color(*get_color_from_hex('#0f172a'))
            self.bg_rect = RoundedRectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(self.bg_rect, 'pos', v),
                  size=lambda i, v: setattr(self.bg_rect, 'size', v))

        # بطاقة تسجيل الدخول مركزية
        card = BoxLayout(
            orientation='vertical',
            size_hint=(0.88, None),
            height=dp(480),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            padding=dp(30),
            spacing=dp(14)
        )

        with card.canvas.before:
            Color(*get_color_from_hex('#1e293b'))
            self.card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(20)])
        card.bind(
            pos=lambda i, v: setattr(self.card_rect, 'pos', v),
            size=lambda i, v: setattr(self.card_rect, 'size', v)
        )

        # ─── شعار ───
        card.add_widget(Label(
            text='Student',
            font_size=dp(52),
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(60)
        ))
        card.add_widget(Label(
            text='MyStudent',
            font_size=dp(28),
            bold=True,
            font_name=self.app.font_name,
            color=get_color_from_hex('#f1f5f9'),
            size_hint_y=None,
            height=dp(40)
        ))
        card.add_widget(Label(
            text=ar('سجّل دخولك للمتابعة'),
            font_size=dp(13),
            font_name=self.app.font_name,
            color=get_color_from_hex('#64748b'),
            size_hint_y=None,
            height=dp(22)
        ))

        # ─── حقل الكود ───
        self.username = TextInput(
            hint_text=ar('الكود الجامعي أو admin'),
            multiline=False,
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(14), dp(14)],
            background_color=get_color_from_hex('#334155'),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=get_color_from_hex('#64748b'),
            cursor_color=(1, 1, 1, 1),
        )
        card.add_widget(self.username)

        # ─── حقل كلمة المرور ───
        self.password = TextInput(
            hint_text=ar('كلمة المرور'),
            password=True,
            multiline=False,
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(14), dp(14)],
            background_color=get_color_from_hex('#334155'),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=get_color_from_hex('#64748b'),
            cursor_color=(1, 1, 1, 1),
        )
        self.password.bind(on_text_validate=self.login)
        card.add_widget(self.password)

        # ─── رسالة الخطأ ───
        self.error_label = Label(
            text='',
            color=get_color_from_hex('#ef4444'),
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(28),
            font_size=dp(13),
            halign='center'
        )
        self.error_label.bind(size=self.error_label.setter('text_size'))
        card.add_widget(self.error_label)

        # ─── زر الدخول ───
        login_btn = Button(
            text=ar('دخول'),
            font_size=dp(17),
            bold=True,
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(54),
            background_normal='',
            background_color=get_color_from_hex('#3b82f6'),
            color=(1, 1, 1, 1)
        )
        login_btn.bind(on_release=self.login)
        card.add_widget(login_btn)

        # ─── فاصل ───
        card.add_widget(Label(
            text=ar('أو'),
            color=get_color_from_hex('#334155'),
            font_name=self.app.font_name,
            font_size=dp(12),
            size_hint_y=None,
            height=dp(20)
        ))

        # ─── زر التسجيل الجديد ───
        register_btn = Button(
            text=ar('حساب جديد - طالب'),
            font_size=dp(14),
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(46),
            background_normal='',
            background_color=get_color_from_hex('#0f4c75'),
            color=get_color_from_hex('#93c5fd')
        )
        register_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'register'))
        card.add_widget(register_btn)

        main.add_widget(card)
        self.add_widget(main)

    def login(self, instance=None):
        user = self.username.text.strip()
        pw   = self.password.text.strip()

        if not user or not pw:
            self.error_label.text = ar('يرجى إدخال الكود وكلمة المرور')
            return

        # ─── Admin ───
        if user == 'admin' and pw == 'admin123':
            self.app.user_role = 'admin'
            self.app.username  = 'المدير'
            self.app.user_code = 'admin'
            self.error_label.text = ''
            self.username.text = ''
            self.password.text = ''
            self.manager.current = 'admin'
            return

        # ─── طالب ───
        try:
            students = FirebaseManager.get_students()
        except Exception:
            self.error_label.text = ar('لا يوجد اتصال بالبيانات')
            return

        if user in students and students[user].get('password') == pw:
            self.app.user_role = 'student'
            self.app.user_code = user
            self.app.username  = students[user].get('name', user)
            # ── تسجيل الجلسة ──
            FirebaseManager.set_session(user, self.app.username)
            self.error_label.text = ''
            self.username.text = ''
            self.password.text = ''
            self.manager.current = 'home'
        else:
            self.error_label.text = ar('بيانات الدخول غير صحيحة!')
