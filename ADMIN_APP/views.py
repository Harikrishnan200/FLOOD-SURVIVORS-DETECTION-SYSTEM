# from django.shortcuts import render, redirect
# from django.http import StreamingHttpResponse, JsonResponse
# import cv2
# import threading
# import time
# import torch
# import numpy as np
# from collections import deque
# import pyttsx3
# import winsound
# from .deep_sort.deep_sort import DeepSort
# import os
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from share import get_current_location

# engine = pyttsx3.init()
# engine.setProperty('rate', 200)
# engine.setProperty('volume', 1)

# # Load YOLOv5 model
# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True).to(device)
# model.conf = 0.5  # Set confidence threshold to 0.5

# print("Current working directory:", os.getcwd())

# deep_sort_weights = r'C:\Users\harip\OneDrive\Desktop\FLOOD_SURVIVORS_PROJECT\venv\Scripts\FLOOD_SURVIVORS_DETECTION_SYSTEM\ADMIN_APP\deep_sort\deep\checkpoint\ckpt.t7'
# print("Path to ckpt.t7:", deep_sort_weights)

# tracker = DeepSort(model_path=deep_sort_weights,
#                    max_age=50,
#                    n_init=3,
#                    nn_budget=100)

# beep_flag = threading.Event()

# unique_person_ids = set()
# person_paths = {}


# class VideoStream:
#     def __init__(self, src):
#         self.stream = cv2.VideoCapture(src)
#         (self.grabbed, self.frame) = self.stream.read()
#         self.stopped = False
#         threading.Thread(target=self.update, args=()).start()

#     def update(self):
#         while not self.stopped:
#             (self.grabbed, self.frame) = self.stream.read()

#     def read(self):
#         return self.frame

#     def stop(self):
#         self.stopped = True
#         self.stream.release()

# def beep_sound_thread():
#     """Dedicated thread to play beep sound when event is set."""
#     while True:
#         beep_flag.wait()
#         while beep_flag.is_set():
#             winsound.Beep(1000, 500)
#             time.sleep(0.5)

# def start_beep_thread():
#     """Starts the beep sound thread."""
#     threading.Thread(target=beep_sound_thread, daemon=True).start()

# @csrf_exempt
# def gen(camera):
#     global beep_flag, unique_person_ids, person_paths
#     target_fps = 30.0
#     frame_time = 1.0 / target_fps
#     frame_count = 0
#     count_interval = 30  # Send the count every 30 frames

#     while True:
#         start_time = time.time()

#         frame = camera.read()
#         if frame is None:
#             print("No frame received from camera")
#             break

#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = model(rgb_frame, size=640)
#         detected_objects = results.xyxy[0].cpu().numpy()

#         dets = []
#         for det in detected_objects:
#             x1, y1, x2, y2, conf, cls = det[:6]
#             x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
#             label = results.names[int(cls)]

#             if label == "person":
#                 dets.append((x1, y1, x2, y2, conf))

#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 label = f"{label} {conf:.2f}"
#                 cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#         if dets:
#             xywhs = np.array([[((x1 + x2) // 2), ((y1 + y2) // 2), x2 - x1, y2 - y1] for x1, y1, x2, y2, conf in dets])
#             confs = np.array([conf for x1, y1, x2, y2, conf in dets])
#             outputs = tracker.update(xywhs, confs, rgb_frame)
#         else:
#             outputs = tracker.update(np.empty((0, 4)), np.empty((0,)), rgb_frame)

#         people_count = 0
#         for output in outputs:
#             x1, y1, x2, y2, track_id = output[:5]
#             people_count += 1
#             unique_person_ids.add(int(track_id))

#             center = ((x1 + x2) // 2, (y1 + y2) // 2)
#             if track_id not in person_paths:
#                 person_paths[track_id] = deque(maxlen=64)
#             person_paths[track_id].appendleft(center)

#             for i in range(1, len(person_paths[track_id])):
#                 if person_paths[track_id][i - 1] is None or person_paths[track_id][i] is None:
#                     continue
#                 thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
#                 cv2.line(frame, person_paths[track_id][i - 1], person_paths[track_id][i], (0, 255, 0), thickness)

#         print(f"People detected: {people_count}")
#         print(f"Total unique persons detected: {len(unique_person_ids)}")

#         if people_count > 0:
#             beep_flag.set()
#         else:
#             beep_flag.clear()

#         _, jpeg = cv2.imencode('.jpg', frame)
#         frame = jpeg.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#         frame_count += 1
#         if frame_count % count_interval == 0:
#             yield (b'--count\r\n'
#                    b'Content-Type: application/json\r\n\r\n' +
#                    bytes(JsonResponse({'unique_person_count': len(unique_person_ids)}).content) +
#                    b'\r\n\r\n')

#         elapsed_time = time.time() - start_time
#         sleep_time = max(0, frame_time - elapsed_time)
#         time.sleep(sleep_time)



# @login_required(login_url='login')
# def admin_dashboard(request):
#     ip_cam_url = None
#     if request.method == 'POST':
#         ip_cam_url = request.POST.get('ip_cam_url')
#         print("IP Camera URL:", ip_cam_url)
#         return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})
#     return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})


# @login_required(login_url='login')
# def video_feed(request):
#     ip_cam_url = request.GET.get('ip_cam_url')
#     print("Inside the video feed fn")
#     print(ip_cam_url)
#     if ip_cam_url:
#         camera = VideoStream(ip_cam_url)
#         start_beep_thread()
#         return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')
#     else:
#         return render(request, 'AdminDashboard.html', {'error': 'Please provide a valid IP camera URL.'})

# @login_required(login_url='login')
# def uploadVideo(request):
#     return render(request, 'UploadVideo.html')

# @login_required(login_url='login')
# def previous_data(request):
#     return render(request, 'PreviousData.html')

# @login_required(login_url='login')
# def user_profile(request):
#     return render(request, 'UserProfile.html')


# def add_user(request):
#     return render(request, 'AddUsers.html')

# @login_required(login_url='login')
# def get_unique_person_count(request):
#     global unique_person_ids
#     latitude, longitude = get_current_location()
#     print(f"Current location: {latitude}, {longitude}")
#     return JsonResponse({'unique_person_count': len(unique_person_ids),
#                             'latitude': latitude,
#                             'longitude': longitude
#                          })


# from django.shortcuts import render, redirect
# from django.http import StreamingHttpResponse, JsonResponse
# import cv2
# import threading
# import multiprocessing as mp
# import time
# import torch
# import numpy as np
# from collections import deque
# import pyttsx3
# import winsound
# from .deep_sort.deep_sort import DeepSort
# import os
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from share import get_current_location

# engine = pyttsx3.init()
# engine.setProperty('rate', 200)
# engine.setProperty('volume', 1)

# # Load YOLOv5 model
# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True).to(device)
# model.conf = 0.5  # Set confidence threshold to 0.5

# print("Current working directory:", os.getcwd())

# deep_sort_weights = r'C:\Users\harip\OneDrive\Desktop\FLOOD_SURVIVORS_PROJECT\venv\Scripts\FLOOD_SURVIVORS_DETECTION_SYSTEM\ADMIN_APP\deep_sort\deep\checkpoint\ckpt.t7'
# print("Path to ckpt.t7:", deep_sort_weights)

# tracker = DeepSort(model_path=deep_sort_weights,
#                    max_age=50,
#                    n_init=3,
#                    nn_budget=100)

# beep_flag = threading.Event()

# # Updated to use multiprocessing.Manager for shared state
# manager = mp.Manager()
# unique_person_ids = manager.list()
# person_paths = manager.dict()
# unique_person_lock = threading.Lock()

# class VideoStream:
#     def __init__(self, src):
#         self.stream = cv2.VideoCapture(src)
#         (self.grabbed, self.frame) = self.stream.read()
#         self.stopped = False
#         threading.Thread(target=self.update, args=()).start()

#     def update(self):
#         while not self.stopped:
#             (self.grabbed, self.frame) = self.stream.read()

#     def read(self):
#         return self.frame

#     def stop(self):
#         self.stopped = True
#         self.stream.release()

# def beep_sound_thread():
#     """Dedicated thread to play beep sound when event is set."""
#     while True:
#         beep_flag.wait()
#         while beep_flag.is_set():
#             winsound.Beep(1000, 500)
#             time.sleep(0.5)

# def start_beep_thread():
#     """Starts the beep sound thread."""
#     threading.Thread(target=beep_sound_thread, daemon=True).start()

# @csrf_exempt
# def gen(camera):
#     global beep_flag, unique_person_ids, person_paths
#     target_fps = 30.0
#     frame_time = 1.0 / target_fps
#     frame_count = 0
#     count_interval = 30  # Send the count every 30 frames

#     while True:
#         start_time = time.time()

#         frame = camera.read()
#         if frame is None:
#             print("No frame received from camera")
#             break

#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = model(rgb_frame, size=640)
#         detected_objects = results.xyxy[0].cpu().numpy()

#         dets = []
#         for det in detected_objects:
#             x1, y1, x2, y2, conf, cls = det[:6]
#             x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
#             label = results.names[int(cls)]

#             if label == "person":
#                 dets.append((x1, y1, x2, y2, conf))

#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 label = f"{label} {conf:.2f}"
#                 cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#         if dets:
#             xywhs = np.array([[((x1 + x2) // 2), ((y1 + y2) // 2), x2 - x1, y2 - y1] for x1, y1, x2, y2, conf in dets])
#             confs = np.array([conf for x1, y1, x2, y2, conf in dets])
#             outputs = tracker.update(xywhs, confs, rgb_frame)
#         else:
#             outputs = tracker.update(np.empty((0, 4)), np.empty((0,)), rgb_frame)

#         people_count = 0
#         with unique_person_lock:
#             for output in outputs:
#                 x1, y1, x2, y2, track_id = output[:5]
#                 people_count += 1
#                 if track_id not in unique_person_ids:
#                     unique_person_ids.append(int(track_id))

#                 center = ((x1 + x2) // 2, (y1 + y2) // 2)
#                 if track_id not in person_paths:
#                     person_paths[track_id] = deque(maxlen=64)
#                 person_paths[track_id].appendleft(center)

#                 for i in range(1, len(person_paths[track_id])):
#                     if person_paths[track_id][i - 1] is None or person_paths[track_id][i] is None:
#                         continue
#                     thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
#                     cv2.line(frame, person_paths[track_id][i - 1], person_paths[track_id][i], (0, 255, 0), thickness)

#         print(f"People detected: {people_count}")
#         print(f"Total unique persons detected: {len(unique_person_ids)}")

#         if people_count > 0:
#             beep_flag.set()
#         else:
#             beep_flag.clear()

#         _, jpeg = cv2.imencode('.jpg', frame)
#         frame = jpeg.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#         frame_count += 1
#         if frame_count % count_interval == 0:
#             yield (b'--count\r\n'
#                    b'Content-Type: application/json\r\n\r\n' +
#                    bytes(JsonResponse({'unique_person_count': len(unique_person_ids)}).content) +
#                    b'\r\n\r\n')

#         elapsed_time = time.time() - start_time
#         sleep_time = max(0, frame_time - elapsed_time)
#         time.sleep(sleep_time)


# @login_required(login_url='login')
# def admin_dashboard(request):
#     ip_cam_url = None
#     if request.method == 'POST':
#         ip_cam_url = request.POST.get('ip_cam_url')
#         print("IP Camera URL:", ip_cam_url)
#         return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})
#     return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})


# @login_required(login_url='login')
# def video_feed(request):
#     ip_cam_url = request.GET.get('ip_cam_url')
#     print("Inside the video feed fn")
#     print(ip_cam_url)
#     if ip_cam_url:
#         camera = VideoStream(ip_cam_url)
#         start_beep_thread()
#         return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')
#     else:
#         return render(request, 'AdminDashboard.html', {'error': 'Please provide a valid IP camera URL.'})


# @login_required(login_url='login')
# def uploadVideo(request):
#     return render(request, 'UploadVideo.html')


# @login_required(login_url='login')
# def previous_data(request):
#     return render(request, 'PreviousData.html')


# @login_required(login_url='login')
# def user_profile(request):
#     return render(request, 'UserProfile.html')


# def add_user(request):
#     return render(request, 'AddUsers.html')


# @login_required(login_url='login')
# def get_unique_person_count(request):
#     global unique_person_ids
#     latitude, longitude = get_current_location()
#     print(f"Current location: {latitude}, {longitude}")
#     return JsonResponse({'unique_person_count': len(unique_person_ids),
#                          'latitude': latitude,
#                          'longitude': longitude
#                          })


# from django.shortcuts import render, redirect
# from django.http import StreamingHttpResponse, JsonResponse
# import cv2
# import threading
# import time
# import torch
# import numpy as np
# from collections import deque
# import pyttsx3
# import winsound
# from .deep_sort.deep_sort import DeepSort
# import os
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from share import get_current_location

# engine = pyttsx3.init()
# engine.setProperty('rate', 200)
# engine.setProperty('volume', 1)

# # Load YOLOv5 model
# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True).to(device)
# model.conf = 0.5  # Set confidence threshold to 0.5

# print("Current working directory:", os.getcwd())

# deep_sort_weights = r'C:\Users\harip\OneDrive\Desktop\FLOOD_SURVIVORS_PROJECT\venv\Scripts\FLOOD_SURVIVORS_DETECTION_SYSTEM\ADMIN_APP\deep_sort\deep\checkpoint\ckpt.t7'
# print("Path to ckpt.t7:", deep_sort_weights)

# tracker = DeepSort(model_path=deep_sort_weights,
#                    max_age=50,
#                    n_init=3,
#                    nn_budget=100)

# beep_flag = threading.Event()

# unique_person_ids = []
# person_paths = {}
# unique_person_lock = threading.Lock()

# class VideoStream:
#     def __init__(self, src):
#         self.stream = cv2.VideoCapture(src)
#         (self.grabbed, self.frame) = self.stream.read()
#         self.stopped = False
#         threading.Thread(target=self.update, args=()).start()

#     def update(self):
#         while not self.stopped:
#             (self.grabbed, self.frame) = self.stream.read()

#     def read(self):
#         return self.frame

#     def stop(self):
#         self.stopped = True
#         self.stream.release()

# def beep_sound_thread():
#     """Dedicated thread to play beep sound when event is set."""
#     while True:
#         beep_flag.wait()
#         while beep_flag.is_set():
#             winsound.Beep(1000, 500)
#             time.sleep(0.5)

# def start_beep_thread():
#     """Starts the beep sound thread."""
#     threading.Thread(target=beep_sound_thread, daemon=True).start()

# @csrf_exempt
# def gen(camera):
#     global beep_flag, unique_person_ids, person_paths
#     target_fps = 30.0
#     frame_time = 1.0 / target_fps
#     frame_count = 0
#     count_interval = 30  # Send the count every 30 frames

#     while True:
#         start_time = time.time()

#         frame = camera.read()
#         if frame is None:
#             print("No frame received from camera")
#             break

#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = model(rgb_frame, size=640)
#         detected_objects = results.xyxy[0].cpu().numpy()

#         dets = []
#         for det in detected_objects:
#             x1, y1, x2, y2, conf, cls = det[:6]
#             x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
#             label = results.names[int(cls)]

#             if label == "person":
#                 dets.append((x1, y1, x2, y2, conf))

#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 label = f"{label} {conf:.2f}"
#                 cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#         if dets:
#             xywhs = np.array([[((x1 + x2) // 2), ((y1 + y2) // 2), x2 - x1, y2 - y1] for x1, y1, x2, y2, conf in dets])
#             confs = np.array([conf for x1, y1, x2, y2, conf in dets])
#             outputs = tracker.update(xywhs, confs, rgb_frame)
#         else:
#             outputs = tracker.update(np.empty((0, 4)), np.empty((0,)), rgb_frame)

#         people_count = 0
#         with unique_person_lock:
#             for output in outputs:
#                 x1, y1, x2, y2, track_id = output[:5]
#                 people_count += 1
#                 if track_id not in unique_person_ids:
#                     unique_person_ids.append(int(track_id))

#                 center = ((x1 + x2) // 2, (y1 + y2) // 2)
#                 if track_id not in person_paths:
#                     person_paths[track_id] = deque(maxlen=64)
#                 person_paths[track_id].appendleft(center)

#                 for i in range(1, len(person_paths[track_id])):
#                     if person_paths[track_id][i - 1] is None or person_paths[track_id][i] is None:
#                         continue
#                     thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
#                     cv2.line(frame, person_paths[track_id][i - 1], person_paths[track_id][i], (0, 255, 0), thickness)

#         print(f"People detected: {people_count}")
#         print(f"Total unique persons detected: {len(unique_person_ids)}")

#         if people_count > 0:
#             beep_flag.set()
#         else:
#             beep_flag.clear()

#         _, jpeg = cv2.imencode('.jpg', frame)
#         frame = jpeg.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#         frame_count += 1
#         if frame_count % count_interval == 0:
#             yield (b'--count\r\n'
#                    b'Content-Type: application/json\r\n\r\n' +
#                    bytes(JsonResponse({'unique_person_count': len(unique_person_ids)}).content) +
#                    b'\r\n\r\n')

#         elapsed_time = time.time() - start_time
#         sleep_time = max(0, frame_time - elapsed_time)
#         time.sleep(sleep_time)


# @login_required(login_url='login')
# def admin_dashboard(request):
#     ip_cam_url = None
#     if request.method == 'POST':
#         ip_cam_url = request.POST.get('ip_cam_url')
#         print("IP Camera URL:", ip_cam_url)
#         return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})
#     return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})


# @login_required(login_url='login')
# def video_feed(request):
#     ip_cam_url = request.GET.get('ip_cam_url')
#     print("Inside the video feed fn")
#     print(ip_cam_url)
#     if ip_cam_url:
#         camera = VideoStream(ip_cam_url)
#         start_beep_thread()
#         return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')
#     else:
#         return render(request, 'AdminDashboard.html', {'error': 'Please provide a valid IP camera URL.'})


# @login_required(login_url='login')
# def uploadVideo(request):
#     return render(request, 'UploadVideo.html')


# @login_required(login_url='login')
# def previous_data(request):
#     return render(request, 'PreviousData.html')


# @login_required(login_url='login')
# def user_profile(request):
#     return render(request, 'UserProfile.html')


# def add_user(request):
#     return render(request, 'AddUsers.html')


# @login_required(login_url='login')
# def get_unique_person_count(request):
#     global unique_person_ids
#     latitude, longitude = get_current_location()
#     print(f"Current location: {latitude}, {longitude}")
#     return JsonResponse({'unique_person_count': len(unique_person_ids),
#                          'latitude': latitude,
#                          'longitude': longitude
#                          })






from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
import cv2
import threading
import time
import torch
import numpy as np
from collections import deque
import pyttsx3
import winsound
from .deep_sort.deep_sort import DeepSort
import os
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from share import get_current_location
from AUTHENTICATION_APP.models import CustomUser
from RESCUE_APP.models import RescueDetails, RescueTeam
from django.utils import timezone
from django.views.decorators.http import require_http_methods



engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1)

# Load YOLOv5 model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True).to(device)
model.conf = 0.5  # Set confidence threshold to 0.5

print("Current working directory:", os.getcwd())

deep_sort_weights = r'C:\Users\harip\OneDrive\Desktop\FLOOD_SURVIVORS_PROJECT\venv\Scripts\FLOOD_SURVIVORS_DETECTION_SYSTEM\ADMIN_APP\deep_sort\deep\checkpoint\ckpt.t7'
print("Path to ckpt.t7:", deep_sort_weights)

tracker = DeepSort(model_path=deep_sort_weights,
                   max_age=50,
                   n_init=3,
                   nn_budget=100)

beep_flag = threading.Event()

unique_person_ids = []
person_paths = {}
unique_person_lock = threading.Lock()

class VideoStream:
    def __init__(self, src):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        threading.Thread(target=self.update, args=()).start()

    def update(self):
        while not self.stopped:
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

def beep_sound_thread():
    """Dedicated thread to play beep sound when event is set."""
    while True:
        beep_flag.wait()
        while beep_flag.is_set():
            winsound.Beep(1000, 500)
            time.sleep(0.5)

def start_beep_thread():
    """Starts the beep sound thread."""
    threading.Thread(target=beep_sound_thread, daemon=True).start()

@csrf_exempt
def gen(camera):
    global beep_flag, unique_person_ids, person_paths
    target_fps = 30.0
    frame_time = 1.0 / target_fps
    frame_count = 0
    count_interval = 30  # Send the count every 30 frames

    while True:
        start_time = time.time()

        frame = camera.read()
        if frame is None:
            print("No frame received from camera")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(rgb_frame, size=640)
        detected_objects = results.xyxy[0].cpu().numpy()

        dets = []
        for det in detected_objects:
            x1, y1, x2, y2, conf, cls = det[:6]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            label = results.names[int(cls)]

            if label == "person":
                dets.append((x1, y1, x2, y2, conf))

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{label} {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if dets:
            xywhs = np.array([[((x1 + x2) // 2), ((y1 + y2) // 2), x2 - x1, y2 - y1] for x1, y1, x2, y2, conf in dets])
            confs = np.array([conf for x1, y1, x2, y2, conf in dets])
            outputs = tracker.update(xywhs, confs, rgb_frame)
        else:
            outputs = tracker.update(np.empty((0, 4)), np.empty((0,)), rgb_frame)

        people_count = 0
        with unique_person_lock:
            for output in outputs:
                x1, y1, x2, y2, track_id = output[:5]
                people_count += 1
                if track_id not in unique_person_ids:
                    unique_person_ids.append(int(track_id))

                center = ((x1 + x2) // 2, (y1 + y2) // 2)
                if track_id not in person_paths:
                    person_paths[track_id] = deque(maxlen=64)
                person_paths[track_id].appendleft(center)

                for i in range(1, len(person_paths[track_id])):
                    if person_paths[track_id][i - 1] is None or person_paths[track_id][i] is None:
                        continue
                    thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
                    cv2.line(frame, person_paths[track_id][i - 1], person_paths[track_id][i], (0, 255, 0), thickness)

        print(f"People detected: {people_count}")
        print(f"Total unique persons detected: {len(unique_person_ids)}")

        if people_count > 0:
            beep_flag.set()
        else:
            beep_flag.clear()

        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        frame_count += 1
        if frame_count % count_interval == 0:
            yield (b'--count\r\n'
                   b'Content-Type: application/json\r\n\r\n' +
                   bytes(JsonResponse({'unique_person_count': len(unique_person_ids)}).content) +
                   b'\r\n\r\n')

        elapsed_time = time.time() - start_time
        sleep_time = max(0, frame_time - elapsed_time)
        time.sleep(sleep_time)

@login_required(login_url='login')
def admin_dashboard(request):
    ip_cam_url = None
    if request.method == 'POST':
        ip_cam_url = request.POST.get('ip_cam_url')
        print("IP Camera URL:", ip_cam_url)
        return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})
    return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})

@login_required(login_url='login')
def video_feed(request):
    ip_cam_url = request.GET.get('ip_cam_url')
    print("Inside the video feed fn")
    print(ip_cam_url)
    if ip_cam_url:
        camera = VideoStream(ip_cam_url)
        start_beep_thread()
        return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')
    else:
        return render(request, 'AdminDashboard.html', {'error': 'Please provide a valid IP camera URL.'})

@login_required(login_url='login')
def uploadVideo(request):
    return render(request, 'UploadVideo.html')

@login_required(login_url='login')
def previous_data(request):
    current_year = timezone.now().year
    current_year_data = RescueDetails.objects.filter(created_by=request.user, created_at__year=current_year).values('id', 'location_name', 'detected_count', 'status', 'created_at','is_rescued')
    previous_year_data = RescueDetails.objects.filter(created_by=request.user, created_at__year=current_year-1).values('id', 'location_name', 'detected_count', 'status', 'created_at','is_rescued')
    
    context = {
        'current_year_data': current_year_data,
        'previous_year_data': previous_year_data
    }
    return render(request, 'PreviousData.html', context)

@login_required(login_url='login')
def user_profile(request):
    return render(request, 'UserProfile.html')


@login_required(login_url='login')
def add_users(request, email=None):
    print(request.user)
    if email and request.user.is_admin:
        try:
            user = CustomUser.objects.get(email=email)
            rescue_team_members = list(RescueTeam.objects.filter(added_by=request.user).values_list('rescue_user__id', flat=True))
            if not user.is_admin and user.id not in rescue_team_members:
                RescueTeam.objects.create(rescue_user = user,
                                          added_by = request.user
                                          )
                return JsonResponse({'message': 'User added successfully.'})
            elif user.is_admin:
                return JsonResponse({'message': 'Admin added successfully.'})
            else:
                return JsonResponse({'message': 'Email found but user type not recognized.'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'message': 'Email not found in CustomUser table.'})

    else:
        context = {'team_members': RescueTeam.objects.filter(added_by=request.user)}
        return render(request, 'AddUsers.html', context)

@login_required(login_url='login')   
def delete_rescue_team_member(request, email=None):
    try:
        user = CustomUser.objects.get(email=email)
        rescue_team_members = RescueTeam.objects.filter(rescue_user=user, added_by=request.user)
        if rescue_team_members.exists():
            rescue_team_members.delete()
            return JsonResponse({'message': 'User deleted successfully.'})
        else:
            return JsonResponse({'message': 'Rescue team member not found.'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'message': 'User not found.'})
    

# Not required
def update_rescue_team_member(request, email=None):
    # try:
    #     user = CustomUser.objects.get(email=email)
    #     rescue_team_member = RescueTeam.objects.get(rescue_user=user, added_by=request.user)
    #     if request.method == 'POST':
    #         rescue_team_member.rescue_user = CustomUser.objects.get(email=request.POST.get('email'))
    #         rescue_team_member.save()
    #         return redirect('add_users')
    #     return render(request, 'EditRescueTeamMember.html', {'rescue_team_member': rescue_team_member})
    # except CustomUser.DoesNotExist:
    print("Inside the edit rescue team member fn")
    return JsonResponse({'message': 'User not found.'})

@login_required(login_url='login')
def update_rescue_team_table_content(request):
    rescue_team_members = RescueTeam.objects.filter(added_by=request.user)
    members_data = []
    
    for member in rescue_team_members:
        user = CustomUser.objects.get(id=member.rescue_user_id)
        member_data = {
            'id': member.id,
            'email': user.email,
            'added_date': member.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        members_data.append(member_data)
    
    return JsonResponse({'rescue_team_members': members_data})

@login_required(login_url='login')
def get_unique_person_count(request):
    global unique_person_ids
    latitude, longitude = get_current_location()
    print(f"Current location: {latitude}, {longitude}")
    return JsonResponse({'unique_person_count': len(unique_person_ids),
                         'latitude': latitude,
                         'longitude': longitude
                         })



@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def admin_details(request):
    """
    Handle admin profile details retrieval and update.
    GET: Return admin profile details.
    POST: Update admin profile details.
    """
    if request.user.role != 'Admin':
        return JsonResponse({
            'success': False,
            'message': 'Unauthorized. Only admin users can access this page.'
        }, status=403)
    
    # GET request - return user details
    if request.method == 'GET':
        user_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'role': request.user.role,
            'country': request.user.country,
            'is_admin': request.user.is_admin,
            'created_at': request.user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': request.user.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # If you have a profile picture field, include it here
        # if request.user.profile_picture:
        #     user_data['profile_picture'] = request.user.profile_picture.url
            
        return JsonResponse(user_data)
    
    # POST request - update user details
    elif request.method == 'POST':
        try:
            if 'first_name' in request.POST:
                request.user.first_name = request.POST['first_name']
                
            if 'last_name' in request.POST:
                request.user.last_name = request.POST['last_name']
                
            if 'country' in request.POST:
                country = request.POST['country']
    
                valid_countries = [choice[0] for choice in request.user.COUNTRY_CHOICES]
                if country in valid_countries:
                    request.user.country = country
                else:
                    # Log the error for debugging
                    print(f"Invalid country '{country}' selected. Valid choices are: {valid_countries}")
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid country selected.'
                    }, status=400)
            

            if 'profile_picture' in request.FILES:
                # and appropriate storage settings before uncommenting this
                # request.user.profile_picture = request.FILES['profile_picture']
                pass
                
            # Save user changes
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully'
            })
            
        except Exception as e:
            import traceback
            print(f"Error updating profile: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'message': f'Error updating profile: {str(e)}'
            }, status=500)