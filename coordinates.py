from pygeocoder import Geocoder

address = Geocoder.geocode("1 Rugby Street, Newtown, Wellington 6021, New Zealand")
print(address.valid_address)

print(address.country)

print(address.coordinates)
# (-41.3068463, 174.7812157)