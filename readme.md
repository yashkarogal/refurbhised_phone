# Refurbished Phone Selling App

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat&logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🚀 Overview

The Refurbished Phone Selling App is a simple web application designed to manage an inventory of refurbished phones, calculate their optimal selling prices across various e-commerce platforms, and track their listing status. It consists of a Flask backend API and a pure HTML/CSS/JavaScript frontend.

This application helps users:
* Add new refurbished phones to their inventory.
* View all phones, their base costs, conditions, and stock levels.
* See calculated selling prices and mapped conditions for different platforms (PlatformX, PlatformY, PlatformZ) based on defined profit margins and platform fees.
* Identify phones that are not currently listed for sale and understand the reasons (e.g., out of stock, sold B2B/direct, unprofitable).
* Update stock levels and mark phones as sold B2B/direct, instantly reflecting changes in listing status.

---

## ✨ Features

### Backend (Flask)
* **RESTful API:** Provides endpoints for managing phone inventory.
* **Dynamic Pricing Calculation:** Computes selling prices considering:
    * `base_cost` of the phone.
    * `DESIRED_PROFIT_MARGIN` (20% by default).
    * Platform-specific fees (`PLATFORM_FEES` - percentage or mixed flat + percentage).
* **Condition Mapping:** Translates internal phone conditions (Like New, Good, Fair) to platform-specific labels.
* **Listing Status Logic:** Determines if a phone is `is_listed` based on stock, B2B/direct sales, and profitability across platforms. Provides `not_listed_reasons` for clarity.
* **In-Memory Database:** Uses a Python dictionary (`phones_db`) for simplicity (data is not persistent across restarts).
* **Dummy Login:** A basic `/api/login` endpoint with hardcoded credentials (`admin`/`password123`) for demonstration purposes.

### Frontend (HTML, Tailwind CSS, JavaScript)
* **Intuitive User Interface:** Built with HTML and styled using Tailwind CSS for a modern, responsive design.
* **Login Page:** Secures access to the main application (with dummy credentials).
* **Add Phone Form:** Allows users to input new phone details.
* **Dynamic Inventory Table:** Displays all phone details fetched from the backend.
    * Shows **real-time calculated selling prices** and **platform-specific conditions**.
    * Visually indicates `Listing Status` (Listed/Not Listed).
    * Action buttons to `Sell One` (decreases stock) or `Toggle B2B Sale`.
* **"Phones Not Listed" Section:** Clearly highlights phones that cannot be listed, along with the precise reasons (e.g., "Out of Stock", "Unprofitable on PlatformX", "Sold B2B/Direct").
* **Transient Messages:** Provides user feedback via temporary notification pop-ups.

---

## 🛠️ Installation and Setup

### Prerequisites
* [Python 3.8+](https://www.python.org/downloads/)
* [pip](https://pip.pypa.io/en/stable/installation/) (Python package installer)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/refurbished-phone-app.git](https://github.com/your-username/refurbished-phone-app.git)
    cd refurbished-phone-app
    ```

2.  **Set up a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate   # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install Flask Flask-Cors
    ```

4.  **Run the Flask backend:**
    Ensure both the Python script (`your_app_name.py`, assuming you saved the Flask code as `app.py`) and the `index.html` file are in the same directory.
    ```bash
    python app.py
    ```
    The Flask app will start on `http://127.0.0.1:5000/`.

5.  **Access the frontend:**
    Open your web browser and navigate to `http://127.0.0.1:5000/`.

---

## 👨‍💻 Usage

### Login
* **Username:** `admin`
* **Password:** `password123`
    (These are hardcoded for demonstration purposes.)

### Add New Phone
1.  Fill in the "Add New Phone" form with `Model`, `Base Cost`, `Condition` (select from dropdown: "Like New", "Good", "Fair"), and `Stock`.
2.  Click "Add Phone". The new phone will appear in the "Current Inventory & Listings" table.

### Current Inventory & Listings Table
* **Model, Base Cost, Internal Condition, Stock:** Basic phone information.
* **Sold B2B/Direct:** Indicates if the phone was sold directly or business-to-business.
* **Platform X/Y/Z (Price / Condition):** Shows the calculated selling price for each platform (or "N/A" if unprofitable) and the condition mapping. An "(Unprofitable)" note appears if the phone cannot be listed profitably on that specific platform.
* **Listing Status:** A badge indicating "Listed" (green) if the phone can be profitably sold on at least one platform, is in stock, and not sold B2B/direct. Otherwise, it's "Not Listed" (red).
* **Actions:**
    * **Sell One:** Decreases the stock by 1. The button is disabled if stock is 0.
    * **Toggle B2B Sale:** Changes the `Sold B2B/Direct` status (Yes/No).

### Phones Not Listed (Reasons)
* This section dynamically lists all phones that have a "Not Listed" status, providing the specific reasons (e.g., "Out of Stock", "Sold B2B/Direct", "Unprofitable on [Platform Name]", "Unprofitable on all platforms").

---

## ⚙️ Configuration

You can modify the following parameters in the `app.py` file:

* **`PLATFORM_FEES`**: Adjust platform fees for `PlatformX`, `PlatformY`, and `PlatformZ`.
    ```python
    PLATFORM_FEES = {
        "PlatformX": {"type": "percentage", "value": 0.10},  # 10%
        "PlatformY": {"type": "mixed", "percentage": 0.08, "flat": 2.00},  # 8% + $2
        "PlatformZ": {"type": "percentage", "value": 0.12}   # 12%
    }
    ```
* **`CONDITION_MAPPING`**: Customize how internal conditions map to platform-specific conditions.
* **`DESIRED_PROFIT_MARGIN`**: Change the target profit margin.
    ```python
    DESIRED_PROFIT_MARGIN = 0.20  # 20% profit margin
    ```
* **Dummy Data**: The `phones_db` dictionary in the `if __name__ == '__main__':` block can be modified to include different initial inventory.

---

## ⚠️ Important Notes

* **In-Memory Database:** The `phones_db` is an in-memory dictionary. This means **all data will be lost when the Flask server restarts.** For a production application, you would integrate a persistent database (e.g., SQLite, PostgreSQL, MongoDB).
* **Dummy Authentication:** The login system is purely for demonstration. Do **not** use `admin`/`password123` or this authentication method in a real-world application. Implement proper user management, password hashing, and secure token-based authentication (like JWT).
* **Error Handling:** While some basic error handling is present, a production application would require more robust validation, logging, and comprehensive error responses.

---

## 🤝 Contributing

Feel free to fork the repository, open issues, or submit pull requests.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or feedback, please open an issue in the repository.


https://github.com/user-attachments/assets/a173a05d-5ae0-4584-910b-32b197799f16


