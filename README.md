# 🎓 Student Attendance Management System

> A comprehensive solution for digitizing the student attendance process in universities, replacing traditional paper-based methods.

## 📖 Introduction

The **Student Attendance Management System** is designed to streamline the attendance tracking process for educational institutions. It provides a centralized platform where Administrators, Professors, and Students can interact efficiently. The system ensures data accuracy, reduces manual workload, and provides real-time insights into student attendance records.

## ✨ Key Features

### 1. 👨‍💼 Administrator (Admin)
- **User Management:** Create, update, and delete accounts for Students and Professors.
- **System Configuration:** Manage roles, permissions, and system settings.
- **Academic Management:** Manage Subjects (Courses) and Course Classes.

### 2. 👨‍🏫 Professor
- **Class Management:** View assigned teaching schedules and student lists.
- **Attendance Tracking:** Record attendance for each session with statuses: *Present, Absent, Late, Excused*.
- **Edit Records:** Modify attendance status within a permitted timeframe.
- **Reports:** View and export attendance statistics for managed classes.

### 3. 👨‍🎓 Student
- **Dashboard:** View personal class schedules.
- **Attendance History:** Track personal attendance records and calculate absence percentage per subject.
- **Notifications:** Receive alerts regarding attendance status (optional).

## 🛠️ Tech Stack

- **Database:** SQL Server
- **Backend:** [...]
- **Frontend:** [...]
- **Design Tools:** VS Code , Draw.io,...

**Key Database Tables:**
- **`Users`**: Centralized authentication and role management (Single Table Inheritance strategy for IDs).
- **`Students` / `Professors`**: specialized profile data linked to `Users`.
- **`CourseClasses`**: Represents specific class sections for a semester.
- **`Enrollments`**: Junction table linking Students to Classes.
- **`Schedules` & `AttendanceRecords`**: The core logic for session-based attendance tracking.

## Installation & Setup

### Prerequisites
- **SQL Server** (2019 or later).
- [Your IDE Requirements:...].
