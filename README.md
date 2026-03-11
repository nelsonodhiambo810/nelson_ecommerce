# Nyar Gi Jack Sound - Premium Audio E-Commerce 🔊

A high-performance, full-stack E-commerce platform built for the professional audio engineering industry in Kenya. This platform manages high-end gear inventory and handles secure mobile payments.

## 🛠️ Tech Stack
* **Backend:** Django 5.x (Python)
* **Frontend:** Bootstrap 5, Custom CSS, JavaScript
* **Database:** SQLite (Development)
* **Payments:** Safaricom M-Pesa Daraja API (STK Push Integration)
* **Design:** Custom "Jazzmin" Admin Dashboard

## ✨ Key Features
* **Advanced Search Engine:** Custom Q-object logic to search through titles and descriptions simultaneously.
* **Session-Based Cart:** A custom-built engine that handles complex price math (Price × Quantity) without external plugins.
* **Dynamic Category Filtering:** Optimized slug-based navigation for subwoofers, amplifiers, and accessories.
* **Premium UI/UX:** A sleek, dark-themed interface designed for professional audiophiles.
* **Mobile Ready:** Fully responsive design that looks great on phones and laptops.

## 🚀 How to Run Locally
1. Clone the repo: `git clone https://github.com/nelsonodhiambo810/nelson_ecommerce.git`
2. Create and activate venv: `python -m venv venv`
3. Install requirements: `pip install django django-jazzmin pillow`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

---
**Built by Nelson Odhiambo** *Full-Stack Developer | Python & Django Enthusiast*