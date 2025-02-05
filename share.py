

current_latitude = None
current_longitude = None

def set_current_location(latitude, longitude):
    global current_latitude, current_longitude
    current_latitude, current_longitude = latitude, longitude

def get_current_location():
    return current_latitude, current_longitude