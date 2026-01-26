/* CREATE DATABASE AttendanceSystem;
GO

USE AttendanceSystem;
GO
CREATE TABLE [User] (
    userID VARCHAR(50) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    [password] VARCHAR(255) NOT NULL,
    fullName NVARCHAR(50),
    email VARCHAR(100),
    role VARCHAR(20) NOT NULL
);
GO
CREATE TABLE Student (
    studentID VARCHAR(50) PRIMARY KEY,
    userID VARCHAR(50) UNIQUE,
    CONSTRAINT FK_Student_User
        FOREIGN KEY (userID)
        REFERENCES [User](userID)
        ON DELETE CASCADE
);
GO
CREATE TABLE Professor (
    professorID VARCHAR(50) PRIMARY KEY,
    userID VARCHAR(50) UNIQUE,
    CONSTRAINT FK_Professor_User
        FOREIGN KEY (userID)
        REFERENCES [User](userID)
        ON DELETE CASCADE
);
GO
CREATE TABLE CourseClass (
    classID VARCHAR(50) PRIMARY KEY,
    className VARCHAR(50) NOT NULL,
    professorID VARCHAR(50),
    room VARCHAR(50),
    startTime TIME,
    endTime TIME,
    CONSTRAINT FK_CourseClass_Professor
        FOREIGN KEY (professorID)
        REFERENCES Professor(professorID)
        ON DELETE SET NULL
);
GO
CREATE TABLE Enrollment (
    enrollmentID INT IDENTITY(1,1) PRIMARY KEY,
    classID VARCHAR(50) NOT NULL,
    studentID VARCHAR(50) NOT NULL,
    CONSTRAINT FK_Enrollment_Class
        FOREIGN KEY (classID)
        REFERENCES CourseClass(classID)
        ON DELETE CASCADE,
    CONSTRAINT FK_Enrollment_Student
        FOREIGN KEY (studentID)
        REFERENCES Student(studentID)
        ON DELETE CASCADE,
    CONSTRAINT UQ_Enrollment UNIQUE (classID, studentID)
);
GO
CREATE TABLE AttendanceSession (
    sessionID VARCHAR(50) PRIMARY KEY,
    classID VARCHAR(50) NOT NULL,
    sessionDate DATETIME NOT NULL,
    status VARCHAR(20),
    CONSTRAINT FK_AttendanceSession_Class
        FOREIGN KEY (classID)
        REFERENCES CourseClass(classID)
        ON DELETE CASCADE
);
GO
CREATE TABLE AttendanceRecord (
    attendanceID VARCHAR(50) PRIMARY KEY,
    sessionID VARCHAR(50) NOT NULL,
    studentID VARCHAR(50) NOT NULL,
    status VARCHAR(20),
    checkinMethod VARCHAR(50),
    checkinTime DATETIME,
    CONSTRAINT FK_AttendanceRecord_Session
        FOREIGN KEY (sessionID)
        REFERENCES AttendanceSession(sessionID)
        ON DELETE CASCADE,
    CONSTRAINT FK_AttendanceRecord_Student
        FOREIGN KEY (studentID)
        REFERENCES Student(studentID)
        ON DELETE CASCADE,
    CONSTRAINT UQ_Attendance UNIQUE (sessionID, studentID)
);
GO 
