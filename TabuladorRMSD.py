import sys
import os
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QHeaderView, QDialog, 
                             QLabel, QLineEdit, QFormLayout, QAbstractItemView)
from PyQt5.QtCore import Qt

class ComplexDialog(QDialog):
    """Janela para Adicionar ou Editar um Complexo."""
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Complexo")
        self.resize(450, 250)
        
        self.prot_path = data['prot_path'] if data else ""
        self.lig_path = data['lig_path'] if data else ""
        
        self.init_ui(data)

    def init_ui(self, data):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.input_name = QLineEdit()
        self.input_name.setText(data['name'] if data else "")
        self.input_name.setPlaceholderText("Ex: Prot1_LigA")
        form.addRow("Nome do Complexo:", self.input_name)

        # Seleção Proteína
        self.btn_prot = QPushButton("Selecionar Arquivo Prot (.xvg)")
        self.btn_prot.clicked.connect(lambda: self.get_file('prot'))
        self.lbl_prot = QLabel(os.path.basename(self.prot_path) if self.prot_path else "Não selecionado")
        form.addRow("RMSD Proteína:", self.btn_prot)
        form.addRow("", self.lbl_prot)

        # Seleção Ligante
        self.btn_lig = QPushButton("Selecionar Arquivo Lig (.xvg)")
        self.btn_lig.clicked.connect(lambda: self.get_file('lig'))
        self.lbl_lig = QLabel(os.path.basename(self.lig_path) if self.lig_path else "Não selecionado")
        form.addRow("RMSD Ligante:", self.btn_lig)
        form.addRow("", self.lbl_lig)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btn_ok = QPushButton("Salvar")
        btn_ok.clicked.connect(self.validate_and_accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def get_file(self, mode):
        path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo XVG", "", "XVG (*.xvg)")
        if path:
            if mode == 'prot':
                self.prot_path = path
                self.lbl_prot.setText(os.path.basename(path))
            else:
                self.lig_path = path
                self.lbl_lig.setText(os.path.basename(path))

    def validate_and_accept(self):
        if not self.input_name.text().strip() or not self.prot_path or not self.lig_path:
            QMessageBox.warning(self, "Erro", "Preencha o nome e selecione ambos os arquivos.")
            return
        self.accept()

class RMSDAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BioTools - Analisador de RMSD Avançado")
        self.resize(1100, 600)
        self.complexes = [] # Armazena dicts com dados brutos e calculados

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Barra de Ferramentas
        top_bar = QHBoxLayout()
        self.btn_add = QPushButton("➕ Novo Complexo")
        self.btn_add.clicked.connect(self.add_complex)
        
        self.btn_edit = QPushButton("📝 Editar Selecionado")
        self.btn_edit.clicked.connect(self.edit_complex)
        
        self.btn_del = QPushButton("🗑️ Excluir")
        self.btn_del.clicked.connect(self.delete_complex)
        
        self.btn_export = QPushButton("💾 Exportar CSV")
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_export.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")

        for btn in [self.btn_add, self.btn_edit, self.btn_del, self.btn_export]:
            top_bar.addWidget(btn)
        
        layout.addLayout(top_bar)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Complexo", 
            "Média Prot (nm)", "Desvio Prot (nm)", "Média Prot (Å)", "Desvio Prot (Å)",
            "Média Lig (nm)", "Desvio Lig (nm)", "Média Lig (Å)", "Desvio Lig (Å)"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def calculate_stats(self, path):
        """Calcula média e desvio padrão usando Numpy."""
        try:
            data = np.loadtxt(path, comments=['#', '@'])
            values = data[:, 1] if data.ndim == 2 else data
            return np.mean(values), np.std(values)
        except:
            return None, None

    def add_complex(self):
        dialog = ComplexDialog(self)
        if dialog.exec_():
            self.process_entry(dialog.input_name.text(), dialog.prot_path, dialog.lig_path)

    def edit_complex(self):
        idx = self.table.currentRow()
        if idx < 0:
            return QMessageBox.information(self, "Aviso", "Selecione uma linha para editar.")
        
        current_data = self.complexes[idx]
        dialog = ComplexDialog(self, {
            'name': current_data['name'],
            'prot_path': current_data['prot_path'],
            'lig_path': current_data['lig_path']
        })
        
        if dialog.exec_():
            # Remove a antiga e insere a nova no mesmo lugar
            del self.complexes[idx]
            self.process_entry(dialog.input_name.text(), dialog.prot_path, dialog.lig_path, position=idx)

    def delete_complex(self):
        idx = self.table.currentRow()
        if idx >= 0:
            confirm = QMessageBox.question(self, "Confirmar", "Deseja excluir este complexo?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                del self.complexes[idx]
                self.refresh_table()

    def process_entry(self, name, p_path, l_path, position=None):
        p_mean, p_std = self.calculate_stats(p_path)
        l_mean, l_std = self.calculate_stats(l_path)
        
        entry = {
            'name': name, 'prot_path': p_path, 'lig_path': l_path,
            'p_mean': p_mean, 'p_std': p_std,
            'l_mean': l_mean, 'l_std': l_std
        }
        
        if position is not None:
            self.complexes.insert(position, entry)
        else:
            self.complexes.append(entry)
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        for i, c in enumerate(self.complexes):
            self.table.insertRow(i)
            
            # Dados formatados
            vals = [
                c['name'],
                f"{c['p_mean']:.4f}", f"{c['p_std']:.4f}", f"{c['p_mean']*10:.4f}", f"{c['p_std']*10:.4f}",
                f"{c['l_mean']:.4f}", f"{c['l_std']:.4f}", f"{c['l_mean']*10:.4f}", f"{c['l_std']*10:.4f}"
            ]
            
            for col, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, col, item)

    def export_csv(self):
        if not self.complexes: return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Dados", "rmsd_final.csv", "CSV (*.csv)")
        if path:
            df = pd.DataFrame([{
                'Complexo': c['name'],
                'Prot_Media_nm': c['p_mean'], 'Prot_Desvio_nm': c['p_std'],
                'Prot_Media_Ang': c['p_mean']*10, 'Prot_Desvio_Ang': c['p_std']*10,
                'Lig_Media_nm': c['l_mean'], 'Lig_Desvio_nm': c['l_std'],
                'Lig_Media_Ang': c['l_mean']*10, 'Lig_Desvio_Ang': c['l_std']*10
            } for c in self.complexes])
            df.to_csv(path, index=False, sep=';', decimal=',')
            QMessageBox.information(self, "Sucesso", "Arquivo exportado!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RMSDAnalyzer()
    win.show()
    sys.exit(app.exec_())