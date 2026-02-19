# test_system.py - نسخة معدلة لتناسب منطق طلبات الـ PDF
import sys
import os

sys.path.insert(0, os.path.abspath('.'))
from utils.firebase_manager import FirebaseManager

def run_test():
    print("--- Starting MyStudent System Test (Local Mode) ---")
    
    test_student_code = "TEST_999"
    test_student_name = "Test Student"
    test_password = "password123"
    
    # 1. Registration Request
    print("\n1. Testing Registration Request:")
    ok, msg = FirebaseManager.submit_registration_request(test_student_code, test_student_name, test_password)
    print(f"   Result: {'PASS' if ok else 'FAIL'}")
    
    # 2. Check Pending
    pending = FirebaseManager.get_pending_requests()
    if test_student_code in pending:
        print("   PASS: Student in pending requests.")
    else:
        print("   FAIL: Student not in pending.")

    # 3. Admin Approval
    print("\n2. Testing Admin Approval:")
    ok = FirebaseManager.approve_request(test_student_code)
    print(f"   Result: {'PASS' if ok else 'FAIL'}")
    
    students = FirebaseManager.get_students()
    if test_student_code in students:
        print("   PASS: Student in official list.")
    else:
        print("   FAIL: Student not in official list.")

    # 4. Sessions
    print("\n3. Testing Active Sessions:")
    FirebaseManager.set_session(test_student_code, "Logged In Name")
    sessions = FirebaseManager.get_active_sessions()
    if test_student_code in sessions:
        print("   PASS: Session is active.")
    else:
        print("   FAIL: Session not active.")
        
    FirebaseManager.remove_session(test_student_code)
    sessions = FirebaseManager.get_active_sessions()
    if test_student_code not in sessions:
        print("   PASS: Session removed.")
    else:
        print("   FAIL: Session still exists.")

    # 5. PDF System
    print("\n4. Testing PDF System:")
    test_pdf_id = "test_doc_001"
    ok = FirebaseManager.save_pdf(test_pdf_id, "Test PDF", "http://example.com/test.pdf", requires_approval=True)
    print(f"   Upload PDF: {'PASS' if ok else 'FAIL'}")
    
    # طلب الوصول يرجع False عادة لأنه ينتظر موافقة الأدمن
    ok, msg = FirebaseManager.request_pdf_access(test_pdf_id, test_student_code)
    print(f"   Request Access (Should be 'Request sent'): {msg}")
    
    # موافقة الأدمن
    ok = FirebaseManager.approve_pdf_access(test_pdf_id, test_student_code)
    print(f"   Approve Access: {'PASS' if ok else 'FAIL'}")
    
    # التحقق من الصلاحية بعد الموافقة
    ok_now, msg_now = FirebaseManager.request_pdf_access(test_pdf_id, test_student_code)
    if ok_now:
        print("   PASS: Access officially granted.")
    else:
        print("   FAIL: Access still not granted.")

    # 6. Cleanup
    print("\n--- Cleaning up ---")
    FirebaseManager.delete_student(test_student_code)
    FirebaseManager.delete_pdf(test_pdf_id)
    print("   Test data cleared.")
    print("\nSYSTEM TEST COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_test()
