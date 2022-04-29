from amadeus import Client, ResponseError

amadeus = Client(
    client_id='ZVCEHBaThOa3dgit8AkvVC4ATmLpcMAv',
    client_secret='wKv8R9a23vuhs2uG'
)

try:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='MAD',
        destinationLocationCode='ATH',
        departureDate='2022-11-01',
        returnDate='2022-12-01',
        adults=1)
    print(response.data)
except ResponseError as error:
    print(error)