import customtkinter as ctk
from tkinter import messagebox
import random
from controllers import AttendanceController, ClassController

def _fixed_destroy(self):
    try:
        super(ctk.CTkOptionMenu, self).destroy()
        if hasattr(self, '_variable') and self._variable is not None:
            del self._variable
    except AttributeError: pass
    except Exception as e: print(f"Warning: OptionMenu destroy error ignored: {e}")

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
        
        # --- HEADER ---
        self.header = ctk.CTkFrame(self, height=70, fg_color="white", corner_radius=0)
        self.header.pack(side="top", fill="x")
        
        # Avatar
        ctk.CTkButton(self.header, text="", width=45, height=45, corner_radius=22, 
                      fg_color="#C4C4C4", hover=False, command=self.show_dashboard).pack(side="left", padx=(40, 15), pady=12)
        
        self.lbl_name = ctk.CTkLabel(self.header, text="Giảng Viên", font=("Arial", 16, "bold"), text_color="black")
        self.lbl_name.pack(side="left")

        # Nav Area
        self.nav_area = ctk.CTkFrame(self.header, fg_color="white")
        self.nav_area.pack(side="right", padx=40)

        # Body
        self.body = ctk.CTkFrame(self, fg_color=COLOR_BG_APP)
        self.body.pack(fill="both", expand=True)

        self._init_dashboard_ui()

    # --- HELPERS ---
    def get_current_user_id(self):
        if self.controller.current_user:
            return self.controller.current_user['id']
        return 'U-GV01' # Fallback

    def clear_body(self):
        for w in self.body.winfo_children(): w.destroy()

    def update_navbar(self, mode="dashboard", active_tab=""):
        for w in self.nav_area.winfo_children(): w.destroy()
        if mode == "dashboard":
            self._add_nav_item("Trang chủ", True, self.show_dashboard)
        else:
            # Menu 3 tab
            self._add_nav_item("Danh sách sinh viên", active_tab=="attendance", lambda: self.show_attendance(self.current_class))
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
                ctk.CTkLabel(grid, text="Chưa có lớp học nào.", text_color="gray", font=("Arial", 16)).pack(pady=50)
            for idx, cls in enumerate(classes):
                self._create_class_card(grid, idx, cls)
        except Exception as e:
            ctk.CTkLabel(grid, text=f"Lỗi kết nối DB: {e}", text_color="red").pack()

    def _create_class_card(self, parent, idx, data):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E5E5")
        card.grid(row=idx//3, column=idx%3, padx=12, pady=12, sticky="nsew")
        cmd = lambda e=None: self.show_attendance(data)
        card.bind("<Button-1>", cmd)
        ctk.CTkLabel(card, text=data['name'], font=("Arial", 16, "bold"), text_color="black", anchor="w").pack(padx=15, pady=(15,5), fill="x")
        ctk.CTkLabel(card, text=f"  {data['id']}  ", fg_color="#F3F4F6", text_color="#5F6368", corner_radius=6).pack(padx=15, anchor="w")
        ctk.CTkLabel(card, text=f"👥 {data.get('count', 0)} Sinh viên", text_color="gray").pack(side="bottom", anchor="w", padx=15, pady=15)
        for c in card.winfo_children(): c.bind("<Button-1>", cmd)

    # =========================================================================
    # 2. ATTENDANCE (Điểm danh)
    # =========================================================================
    def show_attendance(self, class_data):
        self.current_class = class_data
        self.clear_body()
        self.update_navbar("class", "attendance")

        title_fr = ctk.CTkFrame(self.body, fg_color="transparent")
        title_fr.pack(pady=(15, 5))
        ctk.CTkLabel(title_fr, text="Danh sách sinh viên lớp", font=("Arial", 22), text_color="black").pack()
        ctk.CTkLabel(title_fr, text=class_data['name'], font=("Arial", 22, "bold"), text_color=COLOR_PRIMARY).pack()

        container = ctk.CTkFrame(self.body, fg_color="white", corner_radius=15)
        container.pack(fill="both", expand=True, padx=40, pady=(10, 30))

        tb = ctk.CTkFrame(container, fg_color="transparent")
        tb.pack(fill="x", padx=30, pady=20)
        ctk.CTkOptionMenu(tb, values=["Section 1"], width=120, fg_color="#A0A0A0").pack(side="left")
        ctk.CTkButton(tb, text="Refresh", fg_color="transparent", text_color="#2196F3", width=60, command=lambda: self.show_attendance(class_data)).pack(side="right")
        
        # Nút Mở Phiên Điểm Danh
        ctk.CTkButton(tb, text="▶ Tạo phiên điểm danh", fg_color="#2e7d32", width=160, 
                      command=lambda: self.open_session_popup(class_data)).pack(side="right", padx=10)

        grid = ctk.CTkScrollableFrame(container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=20, pady=10)
        grid.grid_columnconfigure((0,1,2,3), weight=1)

        try:
            res = AttendanceController.get_student_list(class_data['id'])
            students = res[0] if isinstance(res, tuple) else res
            if not students: ctk.CTkLabel(grid, text="Danh sách trống.", text_color="red").pack(pady=50)
            for idx, std in enumerate(students): self._create_student_card(grid, idx, std)
        except Exception as e: print(e)

    def _create_student_card(self, parent, idx, std):
        row, col = idx // 4, idx % 4
        is_p = std.get('status') == 'present'
        bg = "#373737" if is_p else "#B4C1BB"
        
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=8, height=55)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="ew")

        def toggle(e=None):
            new_st = 'absent' if std.get('status') == 'present' else 'present'
            AttendanceController.update_attendance(std['session_id'], std['id'], new_st)
            std['status'] = new_st
            is_now_p = new_st == 'present'
            card.configure(fg_color="#373737" if is_now_p else "#B4C1BB")
            lbl.configure(text_color="white" if is_now_p else "black")
            chk.configure(text="☑" if is_now_p else "☐", text_color="white" if is_now_p else "#555")

        card.bind("<Button-1>", toggle)
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=10)
        lbl = ctk.CTkLabel(info, text=f"{idx+1}. {std['name']}", font=("Arial", 12, "bold"), text_color="white" if is_p else "black")
        lbl.pack(side="left")
        chk = ctk.CTkLabel(card, text="☑" if is_p else "☐", font=("Arial", 18), text_color="white" if is_p else "#555")
        chk.pack(side="right", padx=10)
        lbl.bind("<Button-1>", toggle)
        chk.bind("<Button-1>", toggle)

    # =========================================================================
    # 3. DETAILS (Chi tiết)
    # =========================================================================
    def show_details(self, class_data):
        self.clear_body()
        self.update_navbar("class", "details")

        # 1. Thanh tìm kiếm (Floating Search Bar)
        search_fr = ctk.CTkFrame(self.body, fg_color="transparent")
        search_fr.pack(pady=(20, 15))
        ctk.CTkEntry(search_fr, placeholder_text="Tìm kiếm...", width=400, height=45, corner_radius=22, 
                     fg_color="white", border_color="#E0E0E0", border_width=1, text_color="black").pack()

        # 2. Container Bảng
        container = ctk.CTkFrame(self.body, fg_color="white", corner_radius=15)
        container.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        # 3. Header Bảng (Căn chỉnh cột Grid)
        # Cấu hình tỷ lệ: Họ tên (3), Mã (2), Trạng thái (2), Hành động (1)
        h_frame = ctk.CTkFrame(container, fg_color="transparent", height=50)
        h_frame.pack(fill="x", padx=30, pady=(20, 10))
        h_frame.grid_columnconfigure(0, weight=3) 
        h_frame.grid_columnconfigure(1, weight=2)
        h_frame.grid_columnconfigure(2, weight=2)
        h_frame.grid_columnconfigure(3, weight=1)

        fonts = ("Arial", 13, "bold")
        ctk.CTkLabel(h_frame, text="Họ tên", font=fonts, text_color="black", anchor="w").grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(h_frame, text="Mã sinh viên", font=fonts, text_color="black", anchor="center").grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(h_frame, text="Trạng thái điểm danh", font=fonts, text_color="black", anchor="center").grid(row=0, column=2, sticky="ew")
        ctk.CTkLabel(h_frame, text="Hành động", font=fonts, text_color="black", anchor="center").grid(row=0, column=3, sticky="ew")
        
        # Line separator
        ctk.CTkFrame(container, height=1, fg_color="#E0E0E0").pack(fill="x", padx=30)

        # 4. Body Bảng
        body = ctk.CTkScrollableFrame(container, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=5)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_columnconfigure(2, weight=2)
        body.grid_columnconfigure(3, weight=1)
        
        try:
            res = AttendanceController.get_student_list(class_data['id'])
            students = res[0] if isinstance(res, tuple) else res
            for idx, std in enumerate(students):
                self._create_detail_row(body, idx, std)
        except Exception as e:
            print(e)

    def _create_detail_row(self, parent, idx, std):
        # Map trạng thái sang màu sắc
        st_map = {
            'present': ('Đã điểm danh', COLOR_PRESENT), 
            'absent': ('Vắng', COLOR_ABSENT), 
            'none': ('Chưa điểm danh', 'gray')
        }
        txt, col = st_map.get(std.get('status', 'none'), st_map['none'])
        
        # Row content
        ctk.CTkLabel(parent, text=std['name'], text_color="black", anchor="w", font=("Arial", 13)).grid(row=idx, column=0, pady=12, sticky="ew", padx=10)
        ctk.CTkLabel(parent, text=std['id'], text_color="black", font=("Arial", 13)).grid(row=idx, column=1)
        lbl_st = ctk.CTkLabel(parent, text=txt, text_color=col, font=("Arial", 12, "bold"))
        lbl_st.grid(row=idx, column=2)
        
        # Dropdown Hành động (Giả lập nút Edit)
        def on_change(choice):
            new_val = 'present' if choice == "Có mặt" else 'absent'
            AttendanceController.update_attendance(std['session_id'], std['id'], new_val)
            # Update UI Local
            t, c = st_map.get(new_val)
            lbl_st.configure(text=t, text_color=c)
            menu.set("✎") # Reset về icon bút chì

        menu = ctk.CTkOptionMenu(parent, values=["Có mặt", "Vắng"], width=60, height=24, 
                                 fg_color="#F5F5F5", text_color="black", button_color="#F5F5F5", button_hover_color="#E0E0E0",
                                 dropdown_fg_color="white", dropdown_text_color="black",
                                 command=on_change)
        menu.set("✎")
        menu.grid(row=idx, column=3)
        
        # Kẻ ngang mờ
        ctk.CTkFrame(parent, height=1, fg_color="#F9F9F9").grid(row=idx+1, column=0, columnspan=4, sticky="ew")


    # =========================================================================
    # 4. STATISTICS
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
        for i, t in enumerate(["Họ tên", "Mã SV", "Số buổi", "Tỷ lệ"]):
            ctk.CTkLabel(h, text=t, font=("Arial", 13, "bold"), text_color="black", anchor="w" if i==0 else "center").grid(row=0, column=i, sticky="ew")

        ctk.CTkFrame(container, height=1, fg_color="#E0E0E0").pack(fill="x", padx=30)

        body = ctk.CTkScrollableFrame(container, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=5)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure((1,2,3), weight=2)

        try:
            stats = AttendanceController.get_statistics(class_data['id'])
            for idx, st in enumerate(stats):
                ctk.CTkLabel(body, text=st['name'], text_color="black", anchor="w").grid(row=idx, column=0, pady=12, padx=10, sticky="ew")
                ctk.CTkLabel(body, text=st['id'], text_color="black").grid(row=idx, column=1)
                ctk.CTkLabel(body, text=str(st['attended']), text_color="black").grid(row=idx, column=2)
                col = "#2e7d32" if st['rate'] >= 80 else ("#ef6c00" if st['rate'] >= 50 else "#c62828")
                ctk.CTkLabel(body, text=f"{st['rate']}%", text_color=col, font=("Arial", 13, "bold")).grid(row=idx, column=3)
                ctk.CTkFrame(body, height=1, fg_color="#F9F9F9").grid(row=idx+1, column=0, columnspan=4, sticky="ew")
        except: pass

    # =========================================================================
    # POPUP: TẠO PHIÊN ĐIỂM DANH (QR & CODE)
    # =========================================================================
    def open_session_popup(self, class_data):
        # Tạo cửa sổ Popup
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thiết lập phiên điểm danh")
        dialog.geometry("450x400")
        dialog.transient(self) # Nổi trên cửa sổ chính
        dialog.grab_set()      # Chặn tương tác bên ngoài
        dialog.configure(fg_color="white")

        ctk.CTkLabel(dialog, text=f"Lớp: {class_data['name']}", font=("Arial", 18, "bold"), text_color="black").pack(pady=(20, 10))

        # Tab View
        tabview = ctk.CTkTabview(dialog, width=400, height=300, text_color="black", segmented_button_fg_color="#F0F0F0", segmented_button_selected_color=COLOR_PRIMARY)
        tabview.pack(pady=10)
        
        # --- TAB 1: QR CODE ---
        t_qr = tabview.add("Mã QR")
        ctk.CTkLabel(t_qr, text="Sinh viên quét mã để điểm danh", text_color="gray").pack(pady=5)
        
        # Placeholder cho QR (Hình vuông đen demo)
        qr_frame = ctk.CTkFrame(t_qr, width=180, height=180, fg_color="black", corner_radius=0)
        qr_frame.pack(pady=15)
        ctk.CTkLabel(qr_frame, text="[QR IMAGE DEMO]", text_color="white").place(relx=0.5, rely=0.5, anchor="center")
        
        # --- TAB 2: MÃ SỐ (CODE) ---
        t_code = tabview.add("Mã Số")
        ctk.CTkLabel(t_code, text="Cung cấp mã này cho sinh viên", text_color="gray").pack(pady=20)
        
        # Random Code Generation
        random_code = f"{random.randint(100000, 999999)}"
        code_lbl = ctk.CTkLabel(t_code, text=random_code, font=("Arial", 40, "bold"), text_color="#2196F3", fg_color="#F5F9FF", corner_radius=10, width=200, height=60)
        code_lbl.pack(pady=20)
        
        ctk.CTkButton(t_code, text="Làm mới mã", fg_color="transparent", border_width=1, text_color="gray", 
                      command=lambda: code_lbl.configure(text=f"{random.randint(100000, 999999)}")).pack()
