from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
import threading
import time

# Video stream class that runs in a separate thread to avoid blocking the main thread
class VideoStream:
    def __init__(self, src):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        # Start the thread to read frames
        threading.Thread(target=self.update, args=()).start()

    def update(self):
        while not self.stopped:
            # Read the next frame from the video stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()  # Release the stream when stopping

# Function to generate frames from the IP webcam feed
def gen(camera):
    while True:
        frame = camera.read()
        if frame is None:
            break
        
        # Resize frame to lower resolution (e.g., 640x480) to reduce lag
        frame = cv2.resize(frame, (640, 480))
        
        # Encode the frame to JPEG format
        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        # Yield frame in multipart format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

        # Introduce a small delay to limit the FPS (e.g., 10 FPS)
        time.sleep(0.1)

# View to handle the dashboard, where the user can input the IP camera URL
def dashboard(request):
    ip_cam_url = None
    if request.method == 'POST':
        # Get the IP camera URL entered by the user
        ip_cam_url = request.POST.get('ip_cam_url')
        print("IP Camera URL:", ip_cam_url)
        return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})

    # Render the dashboard template with the IP camera URL if it's a GET request
    return render(request, 'AdminDashboard.html', {'ip_cam_url': ip_cam_url})

# View to handle the streaming of video from the IP camera
def video_feed(request):
    # Get the IP camera URL from the request
    ip_cam_url = request.GET.get('ip_cam_url')
    if ip_cam_url:
        # Use the threaded video stream class to capture video
        camera = VideoStream(ip_cam_url)
        return StreamingHttpResponse(gen(camera), content_type='multipart/x-mixed-replace; boundary=frame')
    else:
        return render(request, 'AdminDashboard.html', {'error': 'Please provide a valid IP camera URL.'})
