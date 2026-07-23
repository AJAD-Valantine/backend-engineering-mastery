# Campus Helpdesk Ticket Management System

## 🚀 Project Overview
The Campus Helpdesk Ticket Management System is a robust, server-side rendered web application designed to allow students and staff members to report technical and administrative problems to the campus support team. 

## 🛠️ Tech Stack
This application was built strictly without JavaScript or frontend frameworks to focus entirely on core backend mechanics and server-side rendering[cite: 1].
* **Backend:** Python, FastAPI
* **Database:** MySQL, SQLAlchemy (ORM)
* **Frontend:** HTML5, CSS3, Jinja2 Templates[cite: 1]

## ✨ Core Features
* **Ticketing Dashboard:** Displays real-time statistics of total, open, in-progress, and resolved tickets[cite: 1].
* **Full CRUD Operations:** Users can submit new tickets, while helpdesk staff can view, edit, update statuses, and delete existing tickets[cite: 1].
* **Custom Error Handling:** Elegant UI fallbacks for 404 (Not Found) and 422 (Unprocessable Entity) errors.

---

## 🧠 Key Concepts Mastered

Building this project without modern frontend frameworks forced me to learn the foundational mechanics of how the web actually works. Here are the major concepts I implemented:

### 1. Jinja2 Template Inheritance
Instead of copying and pasting the navigation bar and HTML `<head>` into every single file, I learned how to use template inheritance. 
* I created a master `base.html` file that acts as the application's skeleton.
* I used `{% block content %}` spaces within the base file.
* Child templates (like `index.html` or `ticket_create.html`) simply use `{% extends "base.html" %}` to plug their unique content directly into the master layout, keeping the codebase incredibly DRY (Don't Repeat Yourself).

### 2. Catching HTML Form Data (URL-Encoded Data)
Modern APIs usually communicate via JSON, but standard HTML `<form>` tags send data differently (`x-www-form-urlencoded`).
* I learned how to bridge the gap between standard HTML and FastAPI using the `Form(...)` class.
* By ensuring the `name="category"` attribute in my HTML exactly matched the `category: str = Form(...)` parameter in my Python route, I successfully caught, validated, and processed user input directly from the browser.

### 3. The Post/Redirect/Get Pattern 
I learned how to properly handle HTTP POST requests so users don't get trapped on a blank processing page or accidentally submit a form twice.
* When a user submits a ticket, the backend processes the database insertion.
* Instead of returning a template directly from the POST route, I learned to use `RedirectResponse(url="/tickets", status_code=303)`. 
* This immediately bounces the user's browser back to a standard GET route, seamlessly displaying their newly created or updated data.

### 4. Global Exception Handling
To make the application feel professional, I learned how to intercept FastAPI's default raw JSON error responses.
* I implemented `@app.exception_handler` decorators for `StarletteHTTPException` and `RequestValidationError`.
* If a user types a bad URL or bypasses HTML form validation, these global catchers intercept the error and serve a beautifully styled `error.html` page instead of crashing the browser or leaking JSON code to the frontend.

### 5. SQLAlchemy ORM Integration
I learned how to interact with a MySQL database using Python objects instead of writing raw SQL strings.
* Mapped database tables to Python classes.
* Used `.scalar_one_or_none()` to safely fetch single records and handle missing IDs without crashing the server.

---