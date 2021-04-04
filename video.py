from pathlib import Path 
from fastapi import FastAPI 
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from fastapi import Header 
from fastapi.templating import Jinja2Templates 
import threading
import cv2 

from timer import Timer

app = FastAPI()

config = {
    "timer_period": 30, 
    "font": cv2.FONT_HERSHEY_SIMPLEX,
    "font_scale": 5,
    "text_thickness": 1,
}

lock = threading.Lock()
output_frame = None 

# def generate():
#     global outputFrame, lock 
#     while True: 
#         with lock:
#             if outputFrame is None:
#                 continue 
#             (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
#             if not flag:
#                 continue 
#     yield (b'--frame\r\n' b'Content-Type: image/jpeg/\r\n\r\n' + bytearray(encodedImage) + b'\r\n') 

def process_video(cap, timer):
    global config, output_frame

    while True:
        _, frame = cap.read()
        # draw rectangle
        xmin = int(0.1 * frame.shape[1])
        ymin = int(0.1 * frame.shape[0])
        xmax = int(0.9 * frame.shape[1])
        ymax = int(0.9 * frame.shape[0])
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0,255,0), 1)
        # count time 
        ret, current_time = timer.count()
        if ret:
            text_size = cv2.getTextSize(str(current_time), 
                                        config["font"], 
                                        config["font_scale"], 
                                        config["text_thickness"])[0]
            cv2.putText(frame, 
                str(current_time),
                ((frame.shape[1] - text_size[0])//2, (frame.shape[0] - text_size[1])//2), 
                config["font"], 
                config["font_scale"], 
                (0,0,255), 
                config["text_thickness"])
        with lock:
            output_frame = frame.copy()

def feed_video():
    global config, output_frame
    while True:
        with lock:
            if output_frame is None: 
                continue 
            _, encodedImage = cv2.imencode(".jpg", output_frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg/\r\n\r\n' + bytearray(encodedImage) + b'\r\n') 

@app.on_event("shutdown")
async def on_shutdown() -> None: 
    pass

@app.get("/")
def main():
    global config 
    cap = cv2.VideoCapture(0)
    timer = Timer(config["timer_period"]) 
    thread = threading.Thread(target=process_video, args=(cap, timer))
    thread.setDaemon(True)
    thread.start()
    return StreamingResponse(feed_video(), media_type="multipart/x-mixed-replace;boundary=frame")

# cap = cv2.VideoCapture(0)
# outputFrame = None 
# lock = threading.Lock()
# timer_period = 3

# app = FastAPI()
# templates = Jinja2Templates(directory='templates')

# def timer_to_capture():
#     global cap, outputFrame, lock, timer_period
    
#     timer = Timer(period=timer_period)
#     while True:
#         _, frame = cap.read()
#         is_end_timer, current_time = timer.count()
#         if is_end_timer == False:
#             print('Finished couting timer')
#             break
#         cv2.putText(frame, 
#             str(current_time),
#             (0,0), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,255), 1)
#         with lock:
#             outputFrame = frame.copy()

# @app.get("/")
# def index():
#     return templates.TemplateResponse("index.html", context={'request': request})

# def generate():
#     global outputFrame, lock 
#     while True: 
#         with lock:
#             if outputFrame is None:
#                 continue 
#             (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
#             if not flag:
#                 continue 
#     yield (b'--frame\r\n' b'Content-Type: image/jpeg/\r\n\r\n' + bytearray(encodedImage) + b'\r\n') 

# @app.get("/video")
# def video_feed():
#     return StreamingResponse(generate(), media_type="multipart/x-mixed-replace;boundary=frame")

# if __name__ == '__main__':
#     t = threading.Thread(target=read_frame)
#     t.daemon = True 
#     t.start()

#     app.run(threaded=True)