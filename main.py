from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
# from model import train, convert, predict
import databases, sqlalchemy, datetime, uuid
from typing import List

## Postgres Database
DATABASE_URL = "postgres://podbrtrvupzwrs:3ae577a84fe32e348dd104312d8d6cd7a60b90e063c3803cad90c8b341278892@ec2-34-233-0-64.compute-1.amazonaws.com:5432/d8mf2fka342hhv"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

energies = sqlalchemy.Table(
    "energies",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("created_at", sqlalchemy.String),
    sqlalchemy.Column("energy", sqlalchemy.Float),
    sqlalchemy.Column("power", sqlalchemy.Float),
    sqlalchemy.Column("voltage", sqlalchemy.Float),
    sqlalchemy.Column("current", sqlalchemy.Float)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)


app = FastAPI()

# pydantic models

class StockIn(BaseModel):
    ticker: str


class StockOut(StockIn):
    forecast: dict

class Energies(BaseModel):
    id          :str
    created_at  :str
    energy      :float
    power       :float
    voltage     :float
    current     :float

class EnergyEntry(BaseModel):
    energy  :float = Field(..., example=0.001)
    power   :float = Field(..., example=30.0)
    voltage :float = Field(..., example=220.25)
    current :float = Field(..., example=0.05)


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# routes

@app.get("/energies", response_model=List[Energies])
async def fetch_energies():
    query = energies.select()
    return await database.fetch_all(query)

@app.post("/energies", response_model=Energies, status_code=201)
async def create_energy(entry: EnergyEntry):
    print(entry.body)
    gID     = str(uuid.uuid1())
    gDate   = str(datetime.datetime.now())
    query   = energies.insert().values(
        id          = gID,
        created_at  = gDate,
        energy      = entry.energy,
        power       = entry.power,
        voltage     = entry.voltage,
        current     = entry.current
    )
    await database.execute(query)
    return {
        "id": gID,
        **entry.dict(),
        "created_at": gDate
    }

@app.get("/ping")
async def pong():
    return {"ping": "pong!"}

@app.post("/energy", status_code=201)
async def energy():
    return {"succes"}


# @app.post("/predict", response_model=StockOut, status_code=200)
# def get_prediction(payload: StockIn):
#     train("FB")
#     train("AAPL")
#     train("GOOGL")
#     train("MSFT")

#     ticker = payload.ticker

#     prediction_list = predict(ticker)

#     if not prediction_list:
#         raise HTTPException(status_code=400, detail="Model not found.")

#     response_object = {"ticker": ticker, "forecast": convert(prediction_list)}
#     return response_object

if __name__ == "__main__":
    app.run()