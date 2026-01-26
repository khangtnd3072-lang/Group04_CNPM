import sys
import customtkinter as ctk
from views.login_view import LoginView
from views.admin_view import AdminView
from views.student_view import StudentView
from views.professor_view import ProfessorView 

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hệ Thống Quản Lý Điểm Danh - AMS")
        self.geometry("1100x700")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.current_user = None

        view_list = (LoginView, AdminView, StudentView, ProfessorView)

        for F in view_list:
            page_name = F.__name__
            try:
                frame = F(parent=self.container, controller=self)
                self.frames[page_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
            except Exception as e:
                print(f"Lỗi khởi tạo {page_name}: {e}")

        # Mở màn hình đăng nhập đầu tiên
        self.show_frame("LoginView")

    def show_frame(self, page_name, data=None):
        try:
            frame = self.frames[page_name]
            
            # --- XỬ LÝ RIÊNG CHO TỪNG VIEW ---

            # 1. View Giảng Viên (Gộp)
            if page_name == "ProfessorView":
                if hasattr(frame, 'show_dashboard'):
                    frame.show_dashboard()

            # 2. View Admin
            elif page_name == "AdminView" and hasattr(frame, 'refresh_data'):
                frame.refresh_data()

            # 3. View Sinh Viên
            elif page_name == "StudentView" and hasattr(frame, 'refresh_data'):
                frame.refresh_data()
            
            # Hiển thị frame lên trên cùng
            frame.tkraise()

        except KeyError:
            print(f"LỖI: Màn hình '{page_name}' chưa được đăng ký trong main.py!")

    def on_closing(self):
        try: self.destroy()
        except: pass
        finally: sys.exit(0)

if __name__ == "__main__":
    app = App()
    app.mainloop()
