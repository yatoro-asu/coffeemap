import json
import requests
import folium
from geopy.distance import geodesic

def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None
    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)

def main():
    with open('coffee.json', 'r', encoding='cp1251') as file:
        coffee_data = json.load(file)

    YANDEX_API_KEY = 'a120c6e8-06ed-4596-8199-21432674f9da'
    user_address = input("Введите ваш адрес: ")
    user_coords = fetch_coordinates(YANDEX_API_KEY, user_address)

    if not user_coords:
        print("Адрес не найден.")
        return

    coffee_shops = []
    for cafe in coffee_data:
        name = cafe['Name']
        cafe_coords = cafe['geoData']['coordinates']
        cafe_lat, cafe_lon = cafe_coords[1], cafe_coords[0]
        distance = geodesic(user_coords, (cafe_lat, cafe_lon)).km
        coffee_shops.append({
            'name': name,
            'coordinates': (cafe_lat, cafe_lon),
            'distance': distance
        })

    sorted_coffee = sorted(coffee_shops, key=lambda x: x['distance'])[:5]

    m = folium.Map(location=user_coords, zoom_start=15)

    folium.Marker(
        location=user_coords,
        popup="Ваше местоположение",
        icon=folium.Icon(color="red")
    ).add_to(m)

    for cafe in sorted_coffee:
        folium.Marker(
            location=cafe['coordinates'],
            popup=f"{cafe['name']}<br>{cafe['distance']:.2f} км",
            icon=folium.Icon(color="green", icon="coffee")
        ).add_to(m)

    m.save('index.html')

if __name__ == "__main__":
    main()