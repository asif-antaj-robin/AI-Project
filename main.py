from fastapi import FastAPI, Query, HTTPException
from doctors_api import fetch_doctors_from_api
import uvicorn

app = FastAPI(title="NovaHealth - Doctor Search")

@app.get("/")
def read_root():
    return {"status": "DoctorsAPI.com Integration is Active"}

@app.get("/search")
async def search_doctors(
    city: str = Query(..., description="City name"),
    specialty: str = Query(..., description="Medical specialty")
):

    doctors = fetch_doctors_from_api(city, specialty)
    
    if not doctors:
        raise HTTPException(
            status_code=404, 
            detail="No doctors found. Please check your API Key or search criteria."
        )

    return {
        "search_info": {
            "city": city,
            "specialty": specialty,
            "provider": "DoctorsAPI.com"
        },
        "results": doctors
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




#uvicorn main:app --reload