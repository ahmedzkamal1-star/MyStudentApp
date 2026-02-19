# screens/register.py - شاشة طلب التسجيل للطلاب الجدد
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.app import App
from kivy.clock import Clock
from utils.firebase_manager import FirebaseManager
from utils.arabic_utils import ar


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.setup_ui()

    def setup_ui(self):
        from kivy.uix.floatlayout import FloatLayout
        main = FloatLayout()

        # خلفية متدرجة
        with main.canvas.before:
            Color(*get_color_from_hex('#1e293b'))
            self.bg_rect = RoundedRectangle(pos=main.pos, size=main.size)
        main.bind(pos=lambda i, v: setattr(self.bg_rect, 'pos', v),
                  size=lambda i, v: setattr(self.bg_rect, 'size', v))

        scroll = ScrollView(size_hint=(1, 1))
        content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(30), dp(40)],
            spacing=dp(16)
        )
        content.bind(minimum_height=content.setter('height'))

        # ─── العنوان ───
        title_box = BoxLayout(
            orientation='vertical', size_hint_y=None, height=dp(90), spacing=dp(5)
        )
        title_box.add_widget(Label(
            text='Student',
            font_size=dp(44),
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(50)
        ))
        title_box.add_widget(Label(
            text=ar('طلب التسجيل'),
            font_size=dp(24),
            bold=True,
            font_name=self.app.font_name,
            color=get_color_from_hex('#f1f5f9'),
            size_hint_y=None,
            height=dp(35)
        ))
        content.add_widget(title_box)

        content.add_widget(Label(
            text=ar('سيتم مراجعة طلبك من قبل الإدارة'),
            font_size=dp(14),
            font_name=self.app.font_name,
            color=get_color_from_hex('#94a3b8'),
            size_hint_y=None,
            height=dp(25)
        ))

        # ─── حقول الإدخال ───
        self.name_input = self._make_input('الاسم الكامل', False)
        self.code_input = self._make_input('الكود الجامعي', False)
        self.pw_input   = self._make_input('كلمة المرور', False, password=True)
        self.pw2_input  = self._make_input('تأكيد كلمة المرور', True, password=True)

        content.add_widget(self._labeled_field('الاسم الكامل', self.name_input))
        content.add_widget(self._labeled_field('الكود الجامعي', self.code_input))
        content.add_widget(self._labeled_field('كلمة المرور', self.pw_input))
        content.add_widget(self._labeled_field('تأكيد كلمة المرور', self.pw2_input))

        # ─── رسالة الحالة ───
        self.status_label = Label(
            text='',
            font_size=dp(14),
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        content.add_widget(self.status_label)

        # ─── زر الإرسال ───
        send_btn = Button(
            text=ar('إرسال الطلب'),
            font_size=dp(17),
            bold=True,
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(55),
            background_normal='',
            background_color=get_color_from_hex('#3b82f6'),
            color=(1, 1, 1, 1)
        )
        send_btn.bind(on_release=self.submit_request)
        content.add_widget(send_btn)

        # ─── زر العودة ───
        back_btn = Button(
            text=ar('العودة لتسجيل الدخول'),
            font_size=dp(14),
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(40),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=get_color_from_hex('#64748b')
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'login'))
        content.add_widget(back_btn)

        scroll.add_widget(content)
        main.add_widget(scroll)
        self.add_widget(main)

    def _make_input(self, hint, last_field, password=False):
        inp = TextInput(
            hint_text=ar(hint),
            password=password,
            multiline=False,
            font_name=self.app.font_name,
            size_hint_y=None,
            height=dp(50),
            padding=[dp(12), dp(12)],
            background_color=get_color_from_hex('#334155'),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=get_color_from_hex('#64748b'),
            cursor_color=(1, 1, 1, 1),
        )
        if last_field:
            inp.on_text_validate = lambda: self.submit_request(None)
        return inp

    def _labeled_field(self, label_text, input_widget):
        box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(4))
        lbl = Label(
            text=ar(label_text),
            font_size=dp(13),
            font_name=self.app.font_name,
            color=get_color_from_hex('#94a3b8'),
            size_hint_y=None,
            height=dp(20),
            halign='right'
        )
        lbl.bind(size=lbl.setter('text_size'))
        box.add_widget(lbl)
        box.add_widget(input_widget)
        return box

    def submit_request(self, instance):
        name = self.name_input.text.strip()
        code = self.code_input.text.strip()
        pw   = self.pw_input.text.strip()
        pw2  = self.pw2_input.text.strip()

        # التحقق من الحقول
        if not all([name, code, pw, pw2]):
            self._show_msg('يرجى ملء جميع الحقول!', error=True)
            return
        if pw != pw2:
            self._show_msg('كلمتا المرور غير متطابقتان!', error=True)
            return
        if len(pw) < 4:
            self._show_msg('كلمة المرور يجب أن تكون 4 أحرف على الأقل', error=True)
            return

        self._show_msg('⏳ جارٍ إرسال الطلب...', error=False)

        ok, msg = FirebaseManager.submit_registration_request(code, name, pw)
        if ok:
            self._show_msg(f'✅ {msg}', error=False)
            self.name_input.text = ''
            self.code_input.text = ''
            self.pw_input.text   = ''
            self.pw2_input.text  = ''
        else:
            self._show_msg(f'❌ {msg}', error=True)

    def _show_msg(self, msg, error=False):
        self.status_label.text  = ar(msg)
        self.status_label.color = get_color_from_hex('#ef4444') if error else get_color_from_hex('#10b981')
