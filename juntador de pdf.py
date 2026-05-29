import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QFileDialog, QMessageBox, 
                             QAbstractItemView)
from pypdf import PdfWriter

class MescladorPDFApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Configurações da Janela Principal
        self.setWindowTitle('Mesclador de PDFs')
        self.resize(600, 400)

        # Layout Principal
        layout_principal = QVBoxLayout()

        # Lista de Arquivos (Com suporte a Drag and Drop para reordenar)
        self.lista_arquivos = QListWidget()
        self.lista_arquivos.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.lista_arquivos.setDragDropMode(QAbstractItemView.InternalMove)
        self.lista_arquivos.setToolTip("Arraste e solte os itens para reordená-los.")
        layout_principal.addWidget(self.lista_arquivos)

        # Layout dos Botões
        layout_botoes = QHBoxLayout()

        self.btn_adicionar = QPushButton('Adicionar PDFs')
        self.btn_remover = QPushButton('Remover Selecionado')
        self.btn_limpar = QPushButton('Limpar Lista')
        self.btn_mesclar = QPushButton('Juntar PDFs')

        layout_botoes.addWidget(self.btn_adicionar)
        layout_botoes.addWidget(self.btn_remover)
        layout_botoes.addWidget(self.btn_limpar)
        layout_botoes.addWidget(self.btn_mesclar)

        layout_principal.addLayout(layout_botoes)
        self.setLayout(layout_principal)

        # Conectando os sinais aos slots
        self.btn_adicionar.clicked.connect(self.adicionar_pdfs)
        self.btn_remover.clicked.connect(self.remover_pdf)
        self.btn_limpar.clicked.connect(self.lista_arquivos.clear)
        self.btn_mesclar.clicked.connect(self.mesclar_pdfs)

    def adicionar_pdfs(self):
        arquivos, _ = QFileDialog.getOpenFileNames(
            self, 
            "Selecionar PDFs", 
            "", 
            "Arquivos PDF (*.pdf)"
        )
        if arquivos:
            self.lista_arquivos.addItems(arquivos)

    def remover_pdf(self):
        # Remove os itens selecionados (precisa ser de trás para frente para não alterar os índices)
        itens_selecionados = self.lista_arquivos.selectedItems()
        if not itens_selecionados:
            return
            
        for item in itens_selecionados:
            linha = self.lista_arquivos.row(item)
            self.lista_arquivos.takeItem(linha)

    def mesclar_pdfs(self):
        total_arquivos = self.lista_arquivos.count()
        
        if total_arquivos < 2:
            QMessageBox.warning(self, "Aviso", "Adicione pelo menos dois arquivos PDF para mesclar.")
            return

        # Abre o diálogo para escolher onde salvar o novo arquivo
        caminho_salvar, _ = QFileDialog.getSaveFileName(
            self, 
            "Salvar PDF Mesclado", 
            "documento_mesclado.pdf", 
            "Arquivos PDF (*.pdf)"
        )
        
        if not caminho_salvar:
            return

        escritor_pdf = PdfWriter()

        try:
            # Itera sobre a lista na ordem exata em que o usuário deixou
            for indice in range(total_arquivos):
                caminho_arquivo = self.lista_arquivos.item(indice).text()
                escritor_pdf.append(caminho_arquivo)

            # Escreve o arquivo final no disco
            with open(caminho_salvar, "wb") as arquivo_saida:
                escritor_pdf.write(arquivo_saida)
            
            QMessageBox.information(self, "Sucesso", "Os arquivos PDF foram mesclados com sucesso!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao mesclar os arquivos:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Aplica um estilo básico para melhorar a aparência em sistemas Linux/GTK
    app.setStyle("Fusion") 
    
    janela = MescladorPDFApp()
    janela.show()
    sys.exit(app.exec_())
    