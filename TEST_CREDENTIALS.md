# Test Credentials

This file contains test credentials for the Campus Resource Hub application.

## Admin Account
- **Email:** admin@university.edu
- **Password:** admin123
- **Role:** Admin
- **Department:** IT Services

## Staff Accounts

### Dr. Sarah Johnson
- **Email:** sarah.johnson@university.edu
- **Password:** staff123
- **Role:** Staff
- **Department:** Computer Science
- **Owns:** Innovation Lab Study Room A, Engineering Lab - 3D Printer Station

### Prof. Michael Chen
- **Email:** michael.chen@university.edu
- **Password:** staff123
- **Role:** Staff
- **Department:** Engineering
- **Owns:** Professional Camera & Lighting Kit, Math Tutoring

## Student Accounts

### Alex Martinez
- **Email:** alex.martinez@university.edu
- **Password:** student123
- **Role:** Student
- **Department:** Engineering
- **Has bookings and reviews**

### Emily Wilson
- **Email:** emily.wilson@university.edu
- **Password:** student123
- **Role:** Student
- **Department:** Business
- **Has bookings and reviews**

### John Doe
- **Email:** john.doe@university.edu
- **Password:** student123
- **Role:** Student
- **Department:** Business
- **Has bookings**

---

## How to Populate Dummy Data

Run the following command to populate the database with dummy data:

```bash
python populate_dummy_data.py
```

This will create:
- 6 users (1 admin, 2 staff, 3 students)
- 6 resources (study rooms, lab equipment, event spaces, etc.)
- 4 bookings (some approved, some pending)
- 4 reviews
- Sample messages

**Note:** Running this script will clear all existing data in the database!

