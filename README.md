# 🏨 FastAPI Hotel Booking API

A RESTful API built with FastAPI to manage hotel room bookings, including real-time availability, filtering, sorting, and pagination.

---

## 🚀 Features

- Real-time room availability tracking
- Dynamic filtering, sorting, and pagination
- Booking lifecycle (create → check-in → check-out)
- Combined query API for optimized search

---

## 🚀 What Makes This Project Strong

- Designed RESTful APIs with clean route structure
- Implemented combined filtering + sorting + pagination in a single endpoint
- Handled state changes (room availability during booking lifecycle)
- Structured scalable backend logic without database dependency

---

## 🛠️ Tech Stack

- Python
- FastAPI
- Uvicorn

---
## 📂 Project Structure

```
fastapi-hotel-booking-api/
│
├── main.py
├── requirements.txt
├── screenshots/
│   ├── Q1_home.png
│   ├── Q2_rooms.png
│   ├── ...
│   ├── Q20_browse_rooms.png
│   └── final_api_overview.png
```


---

## ⚙️ How to Run

1. Install dependences:
pip install -r requirements.txt

2. Run server:
uvicorn main:app --reload

3. Open Swagger UI:
   http://127.0.0.1:8000/docs

---

## 📸 Screenshots

### 🔹 API Overview
![API Overview](screenshots/final_api_overview.png)

---

## 📌 Key APIs

- `GET /rooms` → Get all rooms  
- `POST /rooms` → Add room  
- `PUT /rooms/{room_id}` → Update room  
- `DELETE /rooms/{room_id}` → Delete room  

- `POST /bookings` → Create booking  
- `GET /bookings` → Get bookings  

- `POST /checkin/{booking_id}` → Check-in  
- `POST /checkout/{booking_id}` → Check-out  

- `GET /rooms/search` → Search rooms  
- `GET /rooms/sort` → Sort rooms  
- `GET /rooms/page` → Pagination  

- `GET /rooms/browse` → Combined API  

---


   
