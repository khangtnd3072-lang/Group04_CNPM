import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from controllers import StudentController

# --- MÀU SẮC ---
COLOR_BG_MAIN = "#F5F7FA"
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT_PRIMARY = "#1F2937"
COLOR_TEXT_SECONDARY = "#6B7280"
COLOR_ACCENT_GREEN = "#10B981"
COLOR_BG_GREEN = "#D1FAE5"
COLOR_ACCENT_RED = "#EF4444"
COLOR_BG_RED = "#FEE2E2"
COLOR_ACCENT_YELLOW = "#F59E0B"
COLOR_BG_YELLOW = "#FEF3C7"
COLOR_BLUE = "#2563EB"

class StudentView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG_MAIN)
        self.controller = controller
        self.student_id = None
        self.current_user_name = "Sinh viên"
        
        self.grid_columnconfigure(0, weight=3) # Sidebar
        self.grid_columnconfigure(1, weight=7) # Main
        self.grid_rowconfigure(1, weight=1)

        self._setup_header()

        # Sidebar
        self.sidebar = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        ctk.CTkLabel(self.sidebar, text="Môn học của bạn", font=("Arial", 16, "bold"), text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 10))
        self.subject_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.subject_container.pack(fill="x")

        # Main Content
        self.main_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_area.grid(row=1, column=1, sticky="nsew", padx=(0, 20), pady=10)
        
        self.detail_card = ctk.CTkFrame(self.main_area, fg_color=COLOR_WHITE, corner_radius=15)
        self.detail_card.pack(fill="both", expand=True)
        
        self.lbl_placeholder = ctk.CTkLabel(self.detail_card, text="← Chọn môn học để xem chi tiết", text_color="gray", font=("Arial", 14))
        self.lbl_placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def _setup_header(self):
        header = ctk.CTkFrame(self, fg_color=COLOR_WHITE, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        self.avatar = ctk.CTkButton(header, text="SV", width=40, height=40, corner_radius=20, fg_color="#E5E7EB", text_color="black", hover=False)
        self.avatar.pack(side="left", padx=(20, 10), pady=10)
        
        self.lbl_welcome = ctk.CTkLabel(header, text="Loading...", font=("Arial", 14, "bold"), text_color="black")
        self.lbl_welcome.pack(side="left")
        
        ctk.CTkButton(header, text="Đăng xuất", width=80, fg_color=COLOR_BG_RED, text_color=COLOR_ACCENT_RED, hover_color="#FECACA", 
                      command=self.logout).pack(side="right", padx=20)

    # --- LOGIC LOAD DỮ LIỆU ---
    def refresh_data(self):
        user = self.controller.current_user
        if not user: return
        self.current_user_name = user.get('name', 'Sinh viên')
        self.lbl_welcome.configure(text=f"Xin chào, {self.current_user_name}")
        
        self.student_id = StudentController.get_student_id(user.get('id'))
        if self.student_id:
            self._load_subject_list()
        else:
            messagebox.showwarning("Cảnh báo", "Tài khoản này chưa liên kết hồ sơ Sinh viên!")

    def _load_subject_list(self):
        for w in self.subject_container.winfo_children(): w.destroy()
        
        classes = StudentController.list_enrolled_classes(self.student_id)
        if not classes:
            ctk.CTkLabel(self.subject_container, text="Chưa đăng ký môn nào").pack()
            return

        for idx, cls in enumerate(classes):
            # Tính nhanh tỷ lệ chuyên cần
            _, counts = StudentController.attendance_history(self.student_id, cls['classID'])
            total = sum(counts.values()) if counts else 0
            rate = int((counts['present']/total)*100) if total > 0 else 100
            
            self._create_subject_card(cls, rate, is_first=(idx==0))

    def _create_subject_card(self, cls, rate, is_first):
        card = ctk.CTkFrame(self.subject_container, fg_color=COLOR_WHITE, corner_radius=10)
        card.pack(fill="x", pady=5)
        
        # Color indicator
        col = COLOR_ACCENT_GREEN if rate >= 80 else (COLOR_ACCENT_YELLOW if rate >= 50 else COLOR_ACCENT_RED)
        ctk.CTkFrame(card, width=5, fg_color=col, corner_radius=0).pack(side="left", fill="y")
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(content, text=cls['className'], font=("Arial", 13, "bold"), text_color=COLOR_TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(content, text=cls['classID'], font=("Arial", 11), text_color=COLOR_TEXT_SECONDARY).pack(anchor="w")
        
        ctk.CTkLabel(card, text=f"{rate}%", font=("Arial", 14, "bold"), text_color=col).pack(side="right", padx=15)

        # Bind click
        cmd = lambda e: self._load_detail(cls, rate)
        card.bind("<Button-1>", cmd)
        for w in [content] + content.winfo_children(): w.bind("<Button-1>", cmd)

        if is_first: self._load_detail(cls, rate)

    # --- CHI TIẾT & ĐIỂM DANH ---
    def _load_detail(self, cls, rate):
        for w in self.detail_card.winfo_children(): w.destroy()

        # 1. Header chi tiết
        header = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=20)
        
        info = ctk.CTkFrame(header, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text=cls['className'], font=("Arial", 24, "bold"), text_color=COLOR_TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Mã lớp: {cls['classID']}", font=("Arial", 14), text_color="gray").pack(anchor="w")

        # === CHECK ACTIVE SESSION ===
        active_session = None
        sessions = StudentController.upcoming_sessions(self.student_id)
        for s in sessions:
            # Logic: Đúng lớp + Đang mở (Open) + Có thể checkin (chưa điểm danh)
            if s['classID'] == cls['classID'] and s['canCheckin']:
                active_session = s
                break
        
        if active_session:
            # Nút Điểm Danh Nổi Bật
            btn = ctk.CTkButton(header, text="📍 ĐIỂM DANH NGAY", width=180, height=40,
                                fg_color=COLOR_ACCENT_GREEN, hover_color="#047857", font=("Arial", 14, "bold"),
                                command=lambda: self.open_checkin_popup(active_session, cls))
            btn.pack(side="right", padx=20)
        
        # 2. Stats Boxes
        stats_frame = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=10)
        stats_frame.grid_columnconfigure((0,1,2), weight=1)
        
        _, counts = StudentController.attendance_history(self.student_id, cls['classID'])
        if not counts: counts = {'present':0, 'absent':0, 'late':0, 'excused':0}
        
        self._stat_box(stats_frame, 0, "Có mặt", counts['present'], COLOR_BG_GREEN, COLOR_ACCENT_GREEN)
        self._stat_box(stats_frame, 1, "Vắng", counts['absent']+counts['late'], COLOR_BG_RED, COLOR_ACCENT_RED)
        self._stat_box(stats_frame, 2, "Có phép", counts['excused'], COLOR_BG_YELLOW, COLOR_ACCENT_YELLOW)

        # 3. Lịch sử Table
        ctk.CTkLabel(self.detail_card, text="Lịch sử điểm danh", font=("Arial", 16, "bold"), text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", padx=30, pady=(20, 10))
        
        # Table Header
        tbl_head = ctk.CTkFrame(self.detail_card, fg_color=COLOR_BG_MAIN, height=40)
        tbl_head.pack(fill="x", padx=30)
        cols = ["Buổi", "Ngày", "Thời gian", "Phòng", "Trạng thái", "Ghi chú"]
        wts = [1, 2, 2, 1, 2, 2]
        for i, c in enumerate(cols):
            tbl_head.grid_columnconfigure(i, weight=wts[i])
            ctk.CTkLabel(tbl_head, text=c, font=("Arial", 12, "bold"), text_color=COLOR_TEXT_SECONDARY).grid(row=0, column=i, sticky="w", padx=10, pady=10)

        # Table Body
        tbl_body = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        tbl_body.pack(fill="both", expand=True, padx=30, pady=5)
        
        history, _ = StudentController.attendance_history(self.student_id, cls['classID'])
        if not history:
            ctk.CTkLabel(tbl_body, text="Chưa có dữ liệu", text_color="gray").pack(pady=20)
        
        for idx, h in enumerate(history):
            self._history_row(tbl_body, idx, h, wts, len(history))

    def _stat_box(self, parent, col, title, val, bg, fg):
        f = ctk.CTkFrame(parent, fg_color=bg, corner_radius=10, height=80)
        f.grid(row=0, column=col, sticky="ew", padx=5)
        inner = ctk.CTkFrame(f, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(inner, text=str(val), font=("Arial", 22, "bold"), text_color=fg).pack()
        ctk.CTkLabel(inner, text=title, font=("Arial", 12), text_color=fg).pack()

    def _history_row(self, parent, idx, item, wts, total):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        date_str = item['sessionDate'].strftime("%d/%m/%Y")
        time_str = item.get('timeText') or "--:--"
        room = item.get('room') or "Online"
        
        st = item.get('attendStatus')
        st_text, st_bg, st_fg = "Vắng", COLOR_BG_RED, COLOR_ACCENT_RED
        if st == 'Present': st_text, st_bg, st_fg = "Có mặt", COLOR_BG_GREEN, COLOR_ACCENT_GREEN
        elif st == 'Excused': st_text, st_bg, st_fg = "Có phép", COLOR_BG_YELLOW, COLOR_ACCENT_YELLOW
        elif st is None: st_text, st_bg, st_fg = "Chưa có", "#F3F4F6", "gray"
        
        note = item['checkinTime'].strftime("%H:%M") if item.get('checkinTime') else "-"

        vals = [f"{total-idx:02d}", date_str, time_str, room]
        for i, v in enumerate(vals):
            row.grid_columnconfigure(i, weight=wts[i])
            ctk.CTkLabel(row, text=v, text_color="black").grid(row=0, column=i, sticky="w", padx=10)
        
        # Status Pill
        row.grid_columnconfigure(4, weight=wts[4])
        pill = ctk.CTkFrame(row, fg_color=st_bg, corner_radius=12, height=24)
        pill.grid(row=0, column=4, sticky="w", padx=10)
        ctk.CTkLabel(pill, text=f"• {st_text}", text_color=st_fg, font=("Arial", 11, "bold")).pack(padx=10, pady=2)

        row.grid_columnconfigure(5, weight=wts[5])
        ctk.CTkLabel(row, text=note, text_color="gray").grid(row=0, column=5, sticky="w", padx=10)
        
        ctk.CTkFrame(parent, height=1, fg_color="#E5E5E5").pack(fill="x")

    # ================= POPUP ĐIỂM DANH =================
    def open_checkin_popup(self, session, cls):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Điểm danh")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color="white")
        
        ctk.CTkLabel(dialog, text=f"Lớp: {cls['className']}", font=("Arial", 16, "bold"), text_color="black").pack(pady=15)
        
        tab = ctk.CTkTabview(dialog, height=250, text_color="black")
        tab.pack(fill="both", expand=True, padx=20, pady=5)
        
        # 1. Tự động
        t1 = tab.add("Tự động")
        ctk.CTkLabel(t1, text="Xác thực vị trí lớp học...", text_color="gray").pack(pady=30)
        ctk.CTkButton(t1, text="Xác nhận có mặt", fg_color=COLOR_ACCENT_GREEN, 
                      command=lambda: self._do_checkin(session, cls, dialog, 'GPS')).pack()

        # 2. Mã số
        t2 = tab.add("Nhập Mã")
        ctk.CTkLabel(t2, text="Nhập mã số giảng viên cung cấp:", text_color="gray").pack(pady=10)
        entry = ctk.CTkEntry(t2, placeholder_text="Ví dụ: 8921")
        entry.pack(pady=10)
        ctk.CTkButton(t2, text="Gửi mã", fg_color=COLOR_BLUE, 
                      command=lambda: self._do_checkin(session, cls, dialog, 'Code', entry.get())).pack(pady=10)

        # 3. QR Code
        t3 = tab.add("Quét QR")
        f_qr = ctk.CTkFrame(t3, width=120, height=120, fg_color="black")
        f_qr.pack(pady=10)
        ctk.CTkLabel(f_qr, text="[CAM]", text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkButton(t3, text="Quét ngay", fg_color="black", 
                      command=lambda: self._do_checkin(session, cls, dialog, 'QR')).pack(pady=5)

    def _do_checkin(self, session, cls, dialog, method, code=None):
        if method == 'Code' and (not code or len(code) < 3):
            messagebox.showerror("Lỗi", "Mã không hợp lệ")
            return
            
        success, msg = StudentController.check_in(session['sessionID'], self.student_id, method)
        if success:
            messagebox.showinfo("Thành công", msg)
            dialog.destroy()
            self._load_detail(cls, 100) # Reload UI (Rate tạm để 100, hàm load sẽ tính lại)
        else:
            messagebox.showerror("Thất bại", msg)

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame("LoginView")