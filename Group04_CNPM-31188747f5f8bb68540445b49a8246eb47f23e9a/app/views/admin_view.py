import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers import AdminController

# --- CẤU HÌNH MÀU SẮC (THEME) ---
THEME = {
    "sidebar_bg": "#1E293B",         # Dark Slate (Sidebar)
    "sidebar_btn_hover": "#334155",  # Lighter Slate
    "sidebar_text": "#F8FAFC",       # White text
    "main_bg": "#F1F5F9",            # Light Gray (Background)
    "card_bg": "#FFFFFF",            # White (Cards)
    "primary": "#3B82F6",            # Blue (Buttons, Active)
    "primary_hover": "#2563EB",
    "danger": "#EF4444",             # Red (Delete)
    "success": "#10B981",            # Green (Add/Edit)
    "text_dark": "#1F2937",
    "text_light": "#64748B"
}

class AdminView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=THEME["main_bg"])
        self.controller = controller

        # Grid: Cột 0 (Sidebar) - Cột 1 (Main Content)
        self.grid_columnconfigure(0, weight=0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR
        self.sidebar = ctk.CTkFrame(self, fg_color=THEME["sidebar_bg"], corner_radius=0, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1) # Đẩy nút logout xuống đáy

        # Logo / Title
        ctk.CTkLabel(self.sidebar, text="AMS ADMIN", font=("Arial", 24, "bold"), text_color="white").grid(row=0, column=0, padx=30, pady=(40, 20), sticky="w")

        # Menu Buttons
        self.nav_buttons = {}
        self._create_sidebar_btn("Bảng điều khiển", "dashboard", 1)
        self._create_sidebar_btn("Quản lý Người dùng", "users", 2)
        self._create_sidebar_btn("Quản lý Lớp học", "classes", 3)
        self._create_sidebar_btn("Ghi danh & Xếp lớp", "enroll", 4)

        # Logout Button
        logout_btn = ctk.CTkButton(self.sidebar, text="Đăng xuất  ➔", fg_color="transparent", 
                                   text_color="#F87171", hover_color=THEME["sidebar_btn_hover"], 
                                   anchor="w", command=self.logout)
        logout_btn.grid(row=7, column=0, padx=20, pady=20, sticky="ew")

        # 2. MAIN CONTENT AREA
        self.main_panel = ctk.CTkFrame(self, fg_color=THEME["main_bg"], corner_radius=0)
        self.main_panel.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_panel.grid_rowconfigure(1, weight=1) # Dòng 0: Header, Dòng 1: Content
        self.main_panel.grid_columnconfigure(0, weight=1)

        # Header chung (Search bar + User info)
        self.topbar = ctk.CTkFrame(self.main_panel, fg_color="white", height=70, corner_radius=0)
        self.topbar.grid(row=0, column=0, sticky="ew")
        self._setup_topbar()

        # Container cho các trang con
        self.content_container = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=30)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Khởi tạo các trang
        self.pages = {
            "dashboard": DashboardPage(self.content_container, controller),
            "users": UsersPage(self.content_container, controller),
            "classes": ClassesPage(self.content_container, controller),
            "enroll": EnrollmentsPage(self.content_container, controller),
        }

        # Setup Treeview Style chung
        self._setup_treeview_style()
        
        # Mặc định vào Dashboard
        self.navigate("dashboard")

    def _create_sidebar_btn(self, text, key, row):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", 
                            text_color=THEME["sidebar_text"], hover_color=THEME["sidebar_btn_hover"], 
                            anchor="w", font=("Arial", 14), height=45,
                            command=lambda: self.navigate(key))
        btn.grid(row=row, column=0, padx=15, pady=5, sticky="ew")
        self.nav_buttons[key] = btn

    def _setup_topbar(self):
        # Page Title
        self.lbl_page_title = ctk.CTkLabel(self.topbar, text="Tổng quan", font=("Arial", 20, "bold"), text_color=THEME["text_dark"])
        self.lbl_page_title.pack(side="left", padx=30, pady=20)

        # User Profile (Giả lập)
        profile_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        profile_frame.pack(side="right", padx=30)
        ctk.CTkButton(profile_frame, text="AD", width=40, height=40, corner_radius=20, 
                      fg_color=THEME["sidebar_bg"], hover=False).pack(side="left", padx=10)
        ctk.CTkLabel(profile_frame, text="Administrator", font=("Arial", 14, "bold"), text_color=THEME["text_dark"]).pack(side="left")

        # Search Bar (Kết nối với trang hiện tại)
        self.entry_search = ctk.CTkEntry(self.topbar, placeholder_text="🔍 Tìm kiếm...", width=300, border_width=0, fg_color="#F3F4F6")
        self.entry_search.pack(side="right", padx=20, ipady=5)
        self.entry_search.bind("<Return>", self._on_search)

    def _setup_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Header
        style.configure("Treeview.Heading", background="#F8FAFC", foreground=THEME["text_dark"], 
                        font=("Arial", 12, "bold"), borderwidth=0, relief="flat")
        # Rows
        style.configure("Treeview", background="white", fieldbackground="white", 
                        foreground=THEME["text_dark"], rowheight=40, font=("Arial", 12), borderwidth=0)
        # Selected Row
        style.map("Treeview", background=[('selected', '#E0F2FE')], foreground=[('selected', THEME["primary"])])
        
        # Loại bỏ border focus
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    def navigate(self, key):
        self.active_key = key
        # Update Title
        titles = {"dashboard": "Bảng điều khiển", "users": "Quản lý Người dùng", "classes": "Quản lý Lớp học", "enroll": "Ghi danh & Xếp lớp"}
        self.lbl_page_title.configure(text=titles.get(key, ""))
        
        # Active button styling
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=THEME["primary"], font=("Arial", 14, "bold"))
            else:
                btn.configure(fg_color="transparent", font=("Arial", 14))

        # Show page
        page = self.pages[key]
        page.tkraise()
        page.grid(row=0, column=0, sticky="nsew")
        if hasattr(page, "refresh"):
            page.refresh()

    def _on_search(self, event):
        keyword = self.entry_search.get()
        page = self.pages[self.active_key]
        if hasattr(page, "search_data"):
            page.search_data(keyword)

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame("LoginView")


# =============================================================================
# 1. DASHBOARD PAGE (Thống kê)
# =============================================================================
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Grid layout cho Cards
        self.grid_columnconfigure((0,1,2,3), weight=1)
        
        self.lbl_cards = {}
        # Tạo 4 Cards thống kê
        self._create_card(0, "Tổng Người dùng", "users", "#DBEAFE", "#1E40AF")
        self._create_card(1, "Tổng Sinh viên", "students", "#D1FAE5", "#065F46")
        self._create_card(2, "Lớp học phần", "classes", "#FEF3C7", "#92400E")
        self._create_card(3, "Phiên điểm danh", "sessions", "#FEE2E2", "#991B1B")

        # Khu vực biểu đồ / chi tiết (Placeholder)
        self.details_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.details_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=30)
        
        ctk.CTkLabel(self.details_frame, text="Hoạt động gần đây", font=("Arial", 16, "bold"), text_color=THEME["text_dark"]).pack(anchor="w", padx=20, pady=20)
        ctk.CTkLabel(self.details_frame, text="(Tính năng biểu đồ đang được phát triển...)", text_color=THEME["text_light"]).pack(pady=50)

    def _create_card(self, col, title, key, bg_color, text_color):
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=15, height=140)
        card.grid(row=0, column=col, sticky="ew", padx=(0 if col==0 else 15, 0))
        
        # Icon box (color block)
        icon = ctk.CTkFrame(card, width=60, height=60, corner_radius=12, fg_color=bg_color)
        icon.place(relx=0.1, rely=0.5, anchor="w")
        
        # Text
        ctk.CTkLabel(card, text=title, font=("Arial", 14), text_color=THEME["text_light"]).place(relx=0.4, rely=0.35)
        lbl_val = ctk.CTkLabel(card, text="0", font=("Arial", 28, "bold"), text_color=THEME["text_dark"])
        lbl_val.place(relx=0.4, rely=0.65)
        self.lbl_cards[key] = lbl_val

    def refresh(self):
        counts = AdminController.dashboard_counts()
        for key, lbl in self.lbl_cards.items():
            lbl.configure(text=str(counts.get(key, 0)))


# =============================================================================
# 2. USERS PAGE (Layout: Form Trái - Table Phải)
# =============================================================================
class UsersPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=3) # Form 30%
        self.grid_columnconfigure(1, weight=7) # Table 70%
        self.grid_rowconfigure(0, weight=1)
        self.selected_user_id = None

        # --- LEFT: FORM ---
        self.form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        ctk.CTkLabel(self.form_frame, text="Thông tin Người dùng", font=("Arial", 18, "bold"), text_color=THEME["text_dark"]).pack(anchor="w", padx=20, pady=20)
        
        self.entry_user = self._entry(self.form_frame, "Tên đăng nhập")
        self.entry_pass = self._entry(self.form_frame, "Mật khẩu", show="*")
        self.entry_name = self._entry(self.form_frame, "Họ và tên")
        self.entry_email = self._entry(self.form_frame, "Email")
        
        ctk.CTkLabel(self.form_frame, text="Vai trò", font=("Arial", 13, "bold"), text_color=THEME["text_dark"]).pack(anchor="w", padx=20, pady=(10, 5))
        self.opt_role = ctk.CTkOptionMenu(self.form_frame, values=["Professor", "Student", "Admin"], width=200, fg_color=THEME["main_bg"], text_color=THEME["text_dark"], button_color="gray")
        self.opt_role.pack(padx=20, fill="x")

        # Buttons
        btn_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=30)
        
        self.btn_add = ctk.CTkButton(btn_box, text="+ Thêm", fg_color=THEME["success"], width=80, command=self.add_user)
        self.btn_add.pack(side="left", padx=(0, 5))
        
        self.btn_update = ctk.CTkButton(btn_box, text="Cập nhật", fg_color=THEME["primary"], width=80, command=self.update_user)
        self.btn_update.pack(side="left", padx=5)
        
        self.btn_clear = ctk.CTkButton(btn_box, text="Làm mới", fg_color="gray", width=80, command=self.clear_form)
        self.btn_clear.pack(side="left", padx=5)

        # --- RIGHT: TABLE ---
        self.table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.table_frame.grid(row=0, column=1, sticky="nsew")
        
        # Treeview
        cols = ("userID", "username", "fullName", "role")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", style="Treeview")
        self.tree.heading("userID", text="ID")
        self.tree.heading("username", text="Username")
        self.tree.heading("fullName", text="Họ tên")
        self.tree.heading("role", text="Vai trò")
        
        self.tree.column("userID", width=60, anchor="center")
        self.tree.column("role", width=100, anchor="center")
        
        # Scrollbar
        sb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        sb.pack(side="right", fill="y", pady=15, padx=(0, 15))

        # Event click row
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)
        
        # Context Menu for Delete
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Xóa Người dùng này", command=self.delete_user)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def _entry(self, parent, placeholder, show=None):
        ctk.CTkLabel(parent, text=placeholder, font=("Arial", 12, "bold"), text_color=THEME["text_light"]).pack(anchor="w", padx=20, pady=(10, 0))
        e = ctk.CTkEntry(parent, border_width=1, fg_color="#F8FAFC", border_color="#E2E8F0", show=show)
        e.pack(padx=20, pady=(5, 0), fill="x")
        return e

    def refresh(self):
        self.search_data()

    def search_data(self, keyword=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        users = AdminController.list_users(keyword)
        for u in users:
            self.tree.insert("", "end", values=(u["userID"], u["username"], u["fullName"], u["role"]))

    def on_select_row(self, event):
        sel = self.tree.selection()
        if not sel: return
        val = self.tree.item(sel[0], "values")
        self.selected_user_id = val[0]
        # Auto fill form
        self.entry_user.delete(0, "end"); self.entry_user.insert(0, val[1])
        self.entry_name.delete(0, "end"); self.entry_name.insert(0, val[2])
        self.opt_role.set(val[3])
        # Note: Cannot get password back safely

    def clear_form(self):
        self.selected_user_id = None
        for e in [self.entry_user, self.entry_pass, self.entry_name, self.entry_email]: e.delete(0, "end")
        self.opt_role.set("Professor")
        self.tree.selection_remove(self.tree.selection())

    def add_user(self):
        ok, msg = AdminController.create_user(self.entry_user.get(), self.entry_pass.get(), self.entry_name.get(), self.entry_email.get(), self.opt_role.get())
        if ok: self.refresh(); self.clear_form(); messagebox.showinfo("Success", "Đã thêm!")
        else: messagebox.showerror("Error", msg)

    def update_user(self):
        if not self.selected_user_id: return
        ok, msg = AdminController.update_user(self.selected_user_id, self.entry_user.get(), self.entry_pass.get(), self.entry_name.get(), self.entry_email.get(), self.opt_role.get())
        if ok: self.refresh(); messagebox.showinfo("Success", "Đã cập nhật!")
        else: messagebox.showerror("Error", msg)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def delete_user(self):
        if not self.selected_user_id: return
        if messagebox.askyesno("Confirm", "Xóa người dùng này?"):
            AdminController.delete_user(self.selected_user_id)
            self.refresh()
            self.clear_form()

# =============================================================================
# 3. CLASSES PAGE (Lớp học)
# =============================================================================
class ClassesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=7)
        self.grid_rowconfigure(0, weight=1)
        self.selected_class_id = None

        # --- LEFT: FORM ---
        self.form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        ctk.CTkLabel(self.form_frame, text="Thông tin Lớp học", font=("Arial", 18, "bold"), text_color=THEME["text_dark"]).pack(anchor="w", padx=20, pady=20)
        
        self.entry_name = self._entry(self.form_frame, "Tên Lớp / Môn học")
        self.entry_room = self._entry(self.form_frame, "Phòng học")
        self.entry_start = self._entry(self.form_frame, "Giờ bắt đầu (HH:MM)")
        self.entry_end = self._entry(self.form_frame, "Giờ kết thúc (HH:MM)")
        
        ctk.CTkLabel(self.form_frame, text="Giảng viên", font=("Arial", 12, "bold"), text_color=THEME["text_light"]).pack(anchor="w", padx=20, pady=(10, 0))
        self.prof_var = ctk.StringVar()
        self.opt_prof = ctk.CTkOptionMenu(self.form_frame, variable=self.prof_var, fg_color=THEME["main_bg"], text_color=THEME["text_dark"], button_color="gray")
        self.opt_prof.pack(padx=20, pady=(5,0), fill="x")

        # Buttons
        btn_box = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        btn_box.pack(fill="x", padx=20, pady=30)
        ctk.CTkButton(btn_box, text="+ Thêm", fg_color=THEME["success"], width=80, command=self.add_class).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_box, text="Sửa", fg_color=THEME["primary"], width=80, command=self.update_class).pack(side="left", padx=5)
        ctk.CTkButton(btn_box, text="Xóa", fg_color=THEME["danger"], width=80, command=self.delete_class).pack(side="left", padx=5)

        # --- RIGHT: TABLE ---
        self.table_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.table_frame.grid(row=0, column=1, sticky="nsew")
        
        cols = ("id", "name", "prof", "room", "time")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", style="Treeview")
        self.tree.heading("id", text="Mã Lớp")
        self.tree.heading("name", text="Tên Môn")
        self.tree.heading("prof", text="Giảng viên")
        self.tree.heading("room", text="Phòng")
        self.tree.heading("time", text="Thời gian")
        
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("room", width=60, anchor="center")
        
        sb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        sb.pack(side="right", fill="y", pady=15, padx=(0, 15))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _entry(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 12, "bold"), text_color=THEME["text_light"]).pack(anchor="w", padx=20, pady=(10, 0))
        e = ctk.CTkEntry(parent, border_width=1, fg_color="#F8FAFC", border_color="#E2E8F0")
        e.pack(padx=20, pady=(5, 0), fill="x")
        return e

    def refresh(self):
        # Update professor list
        profs = AdminController.list_professors()
        self.prof_map = {f"{p['id']} - {p['name']}": p['id'] for p in profs}
        self.opt_prof.configure(values=[""] + list(self.prof_map.keys()))
        self.search_data()

    def search_data(self, keyword=None):
        for i in self.tree.get_children(): self.tree.delete(i)
        classes = AdminController.list_classes(keyword)
        for c in classes:
            time_str = f"{str(c['startTime'])[:5]} - {str(c['endTime'])[:5]}"
            self.tree.insert("", "end", values=(c['classID'], c['className'], c['professorName'], c['room'], time_str))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        val = self.tree.item(sel[0], "values")
        self.selected_class_id = val[0]
        self.entry_name.delete(0, "end"); self.entry_name.insert(0, val[1])
        self.entry_room.delete(0, "end"); self.entry_room.insert(0, val[3])
        # Time parsing is simple string split here for demo
        times = val[4].split(" - ")
        if len(times) == 2:
            self.entry_start.delete(0, "end"); self.entry_start.insert(0, times[0])
            self.entry_end.delete(0, "end"); self.entry_end.insert(0, times[1])
        
        pass

    def add_class(self):
        pid = self.prof_map.get(self.prof_var.get())
        ok, msg = AdminController.create_class(self.entry_name.get(), pid, self.entry_room.get(), self.entry_start.get(), self.entry_end.get())
        if ok: self.refresh(); messagebox.showinfo("OK", "Đã thêm lớp")
        else: messagebox.showerror("Lỗi", msg)

    def update_class(self):
        if not self.selected_class_id: return
        pid = self.prof_map.get(self.prof_var.get())
        ok, msg = AdminController.update_class(self.selected_class_id, self.entry_name.get(), pid, self.entry_room.get(), self.entry_start.get(), self.entry_end.get())
        if ok: self.refresh(); messagebox.showinfo("OK", "Đã cập nhật")
        else: messagebox.showerror("Lỗi", msg)

    def delete_class(self):
        if self.selected_class_id and messagebox.askyesno("Confirm", "Xóa lớp này?"):
            AdminController.delete_class(self.selected_class_id)
            self.refresh()

# =============================================================================
# 4. ENROLLMENT PAGE (Ghi danh - Giữ nguyên logic, đổi giao diện)
# =============================================================================
class EnrollmentsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        
        # Toolbar
        bar = ctk.CTkFrame(self, fg_color="white", corner_radius=15, height=80)
        bar.pack(fill="x", pady=(0, 20))
        
        self.class_var = ctk.StringVar()
        self.stu_var = ctk.StringVar()
        
        ctk.CTkLabel(bar, text="Chọn Lớp:", text_color=THEME["text_dark"]).pack(side="left", padx=(20, 5))
        self.opt_class = ctk.CTkOptionMenu(bar, variable=self.class_var, width=200)
        self.opt_class.pack(side="left", padx=5)
        
        ctk.CTkLabel(bar, text="Chọn Sinh viên:", text_color=THEME["text_dark"]).pack(side="left", padx=(20, 5))
        self.opt_student = ctk.CTkOptionMenu(bar, variable=self.stu_var, width=200)
        self.opt_student.pack(side="left", padx=5)
        
        ctk.CTkButton(bar, text="+ Ghi danh", fg_color=THEME["success"], command=self.add_enroll).pack(side="left", padx=20)

        # Table Wrapper
        bg = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        bg.pack(fill="both", expand=True)
        
        ctk.CTkLabel(bg, text="Danh sách Sinh viên trong lớp", font=("Arial", 16, "bold"), text_color=THEME["text_dark"]).pack(anchor="w", padx=20, pady=20)

        self.tree = ttk.Treeview(bg, columns=("eid", "sid", "name"), show="headings", style="Treeview")
        self.tree.heading("eid", text="ID Ghi danh")
        self.tree.heading("sid", text="Mã SV")
        self.tree.heading("name", text="Họ tên")
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Bind change class
        self.opt_class.configure(command=self.load_table)

    def refresh(self):
        classes = AdminController.list_classes()
        self.classes_map = {f"{c['classID']} - {c['className']}": c['classID'] for c in classes}
        self.opt_class.configure(values=list(self.classes_map.keys()))
        
        students = AdminController.list_students()
        self.students_map = {f"{s['id']} - {s['name']}": s['id'] for s in students}
        self.opt_student.configure(values=list(self.students_map.keys()))

    def load_table(self, choice=None):
        cid = self.classes_map.get(self.class_var.get())
        for i in self.tree.get_children(): self.tree.delete(i)
        if not cid: return
        
        rows = AdminController.list_enrollments_by_class(cid)
        for r in rows:
            self.tree.insert("", "end", values=(r['enrollmentID'], r['studentID'], r['name']))

    def add_enroll(self):
        cid = self.classes_map.get(self.class_var.get())
        sid = self.students_map.get(self.stu_var.get())
        if cid and sid:
            AdminController.add_enrollment(cid, sid)
            self.load_table()
            messagebox.showinfo("OK", "Đã ghi danh!")

import tkinter as tk
