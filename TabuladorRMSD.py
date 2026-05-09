import sys
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView, QDialog, 
                             QLabel, QLineEdit, QFormLayout)
from PyQt5.QtCore import Qt

class AddComplexDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Definir Novo Complexo")
        self.resize(400, 200)
        
        self.complex_name = ""
        self.prot_path = ""
        self.lig_path = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Nome do Complexo
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Ex: ProteinaA_Ligante1")
        form_layout.addRow("Nome do Complexo:", self.input_name)

        # Seleção Proteína
        self.btn_prot = QPushButton("Selecionar arquivo (.xvg)")
        self.btn_prot.clicked.connect(self.select_prot)
        self.lbl_prot = QLabel("Nenhum arquivo selecionado")
        self.lbl_prot.setStyleSheet("color: gray; font-size: 10px;")
        
        prot_layout = QVBoxLayout()
        prot_layout.addWidget(self.btn_prot)
        prot_layout.addWidget(self.lbl_prot)
        form_layout.addRow("RMSD Proteína:", prot_layout)

        # Seleção Ligante
        self.btn_lig = QPushButton("Selecionar arquivo (.xvg)")
        self.btn_lig.clicked.connect(self.select_lig)
        self.lbl_lig = QLabel("Nenhum arquivo selecionado")
        self.lbl_lig.setStyleSheet("color: gray; font-size: 10px;")

        lig_layout = QVBoxLayout()
        lig_layout.addWidget(self.btn_lig)
        lig_layout.addWidget(self.lbl_lig)
        form_layout.addRow("RMSD Ligante:", lig_layout)

        layout.addLayout(form_layout)

        # Botões de Ação
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Adicionar à Tabela")
        self.btn_add.clicked.connect(self.accept_data)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_add)
        layout.addLayout(btn_layout)

    def select_prot(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar RMSD da Proteína", "", "XVG Files (*.xvg);;All Files (*)")
        if path:
            self.prot_path = path
            self.lbl_prot.setText(path.split('/')[-1])

    def select_lig(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar RMSD do Ligante", "", "XVG Files (*.xvg);;All Files (*)")
        if path:
            self.lig_path = path
            self.lbl_lig.setText(path.split('/')[-1])

    def accept_data(self):
        self.complex_name = self.input_name.text().strip()
        if not self.complex_name:
            QMessageBox.warning(self, "Aviso", "Por favor, insira o nome do complexo.")
            return
        if not self.prot_path or not self.lig_path:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione os arquivos da Proteína e do Ligante.")
            return
        self.accept()

class RMSDProcessor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analisador de RMSD por Complexo")
        self.resize(900, 500)
        
        self.processed_data = [] # Lista de dicionários para manter a ordem de inserção

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Botões
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Adicionar Complexo")
        self.btn_add.clicked.connect(self.add_complex)
        self.btn_add.setMinimumHeight(40)
        self.btn_add.setStyleSheet("font-weight: bold;")
        
        self.btn_export = QPushButton("Exportar Tabela (.csv)")
        self.btn_export.clicked.connect(self.export_table)
        self.btn_export.setMinimumHeight(40)
        self.btn_export.setEnabled(False)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_export)
        layout.addLayout(btn_layout)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Complexo", 
            "Média Prot. (nm)", 
            "Média Prot. (Å)", 
            "Média Lig. (nm)", 
            "Média Lig. (Å)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def calculate_mean(self, filepath):
        """Calcula a média do arquivo XVG com alto desempenho."""
        try:
            data = np.loadtxt(filepath, comments=['#', '@'])
            if data.ndim == 2 and data.shape[1] >= 2:
                return np.mean(data[:, 1])
            else:
                return np.mean(data)
        except Exception as e:
            QMessageBox.critical(self, "Erro de Leitura", f"Erro ao ler o arquivo {filepath}:\n{e}")
            return None

    def add_complex(self):
        dialog = AddComplexDialog(self)
        if dialog.exec_():
            # Pega os dados do formulário
            name = dialog.complex_name
            
            # Processa as médias
            prot_mean_nm = self.calculate_mean(dialog.prot_path)
            lig_mean_nm = self.calculate_mean(dialog.lig_path)
            
            if prot_mean_nm is None or lig_mean_nm is None:
                return # Falha na leitura, não insere

            # Armazena e atualiza
            self.processed_data.append({
                'Complexo': name,
                'Prot_nm': prot_mean_nm,
                'Lig_nm': lig_mean_nm
            })
            
            self.update_table()
            self.btn_export.setEnabled(True)

    def update_table(self):
        self.table.setRowCount(0)
        
        for row, data in enumerate(self.processed_data):
            self.table.insertRow(row)
            
            prot_nm = data['Prot_nm']
            lig_nm = data['Lig_nm']
            
            # Formatação
            str_prot_nm = f"{prot_nm:.3f}"
            str_prot_a = f"{prot_nm * 10:.3f}"
            str_lig_nm = f"{lig_nm:.3f}"
            str_lig_a = f"{lig_nm * 10:.3f}"

            # Inserção
            self.table.setItem(row, 0, QTableWidgetItem(data['Complexo']))
            
            for col, val in enumerate([str_prot_nm, str_prot_a, str_lig_nm, str_lig_a], start=1):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

    def export_table(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Tabela", "resultados_rmsd_12complexos.csv", "CSV Files (*.csv)")
        if not path:
            return

        export_list = []
        for d in self.processed_data:
            export_list.append({
                "Complexo": d['Complexo'],
                "Media_Proteina_nm": d['Prot_nm'],
                "Media_Proteina_Angstrons": d['Prot_nm'] * 10,
                "Media_Ligante_nm": d['Lig_nm'],
                "Media_Ligante_Angstrons": d['Lig_nm'] * 10
            })

        df = pd.DataFrame(export_list)
        
        try:
            df.to_csv(path, index=False, sep=';', decimal=',')
            QMessageBox.information(self, "Sucesso", "Dados exportados com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar o arquivo:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    window = RMSDProcessor()
    window.show()
    sys.exit(app.exec_())