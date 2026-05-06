import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Leitor de QR Code de Alta Precisão (WeChat Engine)")
        self.root.geometry("900x750")

       # pra coferir o erro de biblioteca
        try:
            self.detector = cv2.wechat_qrcode_WeChatQRCode()
        except Exception:
            messagebox.showerror("Erro", "Certifique-se de instalar: pip install opencv-contrib-python")
            self.root.destroy()

        self.cap = None
        self.webcam_running = False

        # Interface
        tk.Label(root, text="Leitor de QR Code Profissional", font=("Arial", 18, "bold")).pack(pady=10)
        self.panel = tk.Label(root, bg="black")
        self.panel.pack(pady=10, padx=10, fill="both", expand=True)

        self.result_var = tk.StringVar(value="Resultado: Nenhum")
        self.label_result = tk.Label(root, textvariable=self.result_var, font=("Arial", 12, "bold"), fg="darkgreen", wraplength=800)
        self.label_result.pack(pady=5)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Upload Imagem", command=self.upload_imagem, width=20, height=2).grid(row=0, column=0, padx=10)
        self.btn_webcam = tk.Button(btn_frame, text="Iniciar Webcam", command=self.toggle_webcam, width=20, height=2)
        self.btn_webcam.grid(row=0, column=1, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def process_frame(self, frame):
        # o WeChat retorna (conteúdo, pontos dos cantos)
        data, points = self.detector.detectAndDecode(frame)
        
        if data:
            # retorna uma lista de resultados
            conteudo = data[0] if isinstance(data, list) or isinstance(data, tuple) else data
            if conteudo:
                self.result_var.set(f"Resultado: {conteudo}")
                
                # desenha a marcação verde
                if points is not None:
                    for pts in points:
                        pts = pts.astype(np.int32)
                        for i in range(len(pts)):
                            cv2.line(frame, tuple(pts[i]), tuple(pts[(i+1) % len(pts)]), (0, 255, 0), 4)
        return frame

    def render_to_panel(self, frame):
        cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(cv2_img)
        img_pil.thumbnail((850, 550))
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.panel.imgtk = img_tk
        self.panel.config(image=img_tk)

    def upload_imagem(self):
        self.stop_webcam()
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp")])
        if caminho:
            img = cv2.imread(caminho)
            if img is not None:
                img_processada = self.process_frame(img)
                self.render_to_panel(img_processada)
            else:
                messagebox.showerror("Erro", "Arquivo inválido.")

    def toggle_webcam(self):
        if not self.webcam_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Erro", "Webcam não encontrada.")
                return
            self.webcam_running = True
            self.btn_webcam.config(text="Parar Webcam", bg="red", fg="white")
            self.update_webcam()
        else:
            self.stop_webcam()

    def update_webcam(self):
        if self.webcam_running:
            ret, frame = self.cap.read()
            if ret:
                frame_processado = self.process_frame(frame)
                self.render_to_panel(frame_processado)
                self.root.after(15, self.update_webcam)

    def stop_webcam(self):
        self.webcam_running = False
        if self.cap: self.cap.release()
        self.btn_webcam.config(text="Iniciar Webcam", bg="SystemButtonFace", fg="black")

    def on_close(self):
        self.stop_webcam()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()