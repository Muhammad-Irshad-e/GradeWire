# **GRADEWIRE — Student Performance & Academic Management System**

GradeWire is a comprehensive web-based academic management platform designed to streamline and automate essential academic and administrative activities in educational institutions.
It provides separate role-based dashboards for **Admin**, **Teachers**, and **Students**, ensuring secure and efficient management of attendance, marks, courses, subjects, and student records.

GradeWire is developed using **Django (Python)**, HTML, CSS, JavaScript, and SQLite.

----

## 📌 **Table of Contents**

* [Abstract](#abstract)
* [Features](#features)
* [System Overview](#system-overview)
* [Role-Based Functionalities](#role-based-functionalities)
* [Tech Stack](#tech-stack)
* [Installation Guide](#installation-guide)
* [Future Enhancements](#future-enhancements)
* [Contributors](#contributors)

---

# 📘 **Abstract**

GradeWire is an online platform developed to digitize academic workflows such as attendance tracking, marks management, course administration, student information handling, and performance monitoring.
The system simplifies communication between administrators, teachers, and students while ensuring secure data operations and scalable architecture.

With clear dashboards and automated processes, GradeWire improves institutional efficiency, transparency, and decision-making.

---

# 🚀 **Features**

### ✅ **Admin Features**

* Add/Edit/Delete **Teachers**
* Add/Edit/Delete **Students**
* Manage **Courses**
* Manage **Subjects**
* Approve student registrations
* Full control of academic settings

---

### 👨‍🏫 **Teacher Features**

* Manage attendance
* Record internal & external marks
* View student lists
* View students’ academic statistics
* View/update own profile

---

### 👨‍🎓 **Student Features**

* View personal profile
* Check daily & monthly attendance
* View grades for each exam
* Monitor performance with charts

---

# 🏫 **System Overview**

GradeWire uses a centralized database and separates functionalities based on user roles.
Each module is designed to be user-friendly and secure.

The system includes:

* Secure authentication
* Role-based access (RBAC)
* Attendance module (hour-wise)
* Marks management (internal/external/total)
* Academic dashboards
* Data visualization (charts)
* Admin panel for configuration

---

# 🔐 **Role-Based Functionalities**

### **Admin**

| Feature          | Description                          |
| ---------------- | ------------------------------------ |
| Manage Teachers  | Add, edit, delete teachers           |
| Manage Students  | Add, edit, delete students           |
| Manage Courses   | Create and update courses            |
| Manage Subjects  | Assign subjects to courses/semesters |
| Approve Accounts | Approve student registrations        |

---

### **Teacher**

| Feature    | Description                       |
| ---------- | --------------------------------- |
| Attendance | Mark student attendance hour-wise |
| Marks      | Record internal & external marks  |
| View Stats | Monitor student progress          |
| Profile    | Manage personal details           |

---

### **Student**

| Feature    | Description                 |
| ---------- | --------------------------- |
| Attendance | View present / absent chart |
| Grade      | View subject-wise marks     |
| Profile    | Access personal details     |

---

# 🛠 **Tech Stack**

### **Frontend**

* HTML
* CSS
* JavaScript
* Bootstrap

### **Backend**

* Python
* Django Framework

### **Database**

* SQLite

### **Tools Used**

* VS Code
* Django Admin
* Chart.js (for data visualization)

---

# ⚙️ **Installation Guide**

### **1. Clone the Repository**

```bash
git clone https://github.com/your-username/gradewire.git
cd gradewire
```

### **2. Create Virtual Environment**

```bash
python -m venv env
```

```bash
env\Scripts\activate   # Windows
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Apply Migrations**

```bash
python manage.py migrate
```

### **5. Create Superuser**

```bash
python manage.py createsuperuser
```

### **6. Run Server**

```bash
python manage.py runserver
```

Now open:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**



# 🔮 **Future Enhancements**

* Mobile application (Android/iOS)
* AI-based student performance prediction
* Biometric/RFID attendance
* Cloud-based storage
* Real-time notifications
* Integrated chat system
* LMS Integration (Google Classroom / Moodle)
* Multilingual UI support



# 👥 **Contributors**

* **Muhammad Irshad**
* **Muhammad Shammas**
* **Jumail K**

Guided by:
**Dr. Minimol VK**

