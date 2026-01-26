# 🎓 Student Attendance Management System

> A modern Desktop Application for managing university attendance, built with Python and CustomTkinter.

---

## 📖 Introduction

The Student **Attendance Management System (AMS)** replaces traditional paper-based attendance with a digital, automated solution. Unlike web interfaces, this desktop application offers a responsive, native experience using a modern GUI framework. It connects directly to a centralized SQL Server database to ensure data integrity and real-time updates for **Administrators**, **Professors**, and **Students**.

---

## ✨ Key Features

### 👨‍💼 Administrator (Admin)
- User Management: CRUD operations for Professors and Students.
- Course Management: Assign professors to classes and manage schedules.
- Database Oversight: Direct control over the SQL Server data.

### 👨‍🏫 Professor
- Class Management: View list of assigned courses and student enrollments.
- Session Management: Create new attendance sessions (Status: Open/Closed).
- Flexible Attendance:
    + Manual: Toggle status (Present/Absent) via a visual grid.
    + QR Code Mode: Generate dynamic QR codes for students to scan.
    + Code Mode: Generate a 6-digit PIN for students to enter.
- Real-time Statistics: View attendance rates and history immediately.

### 👨‍🎓 Student
- Dashboard: Overview of enrolled subjects and current attendance percentage.
- Smart Check-in:
   + "Check-in Now" Button: Automatically appears when a session is OPEN.
   + Methods: Supports GPS (Simulated), QR Scanning, or Manual Code entry.
- History Tracking: View detailed logs of every session (Present, Absent, Late, Excused).

---

## 🛠️ Technology Stack

- **Language**: Python 3.x
- **GUI Framework**: CustomTkinter (Modern UI wrapper for Tkinter)
- **Database**: Microsoft SQL Server
- **Database Driver**: pyodbc
- **Key Libraries**:
   + Pillow (Image processing)
   + qrcode (QR generation)
   + tkcalendar (Date picking)

---

## 🗄️ Database Design Overview

**Main Tables:**
- **`Users`**  
  Base table for authentication (UserID, Username, Password, Role).
- **`Students` / `Professors`**  
  Extended profiles linked to User.
- **`CourseClasses`**  
  Stores class details (Name, Room, Schedule).
- **`Enrollments`**  
  Links Students to CourseClasses (N-N relationship).
- **`AttendanceSession`**  
  Represents a specific date/time for a class.
- **`AttendanceRecords`**  
  Stores the actual status (Present/Absent), check-in time, and method.

---

## ⚙️ Installation & Setup

### Prerequisites
1. Python 3.10+ installed.
2. SQL Server installed and running.
3. ODBC Driver 17/18 for SQL Server.

---

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

--- 

## 👥 Default Login Credentials (Demo Data)

Role: Admin
Username: admin
Password: 123

Role: Student
Username: sv1
Password: 123

Role: Professor
Username: gv1
Password: 123
