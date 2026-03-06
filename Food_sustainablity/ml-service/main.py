from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model import SurplusPredictor

app = FastAPI(title="WasteLess Grid - ML Service")

# Initialize the predictor (this will train initially if no model exists)
predictor = SurplusPredictor()

class PredictionRequest(BaseModel):
    day_of_week: int  # 0-6
    weather: int      # 0=Clear, 1=Rain, 2=Storm
    has_event: int    # 0 or 1
    recent_sales_ratio: float # 0.0 to 1.0
    total_meals_cooked: int

@app.get("/")
def read_root():
    return {"message": "WasteLess Grid Prediction API is running."}

@app.post("/predict_surplus")
def predict_surplus(req: PredictionRequest):
    try:
        result = predictor.predict(
            day_of_week=req.day_of_week,
            weather=req.weather,
            has_event=req.has_event,
            recent_sales_ratio=req.recent_sales_ratio,
            total_meals_cooked=req.total_meals_cooked
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
