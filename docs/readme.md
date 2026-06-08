# Development Plan & System Architecture

Welcome to the Family Finance Management application repository. This document outlines the code architecture (Screen-based Architecture with centralized data management) and the task delegation among team members.

## 1. Project Structure

To keep the code clean, avoid circular imports, and prevent massive, unreadable files, the project is divided into structured folders and files inside the `src/` directory.

### Core & Database

- `src/dashboard.py`: The entry point of the application. It contains the main window GUI shell, navigation sidebar, financial summary calculations, and executes the application main loop.
- `src/database/database.py`: The connection manager of the app. It connects to the SQLite database (`financial_management.db`) and handles schema creation.
- `src/config_and_styles.py`: Defines global variables, styling constants, theme colors, dimensions, and typography settings used throughout all GUI windows to maintain visual consistency.

### Authentication

- `src/login_system/auth.py`: Manages the session state. It stores the `User` object (ID, username, and role ID) of the currently logged-in user so that all other views can verify permission.
- `src/login_system/login.py`: The graphical user interface (Tkinter) and logic for user login. It verifies hashed credentials via the database and, if successful, updates `auth.py` and opens the Dashboard.
- `src/login_system/register.py`: The new user registration form. Includes necessary validations (username format, password complexity, birth year check) and secure password storage (hashing).

### Main UI

- `src/finance_files/transactions.py`: The form for entering new transactions, the table (Treeview) displaying transactions, and the automatic monthly transaction generation system.
- `src/finance_files/categories.py`: A management window (add/delete) for available income and expense categories (e.g., Salary, Rent, Supermarket).
- `src/admin/admin_panel.py`: Handles admin-only privileges (user listing, role dropdown updates, password resets).
- `src/admin/profile.py`: Form for active users to update their username and change password with verification.

### Data Analysis & Export

- `src/analytics/charts.py`: Connects with the `matplotlib` library to create pie and bar charts embedded directly into the Tkinter window.
- `src/analytics/export.py`: Exports transaction records for the active user to a Microsoft Excel file (`.xlsx`) using pandas.

---

## 2. Role-Based Access Control (RBAC)

The application enforces security privileges based on the user's role:
*   **Admin (Role ID: 1)**: Full read and write permissions across all views, and exclusive access to the Admin Panel for user management, role updates, and password resets.
*   **Editor (Role ID: 2)**: Full read and write access to transactions and categories, but cannot access the Admin Panel.
*   **Viewer (Role ID: 3)**: Read-only access. The input form and delete controls on the Transactions screen are hidden, and all backend operations block any additions or deletions for transactions and categories.

---

## 3. Tasks per person

The development of the application is carried out in parallel by the 3 team members, organized by directories and components.

### Member 1: Core Architect & Security Lead
**Files**: `src/database/`, `src/login_system/`, `src/admin/`, `src/config_and_styles.py`
**Responsibilities**:
- Design SQLite tables (`roles`, `users`, `categories`, `transactions`).
- Implement user authentication, registration, profiles, and password hashing.
- Manage user session states and admin user management panel.

### Member 2: UI & Transactions Manager
**Files**: `src/dashboard.py`, `src/finance_files/`
**Responsibilities**:
- Create the main window (Dashboard) with the sidebar navigation menu.
- Build the transactions table, filter bar, and category windows.
- Connect the UI forms with database functions to insert and delete data.

### Member 3: Data Analyst & Visuals
**Files**: `src/analytics/`
**Responsibilities**:
- Develop data visualization graphs (pie charts, comparisons) using Matplotlib.
- Handle Excel file export logic.

---

## 4. Packaging the Application (PyInstaller)

To compile the application into a standalone Windows executable (`.exe`), follow these exact instructions:

### Prerequisites
1. Ensure Python 3 is installed.
2. Install the required third-party libraries:
   ```bash
   pip install pandas matplotlib openpyxl xlsxwriter pyinstaller
   ```

### Compilation Command
From the root directory of the project, run the following command in PowerShell or Command Prompt:
```bash
py -m PyInstaller --noconsole --onefile --paths=src --name="Family Financial Management" src/dashboard.py
```

### Explanation of flags:
*   `--noconsole`: Hides the command-line console window, showing only the graphical interface (GUI).
*   `--onefile`: Bundles the entire application and all its dependencies into a single executable file.
*   `--paths=src`: Tells PyInstaller to resolve project modules inside the `src/` directory.
*   `--name="Family Financial Management"`: Sets the name of the generated executable.
*   `src/dashboard.py`: Specifies the main entry point of the application.

### Output
*   The generated executable will be located in the **`dist/`** directory (`dist/Family Financial Management.exe`).
*   The build configuration file will be saved as `Family Financial Management.spec`.
*   All build process temporary files will be stored in the `build/` directory.
*   Note: The `build/`, `dist/`, and `*.spec` paths are added to `.gitignore` to keep the source control clean.

### Running the Executable
*   Copy the `Family Financial Management.exe` file from the `dist/` directory and place it anywhere on a Windows computer.
*   On the first run, the executable will automatically create the `database/` folder (containing `financial_management.db`) and the `logs/` folder (containing `app.log`) in the same directory where it is executed. No other files are required to be distributed with it.
