from django.shortcuts import render
from .models import RescueDetails, RescueTeam
from GPS_LOCATION.models import Location
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from django.contrib.auth.decorators import user_passes_test
import datetime
# Create your views here.

def rescue_dashboard(request):
    return render(request, 'RescueDashboard.html')

def is_admin(user):
    return user.is_authenticated and user.is_admin  

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='login')
def update_rescue_details(request, id):
    print("User: ", request.user)
    print("Id is---------------------: ", id)

    try:
        location_obj = Location.objects.get(id=id)

        geolocator = Nominatim(user_agent="flood_survivor_detection_app")
        location = geolocator.reverse((location_obj.latitude, location_obj.longitude), exactly_one=True)

        if location:
            location_name = location.address  
            # town_name = location.raw.get('address').get('village', 'town', 'city', 'Unknown')
            town_name = location.raw.get('address').get('town', 'Unknown')
        else:
            location_name = "Unknown"
        print("Town name: ", town_name)
        # Create RescueDetails with location name
        RescueDetails.objects.create(
            latitude=location_obj.latitude,
            longitude=location_obj.longitude,
            location_name=location_name,
            town_name=town_name,
            detected_count=location_obj.detected_count,
            status='Pending',
            created_by=request.user
        )

        return JsonResponse({'status': 'success', 'location_name': location_name})

    except Location.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Location not found'}, status=404)

    except (GeocoderServiceError, GeocoderTimedOut):
        return JsonResponse({'status': 'error', 'message': 'Geocoding service error'}, status=500)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    


@login_required(login_url='login')
def update_rescue_table(request):
    if not request.user.is_admin:
        rescue_team = RescueTeam.objects.filter(rescue_user=request.user).first()
        if rescue_team is None:
            return JsonResponse({'status': 'error', 'message': 'Rescue team not found'}, status=404)
        print("added by: ", rescue_team.added_by)
        rescue_details = RescueDetails.objects.filter(
            created_at__date=datetime.date.today(),
            created_by=rescue_team.added_by
        ).values('latitude', 'longitude', 'location_name', 'town_name', 'detected_count', 'status', 'is_rescued')

        return JsonResponse({'status': 'success', 'rescue_details': list(rescue_details.values())})
    else:
        return JsonResponse({'status': 'error', 'message': 'Admin cannot access this page'}, status=404)


@login_required(login_url='login')
def update_complete_and_pending(request,id):
    print("User: ", request.user)
    if not request.user.is_admin:
        rescue_obj = RescueDetails.objects.get(id=id)
        location_table_obj = Location.objects.filter(latitude=rescue_obj.latitude, longitude=rescue_obj.longitude, status=rescue_obj.status).first()
        if location_table_obj:
            if rescue_obj.status == 'Pending':
                rescue_obj.status = 'Completed'
                rescue_obj.is_rescued = True
                location_table_obj.status = 'Completed'
                location_table_obj.save()
                rescue_obj.save()
            else:
                rescue_obj.status = 'Pending'
                rescue_obj.is_rescued = False
                location_table_obj.status = 'Pending'
                location_table_obj.save()
                rescue_obj.save()
        else:
            return JsonResponse({'status': 'error', 'message': 'Location not found'}, status=404)
    rescue_obj = RescueDetails.objects.get(id=id)
    # update_rescue_table(request)
    
    return JsonResponse({'status': 'success', 'message': 'Rescue details updated successfully'})    
    