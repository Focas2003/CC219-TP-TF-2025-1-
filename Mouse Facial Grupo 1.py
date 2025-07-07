import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import cv2
import threading
import time
import speech_recognition as sr
import pyttsx3
import numpy as np
import pyautogui
import mediapipe as mp

class GestureController:
    def __init__(self, text_logger, voice_callback, text_writer):
        self.text_logger = text_logger
        self.voice_callback = voice_callback
        self.text_writer = text_writer
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
        self.pose = mp.solutions.pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.gestures_calibrated = False
        self.frames_calibration = 0
        self.reset_calibration()
        self.sonrisa_inicio_tiempo = None
        self.sonrisa_activa = False
        self.scroll_cejas = 0
        self.scroll_fruncir = 0
        self.enter_lengua = 0
        self.last_left_click = 0
        self.last_right_click = 0
        self.last_blink = 0
        self.last_voice_toggle = 0

    def reset_calibration(self):
        self.hombro_izq_inicial = 0
        self.hombro_der_inicial = 0
        self.sonrisa_inicial = 0
        self.cabeza_inicial = {'x': 0, 'y': 0}
        self.suma_hombro_izq = 0
        self.suma_hombro_der = 0
        self.suma_sonrisa = 0
        self.suma_cabeza_x = 0
        self.suma_cabeza_y = 0

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_result = self.face_mesh.process(rgb)
        pose_result = self.pose.process(rgb)
        h, w, _ = frame.shape
        if face_result.multi_face_landmarks and pose_result.pose_landmarks:
            face_landmarks = face_result.multi_face_landmarks[0]
            pose_landmarks = pose_result.pose_landmarks

            nariz = face_landmarks.landmark[1]
            ojo_izq_sup = face_landmarks.landmark[159]
            ojo_izq_inf = face_landmarks.landmark[145]
            ojo_der_sup = face_landmarks.landmark[386]
            ojo_der_inf = face_landmarks.landmark[374]
            boca_izq = face_landmarks.landmark[61]
            boca_der = face_landmarks.landmark[291]
            labio_sup = face_landmarks.landmark[13]
            labio_inf = face_landmarks.landmark[14]
            entrecejo = face_landmarks.landmark[9]
            ceja_izq = face_landmarks.landmark[65]
            ceja_der = face_landmarks.landmark[295]
            hombro_izq = pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
            hombro_der = pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]

            if not self.gestures_calibrated:
                self.suma_hombro_izq += hombro_izq.y
                self.suma_hombro_der += hombro_der.y
                self.suma_sonrisa += abs(boca_der.x - boca_izq.x)
                self.suma_cabeza_x += nariz.x
                self.suma_cabeza_y += nariz.y
                self.frames_calibration += 1
                if self.frames_calibration >= 30:
                    self.hombro_izq_inicial = self.suma_hombro_izq / self.frames_calibration
                    self.hombro_der_inicial = self.suma_hombro_der / self.frames_calibration
                    self.sonrisa_inicial = self.suma_sonrisa / self.frames_calibration
                    self.cabeza_inicial = {
                        'x': self.suma_cabeza_x / self.frames_calibration,
                        'y': self.suma_cabeza_y / self.frames_calibration
                    }
                    self.gestures_calibrated = True
                    self.text_logger("[CALIBRADO] Gestos calibrados correctamente")
            else:
                # Parpadeo
                ojos_cerrados = abs(ojo_izq_sup.y - ojo_izq_inf.y) < 0.01 and abs(ojo_der_sup.y - ojo_der_inf.y) < 0.01
                if ojos_cerrados:
                    if not hasattr(self, 'ojo_cerrado_inicio'):
                        self.ojo_cerrado_inicio = time.time()
                    else:
                        duracion_cierre = time.time() - self.ojo_cerrado_inicio
                        if duracion_cierre > 3:
                            pyautogui.hotkey('ctrl', 'a')
                            pyautogui.press('backspace')
                            self.text_logger("[GESTO] Ojos cerrados 3s: texto borrado")
                            self.ojo_cerrado_inicio = time.time()  # reiniciar para evitar múltiples borrados
                        elif time.time() - self.last_blink > 1.5:
                            pyautogui.moveTo(pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)
                            self.text_logger("[GESTO] Parpadeo: Mouse centrado")
                            self.last_blink = time.time()
                else:
                    if hasattr(self, 'ojo_cerrado_inicio'):
                        del self.ojo_cerrado_inicio
                        pyautogui.moveTo(pyautogui.size()[0] // 2, pyautogui.size()[1] // 2)
                        self.text_logger("[GESTO] Parpadeo: Mouse centrado")
                        self.last_blink = time.time()

                # Hombro izquierdo levantado
                if self.hombro_izq_inicial - hombro_izq.y > 0.08:
                    if time.time() - self.last_left_click > 1.0:
                        pyautogui.click()
                        self.text_logger("[GESTO] Click izquierdo (hombro izquierdo)")
                        self.last_left_click = time.time()

                # Hombro derecho levantado
                if self.hombro_der_inicial - hombro_der.y > 0.08:
                    if time.time() - self.last_right_click > 1.0:
                        pyautogui.click(button='right')
                        self.text_logger("[GESTO] Click derecho (hombro derecho)")
                        self.last_right_click = time.time()

                # Sonrisa sostenida para activar/desactivar voz
                ancho_boca = abs(boca_der.x - boca_izq.x)
                if ancho_boca - self.sonrisa_inicial > 0.025:
                    if not self.sonrisa_activa:
                        self.sonrisa_inicio_tiempo = time.time()
                        self.sonrisa_activa = True
                    else:
                        duracion = time.time() - self.sonrisa_inicio_tiempo
                        if duracion > 3 and time.time() - self.last_voice_toggle > 2:
                            self.voice_callback(False)
                            self.sonrisa_activa = False
                            self.last_voice_toggle = time.time()
                            self.text_logger("[GESTO] Micrófono desactivado por sonrisa")
                        elif duracion > 2 and time.time() - self.last_voice_toggle > 2:
                            self.voice_callback(True)
                            self.last_voice_toggle = time.time()
                            self.text_logger("[GESTO] Micrófono activado por sonrisa")
                else:
                    self.sonrisa_activa = False

                # Movimiento de cabeza (control del mouse)
                dx = nariz.x - self.cabeza_inicial['x']
                dy = nariz.y - self.cabeza_inicial['y']
                if abs(dx) > 0.02 or abs(dy) > 0.02:
                    x, y = pyautogui.position()
                    new_x = x + int(dx * 1000)
                    new_y = y + int(dy * 1000)
                    pyautogui.moveTo(new_x, new_y)

                # Lengua (labios muy separados)
                if abs(labio_inf.y - labio_sup.y) > 0.05:
                    if time.time() - self.enter_lengua > 2:
                        pyautogui.press('enter')
                        self.text_logger("[GESTO] Lengua detectada: Enter")
                        self.enter_lengua = time.time()

                # Cejas levantadas (scroll arriba)
                if ceja_izq.y < entrecejo.y - 0.015 and ceja_der.y < entrecejo.y - 0.015:
                    if time.time() - self.scroll_cejas > 0.2:
                        pyautogui.scroll(100)
                        self.text_logger("[GESTO] Scroll arriba por cejas levantadas")
                        self.scroll_cejas = time.time()

                # Fruncir ceño (scroll abajo)
                if ceja_izq.y > entrecejo.y + 0.01 and ceja_der.y > entrecejo.y + 0.01:
                    if time.time() - self.scroll_fruncir > 0.2:
                        pyautogui.scroll(-100)
                        self.text_logger("[GESTO] Scroll abajo por ceño fruncido")
                        self.scroll_fruncir = time.time()

        return frame

class VoiceRecognizer:
    def __init__(self, text_logger, text_writer):
        self.text_logger = text_logger
        self.text_writer = text_writer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.listen, daemon=True).start()

    def stop(self):
        self.running = False

    def listen(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        self.text_logger("[MIC] Micrófono calibrado. Escuchando...")
        while self.running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio, language='es-ES')
                self.text_logger(f"[TEXTO] {text}")
                self.text_writer(text)
            except sr.WaitTimeoutError:
                self.text_logger("[TIMEOUT] Esperando...")
            except sr.UnknownValueError:
                self.text_logger("[ERROR] No se entendió el audio")
            except sr.RequestError as e:
                self.text_logger(f"[ERROR] Servicio no disponible: {e}")

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Control por gestos y voz")

        # Video
        self.video_label = tk.Label(root)
        self.video_label.pack(side="left", padx=10, pady=10)

        # Texto
        self.text_frame = tk.Frame(root, bg="white", width=300)
        self.text_frame.pack(side="right", fill="y")
        self.text_area = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, font=("Arial", 11))
        self.text_area.pack(expand=True, fill="both", padx=10, pady=10)

        # Botón
        self.toggle_btn = tk.Button(self.text_frame, text="🎤 Activar voz", command=self.toggle_voice)
        self.toggle_btn.pack(pady=5)

        # Componentes
        self.voice_recognizer = VoiceRecognizer(self.log_text, self.write_text)
        self.gesture_controller = GestureController(self.log_text, self.voice_toggle_from_gesture, self.write_text)
        self.cap = cv2.VideoCapture(0)
        self.running = True
        threading.Thread(target=self.update_video, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log_text(self, text):
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)

    def write_text(self, text):
        try:
            pyautogui.typewrite(text + ' ')
            self.log_text(f"[ESCRITO] {text}")
        except Exception as e:
            self.log_text(f"[ERROR al escribir] {e}")

    def toggle_voice(self):
        if self.voice_recognizer.running:
            self.voice_recognizer.stop()
            self.toggle_btn.config(text="🎤 Activar voz")
            self.log_text("🔇 Voz desactivada")
        else:
            self.voice_recognizer.start()
            self.toggle_btn.config(text="🔇 Desactivar voz")
            self.log_text("🔊 Voz activada")

    def voice_toggle_from_gesture(self, activate):
        if activate and not self.voice_recognizer.running:
            self.voice_recognizer.start()
            self.toggle_btn.config(text="🔇 Desactivar voz")
        elif not activate and self.voice_recognizer.running:
            self.voice_recognizer.stop()
            self.toggle_btn.config(text="🎤 Activar voz")

    def update_video(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            frame = self.gesture_controller.process(frame)
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            time.sleep(0.01)

    def on_close(self):
        self.running = False
        self.cap.release()
        self.voice_recognizer.stop()
        self.root.destroy()

if __name__ == "__main__":
    pyautogui.FAILSAFE = False
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()
