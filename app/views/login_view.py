import customtkinter as ctk
from tkinter import messagebox
from controllers import AuthController

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Side
        left = ctk.CTkFrame(self, fg_color="white")
        left.grid(row=0, column=0, sticky="nswe")
        form = ctk.CTkFrame(left, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(form, text="Đăng nhập", font=("Arial", 24, "bold"), text_color="black").pack(pady=20)
        self.user_entry = ctk.CTkEntry(form, placeholder_text="Username", width=300)
        self.user_entry.pack(pady=10)
        self.pass_entry = ctk.CTkEntry(form, placeholder_text="Password", show="*", width=300)
        self.pass_entry.pack(pady=10)
        ctk.CTkButton(form, text="Đăng nhập", width=300, command=self.handle_login).pack(pady=20)

        # Right Side
        right = ctk.CTkFrame(self, fg_color="#2b2b2b")
        right.grid(row=0, column=1, sticky="nswe")
        ctk.CTkLabel(right, text="Hệ Thống Quản Lý\nĐiểm Danh", font=("Arial", 30, "bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

# Trong file login_view.py -> hàm handle_login

    def handle_login(self):
        u, p = self.user_entry.get(), self.pass_entry.get()
        user = AuthController.login(u, p)
        if user:
            self.controller.current_user = user
            role = (user.get('role') or '').lower()
            
            if role == 'admin':
                self.controller.show_frame("AdminView")
            elif role == 'student':
                self.controller.show_frame("StudentView")
            else:
                self.controller.show_frame("ProfessorView")
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu")
