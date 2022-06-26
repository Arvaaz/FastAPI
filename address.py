from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel, Field
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import requests
from geopy.distance import geodesic as GD
import logging

app = FastAPI()

# Create and configure logger
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
# Creating an object
logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)



# DB_CONNECTION
models.Base.metadata.create_all(bind=engine)
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
# We are getting all the Addresses from DB.
@app.get("/")
def read_api(db: Session = Depends(get_db)):
    logger.info('displayed address successfully ')
    return db.query(models.Address).all()

# POST REQUEST
@app.post("/")
def create_address(address:Address_Book, db:Session = Depends(get_db)):

    address_model = models.Address()
    address_model.address = address.address

    # converting Address in to coordinates here
    key='CU1TpCILyOuQGkttEvco0H9rHOKltqkI'
    url='http://www.mapquestapi.com/geocoding/v1/address?key='
    loc=address_model.address
    main_url=url + key + '&location=' + loc
    data=requests.get(main_url).json()
    data=data['results'][0]
    location=data['locations'][0]
    lat=location['latLng']['lat']
    lon=location['latLng']['lng']
    map_url=location['mapUrl']

    # Getting let long here with the help of geopy
    address_model.coordinates=str(lat)+","+str(lon)
    address_model.map_url=map_url
    db.add(address_model)

    db.commit()
    logger.info('Address Created successfully')
    return address

# GET REQUEST TO GET NEAREST ADDRESS
@app.get('/nearestAddress')
def getNearestAddress(Adress, db: Session = Depends(get_db)):
    # We are creating a new address here from getting the nearest addresses
    loc=Adress
    key='CU1TpCILyOuQGkttEvco0H9rHOKltqkI'
    url='http://www.mapquestapi.com/geocoding/v1/address?key='
    main_url=url + key + '&location=' + loc
    data=requests.get(main_url).json()
    data=data['results'][0]
    location=data['locations'][0]

    # calculating the lat long of the new address here to find out the distance
    origin=(location['latLng']['lat'],location['latLng']['lng'])

    allAddress=db.query(models.Address).all()
    nearestAddress=[]
    # we are getting all the nearest addresses in an array here
    for i in allAddress:
        dist=(i.coordinates)
        Dbtw=GD(origin,dist).km
        if Dbtw <=50:
            nearestAddress.append(i)
    logger.info('addresses displayed successfully')
    # here we are returning the nearest addresses
    return nearestAddress

# PUT REQUEST
@app.put("/{address_id}")
def update_address(address_id:int, address:Address_Book, db: Session = Depends(get_db)):
    address_model = db.query(models.Address).filter(models.Address.id == address_id).first()

    if address_model is None:
        logger.error('Id does not exist')
        raise HTTPException(
            status_code = 404,
            detail = f"ID {address_id} : Not exist"
        )
    # we are updating our address and coordinates also
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
    map_url=location['mapUrl']
    address_model.coordinates=str(lat)+","+str(lon)
    address_model.map_url=map_url

    db.add(address_model)
    db.commit()
    logger.info('address updated successfully')
    return address 

# DELETE REQUEST
@app.delete("/{address_id}")
def delete_address(address_id:int, db: Session = Depends(get_db)):
    
    # deleting the address with the help of the id of that perticulor address
    address_model = db.query(models.Address).filter(models.Address.id == address_id).first()

    if address_model is None:
        logger.error("ID does not exist")
        raise HTTPException(
            status_code=404,
            detail = f"ID {address_id} : Not exist"
        )
    
    db.query(models.Address).filter(models.Address.id == address_id).delete()
    logger.info('Deleted successfully')
    db.commit()
