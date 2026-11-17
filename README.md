# E-Waste Collection Drive and Public Awareness Management System

**An Academic Software Project for Environmental Science & Computer Science Engineering (Course: BCSP508 - CSE)**

---

## 1. Project Overview

The **E-Waste Collection Drive and Public Awareness Management System** is a full-stack, software-based web application developed to address the escalating challenge of electronic waste (e-waste). The system facilitates responsible electronic disposal by providing citizens with a digital platform to register unused/defective electronics, schedule digital collection drives, access authorized government recycling centres, learn scientific disposal protocols, and test their environmental knowledge via an interactive quiz.

> **IMPORTANT ACADEMIC NOTICE:**  
> This is a **completely software-based academic project prototype**. In accordance with academic project specifications:
> - No physical IoT devices, microcontrollers, smart bins, or hardware sensors are required.
> - No actual physical vehicle dispatch or physical scrap recycling transactions are conducted.
> - All collection drives, verification statuses, manifests, and receipts are digitally simulated and managed in software.

---

## 2. Technology Stack

- **Backend:** Python 3.10+ / Flask 3.1
- **Database:** MySQL 8.0+ (via PyMySQL & SQLAlchemy) *(with automatic graceful fallback)*
- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **UI Framework:** Bootstrap 5.3
- **Vector Icons:** Font Awesome 6.5
- **Visual Analytics:** Chart.js 4.4

---

## 3. Key Modules & Features

### A. Multi-User Registration & Authentication Module
- Open citizen registration allowing **ANY** user to register with their own email address, full name, phone number, and password.
- Duplicate email prevention: Displays exact message `"Email already exists. Please login."` if an email is already registered.
- Secure credential management: Passwords stored securely using one-way cryptographic hashing (`generate_password_hash` with scrypt/PBKDF2); plain-text passwords are never stored.
- Multi-user authentication & session management: Each user logs in independently and accesses their own isolated dashboard.
- Strict data isolation: Users can view and manage only their own registered e-waste records and collection requests.
- Integrated **Forgot & Reset Password** workflow with secure time-limited verification tokens.
- Separate, secure administrative authentication portal (`/admin/login`); standard users cannot access admin management consoles.

### B. E-Waste Registration Module
- Register electronic items under standard CPCB categories:
  - Mobile Phones
  - Laptops
  - Computers
  - Batteries (Li-Ion, Lead-Acid, NiMH)
  - Chargers & Adapters
  - Televisions & Displays
  - Other Household Electronics
- Capture item details: Model Name, Quantity, Condition (*Working, Damaged, Not Working*), Description, City/Location, and optional image upload with live client preview.
- Stored relationally in MySQL with user association.

### C. Collection Request Module
- Citizens select registered e-waste items from their inventory.
- Choose collection preference: **Doorstep Pickup** or **Designated Drop-Off Centre**.
- Specify preferred collection date (with future date validation) and address details.
- Generates a **Unique Collection Request ID** (e.g., `EWC-202611-B48A`).
- **Request Tracking Stepper:** 4-stage visual timeline (*Submitted &rarr; Approved &rarr; In Progress &rarr; Completed / Rejected*).
- **Downloadable & Printable Formal Receipt:** Print-optimized letterhead manifest complete with digital verification seal and itemized list (`@media print` CSS).

### D. Authorized Collection Centre Information Module (Objective 2)
- Statutory directory of registered e-waste facilities based on official records from the **Central Pollution Control Board (CPCB) E-Waste EPR Portal** (`https://eprewaste.cpcb.gov.in/`) and the **Karnataka State Pollution Control Board (KSPCB)**.
- Specific facility classification: Distinctly categorizes and labels **Authorized Recyclers**, **Authorized Dismantlers**, **Collection Centres**, and **Authorized Refurbishers**.
- Prioritizes registered facilities in Bengaluru and Karnataka (e.g. M/s. E-Parisaraa, M/s. Sriram Eco Raksha, M/s. 4R Recycling, M/s. Saahas Zero Waste, M/s. Sheeltron Digital Systems, etc.).
- Displays full facility name, complete physical address, city, district, PIN code, facility type, official government registry link, and verification audit date.
- Contact transparency: Officially listed phone numbers and emails are displayed; where official details are unlisted, strictly displays `"Contact details not available"` without inventing fake numbers.
- Search and filter options by **City**, **District**, **PIN code**, **Keyword**, **Facility Type**, and **Accepted E-Waste Categories**.
- **Google Maps Directions** links provided only for verified facilities.
- **Verification Badges** rendered strictly for officially verified statutory facilities.
- All dummy and unverified records completely purged from the system.
- Full Admin capability to manually enter, audit, and update verified facilities.

### E. Proper E-Waste Disposal Guidance Module (Objective 2)
- Category-wise disposal protocols (Mobiles, Laptops, Batteries, Cables, Televisions).
- Step-by-step pre-disposal preparation instructions.
- Critical Do's and Don'ts comparison cards.
- Pre-disposal citizen safety checklist (Data wiping, terminal taping, glass protection).
- Explanation of why electronics must **NEVER** be mixed with domestic garbage (leachate, compaction fires).

### F. Environmental Awareness & Gamified Quiz Module
- Comprehensive analysis of hazardous substances: Lead (Pb), Mercury (Hg), Cadmium (Cd), Brominated Flame Retardants (BFRs), Hexavalent Chromium (Cr VI).
- Human biological effects and groundwater/soil ecological impacts.
- Circular economy and Urban Mining economics (gold/silver concentration in electronics vs mined ore).
- **Interactive 10-Question Eco-Awareness Quiz:** Instant answer evaluation, scientific explanations, animated scoring, and dynamic personalized **Certificate of Eco-Recognition**.

### G. Administrator Dashboard & Management Console
- Separate administrative login portal (`admin@ewaste.gov.in`).
- Real-time KPI statistics: Total Citizens, E-Waste Items, Total Requests, Pending, Approved, In Progress, Completed, Rejected, Total Centres.
- **Interactive Chart.js Visualizations:**
  1. E-Waste Breakdown by Category (Doughnut Chart)
  2. Collection Requests by Status (Bar Chart)
  3. Device Condition Breakdown (Pie Chart)
- Complete workflow review controls: Approve, Reject, Advance status, and append admin notes.
- Citizen directory and inventory inspector with photograph viewer.
- Full CRUD management over Authorized Recycling Centres (add new centre, edit, delete, toggle verification).
- Content management for disposal guidelines.

---

## 4. MySQL Database Design

The relational database is named `ewaste_management` (or configured via `.env`).

### Database Tables:
1. `users` — Citizen accounts, credentials, contact, and address details.
2. `admins` — Administrator accounts and authorization roles.
3. `ewaste_items` — Registered electronic waste records with category, condition, quantity, status, and photos.
4. `collection_requests` — Collection requests with unique code, scheduling, logistics, status, and remarks.
5. `collection_request_items` — Many-to-Many junction mapping multiple e-waste items to requests.
6. `recycling_centres` — Authorized CPCB/KSPCB recycling facilities, addresses, coordinates, sources, and verification status.
7. `disposal_guidelines` — Category-wise scientific disposal guidelines and do's & don'ts.
8. `awareness_content` — Educational articles on toxic substances, biological hazards, and regulations.

---

## 5. Step-by-Step Installation & Execution Guide (Windows)

### Prerequisites:
- Python 3.10 or newer installed (ensure "Add Python to PATH" was checked during install).
- MySQL Server 8.0+ running locally (e.g. MySQL Command Line, Workbench, or XAMPP).

### Step 1: Open Terminal in Project Directory
Open PowerShell or Command Prompt in the project folder:
```powershell
cd "c:\Users\Admin\OneDrive\Documents\ewaste_management_system"
```

### Step 2: Install Python Dependencies
Run:
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Configure Database Connection (.env)
The `.env` file is pre-configured. If you are using standard MySQL credentials (e.g., user `root` with password `1234` or empty), configure your `.env`:
```ini
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=varshitha
MYSQL_PASSWORD=varshitha
MYSQL_DB=varshitha

SECRET_KEY=eco_drive_secure_key_2026_academic_proj
FLASK_DEBUG=True
```

*(Note: You can also import the provided `database.sql` directly into MySQL Workbench or phpMyAdmin to inspect the raw schema and seed queries).*

### Step 4: Initialize and Seed Database
Run the automated initialization script:
```powershell
python init_db.py
```
This automatically connects to MySQL, creates all required tables, and seeds official CPCB/KSPCB centres, disposal guidelines, articles, default administrator, and sample student data.

### Step 5: Start the Web Application
Launch the Flask development server:
```powershell
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 6. Pre-Seeded Default Accounts

For quick evaluation and testing, the system includes two ready-to-use accounts:

| Role | Email | Password | Access Capabilities |
|---|---|---|---|
| **Super Administrator** | `admin@ewaste.gov.in` | `admin123` | Full Admin Dashboard, Charts, Request Approval, Centre CRUD |
| **Demo Student User** | `student@college.edu` | `student123` | Citizen Dashboard, Registered Items, Request History, Receipts |

*(You can also register brand new user accounts directly through the registration form).*

---

## 7. Running Automated Test Suite

To verify that all public routes, authentication workflows, item registration, request scheduling, receipt generation, and admin management controls function correctly:
```powershell
python test_app.py
```
All unit and integration tests run in under 2 seconds and report clean results.

---

## 8. Academic Project Credentials

- **Project Title:** E-Waste Collection Drive and Public Awareness Management System
- **Domain:** Environmental Engineering & Web Technologies
- **Course Code:** BCSP508 - CSE Final Year College Project
- **Regulation References:** *E-Waste (Management) Rules, 2022* (MoEFCC / CPCB)

