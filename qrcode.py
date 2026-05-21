import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading # roda a ia em paralelo
import time
import webbrowser
from urllib.parse import urlparse

class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Leitor de QR Code")
        self.root.geometry("1000x820")

        try:
            self.detector = cv2.wechat_qrcode_WeChatQRCode()
        except Exception:
            messagebox.showerror("Erro de Dependência", 
                                "Esta versão precisa do OpenCV Contrib.\n"
                                "pip install opencv-contrib-python --user")
            self.root.destroy()
            return

        self.cap = None
        self.webcam_running = False
        self.link_atual = None
        
        # --- Variáveis de Otimização (Velocidade) ---
        self.current_frame = None 
        self.data_detectada = "Nenhum" 
        self.pontos_detectados = None 
        self.processando_ia = False # flag para não sobrecarregar
        self.controle_fps_ia = 0 # tempo para controlar a frequência da IA

        # --- Interface Gráfica ---
        tk.Label(root, text="Detecção de QR Code", font=("Arial", 20, "bold")).pack(pady=15)
        self.panel = tk.Label(root, bg="black", bd=2, relief="groove")
        self.panel.pack(pady=10, padx=15, fill="both", expand=True)

        self.result_frame = tk.Frame(root)
        self.result_frame.pack(pady=10, padx=10, fill="x")
        self.result_frame.columnconfigure(0, weight=1)

        self.result_var = tk.StringVar(value="Conteúdo: Nenhum")
        self.label_result = tk.Label(self.result_frame, textvariable=self.result_var, font=("Arial", 13, "bold"), fg="darkblue", wraplength=760, justify="left", anchor="w")
        self.label_result.grid(row=0, column=0, sticky="ew")

        self.btn_abrir_link = tk.Button(self.result_frame, text="Abrir link", command=self.abrir_link, font=("Arial", 11), width=12)
        self.btn_abrir_link.grid(row=0, column=1, padx=(10, 0))
        self.btn_abrir_link.grid_remove()

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)
        
        self.btn_upload = tk.Button(btn_frame, text="Upload Imagem", command=self.upload_imagem, font=("Arial", 11), width=20)
        self.btn_upload.grid(row=0, column=0, padx=10)
        
        self.btn_webcam = tk.Button(btn_frame, text="Iniciar Webcam", command=self.toggle_webcam, font=("Arial", 11, "bold"), width=20, bg="#4CAF50", fg="white")
        self.btn_webcam.grid(row=0, column=1, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def thread_ia_detecao(self, frame_original):
        """Roda a IA pesada em uma Thread separada para não travar o vídeo"""
        self.processando_ia = True
        
        height, width = frame_original.shape[:2]
        escala = 640 / width
        frame_pequeno = cv2.resize(frame_original, None, fx=escala, fy=escala)
        
        data, points = self.detector.detectAndDecode(frame_pequeno)
        
        if not data or not any(data):
            gray = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2GRAY)
            enhanced_gray = cv2.equalizeHist(gray) 
            data, points = self.detector.detectAndDecode(enhanced_gray)

        # Processa os resultados
        if data:
            for i, conteudo in enumerate(data):
                if conteudo and len(conteudo.strip()) > 0:

                    self.data_detectada = conteudo.strip()
                    
                    if points is not None and i < len(points):
                        self.pontos_detectados = points[i] / escala
                    break 
        else:
            self.pontos_detectados = None

        self.processando_ia = False 

    def update_webcam(self):
        """Loop principal do vídeo (Roda a 30 FPS cravados)"""
        if self.webcam_running:
            ret, frame = self.cap.read()
            if ret:

                self.current_frame = frame.copy()
                
                # controla a frequência da ia (ex: roda a ia a cada 200ms = 5 vezes por segundo)
                tempo_atual = time.time()
                if not self.processando_ia and (tempo_atual - self.controle_fps_ia > 0.20):
                    self.controle_fps_ia = tempo_atual
                    # cria e inicia uma Thread para a ia
                    t = threading.Thread(target=self.thread_ia_detecao, args=(frame.copy(),))
                    t.daemon = True # Morre se o programa principal fechar
                    t.start()

                if self.pontos_detectados is not None:
                    pts = self.pontos_detectados.astype(np.int32)
                    cv2.polylines(self.current_frame, [pts], True, (0, 255, 0), 4)
                    self.atualizar_resultado(self.data_detectada)

                self.render_to_panel(self.current_frame)
                
                # agenda o próximo frame do VÍDEO rapidamente (10ms) para manter fluidez
                self.root.after(10, self.update_webcam)
            else:
                self.stop_webcam()

    # --- Funções Auxiliares (Renderização e Hardware) ---
    def extrair_link(self, conteudo):
        texto = conteudo.strip()
        url = urlparse(texto)
        if url.scheme in ("http", "https") and url.netloc:
            return texto

        if not url.scheme and texto.lower().startswith("www."):
            link = f"https://{texto}"
            if urlparse(link).netloc:
                return link

        return None

    def atualizar_resultado(self, conteudo):
        self.result_var.set(f"Conteúdo:\n{conteudo}")
        novo_link = self.extrair_link(conteudo)

        if novo_link == self.link_atual:
            return

        self.link_atual = novo_link
        if self.link_atual:
            self.btn_abrir_link.grid()
        else:
            self.btn_abrir_link.grid_remove()

    def abrir_link(self):
        if self.link_atual:
            webbrowser.open_new_tab(self.link_atual)

    def render_to_panel(self, frame):
        """Converte frame OpenCV para Tkinter mantendo proporção e velocidade"""
        cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(cv2_img)
        
        panel_width = self.panel.winfo_width()
        panel_height = self.panel.winfo_height()
        if panel_width > 10 and panel_height > 10:
            img_pil.thumbnail((panel_width - 10, panel_height - 10), Image.Resampling.NEAREST) # NEAREST é o mais rápido
            
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.panel.imgtk = img_tk
        self.panel.config(image=img_tk)

    def toggle_webcam(self):
        if not self.webcam_running:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            if not self.cap.isOpened():
                messagebox.showerror("Erro", "Webcam não encontrada.")
                return
            
            self.webcam_running = True
            self.btn_webcam.config(text="Parar Webcam", bg="#d32f2f")
            self.btn_upload.config(state="disabled")
            self.data_detectada = "Nenhum"
            self.update_webcam()
        else:
            self.stop_webcam()

    def upload_imagem(self):
        """Upload usa a IA diretamente, sem precisar de Thread"""
        self.stop_webcam()
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if caminho:
            img = cv2.imread(caminho)
            if img is not None:
                data, points = self.detector.detectAndDecode(img)
                if data and data[0]:
                    conteudo = data[0].strip()
                    self.atualizar_resultado(conteudo)
                    if points is not None:
                        pts = points[0].astype(np.int32)
                        cv2.polylines(img, [pts], True, (0, 255, 0), 4)
                else:
                    self.atualizar_resultado("Nenhum QR Code detectado.")
                self.render_to_panel(img)

    def stop_webcam(self):
        self.webcam_running = False
        if self.cap: self.cap.release()
        self.btn_webcam.config(text="Iniciar Webcam", bg="#4CAF50")
        self.btn_upload.config(state="normal")

    def on_close(self):
        self.stop_webcam()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()
