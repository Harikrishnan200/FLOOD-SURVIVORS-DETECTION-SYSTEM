# import json
# import threading
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from .models import Location
# from .utils import haversine_distance
# from ADMIN_APP.views import unique_person_ids
# from AUTHENTICATION_APP.models import UserToken
# from share import set_current_location

# # Lock for thread safety when accessing unique_person_ids
# unique_person_lock = threading.Lock()

# first_save_done = False

# @csrf_exempt
# def receive_gps_data(request):
#     global first_save_done

#     if request.method == "POST":
#         try:
           
#             data = json.loads(request.body)
#             email = data.get('email')
#             latitude = data.get('latitude')
#             longitude = data.get('longitude')
#             token = data.get('token')  

      
#             if not all([email, latitude, longitude, token]):
#                 return JsonResponse({"error": "Missing required fields (email, latitude, longitude, token)"}, status=400)

#             user_token = UserToken.objects.get(user__email=email, token=token)
#             if user_token:
#                 set_current_location(latitude, longitude)


#                 if not first_save_done:
#                     Location.objects.create(email=email, latitude=latitude, longitude=longitude)
#                     first_save_done = True
#                     print(f"First GPS data received and saved: {data}")

#                     with unique_person_lock:
#                         print(f"Number of unique persons detected: {len(unique_person_ids)}")
#                         unique_person_ids.clear()

#                     return JsonResponse({"message": "First location saved after server reload"})

#                 # Handle subsequent location updates
#                 try:
#                     location = Location.objects.filter(email=email).order_by('-timestamp').first()
#                     distance = haversine_distance(location.latitude, location.longitude, latitude, longitude)

#                     # If the distance is greater than 25 meters, save the new location
#                     if distance > 10:
#                         Location.objects.create(email=email, latitude=latitude, longitude=longitude)
#                         print(f"New location saved for {email} with distance: {distance}")

#                         with unique_person_lock:
#                             print(f"Number of unique persons detected: {len(unique_person_ids)}")
#                             unique_person_ids.clear()

#                         return JsonResponse({"message": "New location saved", "distance": distance})
#                     else:
#                         print(f"Location not saved (distance < 25m) for {email}: {data} with distance: {distance}")
#                         return JsonResponse({"message": "Location not saved as distance is less than 25m", "distance": distance})

#                 except Location.DoesNotExist:
    
#                     Location.objects.create(email=email, latitude=latitude, longitude=longitude)
#                     print(f"First location saved for user {email}: {data}")

#                     with unique_person_lock:
#                         print(f"Number of unique persons detected: {len(unique_person_ids)}")
#                         unique_person_ids.clear()

#                     return JsonResponse({"message": "First location saved for user"})

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
    
import json
import multiprocessing as mp
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Location
from .utils import haversine_distance
from ADMIN_APP.views import unique_person_ids
from AUTHENTICATION_APP.models import UserToken
from share import set_current_location

# Lock for process safety when accessing unique_person_ids
unique_person_lock = mp.Lock()

first_save_done = mp.Value('b', False)


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

            if not all([email, latitude, longitude, token]):
                return JsonResponse({"error": "Missing required fields (email, latitude, longitude, token)"}, status=400)

            user_token = UserToken.objects.get(user__email=email, token=token)
            if user_token:
                set_current_location(latitude, longitude)

                if not first_save_done.value:
                    Location.objects.create(email=email, latitude=latitude, longitude=longitude)
                    first_save_done.value = True
                    print(f"First GPS data received and saved: {data}")

                    with unique_person_lock:
                        print(f"Number of unique persons detected: {len(unique_person_ids)}")
                        unique_person_ids.clear()

                    return JsonResponse({"message": "First location saved after server reload"})

                # Handle subsequent location updates
                try:
                    location = Location.objects.filter(email=email).order_by('-timestamp').first()
                    distance = haversine_distance(location.latitude, location.longitude, latitude, longitude)

                    # If the distance is greater than 25 meters, save the new location
                    if distance > 10:
                        Location.objects.create(email=email, latitude=latitude, longitude=longitude)
                        print(f"New location saved for {email} with distance: {distance}")

                        with unique_person_lock:
                            print(f"Number of unique persons detected: {len(unique_person_ids)}")
                            unique_person_ids.clear()

                        return JsonResponse({"message": "New location saved", "distance": distance})
                    else:
                        print(f"Location not saved (distance < 25m) for {email}: {data} with distance: {distance}")
                        return JsonResponse({"message": "Location not saved as distance is less than 25m", "distance": distance})

                except Location.DoesNotExist:
                    Location.objects.create(email=email, latitude=latitude, longitude=longitude)
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