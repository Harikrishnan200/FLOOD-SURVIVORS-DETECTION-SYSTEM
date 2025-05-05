import json
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Location
from .utils import haversine_distance
from ADMIN_APP.views import unique_person_ids
from AUTHENTICATION_APP.models import UserToken
from share import set_current_location
from django.utils import timezone



unique_person_lock = threading.Lock()

first_save_done = False

@csrf_exempt
def receive_gps_data(request):
    global first_save_done

    if request.method == "POST":
        try:
           
            data = json.loads(request.body)
            email = data.get('email')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            token = data.get('token')  


            print("-----------------------------------------------------------------------------------------------------------------------")

      
            if not all([email, latitude, longitude, token]):
                return JsonResponse({"error": "Missing required fields (email, latitude, longitude, token)"}, status=400)
            

            user_token = UserToken.objects.get(user__email=email, token=token)
            if user_token:
                set_current_location(latitude, longitude)


                if not first_save_done:
                    Location.objects.create(email=email, latitude=latitude, longitude=longitude, detected_count=len(unique_person_ids), is_first_location=True)
                    first_save_done = True
                    print(f"First GPS data received and saved: {data}")

                    with unique_person_lock:
                        print(f"Number of unique persons detected: {len(unique_person_ids)}")
                        unique_person_ids.clear()

                    return JsonResponse({"message": "First location saved after server reload"})

                
                try:
                    location = Location.objects.filter(email=email).order_by('-timestamp').first()
                    distance = haversine_distance(location.latitude, location.longitude, latitude, longitude)

                    # If the distance is greater than 25 meters, save the new location
                    if distance > 0 and len(unique_person_ids) > 0:
                        Location.objects.create(email=email, latitude=latitude, longitude=longitude, detected_count=len(unique_person_ids), is_first_location=False, is_detected=True)
                        print(f"New location saved for {email} with distance: {distance}")

                        with unique_person_lock:
                            print(f"Number of unique persons detected: {len(unique_person_ids)}")
                            unique_person_ids.clear()

                        return JsonResponse({"message": "New location saved", "distance": distance})
                    else:
                        print(f"Location not saved (distance < 25m) for {email}: {data} with distance: {distance}")
                        return JsonResponse({"message": "Location not saved as distance is less than 25m", "distance": distance})

                except Location.DoesNotExist:
    
                    Location.objects.create(email=email, latitude=latitude, longitude=longitude, detected_count=len(unique_person_ids), is_first_location=True)
                    print(f"First location saved for user {email}: {data}")

                    with unique_person_lock:
                        print(f"Number of unique persons detected: {len(unique_person_ids)}")
                        unique_person_ids.clear()

                    return JsonResponse({"message": "First location saved for user"})

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing data: {e}")
            return JsonResponse({"error": "Invalid input data"}, status=400)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)



def print_user(request):
    try:
        token = '6d69abcf3e094c41aedf5ca963da4411'
        user_token = UserToken.objects.get(token=token)
        current_user_email = user_token.user.email
        print(current_user_email)
        return JsonResponse({"message": "User printed in console"})
    except UserToken.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=404)
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({"error": "An error occurred"}, status=500)

def update_current_location(request, latitude, longitude, mark=False):
    pass


@login_required(login_url='login')
def get_location_data(request):

    print("inside the get_location_data .....")
    today = timezone.now().date()
    latest_location_true = Location.objects.filter(is_first_location=True, timestamp__date__gte=today).order_by('-timestamp').first()

    location_false_data_list = []

    if latest_location_true:
        location_false_data_list = Location.objects.filter(is_first_location=False, timestamp__gt=latest_location_true.timestamp).values(
            'id','email', 'latitude', 'longitude', 'detected_count', 'is_first_location', 'timestamp', 'status', 'is_detected', 'is_send'
        )

    return JsonResponse({"location_data": list(location_false_data_list)[::-1]})


# def get_location_data(request):

#     print("inside the get_location_data .....")
#     today = timezone.now().date()
#     latest_location_true = Location.objects.filter(is_first_location=True, timestamp__date__gte=today).order_by('-timestamp').first()

#     location_false_data_list = []

#     if latest_location_true:

#         location_false_data_list = Location.objects.filter(is_first_location=False, timestamp__gt=latest_location_true.timestamp).values(
#             'id','email', 'latitude', 'longitude', 'detected_count', 'is_first_location', 'timestamp', 'status'
#         )
#     return JsonResponse({"location_data": list(location_false_data_list)})


# import json
# import multiprocessing as mp
# import django
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from .models import Location
# from .utils import haversine_distance
# from ADMIN_APP.views import unique_person_ids
# from AUTHENTICATION_APP.models import UserToken
# from share import set_current_location

# # Lock for process safety when accessing unique_person_ids
# unique_person_lock = mp.Lock()

# first_save_done = mp.Value('b', False)

# # Queue for handling location data
# location_queue = mp.Queue()

# def handle_location_data(location_queue, unique_person_lock, unique_person_ids, first_save_done):
#     # Ensure Django is set up in the child process
#     django.setup()

#     while True:
#         try:
#             data = location_queue.get(timeout=1)  # Timeout to periodically check for termination
#         except mp.queues.Empty:
#             continue

#         email = data.get('email')
#         latitude = data.get('latitude')
#         longitude = data.get('longitude')
#         token = data.get('token')

#         try:
#             user_token = UserToken.objects.get(user__email=email, token=token)
#         except UserToken.DoesNotExist:
#             print(f"Invalid token for user {email}")
#             continue

#         set_current_location(latitude, longitude)
#         print(f"Set current location to latitude: {latitude}, longitude: {longitude}")

#         if not first_save_done.value:
#             Location.objects.create(email=email, latitude=latitude, longitude=longitude)
#             first_save_done.value = True
#             print(f"First GPS data received and saved for email: {email}")

#             with unique_person_lock:
#                 print(f"Number of unique persons detected: {len(unique_person_ids)}")
#                 unique_person_ids[:] = []  # Clear the list

#             continue

#         # Handle subsequent location updates
#         try:
#             location = Location.objects.filter(email=email).order_by('-timestamp').first()
#             distance = haversine_distance(location.latitude, location.longitude, latitude, longitude)

#             # If the distance is greater than 25 meters, save the new location
#             if distance > 10:
#                 Location.objects.create(email=email, latitude=latitude, longitude=longitude)
#                 print(f"New location saved for {email} with distance: {distance}")

#                 with unique_person_lock:
#                     print(f"Number of unique persons detected: {len(unique_person_ids)}")
#                     unique_person_ids[:] = []  # Clear the list

#             else:
#                 print(f"Location not saved (distance < 25m) for {email}: {data} with distance: {distance}")

#         except Location.DoesNotExist:
#             Location.objects.create(email=email, latitude=latitude, longitude=longitude)
#             print(f"First location saved for user {email}: {data}")

#             with unique_person_lock:
#                 print(f"Number of unique persons detected: {len(unique_person_ids)}")
#                 unique_person_ids[:] = []  # Clear the list

# # Start the location data handler process
# location_process = mp.Process(target=handle_location_data, args=(location_queue, unique_person_lock, unique_person_ids, first_save_done), daemon=True)
# location_process.start()

# @csrf_exempt
# def receive_gps_data(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             latitude = data.get('latitude')
#             longitude = data.get('longitude')
#             token = data.get('token')

#             print(data)
#             print("-----------------------------------------------------------------------------------------------------------------------")

#             if not all([email, latitude, longitude, token]):
#                 return JsonResponse({"error": "Missing required fields (email, latitude, longitude, token)"}, status=400)

#             # Add the location data to the queue
#             location_queue.put(data)
#             print(f"Location data received for email: {email}")
#             return JsonResponse({"message": "Location data received"})

#         except (json.JSONDecodeError, ValueError) as e:
#             print(f"Error processing data: {e}")
#             return JsonResponse({"error": "Invalid input data"}, status=400)

#     else:
#         return JsonResponse({"error": "Invalid request method"}, status=405)

# def print_user(request):
#     try:
#         token = '6d69abcf3e094c41aedf5ca963da4411'
#         user_token = UserToken.objects.get(token=token)
#         current_user_email = user_token.user.email
#         print(current_user_email)
#         return JsonResponse({"message": "User printed in console"})
#     except UserToken.DoesNotExist:
#         return JsonResponse({"error": "Invalid token"}, status=404)
#     except Exception as e:
#         print(f"Error: {e}")
#         return JsonResponse({"error": "An error occurred"}, status=500)

# def update_current_location(request, latitude, longitude, mark=False):
#     pass