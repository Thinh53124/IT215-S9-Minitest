from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI()

flights_db = [
    {"id": 1,"flight_number": "VN-213","destination": "Da Nang","available_seats": 45,"status": "scheduled"},
    {"id": 2,"flight_number": "VJ-122","destination": "Phu Quoc","available_seats": 12,"status": "scheduled"}
]

class NewFlight(BaseModel):
    flight_number: str = Field(..., min_length=5, max_length=10)
    destination: str = Field(..., min_length=1)
    available_seats: int = Field(..., ge=1)

@app.get("/flights")
async def get_flights(request: Request, status: str | None = None):
    if status:
        data = [flight for flight in flights_db if flight["status"] == status]
        if not data:
            raise HTTPException(
                status_code=404,
                detail={
                    "statusCode": 404,
                    "message": f"Không tìm thấy chuyến bay có status: {status}!",
                    "data": None,
                    "error": "ERR-AIR-03: Flight status not found.",
                    "path": request.url.path
                }
            )
        message = f"Lấy danh sách chuyến bay có status: {status} thành công!"
    else:
        data = flights_db
        message = "Lấy danh sách chuyến bay thành công!"

    return {
        "statusCode": 200,
        "message": message,
        "data": data,
        "error": None,
        "path": request.url.path
    }

@app.post("/flights", status_code=201)
async def create_flight(new_flight: NewFlight, request: Request):
    for flight in flights_db:
        if flight["flight_number"] == new_flight.flight_number:
            raise HTTPException(
                status_code=400,
                detail={
                    "statusCode": 400,
                    "message": "Lỗi: Số hiệu chuyến bay này đã tồn tại trên hệ thống điều hành!",
                    "data": None,
                    "error": "ERR-AIR-01: Flight number conflict in current active schedule database.",
                    "path": request.url.path
                }
            )

    flight = new_flight.model_dump()
    flight["id"] = len(flights_db) + 1
    flight["status"] = "scheduled"
    flight["created_at"] = datetime.now().isoformat()

    flights_db.append(flight)
    return {
        "statusCode": 201,
        "message": "Khởi tạo chuyến bay mới thành công!",
        "data": flight,
        "error": None,
        "path": request.url.path
    }

@app.delete("/flights/{flight_id}")
async def delete_flight(flight_id: int, request: Request):

    for flight in flights_db:
        if flight["id"] == flight_id:
            flights_db.remove(flight)
            return {
                "statusCode": 200,
                "message": "Hủy chuyến bay thành công!",
                "data": None,
                "error": None,
                "path": request.url.path
            }
    raise HTTPException(
        status_code=404,
        detail={
            "statusCode": 404,
            "message": "Lỗi: Không tìm thấy mã chuyến bay yêu cầu để hủy!",
            "data": None,
            "error": "ERR-AIR-02: Target flight ID is missing from system scope.",
            "path": request.url.path
        }
    )
