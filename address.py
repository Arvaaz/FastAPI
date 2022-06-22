from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import requests
from geopy.distance import geodesic as GD

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# DB_CONNECTION
def get_db():
    try:
        db =SessionLocal()
        yield db
    finally:
        db.close()

class Address_Book(BaseModel):
    address:str = Field(min_lehgth=1,max_length=200)


ADDRESS = []

# GET REQUEST
@app.get("/")
def read_api(db: Session = Depends(get_db)):
    return db.query(models.Address).all()

# POST REQUEST
@app.post("/")
def create_address(address:Address_Book, db:Session = Depends(get_db)):

    address_model = models.Address()
    address_model.address = address.address
    key='CU1TpCILyOuQGkttEvco0H9rHOKltqkI'
    url='http://www.mapquestapi.com/geocoding/v1/address?key='
    loc=address_model.address
    main_url=url + key + '&location=' + loc
    data=requests.get(main_url).json()
    data=data['results'][0]
    location=data['locations'][0]
    lat=location['latLng']['lat']
    lon=location['latLng']['lng']
    address_model.coordinates=str(lat)+","+str(lon)
    db.add(address_model)

    db.commit()

    return address

# GET REQUEST TO GET NEAREST ADDRESS
@app.get('/nearestAddress')
def getNearestAddress(Adress, db: Session = Depends(get_db)):
    loc=Adress
    key='CU1TpCILyOuQGkttEvco0H9rHOKltqkI'
    url='http://www.mapquestapi.com/geocoding/v1/address?key='
    main_url=url + key + '&location=' + loc
    data=requests.get(main_url).json()
    data=data['results'][0]
    location=data['locations'][0]
    origin=(location['latLng']['lat'],location['latLng']['lng'])

    allAddress=db.query(models.Address).all()
    nearestAddress=[]
    for i in allAddress:
        dist=(i.coordinates)
        Dbtw=GD(origin,dist).km
        if Dbtw <=50:
            nearestAddress.append(i)

    return nearestAddress

# PUT REQUEST
@app.put("/{address_id}")
def update_address(address_id:int, address:Address_Book, db: Session = Depends(get_db)):
    address_model = db.query(models.Address).filter(models.Address.id == address_id).first()

    if address_model is None:
        raise HTTPException(
            status_code = 404,
            detail = f"ID {address_id} : Not exist"
        )

    address_model.address = address.address
    address_model.coordinates = address.coordinates

    db.add(address_model)
    db.commit()

    return address 

# DELETE REQUEST
@app.delete("/{address_id}")
def delete_address(address_id:int, db: Session = Depends(get_db)):
    
    address_model = db.query(models.Address).filter(models.Address.id == address_id).first()

    if address_model is None:
        raise HTTPException(
            status_code=404,
            detail = f"ID {address_id} : Not exist"
        )
    
    db.query(models.Address).filter(models.Address.id == address_id).delete()
    db.commit()