# 🚀 Leitor de QR Code Veloz & Otimizado

Uma aplicação desktop em Python desenvolvida para leitura de QR Codes em altíssima performance utilizando a webcam ou via upload de arquivos locais. O projeto combina uma interface gráfica fluida com o poderoso motor de Visão Computacional do WeChat integrado ao OpenCV.

---

## 🎯 Diferenciais do Projeto

*   **Paralelismo Assíncrono (`Multi-threading`):** A IA pesada roda em uma thread secundária de forma independente. O feed de vídeo da webcam permanece cravado e fluido a 30 FPS.
*   **Frequência Controlada (`Throttling` a 5Hz):** A imagem da câmera atualiza a cada 10ms, mas a IA só é acionada a cada 200ms. Isso evita o uso desnecessário de 100% da CPU.
*   **Filtro Fallback (Aumento de Contraste):** Caso o QR Code esteja em um ambiente escuro ou com sombras, o código automaticamente converte o frame para tons de cinza e aplica uma equalização de histograma (`cv2.equalizeHist`) para tentar uma segunda leitura bem-sucedida.
*   **Redimensionamento Dinâmico (Downscaling):** A imagem é reduzida para 640px de largura antes de ser enviada para a IA, acelerando o tempo de processamento drasticamente.

---

## 🛠️ Tecnologias e Ferramentas

| Biblioteca / Módulo | Função no Projeto | Motivo da Escolha |
| :--- | :--- | :--- |
| **OpenCV (`cv2`)** | Captura de vídeo e Visão Computacional | Padrão da indústria. Usa o módulo `WeChatQRCode` (baseado em redes neurais) para ler códigos danificados, borrados ou distorcidos. |
| **NumPy (`np`)** | Álgebra linear e matrizes | Essencial para manipular as coordenadas geográficas dos cantos do QR Code e desenhar o polígono verde de detecção. |
| **Tkinter (`tk`)** | Interface Gráfica (GUI) | Biblioteca nativa do Python, extremamente leve e ideal para aplicações desktop rápidas. |
| **Pillow (`PIL`)** | Processamento de imagem | Atua como a "ponte" de conversão, transformando matrizes BGR do OpenCV em formatos visuais que o Tkinter consegue renderizar. |
| **Threading** | Multi-processamento | Garante que o processamento pesado de IA não congele a interface visual do usuário. |
| **Webbrowser & Urllib** | Filtro e manipulação de URLs | Valida se o conteúdo detectado é um site seguro e gerencia a abertura automática no navegador padrão. |

---

## ⚙️ Pré-requisitos & Instalação

Este projeto requer o módulo **Contrib** do OpenCV, que contém o algoritmo avançado de detecção do WeChat. Se você tiver apenas a versão padrão do OpenCV instalada, o programa não funcionará.

1. Clone o repositório ou baixe o arquivo do código:
   
```bash
   git clone [https://github.com/ibqrz/identificador-QRcode.git](https://github.com/ibqrz/identificador-QRcode.git)
   cd identificador-qrcode
```

2. Instale as dependências necessárias executando o comando abaixo no seu terminal:

```bash
   pip install opencv-contrib-python pillow numpy --user
```

💻 Como Executar

Com as dependências instaladas, basta iniciar o script principal do Python:

```bash
python qrcode.py
```

Como usar a aplicação:
Via Webcam: Clique em "Iniciar Webcam". Aponte um QR Code para a câmera. O sistema detectará o código, desenhará um retângulo verde ao redor dele e exibirá o conteúdo. Se for um link, um botão "Abrir link" surgirá na tela.

Via Arquivo: Clique em "Upload Imagem", selecione uma foto contendo um QR Code de seu computador (.jpg, .jpeg, .png) e o sistema fará a leitura instantânea.

🔍 Entendendo a Arquitetura do Código
O fluxo interno do sistema funciona de maneira cíclica e segura:

```bash
[Webcam gera Frame] ──> Envia para Tela (Rápido: 10ms)
       │
       └──> Se passou 200ms? ──> [Dispara Thread Separada]
                                        │
                                        └──> Reduz Imagem para 640px
                                        └──> Roda IA do WeChat
                                        └──> Se falhar, melhora contraste e tenta de novo
                                        └──> Retorna coordenadas e texto para a Tela Principal
```

⚠️ Fechamento Seguro: O aplicativo intercepta o fechamento da janela (WM_DELETE_WINDOW) para garantir que o hardware da webcam seja liberado da memória (self.cap.release()) antes de encerrar o programa, evitando bugs de câmera travada no sistema operacional.