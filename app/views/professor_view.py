import customtkinter as ctk
from tkinter import messagebox
import datetime
import random
from controllers import AttendanceController, ClassController

def _fixed_destroy(self):
    try:
        super(ctk.CTkOptionMenu, self).destroy()
        if hasattr(self, '_variable') and self._variable is not None:
            del self._variable
    except AttributeError: pass
    except Exception as e: pass

ctk.CTkOptionMenu.destroy = _fixed_destroy
# =============================================================================

# --- CẤU HÌNH MÀU SẮC ---
COLOR_PRIMARY = "#D93025"       # Đỏ chủ đạo
COLOR_BG_APP = "#F2F4F7"        # Xám nền app
COLOR_PRESENT = "#2e7d32"       # Xanh lá (Có mặt)
COLOR_ABSENT = "#c62828"        # Đỏ đậm (Vắng)
COLOR_EXCUSED = "#ef6c00"       # Cam (Có phép)
COLOR_TEXT_HEADER = "black"

class ProfessorView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG_APP)
        self.controller = controller
        self.current_class = None 
        self.current_session_id = None
        self.current_status = 'Closed'
        self.selected_date = datetime.date.today()
        
        # --- HEADER ---
        self.header = ctk.CTkFrame(self, height=70, fg_color="white", corner_radius=0)
        self.header.pack(side="top", fill="x")
        
        # Avatar
        ctk.CTkButton(self.header, text="", width=45, height=45, corner_radius=22, 
                    fg_color="#C4C4C4", hover=False, command=self.show_dashboard).pack(side="left", padx=(40, 15), pady=12)
        
        self.lbl_name = ctk.CTkLabel(self.header, text="Giảng Viên", font=("Arial", 16, "bold"), text_color="black")
        self.lbl_name.pack(side="left")

        # NÚT ĐĂNG XUẤT
        ctk.CTkButton(self.header, text="Đăng xuất", width=80, height=32, 
                    fg_color="#FFEBEE", text_color="#D93025", hover_color="#FFCDD2",
                    command=self.logout).pack(side="right", padx=20)

        # Nav Area
        self.nav_area = ctk.CTkFrame(self.header, fg_color="white")
        self.nav_area.pack(side="right", padx=20)

        # Body
        self.body = ctk.CTkFrame(self, fg_color=COLOR_BG_APP)
        self.body.pack(fill="both", expand=True)

        self._init_dashboard_ui()

    # --- HELPERS ---
    def get_current_user_id(self):
        return self.controller.current_user['id'] if self.controller.current_user else 'U-GV01'

    def clear_body(self):
        for w in self.body.winfo_children(): w.destroy()

    def update_navbar(self, mode="dashboard", active_tab=""):
        for w in self.nav_area.winfo_children(): w.destroy()
        if mode == "dashboard":
            self._add_nav_item("Trang chủ", True, self.show_dashboard)
        else:
            self._add_nav_item("Danh sách", active_tab=="attendance", lambda: self.show_attendance(self.current_class))
            self._add_nav_item("Chi Tiết", active_tab=="details", lambda: self.show_details(self.current_class))
            self._add_nav_item("Thống Kê", active_tab=="stats", lambda: self.show_statistics(self.current_class))
            ctk.CTkButton(self.nav_area, text="⌂", width=30, fg_color="#E0E0E0", text_color="black", command=self.show_dashboard).pack(side="right", padx=10)

    def _add_nav_item(self, text, is_active, command):
        f = ctk.CTkFrame(self.nav_area, fg_color="white")
        f.pack(side="left", padx=15)
        col = COLOR_PRIMARY if is_active else "black"
        ctk.CTkButton(f, text=text, font=("Arial", 15, "bold"), text_color=col, fg_color="transparent", hover=False, width=40, command=command).pack()
        if is_active: ctk.CTkFrame(f, height=3, width=len(text)*7, fg_color=COLOR_PRIMARY).pack(pady=(2,0))

    # =========================================================================
    # 1. DASHBOARD
    # =========================================================================
    def _init_dashboard_ui(self):
        self.clear_body()
        self.update_navbar("dashboard")
        self.dash_container = ctk.CTkFrame(self.body, fg_color="white", corner_radius=15)
        self.dash_container.pack(fill="both", expand=True, padx=60, pady=(20, 40))

    def show_dashboard(self):
        self.current_class = None
        self.clear_body()
        self.update_navbar("dashboard")
        if self.controller.current_user:
            self.lbl_name.configure(text=self.controller.current_user.get('name', 'Giảng Viên'))

        container = ctk.CTkFrame(self.body, fg_color="white", corner_radius=15)
        container.pack(fill="both", expand=True, padx=60, pady=(20, 40))

        ctk.CTkLabel(container, text="Danh sách lớp học", font=("Arial", 26, "bold"), text_color="black").pack(pady=(30, 20))
        
        grid = ctk.CTkScrollableFrame(container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=10)
        grid.grid_columnconfigure((0,1,2), weight=1)

        try:
            classes = ClassController.get_classes_by_professor(self.get_current_user_id())
            if not classes:
                ctk.CTkLabel(grid, text="Chưa có lớp học nào.", text_color="gray").pack(pady=50)
            for idx, cls in enumerate(classes):
                self._create_class_card(grid, idx, cls)
        except Exception as e:
            ctk.CTkLabel(grid, text=f"Lỗi: {e}", text_color="red").pack()

    def _create_class_card(self, parent, idx, data):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E5E5")
        card.grid(row=idx//3, column=idx%3, padx=12, pady=12, sticky="nsew")
        cmd = lambda e=None: self.show_attendance(data) # Mặc định hôm nay
        card.bind("<Button-1>", cmd)
        ctk.CTkLabel(card, text=data['name'], font=("Arial", 16, "bold"), text_color="black", anchor="w").pack(padx=15, pady=(15,5), fill="x")
        ctk.CTkLabel(card, text=f"  {data['id']}  ", fg_color="#F3F4F6", text_color="#5F6368", corner_radius=6).pack(padx=15, anchor="w")
        ctk.CTkLabel(card, text=f"👥 {data.get('count', 0)} Sinh viên", text_color="gray").pack(side="bottom", anchor="w", padx=15, pady=15)
        for c in card.winfo_children(): c.bind("<Button-1>", cmd)

    # =========================================================================
    # 2. ATTENDANCE
    # =========================================================================
    def show_attendance(self, class_data, target_date=None):
        self.current_class = class_data
        if target_date is None:
            target_date = datetime.date.today()
        self.selected_date = target_date
        
        self.clear_body()
        self.update_navbar("class", "attendance")

        # 1. Dropdown Lịch sử
        sessions_list = AttendanceController.get_class_sessions(class_data['id'])
        today_str = datetime.date.today().strftime("%d/%m/%Y")
        
        combo_values = []
        date_map = {}
        has_today = False
        
        for s in sessions_list:
            display_str = f"{s['date_str']} ({s['status']})"
            combo_values.append(display_str)
            date_map[display_str] = s['date_obj']
            if s['date_str'] == today_str: has_today = True
            
        if not has_today:
            new_str = f"{today_str} (Mới)"
            combo_values.insert(0, new_str)
            date_map[new_str] = datetime.date.today()

        # Giá trị hiển thị mặc định
        current_display = next((k for k, v in date_map.items() if v == self.selected_date), combo_values[0] if combo_values else "")

        # 2. Load Dữ liệu Sinh viên
        try:
            students_data, session_id, status = AttendanceController.get_student_list(class_data['id'], self.selected_date)
            if students_data is None: students_data = []
            self.current_session_id = session_id
            self.current_status = status
        except Exception as e:
            students_data, self.current_session_id, self.current_status = [], None, 'Closed'

        # --- HEADER GIAO DIỆN ---
        title_fr = ctk.CTkFrame(self.body, fg_color="transparent")
        title_fr.pack(pady=(10, 5))
        ctk.CTkLabel(title_fr, text=class_data['name'], font=("Arial", 22, "bold"), text_color=COLOR_PRIMARY).pack()
        
        # Thanh chọn ngày
        date_fr = ctk.CTkFrame(title_fr, fg_color="transparent")
        date_fr.pack(pady=5)
        ctk.CTkLabel(date_fr, text="Ngày: ", text_color="black").pack(side="left")
        
        def on_date_change(choice):
            new_d = date_map.get(choice)
            if new_d: self.show_attendance(class_data, new_d)

        date_menu = ctk.CTkOptionMenu(date_fr, values=combo_values, command=on_date_change, width=180)
        date_menu.set(current_display)
        date_menu.pack(side="left", padx=5)

        # Trạng thái
        status_txt = "🟢 ĐANG MỞ" if self.current_status == 'Open' else "🔴 ĐÃ ĐÓNG / CHƯA TẠO"
        status_col = COLOR_PRESENT if self.current_status == 'Open' else "gray"
        ctk.CTkLabel(title_fr, text=status_txt, font=("Arial", 12, "bold"), text_color=status_col).pack(pady=(5,0))

        # --- TOOLBAR ---
        container = ctk.CTkFrame(self.body, fg_color="white", corner_radius=15)
        container.pack(fill="both", expand=True, padx=40, pady=(10, 30))

        tb = ctk.CTkFrame(container, fg_color="transparent")
        tb.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(tb, text="Refresh", fg_color="transparent", text_color="#2196F3", width=60, 
                    command=lambda: self.show_attendance(class_data, self.selected_date)).pack(side="right")

        # LOGIC NÚT BẤM
        is_today = (self.selected_date == datetime.date.today())
        
        if self.current_session_id:
            # ĐÃ CÓ PHIÊN (Dù là hôm nay hay quá khứ)
            if self.current_status == 'Open':
                # Đang mở -> Nút Đóng
                ctk.CTkButton(tb, text="⏹ Đóng phiên", fg_color=COLOR_ABSENT, width=120, command=self.handle_toggle_session).pack(side="right", padx=10)
                ctk.CTkButton(tb, text="Hiện QR/Code", fg_color="#3B82F6", width=120, command=lambda: self.open_session_popup(class_data)).pack(side="right", padx=10)
            else:
                # Đã đóng -> Nút Mở lại (Cho phép sửa quá khứ)
                ctk.CTkButton(tb, text="🔄 Mở lại phiên này", fg_color=COLOR_EXCUSED, width=150, command=self.handle_toggle_session).pack(side="right", padx=10)
        else:
            # CHƯA CÓ PHIÊN (Chỉ cho tạo mới nếu là hôm nay)
            if is_today:
                ctk.CTkButton(tb, text="▶ Bắt đầu điểm danh", fg_color=COLOR_PRESENT, width=150, command=self.ask_create_session).pack(side="right", padx=10)
            else:
                ctk.CTkLabel(tb, text="(Chưa có dữ liệu)", text_color="gray").pack(side="right", padx=10)

        # --- GRID SINH VIÊN ---
        grid = ctk.CTkScrollableFrame(container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=10)
        grid.grid_columnconfigure((0,1,2,3), weight=1)

        if not students_data:
            ctk.CTkLabel(grid, text="Danh sách trống.", text_color="red").pack(pady=50)
        else:
            for idx, std in enumerate(students_data):
                self._create_student_card(grid, idx, std)

    def handle_toggle_session(self):
        """Xử lý Đóng/Mở lại phiên"""
        new_status = 'Closed' if self.current_status == 'Open' else 'Open'
        success = AttendanceController.update_session_status(self.current_session_id, new_status)
        if success:
            msg = "Đã đóng phiên." if new_status == 'Closed' else "Đã mở lại phiên điểm danh!"
            messagebox.showinfo("Thành công", msg)
            self.show_attendance(self.current_class, self.selected_date)
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật trạng thái.")

    def ask_create_session(self):
        """Hỏi hình thức khi tạo phiên mới"""
        sid = AttendanceController.create_daily_session(self.current_class['id'])
        if not sid:
            messagebox.showerror("Lỗi", "Không thể tạo phiên.")
            return
        
        self.show_attendance(self.current_class, datetime.date.today())
        
        # Dialog chọn
        dialog = ctk.CTkToplevel(self)
        dialog.title("Chọn hình thức")
        dialog.geometry("350x250")
        dialog.transient(self); dialog.grab_set(); dialog.configure(fg_color="white")
        
        ctk.CTkLabel(dialog, text="Phiên điểm danh đã mở!", font=("Arial", 16, "bold"), text_color="black").pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="Bạn muốn hiển thị gì?", text_color="gray").pack(pady=5)
        
        ctk.CTkButton(dialog, text="Mã QR (Cho SV quét)", fg_color="#3B82F6",
                    command=lambda: [dialog.destroy(), self.open_session_popup(self.current_class, "QR")]).pack(pady=5, fill="x", padx=40)
        ctk.CTkButton(dialog, text="Mã Số (Cho SV nhập)", fg_color="#3B82F6",
                    command=lambda: [dialog.destroy(), self.open_session_popup(self.current_class, "Code")]).pack(pady=5, fill="x", padx=40)
        ctk.CTkButton(dialog, text="Danh sách (Tick tay)", fg_color="gray", command=dialog.destroy).pack(pady=5, fill="x", padx=40)

    def _create_student_card(self, parent, idx, std):
        row, col = idx // 4, idx % 4
        is_p = std.get('status') == 'present'
        bg = "#373737" if is_p else "#B4C1BB"
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=8, height=55)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="ew")

        def toggle(e=None):
            if self.current_status != 'Open':
                messagebox.showwarning("Chú ý", "Phiên đang đóng. Vui lòng bấm 'Mở lại' trước khi sửa!")
                return
            new_st = 'absent' if std.get('status') == 'present' else 'present'
            AttendanceController.update_attendance(std['session_id'], std['id'], new_st)
            std['status'] = new_st
            is_now_p = new_st == 'present'
            card.configure(fg_color="#373737" if is_now_p else "#B4C1BB")
            lbl.configure(text_color="white" if is_now_p else "black")
            chk.configure(text="☑" if is_now_p else "☐", text_color="white" if is_now_p else "#555")

        card.bind("<Button-1>", toggle)
        info = ctk.CTkFrame(card, fg_color="transparent"); info.pack(side="left", padx=10)
        lbl = ctk.CTkLabel(info, text=f"{idx+1}. {std['name']}", font=("Arial", 12, "bold"), text_color="white" if is_p else "black")
        lbl.pack(side="left")
        chk = ctk.CTkLabel(card, text="☑" if is_p else "☐", font=("Arial", 18), text_color="white" if is_p else "#555"); chk.pack(side="right", padx=10)
        lbl.bind("<Button-1>", toggle); chk.bind("<Button-1>", toggle)

    # =========================================================================
    # 3. DETAILS
    # =========================================================================
    def show_details(self, class_data):
        self.clear_body()
        self.update_navbar("class", "details")
        
        # Search bar
        search_fr = ctk.CTkFrame(self.body, fg_color="transparent")
        search_fr.pack(pady=(20, 15))
        ctk.CTkEntry(search_fr, placeholder_text="Tìm kiếm sinh viên...", width=400, height=45, corner_radius=22, fg_color="white", border_color="#E0E0E0", border_width=1, text_color="black").pack()

        # Table Container
        container = ctk.CTkFrame(self.body, fg_color="white", corner_radius=15)
        container.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        # Header Row
        h_frame = ctk.CTkFrame(container, fg_color="transparent", height=50)
        h_frame.pack(fill="x", padx=30, pady=(20, 10))
        h_frame.grid_columnconfigure(0, weight=3) 
        h_frame.grid_columnconfigure(1, weight=2)
        h_frame.grid_columnconfigure(2, weight=2)
        h_frame.grid_columnconfigure(3, weight=1)

        fonts = ("Arial", 13, "bold")
        ctk.CTkLabel(h_frame, text="Họ tên", font=fonts, text_color="black", anchor="w").grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(h_frame, text="Mã sinh viên", font=fonts, text_color="black", anchor="center").grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(h_frame, text="Trạng thái (Hôm nay)", font=fonts, text_color="black", anchor="center").grid(row=0, column=2, sticky="ew")
        ctk.CTkLabel(h_frame, text="Hành động", font=fonts, text_color="black", anchor="center").grid(row=0, column=3, sticky="ew")
        
        ctk.CTkFrame(container, height=1, fg_color="#E0E0E0").pack(fill="x", padx=30)

        # Body Rows
        body = ctk.CTkScrollableFrame(container, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=5)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_columnconfigure(2, weight=2)
        body.grid_columnconfigure(3, weight=1)
        
        try:
            # Lấy dữ liệu của ngày đang chọn (hoặc mặc định hôm nay)
            # Nếu chưa chọn ngày ở tab Attendance, mặc định là Today
            target_date = self.selected_date if hasattr(self, 'selected_date') else datetime.date.today()
            students, _, _ = AttendanceController.get_student_list(class_data['id'], target_date)
            
            if not students:
                ctk.CTkLabel(body, text="Chưa có dữ liệu.", text_color="gray").pack(pady=20)
            else:
                for idx, std in enumerate(students):
                    self._create_detail_row(body, idx, std)
        except Exception as e:
            print(f"Error Details: {e}")

    def _create_detail_row(self, parent, idx, std):
        st_map = {
            'present': ('Đã điểm danh', COLOR_PRESENT), 
            'absent': ('Vắng', COLOR_ABSENT), 
            'late': ('Đi muộn', '#F59E0B'),
            'excused': ('Có phép', '#F59E0B'),
            'none': ('Chưa điểm danh', 'gray')
        }
        txt, col = st_map.get(std.get('status', 'none'), st_map['none'])
        
        ctk.CTkLabel(parent, text=std['name'], text_color="black", anchor="w").grid(row=idx, column=0, pady=12, sticky="ew", padx=10)
        ctk.CTkLabel(parent, text=std['id'], text_color="black").grid(row=idx, column=1)
        lbl_st = ctk.CTkLabel(parent, text=txt, text_color=col, font=("Arial", 12, "bold"))
        lbl_st.grid(row=idx, column=2)
        
        # Dropdown sửa nhanh
        def on_change(choice):
            map_val = {"Có mặt": "present", "Vắng": "absent", "Muộn": "late", "Phép": "excused"}
            new_val = map_val.get(choice, "present")
            AttendanceController.update_attendance(std['session_id'], std['id'], new_val)
            t, c = st_map.get(new_val)
            lbl_st.configure(text=t, text_color=c)
            menu.set("✎")

        menu = ctk.CTkOptionMenu(parent, values=["Có mặt", "Vắng", "Muộn", "Phép"], width=80, height=24, 
                                fg_color="#F5F5F5", text_color="black", button_color="#F5F5F5", 
                                dropdown_fg_color="white", dropdown_text_color="black", command=on_change)
        menu.set("✎")
        menu.grid(row=idx, column=3)
        ctk.CTkFrame(parent, height=1, fg_color="#F9F9F9").grid(row=idx+1, column=0, columnspan=4, sticky="ew")

    # =========================================================================
    # 4. STATISTICS (Thống kê)
    # =========================================================================
    def show_statistics(self, class_data):
        self.clear_body()
        self.update_navbar("class", "stats")
        
        search_fr = ctk.CTkFrame(self.body, fg_color="transparent")
        search_fr.pack(pady=(20, 15))
        ctk.CTkEntry(search_fr, placeholder_text="Tìm kiếm...", width=400, height=45, corner_radius=22, fg_color="white", border_width=1, border_color="#E0E0E0", text_color="black").pack()

        container = ctk.CTkFrame(self.body, fg_color="white", corner_radius=15)
        container.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        h = ctk.CTkFrame(container, fg_color="transparent", height=50)
        h.pack(fill="x", padx=30, pady=(20, 10))
        h.grid_columnconfigure(0, weight=3)
        h.grid_columnconfigure((1,2,3), weight=2)
        for i, t in enumerate(["Họ tên", "Mã SV", "Số buổi có mặt", "Tỷ lệ chuyên cần"]):
            ctk.CTkLabel(h, text=t, font=("Arial", 13, "bold"), text_color="black", anchor="w" if i==0 else "center").grid(row=0, column=i, sticky="ew")

        ctk.CTkFrame(container, height=1, fg_color="#E0E0E0").pack(fill="x", padx=30)

        body = ctk.CTkScrollableFrame(container, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=5)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure((1,2,3), weight=2)

        try:
            stats = AttendanceController.get_statistics(class_data['id'])
            if not stats:
                ctk.CTkLabel(body, text="Chưa có dữ liệu thống kê.", text_color="gray").pack(pady=20)
            else:
                for idx, st in enumerate(stats):
                    ctk.CTkLabel(body, text=st['name'], text_color="black", anchor="w").grid(row=idx, column=0, pady=12, padx=10, sticky="ew")
                    ctk.CTkLabel(body, text=st['id'], text_color="black").grid(row=idx, column=1)
                    ctk.CTkLabel(body, text=str(st['attended']), text_color="black").grid(row=idx, column=2)
                    
                    rate = st['rate']
                    col = COLOR_PRESENT if rate >= 80 else ("#ef6c00" if rate >= 50 else COLOR_ABSENT)
                    ctk.CTkLabel(body, text=f"{rate}%", text_color=col, font=("Arial", 13, "bold")).grid(row=idx, column=3)
                    
                    ctk.CTkFrame(body, height=1, fg_color="#F9F9F9").grid(row=idx+1, column=0, columnspan=4, sticky="ew")
        except: pass

    # --- POPUP ---
    def open_session_popup(self, class_data, default_tab="QR"):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Phiên điểm danh")
        dialog.geometry("450x400")
        dialog.transient(self); dialog.grab_set(); dialog.configure(fg_color="white")
        ctk.CTkLabel(dialog, text=f"Lớp: {class_data['name']}", font=("Arial", 18, "bold"), text_color="black").pack(pady=(20, 10))
        
        tabview = ctk.CTkTabview(dialog, width=400, height=300, text_color="black")
        tabview.pack(pady=10)
        
        t1 = tabview.add("Mã QR")
        ctk.CTkLabel(t1, text="Sinh viên quét mã để điểm danh", text_color="gray").pack(pady=5)
        f = ctk.CTkFrame(t1, width=180, height=180, fg_color="black"); f.pack(pady=15)
        ctk.CTkLabel(f, text="[QR IMAGE DEMO]", text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        
        t2 = tabview.add("Mã Số")
        ctk.CTkLabel(t2, text="Cung cấp mã này cho sinh viên", text_color="gray").pack(pady=20)
        ctk.CTkLabel(t2, text=f"{random.randint(100000,999999)}", font=("Arial", 40, "bold"), text_color="#2196F3").pack(pady=20)

        if default_tab == "Code": tabview.set("Mã Số")
        else: tabview.set("Mã QR")

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame("LoginView")
