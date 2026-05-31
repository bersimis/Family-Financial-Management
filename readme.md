# Domestic Financial Management

A desktop application developed for managing family finances and tracking shared household incomes and expenses. This project provides a straightforward way for multiple users to handle personal finance management collaboratively.

## Core Features

*   User Authentication: Secure registration and login system with hashed passwords.
*   Category Management: Create, modify, and delete custom categories for both incomes (e.g., Salary) and expenses (e.g., Groceries, Rent, Loans).
*   Transaction Tracking: Add, edit, or delete specific daily or monthly transactions.
*   Recurring Transactions: Mark specific incomes or expenses as monthly recurring items to automate data entry.
*   Data Visualization: Generate graphical representations of financial data over specific timeframes.
*   Data Export: Export transaction records to Microsoft Excel (.xlsx) files for external processing.

## Application Architecture

This diagram illustrates the high-level architecture of the application.

![Application Architecture Diagram](assets/architecture.png)

## User Login Flow

The following flowchart shows the process of user authentication, from login to accessing the main dashboard.

![User Login Flowchart](assets/UserFlowchart.png)

## Database ERD

This diagram illustrates the database structure and relationships between the core entities of the application.

![Database ERD](docs/database/ERD.png?v=2)

## Built With

*   Python 3
*   Tkinter (GUI)
*   SQLite (Database)
*   Matplotlib (Data Visualization)
*   XlsxWriter (Excel Export)
