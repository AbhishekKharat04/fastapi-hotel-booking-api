from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field

app = FastAPI()

# ---------------- DATA ----------------

rooms = [
    {"id": 1, "room_number": "101", "type": "Deluxe", "price_per_night": 3000, "floor": 1, "is_available": True},
    {"id": 2, "room_number": "102", "type": "Single", "price_per_night": 1500, "floor": 1, "is_available": True},
    {"id": 3, "room_number": "201", "type": "Double", "price_per_night": 2500, "floor": 2, "is_available": False},
    {"id": 4, "room_number": "202", "type": "Suite", "price_per_night": 5000, "floor": 2, "is_available": True},
    {"id": 5, "room_number": "301", "type": "Deluxe", "price_per_night": 3200, "floor": 3, "is_available": True},
    {"id": 6, "room_number": "302", "type": "Single", "price_per_night": 1800, "floor": 3, "is_available": True},
]

bookings = []
booking_counter = 1

# ---------------- MODELS ----------------

class BookingRequest(BaseModel):
    guest_name: str = Field(..., min_length=2)
    room_id: int = Field(..., gt=0)
    nights: int = Field(..., gt=0, le=30)
    phone: str = Field(..., min_length=10)
    meal_plan: str = "none"
    early_checkout: bool = False


class NewRoom(BaseModel):
    room_number: str = Field(..., min_length=1)
    type: str = Field(..., min_length=2)
    price_per_night: int = Field(..., gt=0)
    floor: int = Field(..., gt=0)
    is_available: bool = True


# ---------------- HELPERS ----------------

def find_room(room_id):
    for room in rooms:
        if room["id"] == room_id:
            return room
    return None


def calculate_cost(price, nights, meal_plan, early_checkout=False):
    extra = 0

    if meal_plan == "breakfast":
        extra = 500
    elif meal_plan == "all-inclusive":
        extra = 1200

    total = (price + extra) * nights

    if early_checkout:
        discount = total * 0.1
        total -= discount
        return total, discount

    return total, 0


def filter_rooms_logic(type=None, max_price=None, floor=None, is_available=None):
    result = rooms

    if type is not None:
        result = [r for r in result if r["type"].lower() == type.lower()]

    if max_price is not None:
        result = [r for r in result if r["price_per_night"] <= max_price]

    if floor is not None:
        result = [r for r in result if r["floor"] == floor]

    if is_available is not None:
        result = [r for r in result if r["is_available"] == is_available]

    return result


# ---------------- ROUTES ----------------

@app.get("/")
def home():
    return {"message": "Welcome to Grand Stay Hotel"}


@app.get("/rooms")
def get_rooms():
    return {"total": len(rooms), "rooms": rooms}


@app.post("/rooms")
def add_room(room: NewRoom, response: Response):
    for r in rooms:
        if r["room_number"] == room.room_number:
            raise HTTPException(status_code=400, detail="Room already exists")

    new_room = {
        "id": len(rooms) + 1,
        "room_number": room.room_number,
        "type": room.type,
        "price_per_night": room.price_per_night,
        "floor": room.floor,
        "is_available": room.is_available
    }

    rooms.append(new_room)
    response.status_code = 201

    return {"message": "Room added", "room": new_room}


@app.get("/rooms/summary")
def room_summary():
    total = len(rooms)
    available = sum(1 for r in rooms if r["is_available"])
    occupied = total - available
    prices = [r["price_per_night"] for r in rooms]

    return {
        "total_rooms": total,
        "available": available,
        "occupied": occupied,
        "min_price": min(prices),
        "max_price": max(prices)
    }


# 🔥 IMPORTANT: ALL FIXED ROUTES BEFORE /rooms/{room_id}

@app.get("/rooms/filter")
def filter_rooms(
    type: str = Query(None),
    max_price: int = Query(None),
    floor: int = Query(None),
    is_available: bool = Query(None)
):
    filtered = filter_rooms_logic(type, max_price, floor, is_available)
    return {"total": len(filtered), "rooms": filtered}


@app.get("/rooms/search")
def search_rooms(keyword: str):
    result = [
        r for r in rooms
        if keyword.lower() in r["type"].lower() or keyword in r["room_number"]
    ]

    if not result:
        return {"message": "No rooms found"}

    return {"total_found": len(result), "rooms": result}


@app.get("/rooms/sort")
def sort_rooms(sort_by: str = "price_per_night", order: str = "asc"):
    reverse = order == "desc"
    sorted_rooms = sorted(rooms, key=lambda x: x[sort_by], reverse=reverse)

    return {"sorted_by": sort_by, "order": order, "rooms": sorted_rooms}


@app.get("/rooms/page")
def paginate_rooms(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit

    total = len(rooms)
    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "rooms": rooms[start:end]
    }


@app.get("/rooms/browse")
def browse_rooms(
    keyword: str = None,
    sort_by: str = "price_per_night",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = rooms

    if keyword:
        result = [
            r for r in result
            if keyword.lower() in r["type"].lower()
            or keyword in r["room_number"]
        ]

    reverse = order == "desc"
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    total = len(result)
    start = (page - 1) * limit
    end = start + limit

    total_pages = (total + limit - 1) // limit

    return {
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "rooms": result[start:end]
    }


# 🔴 KEEP THIS LAST
@app.get("/rooms/{room_id}")
def get_room(room_id: int):
    room = find_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@app.put("/rooms/{room_id}")
def update_room(
    room_id: int,
    price_per_night: int = None,
    is_available: bool = None
):
    room = find_room(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if price_per_night is not None:
        room["price_per_night"] = price_per_night

    if is_available is not None:
        room["is_available"] = is_available

    return {"message": "Room updated", "room": room}

@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    room = find_room(room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not room["is_available"]:
        raise HTTPException(status_code=400, detail="Cannot delete occupied room")

    rooms.remove(room)

    return {"message": "Room deleted"}


# ---------------- BOOKINGS ----------------

@app.get("/bookings")
def get_bookings():
    return {"total": len(bookings), "bookings": bookings}


@app.post("/bookings")
def create_booking(request: BookingRequest):
    global booking_counter

    room = find_room(request.room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if not room["is_available"]:
        raise HTTPException(status_code=400, detail="Room not available")

    total_cost, discount = calculate_cost(
        room["price_per_night"],
        request.nights,
        request.meal_plan,
        request.early_checkout
    )

    booking = {
        "booking_id": booking_counter,
        "guest_name": request.guest_name,
        "room_id": request.room_id,
        "nights": request.nights,
        "total_cost": total_cost,
        "discount": discount,
        "status": "confirmed"
    }

    bookings.append(booking)
    booking_counter += 1
    room["is_available"] = False

    return {"message": "Booking confirmed", "booking": booking}


@app.post("/checkin/{booking_id}")
def check_in(booking_id: int):
    for booking in bookings:
        if booking["booking_id"] == booking_id:
            booking["status"] = "checked_in"
            return {"message": "Checked in", "booking": booking}

    raise HTTPException(status_code=404, detail="Booking not found")


@app.post("/checkout/{booking_id}")
def check_out(booking_id: int):
    for booking in bookings:
        if booking["booking_id"] == booking_id:
            booking["status"] = "checked_out"

            room = find_room(booking["room_id"])
            if room:
                room["is_available"] = True

            return {"message": "Checked out", "booking": booking}

    raise HTTPException(status_code=404, detail="Booking not found")


@app.get("/bookings/active")
def active_bookings():
    active = [b for b in bookings if b["status"] in ["confirmed", "checked_in"]]
    return {"total": len(active), "bookings": active}


@app.get("/bookings/search")
def search_bookings(guest_name: str):
    result = [b for b in bookings if guest_name.lower() in b["guest_name"].lower()]
    return {"total": len(result), "bookings": result}


@app.get("/bookings/sort")
def sort_bookings(order: str = "asc"):
    reverse = order == "desc"
    sorted_data = sorted(bookings, key=lambda x: x["total_cost"], reverse=reverse)
    return {"order": order, "bookings": sorted_data}