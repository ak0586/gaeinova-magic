# 🪔 Gaeinova Magic

### A Full-Stack E-Commerce Platform for Handcrafted Candles & Festive Gifts  

**Gaeinova Magic** is a complete e-commerce web application designed for selling handcrafted candles and festive gift sets.  
It features a **beautifully responsive frontend**, a **secure FastAPI backend**, **JWT-based authentication**, and an **admin dashboard** for managing products, categories, and customer orders.  

---

## 🚀 Features

### 🧍 User Features
- 🕯️ Browse products by **category**, **search**, or **price range**
- 🛒 Add items to the **shopping cart**
- 💳 Place **orders with Cash on Delivery (COD)**
- 🔍 View featured and trending products
- 💌 Subscribe to the **newsletter**
- 📞 Send **contact messages** via the contact form

### 🧑‍💼 Admin Features
- 🔐 **Admin authentication** via JWT token
- 🧾 Access **Admin Dashboard** to manage store operations:
  - ➕ Add new products (with image upload)
  - ✏️ Edit or ❌ delete existing products
  - 📦 Add or delete categories
  - 🧾 View and update order status
  - 📬 View and delete contact messages
- 🧮 View revenue, total orders, and stock levels

---

## 🖼️ Project Screenshots

| User Homepage | Product Detail | Admin Dashboard |
|----------------|----------------|-----------------|
| ![HomePage](https://github.com/ak0586/gaeinova-magic/blob/main/assets/Home.png) | ![Product Detail](https://github.com/ak0586/gaeinova-magic/blob/main/assets/Product_detail.png) | 
![Admin Dashboard](https://github.com/ak0586/gaeinova-magic/blob/main/assets/Admin_1.png) |



---

## 🧩 Tech Stack

### 🖥️ Frontend
- **HTML5**, **CSS3**, **Vanilla JavaScript**
- **Fetch API** for REST communication  
- **Responsive design** using **CSS Grid** & **Flexbox**
- **LocalStorage** for JWT token management

### ⚙️ Backend
- **FastAPI** (Python)
- **SQLite** with **SQLAlchemy ORM**
- **JWT Authentication** using `python-jose`
- **Argon2 / SHA256 password hashing** via `passlib`
- **Jinja2 templates** for frontend rendering
- **Static file handling** with FastAPI `StaticFiles`

### 🧱 Database Models
| Entity | Description |
|--------|--------------|
| `User` | Authentication & roles (admin / user) |
| `Product` | Product catalogue |
| `Category` | Product categories |
| `CartItem` | User’s cart items |
| `Order` | Order details |
| `OrderItem` | Items within each order |
| `Newsletter` | Newsletter subscribers |
| `ContactMessage` | Contact form submissions |

---

## 🔒 Authentication & Authorization
- **JWT tokens** protect all authenticated routes.
- **Admin-only endpoints** for catalogue and order management.
- Passwords hashed using **Argon2** (fallback to SHA256).
- Token stored in browser `localStorage` and auto-invalidated on 401.

---

## 🧠 Key API Endpoints

### 🧍 User APIs
| Method | Endpoint | Description |
|--------|-----------|-------------|
| `POST` | `/api/register` | Register new user |
| `POST` | `/api/login` | User login & token generation |
| `GET`  | `/users/me` | Get current user details |
| `POST` | `/api/contact` | Submit contact message |
| `POST` | `/api/newsletter` | Subscribe to newsletter |

### 🛒 Cart APIs
| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/api/cart` | Get user cart |
| `POST` | `/api/cart` | Add to cart |
| `PUT` | `/api/cart/{id}` | Update quantity |
| `DELETE` | `/api/cart/{id}` | Remove item |

### 🕯️ Product APIs
| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/api/products` | Get all products |
| `GET` | `/api/products/featured` | Get featured products |
| `POST` | `/api/products` | Add new product (Admin) |
| `DELETE` | `/api/products/{id}` | Delete product (Admin) |

### 📦 Orders APIs
| Method | Endpoint | Description |
|--------|-----------|-------------|
| `POST` | `/api/orders` | Place new order |
| `GET`  | `/api/orders` | View user orders |
| `GET`  | `/api/admin/orders` | View all orders (Admin) |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
python -m venv venv
source venv/bin/activate  # for Linux/Mac
venv\Scripts\activate     # for Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

Server runs at → http://127.0.0.1:8000

## ☁️ Deployment
Deployed on AWS EC2 using Nginx reverse proxy with HTTPS (Certbot SSL)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d gaeinova-magic.shop
```

## 🧑‍💻 Developer
👤 Ankit Kumar
💻 Developer — Full Stack & API Engineer
📧 gaeinova.magic@gmail.com

🔗 GitHub: [https://github.com/ak0586](ak0586)

## ⭐ Acknowledgements
FastAPI: for the lightning-fast backend

SQLAlchemy: for ORM

Passlib: for secure password hashing

Jinja2: for template rendering


## 📜 License
Copyright (c) 2025 Gaeinova Magic. All Rights Reserved.

This source code and all associated files are proprietary and confidential. 
No part of this project may be reproduced, distributed, or transmitted in any form 
or by any means without prior written permission from the author.

For permissions, contact: gaeinova.magic@gmail.com

git clone https://github.com/ak0586/gaeinova-magic.git
cd gaeinova-magic
