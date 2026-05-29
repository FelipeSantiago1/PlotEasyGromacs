import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QLabel, QFileDialog, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from PIL import Image

class ImageConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.input_file = ""
        self.initUI()

    def initUI(self):
        # Configurações da Janela Principal
        self.setWindowTitle('Conversor Universal de Imagens')
        self.resize(400, 200)

        # Layout Vertical
        layout = QVBoxLayout()

        # Label para mostrar o arquivo selecionado
        self.lbl_info = QLabel('Nenhum arquivo selecionado')
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_info.setStyleSheet("font-size: 12px; color: #333; margin-bottom: 10px;")
        layout.addWidget(self.lbl_info)

        # Botão para selecionar a imagem
        self.btn_select = QPushButton('1. Selecionar Imagem')
        self.btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_select.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select)

        # Menu Dropdown para escolher o formato de saída
        self.combo_format = QComboBox()
        self.combo_format.addItems(['.tif', '.jpg', '.png', '.bmp', '.webp', '.pdf'])
        self.combo_format.setToolTip("Escolha o formato de destino")
        layout.addWidget(self.combo_format)

        # Botão para converter
        self.btn_convert = QPushButton('2. Converter e Salvar')
        self.btn_convert.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_convert.clicked.connect(self.convert_file)
        layout.addWidget(self.btn_convert)

        self.setLayout(layout)

    def select_file(self):
        # Abre o diálogo para selecionar qualquer imagem
        fname, _ = QFileDialog.getOpenFileName(
            self, 
            'Abrir Arquivo', 
            '', 
            'Imagens (*.png *.jpg *.jpeg *.gif *.bmp *.tif *.tiff *.webp)'
        )
        if fname:
            self.input_file = fname
            self.lbl_info.setText(f'Selecionado: {os.path.basename(self.input_file)}')

    def convert_file(self):
        if not self.input_file:
            QMessageBox.warning(self, 'Aviso', 'Por favor, selecione um arquivo primeiro.')
            return

        # Pega a extensão escolhida no ComboBox
        ext = self.combo_format.currentText()
        
        # Sugere um nome de arquivo para salvar no mesmo diretório original
        default_save_path = os.path.splitext(self.input_file)[0] + ext
        save_path, _ = QFileDialog.getSaveFileName(
            self, 
            'Salvar Como', 
            default_save_path, 
            f'Imagem (*{ext})'
        )

        if save_path:
            try:
                # Abre a imagem usando o Pillow
                img = Image.open(self.input_file)
                
                # Tratamento crucial para manter qualidade e evitar erros de formato:
                # GIFs e PNGs com transparência usam modo 'P' (Paleta) ou 'RGBA'.
                # O formato JPG não suporta transparência. Precisamos converter para RGB.
                if ext in ['.jpg', '.jpeg'] and img.mode in ['RGBA', 'P', 'LA']:
                    # Cria um fundo branco para substituir a transparência (se houver)
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[3]) # Usa o canal Alpha como máscara
                    else:
                        img = img.convert('RGB')
                        background = img
                    img = background
                
                # Para formatos sem perdas (lossless) como PNG e TIF, a qualidade original é mantida.
                # Para o JPG (que tem perdas), quality=100 força a mínima compressão possível.
                img.save(save_path, quality=100, optimize=False)
                
                QMessageBox.information(self, 'Sucesso', 'Imagem convertida com sucesso!')
                
            except Exception as e:
                QMessageBox.critical(self, 'Erro', f'Ocorreu um erro durante a conversão:\n{str(e)}')

if __name__ == '__main__':
    # Inicializa a aplicação
    app = QApplication(sys.argv)
    ex = ImageConverter()
    ex.show()
    sys.exit(app.exec())