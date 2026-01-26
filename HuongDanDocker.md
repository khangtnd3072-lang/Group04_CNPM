# Student Attendance System (Database)

Dự án này sử dụng Docker để khởi tạo Microsoft SQL Server.

## 1. Yêu cầu (Prerequisites)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/).

## 2. Cách chạy dự án
Mở Terminal tại thư mục dự án và chạy lệnh sau để khởi động Database:
Lệnh: docker-compose up -d

Sau khi container chạy, thực hiện lệnh sau để nạp dữ liệu mẫu (chỉ cần chạy lần đầu):
Lệnh: docker exec -it my_sql_server /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P Password123! -C -i /do


## 3.Thông tin kết nối (Connection Info)
Server: localhost, 1433
Database: AttendanceSystem
User: sa
Password: Password123!