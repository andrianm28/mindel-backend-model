from fastapi import (
    FastAPI, 
    BackgroundTasks, 
    UploadFile, File, 
    Form, 
    Query,
    Body,
    Depends,
    HTTPException
)
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.sql.elements import True_
from model import train, convert, predict
import databases, datetime, uuid, sqlalchemy
from sqlalchemy import desc
from typing import List
import pytz, json, re

from starlette.responses import JSONResponse
from starlette.requests import Request
# from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
# from fastapi_mail.email_utils import DefaultChecker

import telegram_send

import pandas as pd

from fastapi.encoders import jsonable_encoder

# Timezone

tz = pytz.timezone('Asia/Jakarta')

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
    sqlalchemy.Column("current", sqlalchemy.Float),
    sqlalchemy.Column("frequency", sqlalchemy.Float),
    sqlalchemy.Column("power_factor", sqlalchemy.Float)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

app = FastAPI()



# pydantic models

class EmailSchema(BaseModel):
    email: List[EmailStr]


# conf = ConnectionConfig(
#     MAIL_USERNAME = "andrianm28",
#     MAIL_PASSWORD = "lolipoplolipop",
#     MAIL_FROM = "electrification.io@gmail.com",
#     MAIL_PORT = 587,
#     MAIL_SERVER = "smtp.gmail.com",
#     MAIL_FROM_NAME="Electricist",
#     MAIL_TLS = True,
#     MAIL_SSL = False
# )

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
    frequency   :float
    power_factor:float

class EnergyEntry(BaseModel):
    energy  :float = Field(..., example=0.001)
    power   :float = Field(..., example=30.0)
    voltage :float = Field(..., example=220.25)
    current :float = Field(..., example=0.05)
    frequency :float = Field(..., example=50)
    power_factor :float = Field(..., example=0.9)


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# routes

# @app.post("/emailbackground")
# async def send_in_background(
#     background_tasks: BackgroundTasks,
#     email: EmailSchema
#     ) -> JSONResponse:

#     power = 20.2

#     telegram_send.send(messages=["Wow that was easy! {} ".format(power)])

#     return JSONResponse(status_code=200, content={"message": "email has been sent"})

@app.get("/hourly_energies", response_model=List[Energies])
async def fetch_energies():
    query = energies.select().order_by(energies.c.created_at.desc())
    lists = await database.fetch_all(query)
    # lists_json = jsonable_encoder(lists)
    # print(lists_json)
    return lists

lists_dict = {}
@app.get("/daily_energies", response_model=List[Energies])
async def fetch_energies():
    query = energies.select().order_by(energies.c.created_at.desc())
    lists = await database.fetch_all(query)
    lists_json = jsonable_encoder(lists)
    lists_dict[energies] = lists_json
    r = re.compile('.* 23:.*')
    daily = [d for d in lists_dict[energies] if re.match(r,d['created_at'])]
    # daily_energy = []
    # for i in daily:
    #     substract = i['energy'] - i-1['energy']
    #     daily_energy.append({'id': i['id'], 'created_at': i['created_at'], 'energy': substract})
    # print(daily_energy)
    print(len(daily))
    return daily

@app.get("/monthly_energies")
async def fetch_monthly_energies():
    monthly_e = [
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Aug",
            "month_full": "August",
            "monthly_power": 528.0,
            "monthly_budget": 700000.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Jul",
            "month_full": "July",
            "monthly_power": 500.0,
            "monthly_budget": 500000.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Jun",
            "month_full": "June",
            "monthly_power": 548.0,
            "monthly_budget": 700000.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "May",
            "month_full": "May",
            "monthly_power": 436.0,
            "monthly_budget": 500000.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Apr",
            "month_full": "April",
            "monthly_power": 429.0,
            "monthly_budget": 500000.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Mar",
            "month_full": "March",
            "monthly_power": 361.0,
            "monthly_budget": 350000.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Feb",
            "month_full": "February",
            "monthly_power": 0.0,
            "monthly_budget": 0.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Jan",
            "month_full": "January",
            "monthly_power": 0.0,
            "monthly_budget": 0.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Dec",
            "month_full": "December",
            "monthly_power": 0.0,
            "monthly_budget": 0.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Nov",
            "month_full": "November",
            "monthly_power": 0.0,
            "monthly_budget": 0.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Oct",
            "month_full": "October",
            "monthly_power": 0.0,
            "monthly_budget": 0.0
        },
        {
            "id": "2ebeb9e2-9d7d-11eb-a902-acde48001122",
            "month_simple": "Sep",
            "month_full": "September",
            "monthly_power": 0.0,
            "monthly_budget": 0.0
        }
    ]
    return monthly_e

# @app.get("/current-energy", response_model= Energies)
# async def fetch_current_energy():
#     query = energies.select()
#     lists = await database.fetch_all(query)
#     lists_json = jsonable_encoder(lists)
#     print(lists_json[len(lists_json)-1])
#     return lists_json[len(lists_json)-1] 

@app.post("/energies", response_model=Energies, status_code=201)
async def create_energy(entry: EnergyEntry):

    gID     = str(uuid.uuid1())
    gDate   = str(datetime.datetime.now(tz=tz))
    query   = energies.insert().values(
        id          = gID,
        created_at  = gDate,
        energy      = entry.energy,
        power       = entry.power,
        voltage     = entry.voltage,
        current     = entry.current,
        frequency   = entry.frequency,
        power_factor= entry.power_factor
    )
    await database.execute(query)
    return {
        "id": gID,
        "created_at": gDate,
        **entry.dict()
    }

@app.get("/ping")
async def pong():
    return {"ping": "pong!"}


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