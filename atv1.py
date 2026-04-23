import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton,
QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QImage, QPixmap

class App(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Mini Photoshop - Python")
        self.image = None
        self.label = QLabel("Carregue uma imagem")
        self.btn_load = QPushButton("Abrir Imagem")
        self.btn_gray = QPushButton("Escala de Cinza")
        self.btn_edge = QPushButton("Bordas")
        self.btn_load.clicked.connect(self.load_image)
        self.btn_gray.clicked.connect(self.to_gray)
        self.btn_edge.clicked.connect(self.edges)
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_load)
        layout.addWidget(self.btn_gray)
        layout.addWidget(self.btn_edge)
        
        self.setLayout(layout)

    def load_image(self):
        file, _ = QFileDialog.getOpenFileName()

        if file:
            self.image = cv2.imread(file)
            self.show_image(self.image)

    def to_gray(self):
        if self.image is not None:
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            self.show_image(gray)

    def edges(self):
        if self.image is not None:  
            edge = cv2.Canny(self.image, 100, 200)
            self.show_image(edge)

    def show_image(self, img):
        if len(img.shape) == 2:
            qformat = QImage.Format_Grayscale8
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            qformat = QImage.Format_RGB888
        
        h, w = img.shape[:2]
        qimg = QImage(img.data, w, h, img.strides[0], qformat)
        self.label.setPixmap(QPixmap.fromImage(qimg))
        
app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec_())