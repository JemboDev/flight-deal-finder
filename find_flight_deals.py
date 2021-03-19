'''
This script uses Sheety API and Tequila API
to search for cheap flights to user's chosen destinations
'''
import datetime
import requests
import config


SHEETY_API_ENDPOINT = config.SHEETY_API_ENDPOINT
SHEETY_API_KEY = config.SHEETY_HEADER

TEQUILA_API_ENDPOINT = config.TEQUILA_API_ENDPOINT
TEQUILA_API_KEY = config.TEQUILA_HEADER
TEQUILA_LOCATIONS_ENDPOINT = f"{TEQUILA_API_ENDPOINT}/locations/query"
TEQUILA_SEARCH_ENDPOINT = ""


def get_sheet_data():
    '''
    Returns sheet data (city, iataCode, lowestPrice)
    '''
    sheety_response = requests.get(SHEETY_API_ENDPOINT, headers=SHEETY_API_KEY)
    sheety_response.raise_for_status()

    return sheety_response.json()["prices"]


def get_iata_code(city):
    '''
    Returns IATA Code for given city
    '''
    params = {
            "term": city
        }
    flight_response = requests.get(
        TEQUILA_LOCATIONS_ENDPOINT,
        params=params,
        headers=TEQUILA_API_KEY)
    flight_response.raise_for_status()

    return flight_response.json()["locations"][0]["code"]


def get_lowest_price(to_city):
    '''
    Returns the lowest flight price for given city
    '''
    date_from = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d/%m/%Y")
    date_to = (datetime.datetime.now() + datetime.timedelta(days=180)).strftime("%d/%m/%Y")
    search_endpoint = f"{TEQUILA_API_ENDPOINT}/v2/search"
    params = {
        "fly_from": "ALA",
        "fly_to": to_city,
        "date_from": date_from,
        "date_to": date_to,
        "nights_in_dst_from": 7,
        "nights_in_dst_to": 14,
        "flight_type": "round",
        "one_for_city": 1,
        "curr": "KZT",
        "max_stopovers": 0
    }
    response = requests.get(search_endpoint, params=params, headers=TEQUILA_API_KEY)
    response.raise_for_status()

    try:
        price = response.json()["data"][0]["price"]
    except IndexError:
        return "No direct flights available"
    else:
        return price


def update_sheet_info(cell_id, **columns):
    '''
    Updates the row of given ID w/ new IATA Code
    '''
    params = {"price": {}}
    for column, value in columns.items():
        params["price"][column] = value

    sheety_response = requests.put(
        f"{SHEETY_API_ENDPOINT}/{cell_id}",
        json=params,
        headers=SHEETY_API_KEY)
    sheety_response.raise_for_status()


sheet_data = get_sheet_data()

for row in sheet_data:
    if row.get("iataCode") is None:
        iata_code = get_iata_code(row.get("city"))
        update_sheet_info(row.get("id"), iataCode=iata_code)

    if row.get("lowestPrice") is None:
        lowest_price = get_lowest_price(row.get("iataCode"))
        update_sheet_info(row.get("id"), lowestPrice=lowest_price)

# DONE: get "prices" sheet info (think about lowest prices)
# DONE: get IATA codes for chosen cities
# DONE: get cheapest flight prices
    # 1: From ALA to destination city
    # 2: Direct flights (if no, then 1 stop, 2, 3 etc.)
    # 3: Between tomorrow and in 6 months time
    # 4: Round trips only
    # 5: Return time between 7 and 14 days
    # 6: Currency in KZT
# TODO: set some kind of notification if prices are really low
