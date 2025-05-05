from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, HttpResponse, FileResponse
import cv2
import threading
import time
import torch
import numpy as np
from collections import deque
import pyttsx3
import winsound
from ADMIN_APP.deep_sort.deep_sort import DeepSort
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import ProcessedVideo
from datetime import datetime
from AUTHENTICATION_APP.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from datetime import date


engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Adjust speech rate
engine.setProperty('volume', 1)  # Set volume to maximum


device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = torch.hub.load('ultralytics/yolov5', 'yolov5l', pretrained=True).to(device)
model.conf = 0.5  

print("Current working directory:", os.getcwd())

deep_sort_weights = r'C:\Users\harip\OneDrive\Desktop\FLOOD-SURVIVORS-DETECTION-SYSTEM\venv\Scripts\FLOOD_SURVIVORS_DETECTION_SYSTEM\ADMIN_APP\ckpt.t7'
print("Path to ckpt.t7:", deep_sort_weights)


tracker = DeepSort(model_path=deep_sort_weights, 
                   max_age=50,  # Reduce max age for better accuracy
                   n_init=3,    # Number of frames to confirm a track
                   nn_budget=100)  # Increase budget for more accurate tracking

beep_flag = threading.Event()  # Event flag for beep sound

unique_person_ids = set()
person_paths = {}

class VideoStream:
    def _init_(self, src):
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
            winsound.Beep(1000, 500)  # Beep sound with frequency 1000 Hz and duration 500 ms
            time.sleep(0.5)  # Small sleep to prevent tight loop

def start_beep_thread():
    """Starts the beep sound thread."""
    threading.Thread(target=beep_sound_thread, daemon=True).start()

def gen(camera):
    global beep_flag, unique_person_ids, person_paths   
    target_fps = 30.0
    frame_time = 1.0 / target_fps  # Time per frame for target FPS

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
        for output in outputs:
            x1, y1, x2, y2, track_id = output[:5]
            people_count += 1
            unique_person_ids.add(int(track_id))  

           
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

        elapsed_time = time.time() - start_time
        sleep_time = max(0, frame_time - elapsed_time)
        time.sleep(sleep_time)

def process_video(video_path, user):
    global unique_person_ids, person_paths  
    unique_person_ids.clear()
    person_paths.clear()
    
    start_time = datetime.now()
    
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    
    input_filename = os.path.splitext(os.path.basename(video_path))[0]
    output_filename = f"{input_filename}_output.mp4"
    output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break


        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = model(rgb_frame)
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

        for output in outputs:
            x1, y1, x2, y2, track_id = output[:5]
            unique_person_ids.add(int(track_id))  

            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            if track_id not in person_paths:
                person_paths[track_id] = deque(maxlen=64)  
            person_paths[track_id].appendleft(center)

            # Draw the path
            for i in range(1, len(person_paths[track_id])):
                if person_paths[track_id][i - 1] is None or person_paths[track_id][i] is None:
                    continue
                thickness = int(np.sqrt(64 / float(i + 1)) * 2.5)
                cv2.line(frame, person_paths[track_id][i - 1], person_paths[track_id][i], (0, 255, 0), thickness)

        print(f"Total unique persons detected: {len(unique_person_ids)}")

        out.write(frame)

    cap.release()
    out.release()

    
    end_time = datetime.now()
    processing_time = end_time - start_time

    
    total_persons_detected = len(unique_person_ids)
    processed_video = ProcessedVideo(
                                    user=user, 
                                    video_name=input_filename,
                                    output_video_path=output_path,
                                    total_persons_detected=total_persons_detected,
                                    processing_time=processing_time,
                                    status=True
                                    )
    processed_video.save()
    print(f"Processing time of the video: {processing_time}")

    return os.path.join(settings.MEDIA_URL, output_filename), processing_time  

@login_required
def admin_dashboard(request):
    return render(request, "AdminDashboard.html")

@login_required
def video_feed(request):
    video_path = request.GET.get('video_path')
    if video_path:
        camera = VideoStream(video_path)
        start_beep_thread()  
        return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')
    else:
        return render(request, 'AdminDashboard.html', {'error': 'Please provide a valid video file path.'})



@login_required(login_url='login')
def handle_file_upload(request):
    global uploaded_file_name

    if request.method == "POST" and request.FILES.get("video_file"):
        uploaded_file = request.FILES["video_file"]
        uploaded_file_name = uploaded_file.name
        print("Uploaded file:", uploaded_file.name)
        fs = FileSystemStorage()

 
        if fs.exists(uploaded_file.name):
            fs.delete(uploaded_file.name)

        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = os.path.join(settings.MEDIA_ROOT, filename)

        file_extension = filename.split(".")[-1].lower()

        if file_extension in ["mp4", "avi"]:
            video_result, processing_time = process_video(file_path, request.user)
            print("Processing complete")
            return JsonResponse({"status": "ok", "message": "File uploaded Successfully!"}, status=200)
        else:
            return JsonResponse({"error": "Unsupported file format."}, status=400)

    current_data = ProcessedVideo.objects.filter(
        user=request.user,
        created_at__date=date.today()
        ).values(
        'id','video_name', 'created_at', 'total_persons_detected', 'status', 'output_video_path','processing_time'
    )

    previous_data = ProcessedVideo.objects.filter(
    user=request.user
    ).exclude(
    created_at__date=date.today() 
    ).values(
    'id', 'video_name', 'created_at', 'total_persons_detected', 'status', 'output_video_path','processing_time'
    )
    return render(request, "UploadVideo.html", {"current_data": current_data, "previous_data": previous_data})


@login_required(login_url='login')
def get_current_data(request):
    current_data = ProcessedVideo.objects.filter(
        user=request.user,
        created_at__date=date.today()
        ).values(
        'id','video_name', 'created_at', 'total_persons_detected', 'status', 'output_video_path','processing_time'
    )
    return JsonResponse({"current_data": list(current_data)})
# @login_required(login_url='login')
# def handle_file_upload(request):
#     global uploaded_file_name

#     if request.method == "POST" and request.FILES.get("video_file"):
#         uploaded_file = request.FILES["video_file"]
#         uploaded_file_name = uploaded_file.name
#         print("Uploaded file:", uploaded_file.name)
#         fs = FileSystemStorage()

#         # Check if the file already exists and delete if it does
#         if fs.exists(uploaded_file.name):
#             fs.delete(uploaded_file.name)

#         filename = fs.save(uploaded_file.name, uploaded_file)
#         file_path = os.path.join(settings.MEDIA_ROOT, filename)

#         file_extension = filename.split(".")[-1].lower()

#         if file_extension in ["mp4", "avi"]:
#             video_result, processing_time = process_video(file_path, request.user)
#             context = {
#                 "video_path": video_result,
#                 "processing_time": processing_time,
#                 "message": "Output video is ready to download."
#             }
#             # Render the page with the context
#             rendered_page = render(request, "UploadVideo.html", context)
#             # Create a JSON response
#             json_data = json.dumps(context)
#             # Combine the rendered page and JSON response
#             return HttpResponse(rendered_page, content_type="application/json")

#         else:
#             context = {"error": "Unsupported file format."}
#             rendered_page = render(request, "UploadVideo.html", context)
#             json_data = json.dumps(context)
#             return HttpResponse(rendered_page, content_type="application/json")

#     context = {"error": "No file uploaded."}
#     rendered_page = render(request, "UploadVideo.html", context)
#     json_data = json.dumps(context)
#     return HttpResponse(rendered_page, content_type="application/json")



@login_required(login_url='login')
def get_current_data(request):
    current_data = ProcessedVideo.objects.filter(user=request.user).values(
        'video_name', 'created_at', 'total_persons_detected', 'status', 'output_video_path'
    )
    return JsonResponse({"current_data": list(current_data)})


def user_profile(request):
    return render(request, "userprofile.html")

@login_required(login_url='login')
def download_video(request, video_id=None):
    print("inside download_video")
    try:
        video = ProcessedVideo.objects.get(pk=video_id, user=request.user)
        file_path = video.output_video_path
        print(video_id)
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type="video/mp4")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
        else:
            return HttpResponse("File not found.")
    except ProcessedVideo.DoesNotExist:
        return HttpResponse("Video not found.")
    
# @login_required(login_url='login')
# def get_recent_data(request):
#     processed_videos = ProcessedVideo.objects.filter(user=request.user).order_by('-created_at')[:5]
#     data = {"processed_videos": processed_videos}
#     return JsonResponse(data=data)
@login_required(login_url='login')
def get_recent_data(request):
    processed_videos = ProcessedVideo.objects.filter(
        user=request.user,
        created_at__date=date.today()
    ).values(
        'id', 'video_name', 'created_at', 'total_persons_detected', 'status', 'output_video_path'
    )
    data = list(processed_videos)
    return JsonResponse({"current_data": data})
