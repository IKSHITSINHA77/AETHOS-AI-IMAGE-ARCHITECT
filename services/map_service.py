from geopy.geocoders import Nominatim
from geopy.distance import geodesic

geolocator = Nominatim(user_agent="vision_app")

def get_coordinates(place):

    location = geolocator.geocode(place)

    if location:
        return (location.latitude, location.longitude)

    return None


def get_distance(user_location, place):

    place_location = get_coordinates(place)

    if place_location:

        distance = geodesic(user_location, place_location).km

        return round(distance,2)

    return None