from db import db
import datetime
import json
import time

class AuthController:
    @staticmethod
    def login(username, password):
        conn = db.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            query = "SELECT userID, fullName, role FROM [User] WHERE username = ? AND password = ?"
            cursor.execute(query, (username, password))
            row = cursor.fetchone()
            if row:
                return {"id": row.userID, "name": row.fullName, "role": row.role}
        finally:
            conn.close()
        return None

class ClassController:
    @staticmethod
    def get_classes_by_professor(user_id):
        conn = db.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
            SELECT c.classID, c.className,
                (SELECT COUNT(*) FROM Enrollment e WHERE e.classID = c.classID) as studentCount
            FROM CourseClass c
            JOIN Professor p ON c.professorID = p.professorID
            WHERE p.userID = ?
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            return [{"id": r.classID, "name": r.className, "count": r.studentCount} for r in rows]
        finally:
            conn.close()

class AttendanceController:
    # --- Lấy danh sách các phiên đã có để hiển thị Dropdown ---
    @staticmethod
    def get_class_sessions(class_id):
        conn = db.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            # Lấy danh sách phiên, sắp xếp mới nhất lên đầu
            cursor.execute("SELECT sessionID, sessionDate, status FROM AttendanceSession WHERE classID = ? ORDER BY sessionDate DESC", (class_id,))
            rows = cursor.fetchall()
            result = []
            for r in rows:
                result.append({
                    "session_id": r.sessionID,
                    "date_str": r.sessionDate.strftime("%d/%m/%Y"),
                    "date_obj": r.sessionDate.date(),
                    "status": r.status
                })
            return result
        finally:
            conn.close()

    @staticmethod
    def get_student_list(class_id, session_date=None):
        conn = db.get_connection()
        if not conn: return [], None, 'Closed'
        
        # Mặc định là hôm nay nếu không chọn ngày
        if session_date is None:
            session_date = datetime.date.today()
        
        # Đảm bảo kiểu dữ liệu là date
        if isinstance(session_date, datetime.datetime):
            session_date = session_date.date()

        session_id = None
        session_status = 'Closed'
        
        try:
            cursor = conn.cursor()
            # 1. Tìm phiên điểm danh theo ngày được chọn
            cursor.execute("SELECT sessionID, status FROM AttendanceSession WHERE classID = ? AND CAST(sessionDate AS DATE) = ?", (class_id, session_date))
            row = cursor.fetchone()
            
            if row:
                session_id = row.sessionID
                session_status = row.status
            else:
                session_id = None
                session_status = 'Closed'

            # 2. Lấy danh sách SV
            query = """
            SELECT s.studentID, u.fullName, ar.status
            FROM Student s
            JOIN [User] u ON s.userID = u.userID
            JOIN Enrollment e ON s.studentID = e.studentID
            LEFT JOIN AttendanceRecord ar ON s.studentID = ar.studentID AND ar.sessionID = ?
            WHERE e.classID = ?
            """
            cursor.execute(query, (session_id, class_id))
            rows = cursor.fetchall()
            
            students = []
            for r in rows:
                status_map = {'Present': 'present', 'Absent': 'absent', 'Late': 'late', 'Excused': 'excused'}
                students.append({
                    "id": r.studentID, "name": r.fullName,
                    "status": status_map.get(r.status, 'none'),
                    "session_id": session_id
                })
            return students, session_id, session_status
        finally:
            conn.close()

    @staticmethod
    def create_daily_session(class_id):
        conn = db.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            today = datetime.date.today()
            
            # Kiểm tra xem đã có phiên hôm nay chưa
            cursor.execute("SELECT sessionID FROM AttendanceSession WHERE classID = ? AND CAST(sessionDate AS DATE) = ?", (class_id, today))
            row = cursor.fetchone()
            
            session_id = f"SES-{class_id}-{today.strftime('%Y%m%d')}"
            
            if row:
                # Nếu đã có -> Mở lại
                cursor.execute("UPDATE AttendanceSession SET status = 'Open' WHERE sessionID = ?", (session_id,))
            else:
                # Nếu chưa có -> Tạo mới
                cursor.execute("INSERT INTO AttendanceSession (sessionID, classID, sessionDate, status) VALUES (?, ?, ?, 'Open')",
                            (session_id, class_id, datetime.datetime.now()))
            
            conn.commit()
            return session_id
        except Exception as e:
            print(e)
            return None
        finally:
            conn.close()

    @staticmethod
    def update_session_status(session_id, new_status):
        conn = db.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE AttendanceSession SET status = ? WHERE sessionID = ?", (new_status, session_id))
            conn.commit()
            return True
        finally: conn.close()

    @staticmethod
    def update_attendance(session_id, student_id, new_status):
        if not session_id: return False
        conn = db.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            db_status = {
                'present': 'Present', 'absent': 'Absent', 'late': 'Late', 'excused': 'Excused', 'none': None
            }.get(new_status)
            
            cursor.execute("SELECT attendanceID FROM AttendanceRecord WHERE sessionID = ? AND studentID = ?", (session_id, student_id))
            existed = cursor.fetchone() is not None

            if new_status == 'none':
                if existed:
                    cursor.execute("DELETE FROM AttendanceRecord WHERE sessionID = ? AND studentID = ?", (session_id, student_id))
            else:
                if existed:
                    cursor.execute("UPDATE AttendanceRecord SET status = ?, checkinTime = GETDATE() WHERE sessionID = ? AND studentID = ?", (db_status, session_id, student_id))
                else:
                    att_id = f"ATT-{session_id}-{student_id}"
                    cursor.execute("INSERT INTO AttendanceRecord (attendanceID, sessionID, studentID, status, checkinMethod, checkinTime) VALUES (?, ?, ?, ?, 'Manual', GETDATE())", (att_id, session_id, student_id, db_status))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def get_statistics(class_id):
        conn = db.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
            SELECT s.studentID, u.fullName,
                COUNT(CASE WHEN ar.status = 'Present' THEN 1 END) as presentCount
            FROM Student s
            JOIN [User] u ON s.userID = u.userID
            JOIN Enrollment e ON s.studentID = e.studentID
            LEFT JOIN AttendanceRecord ar ON s.studentID = ar.studentID 
                AND ar.sessionID IN (SELECT sessionID FROM AttendanceSession WHERE classID = ?)
            WHERE e.classID = ?
            GROUP BY s.studentID, u.fullName
            """
            cursor.execute(query, (class_id, class_id))
            rows = cursor.fetchall()
            
            cursor.execute("SELECT COUNT(*) FROM AttendanceSession WHERE classID = ?", (class_id,))
            total_sessions = cursor.fetchone()[0]
            if total_sessions == 0: total_sessions = 1

            stats = []
            for r in rows:
                rate = int((r.presentCount / total_sessions) * 100)
                stats.append({"id": r.studentID, "name": r.fullName, "attended": r.presentCount, "rate": rate})
            return stats
        finally:
            conn.close()

    @staticmethod
    def generate_qr_content(class_id):
        session_id = AttendanceController.create_daily_session(class_id)
        if not session_id: return None
        import json, time
        qr_data = {"type": "attendance", "sid": session_id, "cid": class_id, "exp": time.time() + 300}
        return json.dumps(qr_data)
class AdminController:
    # --- CRUD ADMIN ---
    @staticmethod
    def _next_id(prefix, existing_ids):
        max_n = 0
        for _id in existing_ids:
            if not _id or not str(_id).startswith(prefix): continue
            s = str(_id)[len(prefix):]
            if ''.join(filter(str.isdigit, s)): 
                max_n = max(max_n, int(''.join(filter(str.isdigit, s))))
        return f"{prefix}{max_n + 1:04d}"

    @staticmethod
    def dashboard_counts():
        conn = db.get_connection()
        if not conn: return {}
        try:
            c = conn.cursor()
            def scalar(q):
                c.execute(q)
                r = c.fetchone()
                return int(r[0]) if r and r[0] is not None else 0
            return {
                "users": scalar("SELECT COUNT(*) FROM [User]"),
                "students": scalar("SELECT COUNT(*) FROM Student"),
                "professors": scalar("SELECT COUNT(*) FROM Professor"),
                "classes": scalar("SELECT COUNT(*) FROM CourseClass"),
                "sessions": scalar("SELECT COUNT(*) FROM AttendanceSession"),
            }
        finally: conn.close()

    @staticmethod
    def list_users(keyword=None):
        conn = db.get_connection()
        if not conn: return []
        try:
            c = conn.cursor()
            if keyword:
                kw = f"%{keyword}%"
                c.execute("SELECT userID, username, fullName, email, role FROM [User] WHERE username LIKE ? OR fullName LIKE ? OR role LIKE ? ORDER BY username", (kw, kw, kw))
            else:
                c.execute("SELECT userID, username, fullName, email, role FROM [User] ORDER BY username")
            rows = c.fetchall()
            return [{"userID": r.userID, "username": r.username, "fullName": r.fullName, "email": r.email, "role": r.role} for r in rows]
        finally: conn.close()

    @staticmethod
    def create_user(username, password, full_name, email, role, linked_id=None):
        conn = db.get_connection()
        if not conn: return (False, "Lỗi DB")
        try:
            c = conn.cursor()
            c.execute("SELECT userID FROM [User]")
            ids = [r[0] for r in c.fetchall()]
            user_id = AdminController._next_id("U-", ids)
            c.execute("INSERT INTO [User] (userID, username, password, fullName, email, role) VALUES (?, ?, ?, ?, ?, ?)", (user_id, username, password, full_name, email, role))
            
            if role.lower() == 'student':
                if not linked_id:
                    c.execute("SELECT studentID FROM Student")
                    linked_id = AdminController._next_id("S-", [r[0] for r in c.fetchall()])
                c.execute("INSERT INTO Student (studentID, userID) VALUES (?, ?)", (linked_id, user_id))
            elif role.lower() == 'professor':
                if not linked_id:
                    c.execute("SELECT professorID FROM Professor")
                    linked_id = AdminController._next_id("P-", [r[0] for r in c.fetchall()])
                c.execute("INSERT INTO Professor (professorID, userID) VALUES (?, ?)", (linked_id, user_id))
            conn.commit()
            return (True, user_id)
        except Exception as e: return (False, str(e))
        finally: conn.close()

    @staticmethod
    def update_user(user_id, username, password, full_name, email, role):
        conn = db.get_connection()
        if not conn: return (False, "Lỗi DB")
        try:
            c = conn.cursor()
            c.execute("UPDATE [User] SET username=?, password=?, fullName=?, email=?, role=? WHERE userID=?", (username, password, full_name, email, role, user_id))
            conn.commit()
            return (True, "OK")
        except Exception as e: return (False, str(e))
        finally: conn.close()

    @staticmethod
    def delete_user(user_id):
        conn = db.get_connection()
        if not conn: return (False, "Lỗi DB")
        try:
            c = conn.cursor()
            c.execute("DELETE FROM [User] WHERE userID=?", (user_id,))
            conn.commit()
            return (True, "OK")
        except Exception as e: return (False, str(e))
        finally: conn.close()

    # --- CLASSES ---
    @staticmethod
    def list_classes(keyword=None):
        conn = db.get_connection()
        if not conn: return []
        try:
            c = conn.cursor()
            query = """SELECT c.classID, c.className, c.room, c.startTime, c.endTime, p.professorID, u.fullName
                    FROM CourseClass c LEFT JOIN Professor p ON c.professorID=p.professorID LEFT JOIN [User] u ON p.userID=u.userID"""
            if keyword:
                kw = f"%{keyword}%"
                query += " WHERE c.classID LIKE ? OR c.className LIKE ? OR u.fullName LIKE ?"
                c.execute(query + " ORDER BY c.classID", (kw, kw, kw))
            else:
                c.execute(query + " ORDER BY c.classID")
            rows = c.fetchall()
            return [{"classID": r.classID, "className": r.className, "room": r.room, "startTime": str(r.startTime), "endTime": str(r.endTime), "professorID": r.professorID, "professorName": r.fullName} for r in rows]
        finally: conn.close()

    @staticmethod
    def list_professors():
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT p.professorID, u.fullName FROM Professor p JOIN [User] u ON p.userID=u.userID ORDER BY u.fullName")
            return [{"id": r.professorID, "name": r.fullName} for r in c.fetchall()]
        finally: conn.close()

    @staticmethod
    def create_class(class_name, professor_id=None, room=None, start_time=None, end_time=None):
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT classID FROM CourseClass")
            ids = [r[0] for r in c.fetchall()]
            class_id = AdminController._next_id("C-", ids)
            c.execute("INSERT INTO CourseClass (classID, className, professorID, room, startTime, endTime) VALUES (?, ?, ?, ?, ?, ?)", (class_id, class_name, professor_id, room, start_time, end_time))
            conn.commit()
            return (True, class_id)
        except Exception as e: return (False, str(e))
        finally: conn.close()

    @staticmethod
    def update_class(class_id, class_name, professor_id=None, room=None, start_time=None, end_time=None):
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("UPDATE CourseClass SET className=?, professorID=?, room=?, startTime=?, endTime=? WHERE classID=?", (class_name, professor_id, room, start_time, end_time, class_id))
            conn.commit()
            return (True, "OK")
        except Exception as e: return (False, str(e))
        finally: conn.close()

    @staticmethod
    def delete_class(class_id):
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("DELETE FROM CourseClass WHERE classID=?", (class_id,))
            conn.commit()
            return (True, "OK")
        except Exception as e: return (False, str(e))
        finally: conn.close()

    @staticmethod
    def list_enrollments_by_class(class_id):
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT e.enrollmentID, s.studentID, u.fullName FROM Enrollment e JOIN Student s ON e.studentID=s.studentID JOIN [User] u ON s.userID=u.userID WHERE e.classID=? ORDER BY u.fullName", (class_id,))
            return [{"enrollmentID": r.enrollmentID, "studentID": r.studentID, "name": r.fullName} for r in c.fetchall()]
        finally: conn.close()

    @staticmethod
    def list_students():
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT s.studentID, u.fullName FROM Student s JOIN [User] u ON s.userID=u.userID ORDER BY u.fullName")
            return [{"id": r.studentID, "name": r.fullName} for r in c.fetchall()]
        finally: conn.close()

    @staticmethod
    def add_enrollment(class_id, student_id):
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("INSERT INTO Enrollment (classID, studentID) VALUES (?, ?)", (class_id, student_id))
            conn.commit()
            return (True, "OK")
        except Exception as e: return (False, str(e))
        finally: conn.close()
    
    @staticmethod
    def remove_enrollment(enrollment_id):
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("DELETE FROM Enrollment WHERE enrollmentID=?", (enrollment_id,))
            conn.commit()
            return (True, "OK")
        except Exception as e: return (False, str(e))
        finally: conn.close()


class StudentController:
    @staticmethod
    def get_student_id(user_id):
        if not user_id: return None
        conn = db.get_connection()
        if not conn: return None
        try:
            c = conn.cursor()
            c.execute("SELECT studentID FROM Student WHERE userID=?", (user_id,))
            r = c.fetchone()
            return r[0] if r else None
        finally: conn.close()

    @staticmethod
    def list_enrolled_classes(student_id):
        conn = db.get_connection()
        if not conn: return []
        try:
            c = conn.cursor()
            c.execute("""SELECT c.classID, c.className FROM Enrollment e JOIN CourseClass c ON e.classID = c.classID WHERE e.studentID = ? ORDER BY c.className""", (student_id,))
            return [{"classID": r.classID, "className": r.className} for r in c.fetchall()]
        finally: conn.close()

    @staticmethod
    def upcoming_sessions(student_id, days=30):
        """Lấy danh sách các buổi học. Cho phép Checkin nếu session Open (kể cả đã checkin rồi để update)"""
        conn = db.get_connection()
        if not conn: return []
        try:
            c = conn.cursor()
            start = datetime.datetime.now()
            end = start + datetime.timedelta(days=int(days or 30))
            c.execute("""
                SELECT s.sessionID, s.classID, s.sessionDate, s.status,
                    cc.className, cc.room, cc.startTime, cc.endTime,
                    pu.fullName AS profName, ar.status AS attendStatus
                FROM Enrollment e
                JOIN AttendanceSession s ON e.classID = s.classID
                JOIN CourseClass cc ON s.classID = cc.classID
                LEFT JOIN Professor p ON cc.professorID = p.professorID
                LEFT JOIN [User] pu ON p.userID = pu.userID
                LEFT JOIN AttendanceRecord ar ON ar.sessionID = s.sessionID AND ar.studentID = e.studentID
                WHERE e.studentID = ? AND s.sessionDate >= ? AND s.sessionDate <= ?
                ORDER BY s.sessionDate ASC
            """, (student_id, start, end))
            rows = c.fetchall()
            out = []
            today = datetime.date.today()
            for r in rows:
                dt = r.sessionDate
                time_text = None
                if r.startTime and r.endTime: time_text = f"{str(r.startTime)[:5]}-{str(r.endTime)[:5]}"
                
                # Logic: Nút hiện nếu ĐÚNG NGÀY + OPEN (Bất kể đã điểm danh chưa)
                can_checkin = (dt.date() == today) and (str(r.status).lower() == 'open')
                
                out.append({
                    "sessionID": r.sessionID, "classID": r.classID, "sessionDate": dt,
                    "sessionStatus": r.status, "className": r.className, "room": r.room,
                    "profName": r.profName, "timeText": time_text, "canCheckin": can_checkin,
                })
            return out
        finally: conn.close()

    @staticmethod
    def attendance_history(student_id, class_id):
        conn = db.get_connection()
        try:
            c = conn.cursor()
            c.execute("""
                SELECT s.sessionID, s.sessionDate, s.status AS sessionStatus,
                    cc.room, cc.startTime, cc.endTime,
                    ar.status AS attendStatus, ar.checkinTime
                FROM AttendanceSession s
                JOIN CourseClass cc ON s.classID = cc.classID
                LEFT JOIN AttendanceRecord ar ON ar.sessionID = s.sessionID AND ar.studentID = ?
                WHERE s.classID = ?
                ORDER BY s.sessionDate DESC
            """, (student_id, class_id))
            rows = c.fetchall()
            out = []
            counts = {"present": 0, "absent": 0, "late": 0, "excused": 0}
            for r in rows:
                time_text = None
                if r.startTime and r.endTime: time_text = f"{str(r.startTime)[:5]}-{str(r.endTime)[:5]}"
                st = r.attendStatus
                if st == 'Present': counts["present"] += 1
                elif st == 'Absent': counts["absent"] += 1
                elif st == 'Late': counts["late"] += 1
                elif st == 'Excused': counts["excused"] += 1
                out.append({
                    "sessionID": r.sessionID, "sessionDate": r.sessionDate, "room": r.room,
                    "timeText": time_text, "sessionStatus": r.sessionStatus,
                    "attendStatus": r.attendStatus, "checkinTime": r.checkinTime,
                })
            return out, counts
        finally: conn.close()

    @staticmethod
    def check_in(session_id, student_id, method='Click'):
        """Điểm danh sinh viên. Hỗ trợ Update nếu đã tồn tại."""
        conn = db.get_connection()
        if not conn: return (False, "Lỗi DB")
        try:
            c = conn.cursor()
            c.execute("SELECT sessionDate, status FROM AttendanceSession WHERE sessionID=?", (session_id,))
            r = c.fetchone()
            if not r: return (False, "Phiên không tồn tại")
            if str(r[1]).lower() != 'open': return (False, "Phiên đã đóng")
            if r[0].date() != datetime.date.today(): return (False, "Sai ngày")

            c.execute("SELECT attendanceID FROM AttendanceRecord WHERE sessionID=? AND studentID=?", (session_id, student_id))
            existed = c.fetchone()
            if existed:
                c.execute("UPDATE AttendanceRecord SET status='Present', checkinMethod=?, checkinTime=GETDATE() WHERE sessionID=? AND studentID=?", (method, session_id, student_id))
                conn.commit()
                return (True, "Cập nhật thành công!")
            else:
                att_id = f"ATT-{session_id}-{student_id}"
                c.execute("INSERT INTO AttendanceRecord (attendanceID, sessionID, studentID, status, checkinMethod, checkinTime) VALUES (?, ?, ?, 'Present', ?, GETDATE())", (att_id, session_id, student_id, method))
                conn.commit()
                return (True, "Điểm danh thành công!")
        except Exception as e: 
            try: conn.rollback() 
            except: pass
            return (False, str(e))
        finally: conn.close()
