# screens/admin.py - لوحة تحكم المدير المطورة (إعدادات الطلاب والمواد)
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.app import App
from utils.firebase_manager import FirebaseManager
from utils.arabic_utils import ar
import time

# الألوان
C_BG      = '#0f172a'
C_CARD    = '#1e293b'
C_BLUE    = '#3b82f6'
C_GREEN   = '#10b981'
C_RED     = '#ef4444'
C_YELLOW  = '#f59e0b'
C_SUB     = '#94a3b8'
C_TEXT    = '#f1f5f9'

def make_card_bg(widget, color=C_CARD, radius=12):
    with widget.canvas.before:
        clr = Color(*get_color_from_hex(color))
        r = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius)])
    widget.bind(pos=lambda i, v: setattr(r, 'pos', v), size=lambda i, v: setattr(r, 'size', v))
    return clr, r

def action_btn(text, bg, on_press, height=dp(38), font_size=dp(12)):
    b = Button(
        text=ar(text), font_size=font_size, bold=True,
        font_name=App.get_running_app().font_name,
        size_hint_y=None, height=height,
        background_normal='', background_color=get_color_from_hex(bg),
        color=(1, 1, 1, 1)
    )
    b.bind(on_release=on_press)
    return b

class TabBar(BoxLayout):
    def __init__(self, tabs, on_tab_change, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'; self.size_hint_y = None; self.height = dp(50)
        make_card_bg(self)
        self.btns = []
        for i, (icon, label) in enumerate(tabs):
            b = Button(text=ar(f'{icon} {label}'), font_size=dp(11), font_name=App.get_running_app().font_name, background_normal='', background_color=(0,0,0,0), color=get_color_from_hex(C_SUB))
            b.bind(on_release=lambda x, idx=i: on_tab_change(idx))
            self.add_widget(b); self.btns.append(b)
        self.select(0)
    def select(self, idx):
        for i, b in enumerate(self.btns):
            b.color = get_color_from_hex(C_BLUE if i == idx else C_SUB)
            b.bold = (i == idx)

class AdminScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.current_tab = 0
        self.setup_ui()

    def setup_ui(self):
        from kivy.uix.floatlayout import FloatLayout
        self.root = FloatLayout()
        with self.root.canvas.before:
            Color(*get_color_from_hex(C_BG))
            self.bg_rect = RoundedRectangle(pos=self.root.pos, size=self.root.size)
        self.root.bind(pos=lambda i,v: setattr(self.bg_rect, 'pos', v), size=lambda i,v: setattr(self.bg_rect, 'size', v))
        
        main_box = BoxLayout(orientation='vertical')
        
        # Header
        head = BoxLayout(size_hint_y=None, height=dp(58), padding=[dp(16), dp(8)], spacing=dp(10))
        make_card_bg(head)
        self.badge = Label(text='', font_size=dp(12), color=get_color_from_hex(C_RED), size_hint_x=0.2, font_name=self.app.font_name)
        title = Label(text=ar('إدارة المنصة'), font_size=dp(18), bold=True, font_name=self.app.font_name, color=get_color_from_hex(C_YELLOW), size_hint_x=0.6)
        logout = action_btn('خروج', C_RED, self.logout, dp(38))
        logout.size_hint_x = 0.2
        head.add_widget(self.badge); head.add_widget(title); head.add_widget(logout)
        main_box.add_widget(head)

        # Tabs (3 Tabs as requested)
        tabs = [('👥', 'إعدادات الطلاب'), ('📚', 'المواد'), ('⚙️', 'الإعدادات')]
        self.tab_bar = TabBar(tabs, self.switch_tab)
        main_box.add_widget(self.tab_bar)

        self.content = BoxLayout(orientation='vertical')
        main_box.add_widget(self.content)
        self.root.add_widget(main_box)
        self.add_widget(self.root)

    def on_enter(self): self._update_badge(); self.switch_tab(self.current_tab)

    def switch_tab(self, idx):
        self.current_tab = idx; self.tab_bar.select(idx)
        self.content.clear_widgets()
        if   idx == 0: self.build_student_settings_tab()
        elif idx == 1: self.build_subjects_tab()
        elif idx == 2: self.build_admin_settings_tab()
        self._update_badge()

    # ❶ إعدادات الطلاب (الطلاب + المتابعة)
    def build_student_settings_tab(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        self.content.add_widget(layout)

        # قسم التنبيه السريع
        ann_box = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.ann_in = TextInput(hint_text=ar('إعلان سريع للطلاب...'), font_name=self.app.font_name, multiline=False, size_hint_x=0.8, halign='right')
        ann_box.add_widget(self.ann_in)
        ann_box.add_widget(action_btn('نشر', C_BLUE, self._post_ann, dp(44)))
        layout.add_widget(ann_box)

        scroll = ScrollView()
        self.inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.inner.bind(minimum_height=self.inner.setter('height'))
        scroll.add_widget(self.inner)
        layout.add_widget(scroll)
        self._refresh_student_settings()

    def _refresh_student_settings(self):
        self.inner.clear_widgets()
        
        # 1. طلبات التسجيل والتحميل
        pending = FirebaseManager.get_pending_requests()
        pdf_reqs = FirebaseManager.get_pdf_download_requests()
        if pending or pdf_reqs:
            self.inner.add_widget(Label(text=ar('⚠️ طلبات بانتظار الموافقة'), font_name=self.app.font_name, color=get_color_from_hex(C_YELLOW), size_hint_y=None, height=dp(30), halign='right'))
            for c, d in pending.items():
                row = BoxLayout(size_hint_y=None, height=dp(50), padding=[dp(10), 0], spacing=dp(8))
                make_card_bg(row, '#1c2744')
                row.add_widget(Label(text=ar(f"تسجيل: {d['name']}"), font_name=self.app.font_name, halign='right', size_hint_x=0.5))
                row.add_widget(action_btn('قبول', C_GREEN, lambda x, code=c: self._approve_reg(code), dp(36)))
                row.add_widget(action_btn('رفض', C_RED, lambda x, code=c: self._reject_reg(code), dp(36)))
                self.inner.add_widget(row)
            for r in pdf_reqs:
                row = BoxLayout(size_hint_y=None, height=dp(50), padding=[dp(10), 0], spacing=dp(8))
                make_card_bg(row, '#1c2744')
                row.add_widget(Label(text=ar(f"تحميل: {r['pdf_title']}"), font_name=self.app.font_name, halign='right', size_hint_x=0.5))
                row.add_widget(action_btn('سماح', C_BLUE, lambda x, p=r['pdf_id'], c=r['student_code']: self._approve_pdf(p, c), dp(36)))
                self.inner.add_widget(row)

        # 2. قائمة الطلاب
        self.inner.add_widget(Label(text=ar('👥 قائمة الطلاب'), font_name=self.app.font_name, color=get_color_from_hex(C_SUB), size_hint_y=None, height=dp(30), halign='right'))
        btn_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        btn_bar.add_widget(action_btn('إضافة طالب جديد', C_GREEN, self.show_add_student_dialog, dp(40)))
        self.inner.add_widget(btn_bar)

        students = FirebaseManager.get_students()
        for code, data in students.items():
            row = BoxLayout(size_hint_y=None, height=dp(55), padding=[dp(12), dp(5)], spacing=dp(8))
            make_card_bg(row)
            row.add_widget(Label(text=ar(data['name']), bold=True, font_name=self.app.font_name, halign='right', size_hint_x=0.4))
            row.add_widget(Label(text=f'#{code}', color=get_color_from_hex(C_SUB), font_size=dp(11), size_hint_x=0.2))
            row.add_widget(action_btn('تعديل', C_BLUE, lambda x, c=code, d=data: self.show_edit_student_dialog(c, d), dp(38), dp(11)))
            row.add_widget(action_btn('حذف', C_RED, lambda x, c=code: self._del_student(c), dp(38), dp(11)))
            self.inner.add_widget(row)

    # ❷ المواد (نفس الهيكلية السابقة مع تحسين)
    def build_subjects_tab(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        self.content.add_widget(layout)
        bar = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        bar.add_widget(Label(text=ar('إدارة المواد الدراسية'), font_size=dp(15), bold=True, font_name=self.app.font_name, halign='right'))
        bar.add_widget(action_btn('مادة جديدة', C_BLUE, self.show_add_subject_dialog, dp(42)))
        layout.add_widget(bar)
        
        scroll = ScrollView()
        self.sub_inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        self.sub_inner.bind(minimum_height=self.sub_inner.setter('height'))
        scroll.add_widget(self.sub_inner)
        layout.add_widget(scroll)
        self._refresh_subs()

    def _refresh_subs(self):
        self.sub_inner.clear_widgets()
        subs = FirebaseManager.get_subjects()
        for sid, s in subs.items():
            card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), padding=dp(10), spacing=dp(5))
            make_card_bg(card)
            row1 = BoxLayout(size_hint_y=None, height=dp(30))
            row1.add_widget(Label(text=ar(s['name']), bold=True, font_name=self.app.font_name, halign='right'))
            row1.add_widget(action_btn('🗑️', C_RED, lambda x, i=sid: self._del_sub(i), dp(30)))
            card.add_widget(row1)
            row2 = BoxLayout(size_hint_y=None, height=dp(25))
            row2.add_widget(Label(text=ar(f"د. {s['doctor']}"), font_size=dp(11), color=get_color_from_hex(C_SUB), font_name=self.app.font_name, halign='right'))
            row2.add_widget(action_btn('الملفات', C_BLUE, lambda x, i=sid, d=s: self._manage_pdfs(i, d), dp(28)))
            card.add_widget(row2)
            self.sub_inner.add_widget(card)

    # ❸ إعدادات الأدمن
    def build_admin_settings_tab(self):
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        self.content.add_widget(layout)
        settings = FirebaseManager.get_admin_settings()
        
        layout.add_widget(Label(text=ar('إعدادات النظام'), font_size=dp(16), bold=True, font_name=self.app.font_name, color=get_color_from_hex(C_YELLOW), halign='right'))
        layout.add_widget(Label(text=ar('اسم المركز:'), font_name=self.app.font_name, color=get_color_from_hex(C_SUB), halign='right'))
        name_in = TextInput(text=settings.get('center_name',''), font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        layout.add_widget(name_in)
        
        layout.add_widget(Label(text=ar('كلمة السر الحالية للطلاب:'), font_name=self.app.font_name, color=get_color_from_hex(C_SUB), halign='right'))
        layout.add_widget(Label(text=f"123456", font_name=self.app.font_name, color=(1,1,1,1))) # توضيح
        
        def save(x):
            FirebaseManager.save_admin_settings({'center_name': name_in.text, 'theme': 'dark'})
            self.switch_tab(2)

        layout.add_widget(action_btn('حفظ البيانات', C_GREEN, save, dp(48)))

    # --- Dialogs & Functions ---
    def show_edit_student_dialog(self, code, data):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        content.add_widget(Label(text=ar(f'تعديل بيانات: {data["name"]}'), font_name=self.app.font_name, bold=True))
        n_in = TextInput(text=data['name'], font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        p_in = TextInput(text=data.get('password',''), font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        content.add_widget(n_in); content.add_widget(p_in)
        popup = Popup(title='', content=content, size_hint=(0.85, 0.5), separator_height=0)
        def save(x):
            FirebaseManager.save_student(code, {'name': n_in.text, 'password': p_in.text, 'materials': data.get('materials',[])})
            popup.dismiss(); self._refresh_student_settings()
        content.add_widget(action_btn('تحديث', C_BLUE, save))
        popup.open()

    def show_add_student_dialog(self, *a):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        n_in = TextInput(hint_text=ar('الاسم'), font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        c_in = TextInput(hint_text=ar('الكود'), font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        p_in = TextInput(hint_text=ar('الرمز'), font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        for i in [n_in, c_in, p_in]: content.add_widget(i)
        popup = Popup(title='', content=content, size_hint=(0.85, 0.6), separator_height=0)
        def save(x):
            if n_in.text and c_in.text:
                FirebaseManager.save_student(c_in.text, {'name': n_in.text, 'password': p_in.text, 'materials': []})
                popup.dismiss(); self._refresh_student_settings()
        content.add_widget(action_btn('إضافة', C_GREEN, save))
        popup.open()

    def _del_student(self, c): FirebaseManager.delete_student(c); self._refresh_student_settings()
    def _approve_reg(self, c): FirebaseManager.approve_request(c); self._refresh_student_settings()
    def _reject_reg(self, c): FirebaseManager.reject_request(c); self._refresh_student_settings()
    def _approve_pdf(self, p, c): FirebaseManager.approve_pdf_access(p, c); self._refresh_student_settings()
    
    def _post_ann(self, *a):
        txt = self.ann_in.text.strip()
        if txt: FirebaseManager.add_announcement(txt); self.ann_in.text = ''; self._refresh_student_settings()

    def show_add_subject_dialog(self, *a):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        n_in = TextInput(hint_text=ar('اسم المادة'), font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        d_in = TextInput(hint_text=ar('الدكتور'), font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        content.add_widget(n_in); content.add_widget(d_in)
        popup = Popup(title='', content=content, size_hint=(0.85, 0.5), separator_height=0)
        def save(x):
            if n_in.text:
                FirebaseManager.save_subject(str(int(time.time())), n_in.text, d_in.text)
                popup.dismiss(); self._refresh_subs()
        content.add_widget(action_btn('حفظ', C_GREEN, save))
        popup.open()

    def _del_sub(self, i): FirebaseManager.delete_subject(i); self._refresh_subs()

    def _manage_pdfs(self, sid, sdata):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        content.add_widget(Label(text=ar(f"ملفات: {sdata['name']}"), font_name=self.app.font_name, bold=True))
        scroll = ScrollView(); inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        inner.bind(minimum_height=inner.setter('height')); scroll.add_widget(inner)
        all_pdfs = FirebaseManager.get_pdfs(); sub_pdfs = sdata.get('pdfs',[])
        for pid in sub_pdfs:
            if pid in all_pdfs:
                row = BoxLayout(size_hint_y=None, height=dp(35)); make_card_bg(row, '#334155')
                row.add_widget(Label(text=ar(all_pdfs[pid]['title']), font_name=self.app.font_name, halign='right'))
                inner.add_widget(row)
        content.add_widget(scroll)
        popup = Popup(title='', content=content, size_hint=(0.9, 0.7), separator_height=0)
        content.add_widget(action_btn('رفع ملف', C_GREEN, lambda x: self.show_upload_pdf_dialog(sid), dp(40)))
        content.add_widget(action_btn('إغلاق', '#64748b', lambda x: popup.dismiss(), dp(40)))
        popup.open()

    def show_upload_pdf_dialog(self, sid):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        t_i = TextInput(hint_text=ar('العنوان'), font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        u_i = TextInput(hint_text=ar('الرابط'), font_name=self.app.font_name, multiline=False, height=dp(42), size_hint_y=None, halign='right')
        content.add_widget(t_i); content.add_widget(u_i)
        popup = Popup(title='', content=content, size_hint=(0.85, 0.5), separator_height=0)
        def save(x):
            pid = f"pdf_{int(time.time())}"
            FirebaseManager.save_pdf(pid, t_i.text, u_i.text, True)
            FirebaseManager.add_pdf_to_subject(sid, pid)
            popup.dismiss(); self._refresh_subs()
        content.add_widget(action_btn('رفع', C_BLUE, save))
        popup.open()

    def _update_badge(self):
        t = len(FirebaseManager.get_pending_requests()) + len(FirebaseManager.get_pdf_download_requests())
        self.badge.text = f'({t})' if t > 0 else ''

    def logout(self, *a):
        self.app.user_role = 'guest'; self.manager.current = 'login'
