# utils/firebase_manager.py - محرك البيانات السحابي (Live Firebase Connection)
import json
from datetime import datetime
from kivy.network.urlrequest import UrlRequest
from functools import partial

# ملاحظة: سنستخدم الـ REST API الخاص بـ Firebase للربط السحابي
FIREBASE_URL = "https://mystudent-syste-default-rtdb.firebaseio.com/"

class FirebaseManager:
    """ محرك لإدارة البيانات عبر Firebase Realtime Database أونلاين """

    @staticmethod
    def _call_api(path, method="GET", data=None, on_success=None, on_failure=None):
        """ دالة مساعدة للاتصال بـ Firebase REST API """
        url = f"{FIREBASE_URL}{path}.json"
        body = json.dumps(data) if data else None
        
        # استخدام UrlRequest لضمان عدم تعليق واجهات التطبيق (Non-blocking)
        req = UrlRequest(
            url,
            method=method,
            req_body=body,
            on_success=lambda r, result: on_success(result) if on_success else None,
            on_failure=lambda r, err: on_failure(err) if on_failure else print(f"API Error: {err}"),
            on_error=lambda r, err: print(f"Network Error: {err}")
        )
        return req

    # ملاحظة سرية: لجعل التطبيق يعمل بنفس المنطق "المتزامن" للـ UI الحالي 
    # سنستخدم استراتيجية سريعة وهي جلب البيانات محلياً أول مرة وحفظها لتقليل الطلبات.
    # ولكن في النسخة النهائية يفضل استخدام Async/Callback.
    
    # سنقوم الآن بتعديل الدوال لتكون متوافقة مع منطق الواجهات الحالي 
    # (مؤقتاً سنقوم بمحاكاة العمل عبر طلبات مباشرة لجعل التطبيق "يعمل" فوراً)
    
    # ملاحظة هامة: نظراً لطبيعة Kivy الـ asynchronous، 
    # سأقوم بتعديل بسيط جداً ليتناسب مع الكود الحالي دون كسر الواجهات.

    _cached_db = {}

    @staticmethod
    def sync_data(on_finish=None):
        """ جلب نسخة كاملة من البيانات عند بدء التطبيق """
        def success(res):
            FirebaseManager._cached_db = res if res else {}
            if on_finish: on_finish()
        FirebaseManager._call_api("", "GET", on_success=success)

    @staticmethod
    def get_students():
        return FirebaseManager._cached_db.get('students', {})

    @staticmethod
    def save_student(code, student_data):
        FirebaseManager._cached_db.setdefault('students', {})[code] = student_data
        FirebaseManager._call_api(f"students/{code}", "PUT", data=student_data)
        return True

    @staticmethod
    def delete_student(code):
        if code in FirebaseManager._cached_db.get('students', {}):
            del FirebaseManager._cached_db['students'][code]
            FirebaseManager._call_api(f"students/{code}", "DELETE")
            return True
        return False

    @staticmethod
    def get_pending_requests():
        return FirebaseManager._cached_db.get('pending_requests', {})

    @staticmethod
    def submit_registration_request(code, name, password):
        db = FirebaseManager._cached_db
        if code in db.get('students', {}) or code in db.get('pending_requests', {}):
            return False, "موجود مسبقاً"
        
        req_data = {
            'name': name, 'password': password,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'status': 'pending'
        }
        db.setdefault('pending_requests', {})[code] = req_data
        FirebaseManager._call_api(f"pending_requests/{code}", "PUT", data=req_data)
        return True, "تم الإرسال"

    @staticmethod
    def approve_request(code):
        pending = FirebaseManager._cached_db.get('pending_requests', {})
        if code in pending:
            req = pending[code]
            student_data = {'name': req['name'], 'password': req['password'], 'materials': []}
            FirebaseManager.save_student(code, student_data)
            FirebaseManager.reject_request(code) # حذف من المعلق
            return True
        return False

    @staticmethod
    def reject_request(code):
        if code in FirebaseManager._cached_db.get('pending_requests', {}):
            del FirebaseManager._cached_db['pending_requests'][code]
            FirebaseManager._call_api(f"pending_requests/{code}", "DELETE")
            return True
        return False

    @staticmethod
    def get_pdfs():
        return FirebaseManager._cached_db.get('pdfs', {})

    @staticmethod
    def save_pdf(pdf_id, title, url, requires_approval=True):
        pdata = {
            'title': title, 'url': url, 'requires_approval': requires_approval,
            'approved_students': [], 'pending_download_requests': [],
            'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        FirebaseManager._cached_db.setdefault('pdfs', {})[pdf_id] = pdata
        FirebaseManager._call_api(f"pdfs/{pdf_id}", "PUT", data=pdata)
        return True

    @staticmethod
    def delete_pdf(pdf_id):
        if pdf_id in FirebaseManager._cached_db.get('pdfs', {}):
            del FirebaseManager._cached_db['pdfs'][pdf_id]
            FirebaseManager._call_api(f"pdfs/{pdf_id}", "DELETE")
            return True
        return False

    @staticmethod
    def request_pdf_access(pdf_id, student_code):
        pdfs = FirebaseManager._cached_db.get('pdfs', {})
        if pdf_id not in pdfs: return False, "غير موجود"
        
        pdf = pdfs[pdf_id]
        pending = pdf.setdefault('pending_download_requests', [])
        if student_code not in pending:
            pending.append(student_code)
            FirebaseManager._call_api(f"pdfs/{pdf_id}/pending_download_requests", "PUT", data=pending)
        return False, "تم إرسال الطلب"

    @staticmethod
    def approve_pdf_access(pdf_id, student_code):
        pdf = FirebaseManager._cached_db.get('pdfs', {}).get(pdf_id)
        if pdf:
            approved = pdf.setdefault('approved_students', [])
            if student_code not in approved: approved.append(student_code)
            
            pending = pdf.get('pending_download_requests', [])
            if student_code in pending: pending.remove(student_code)
            
            FirebaseManager._call_api(f"pdfs/{pdf_id}", "PUT", data=pdf)
            return True
        return False

    @staticmethod
    def get_pdf_download_requests():
        all_reqs = []
        for pid, pdf in FirebaseManager._cached_db.get('pdfs', {}).items():
            for scode in pdf.get('pending_download_requests', []):
                all_reqs.append({'pdf_id': pid, 'pdf_title': pdf['title'], 'student_code': scode})
        return all_reqs

    @staticmethod
    def get_subjects():
        return FirebaseManager._cached_db.get('subjects', {})

    @staticmethod
    def save_subject(sub_id, name, doctor):
        s_data = {
            'name': name, 'doctor': doctor,
            'pdfs': FirebaseManager._cached_db.get('subjects', {}).get(sub_id, {}).get('pdfs', [])
        }
        FirebaseManager._cached_db.setdefault('subjects', {})[sub_id] = s_data
        FirebaseManager._call_api(f"subjects/{sub_id}", "PUT", data=s_data)
        return True

    @staticmethod
    def delete_subject(sub_id):
        if sub_id in FirebaseManager._cached_db.get('subjects', {}):
            del FirebaseManager._cached_db['subjects'][sub_id]
            FirebaseManager._call_api(f"subjects/{sub_id}", "DELETE")
            return True
        return False

    @staticmethod
    def add_pdf_to_subject(sub_id, pdf_id):
        subs = FirebaseManager._cached_db.get('subjects', {})
        if sub_id in subs:
            pdfs = subs[sub_id].setdefault('pdfs', [])
            if pdf_id not in pdfs:
                pdfs.append(pdf_id)
                FirebaseManager._call_api(f"subjects/{sub_id}/pdfs", "PUT", data=pdfs)
                return True
        return False

    @staticmethod
    def get_announcements():
        return FirebaseManager._cached_db.get('announcements', [])

    @staticmethod
    def add_announcement(text):
        anns = FirebaseManager._cached_db.get('announcements', [])
        ann_data = {
            'id': f"ann_{int(datetime.now().timestamp())}",
            'text': text, 'time': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        anns.insert(0, ann_data)
        FirebaseManager._cached_db['announcements'] = anns
        FirebaseManager._call_api("announcements", "PUT", data=anns)
        return True

    @staticmethod
    def get_admin_settings():
        return FirebaseManager._cached_db.get('admin_settings', {'center_name': 'MyStudent Center', 'theme': 'dark'})

    @staticmethod
    def save_admin_settings(settings):
        FirebaseManager._cached_db['admin_settings'] = settings
        FirebaseManager._call_api("admin_settings", "PUT", data=settings)
        return True

    @staticmethod
    def change_password(code, new_password):
        students = FirebaseManager._cached_db.get('students', {})
        if code in students:
            students[code]['password'] = new_password
            FirebaseManager._call_api(f"students/{code}/password", "PUT", data=new_password)
            return True
        return False

    @staticmethod
    def remove_session(code): pass
    @staticmethod
    def get_active_sessions(): return {}
