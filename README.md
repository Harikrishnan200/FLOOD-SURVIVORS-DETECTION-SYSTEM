# ResQVision

This project showcases an Automated Disaster Rescue System designed to help identify, locate, and rescue trapped individuals in disaster-affected areas using real-time AI technologies. 

🔧 Technologies Used
● Backend: Python Django, SQLite 
● Frontend: HTML, Tailwind CSS, JavaScript, AJAX 
● Object Detection: YOLOv5l (You Only Look Once – Large variant) 
● Object Tracking: Deep SORT (Simple Online and Realtime Tracking) 
● Frameworks & Libraries: Torch (PyTorch) with GPU acceleration for high-performance inference 

📷 Camera Compatibility 
The system is capable of integrating and processing feeds from: 
● Normal RGB Cameras 
● Thermal Imaging Cameras 
● Night Vision Cameras This makes it suitable for day and night operations, and even in low-visibility environments such as smoke, fog, or complete darkness.

⚙️ Performance 
The model is optimized using GPU acceleration with PyTorch, enabling fast and accurate person detection in real-time.
It delivers high frame-rate processing and stable tracking across video feeds, even under resource-constrained environments. Deep SORT ensures each person is uniquely identified and tracked, avoiding duplicate counts or missed detections.

🧠 Key Features 
● Processes both live video streams from UAVs or mobile phones and uploaded videos, including thermal videos. 
● Designed to function efficiently in critical environments like collapsed structures, forests, flood zones, or fire-affected areas. 
● Provides precise geolocation of detected individuals, which is then used to dispatch rescue teams.

👥 User Roles and Responsibilities
1. Super Admin: 
● Adds and manages volunteers across different locations. 
● Reviews and verifies reports submitted by volunteers. 
2. Volunteers: 
● Report disaster events with details like type of disaster, photos or videos, and exact location coordinates.
3. Admin:
● Monitors incoming videos using UAVs and integrated camera systems. 
● Detects and locates trapped individuals using object detection models.
● Creates rescue teams and sends them the GPS coordinates of detected persons. 
● Can integrate and switch between normal, thermal, or night vision cameras. 
4. Rescue Team Members: 
● These users are created and assigned by the admin. 
● They receive target locations and update the system on the rescue status after reaching the site.

This system brings together advanced AI-based computer vision, real-time video processing, and intelligent user management to build a robust, responsive, and scalable disaster management platform.





