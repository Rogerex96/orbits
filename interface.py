
from space import (load_orbits, load_satellites,save_orbits, save_satellites,update_all_positions, Space)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget,QVBoxLayout, QLabel, QPushButton, QHBoxLayout,QFileDialog, QMessageBox)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot(space, ax):
    # Dibuixa la Terra
    terra = patches.Circle((0, 0), 6371, color='lightblue', label='Terra')
    ax.add_patch(terra)
    # Dibuixa les òrbites
    for orbit in space.orbits:
        x0 = -orbit.a * orbit.epsilon
        ellipse = patches.Ellipse((x0, 0), 2*orbit.a, 2*orbit.b,fill=False, linestyle='--', label=orbit.name)
        ax.add_patch(ellipse)
    
    # Dibuixa els satèl·lits
    for sat in space.satellites:
        x, y = sat.orbit.x, sat.orbit.y
        ax.plot(x, y, 'ro')
        ax.text(x+300, y+300, sat.name, fontsize=8)
    ax.set_aspect('equal')
    ax.set_xlabel("X (km)")
    ax.set_ylabel("Y (km)")
    ax.set_title("Òrbites i satèl·lits al voltant de la Terra")
    ax.legend(loc='upper right')
    ax.grid(True)

def load_orbits_only(space, ax, canvas):
    fname, _ = QFileDialog.getOpenFileName(None, "Selecciona fitxer d'òrbites", "", "Text Files (*.txt);;All Files (*)")
    if not fname:
        return
    
    load_orbits(space, fname)
    update_all_positions(space, 0)
    ax.clear()
    plot(space, ax)
    canvas.draw()

def load_sats_only(space, ax, canvas):
    fname, _ = QFileDialog.getOpenFileName(None, "Selecciona fitxer de satèl·lits", "", "Text Files (*.txt);;All Files (*)")
    if not fname:
        return
    
    load_satellites(space, fname)
    update_all_positions(space, 0)
    ax.clear()
    plot(space, ax)
    canvas.draw()

def save_orbits_only(space):
    fname, _ = QFileDialog.getSaveFileName(None, "Guardar òrbites com", "", "Text Files (*.txt);;All Files (*)")
    if not fname:
        return
    save_orbits(space, fname)
    QMessageBox.information(None, "Guardar dades", "Òrbites desades correctament.")

def save_sats_only(space):
    fname, _ = QFileDialog.getSaveFileName(
        None, "Guardar satèl·lits com", "", "Text Files (*.txt);;All Files (*)")
    if not fname:
        return
    
    save_satellites(space, fname)
    QMessageBox.information(None, "Guardar dades", "Satèl·lits desats correctament.")

class OrbitViewer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def refresh(self, space, time=0):
        update_all_positions(space, time)
        self.ax.clear()
        plot(space, self.ax)
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador Orbital")
        self.resize(1200, 800)

        # Espai orbital
        self.space = Space()

        # Contenidor de pestanyes
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # --- Pestanya Configuració ---
        cfg_tab = QWidget()
        vbox = QVBoxLayout(cfg_tab)
        vbox.addWidget(QLabel("Carregar / Desar dades:"))

        hbox = QHBoxLayout()
        # Botons de carregar
        self.btn_load_orbits = QPushButton("Carregar òrbites")
        self.btn_load_sats   = QPushButton("Carregar satèl·lits")
        # Botons de desar
        self.btn_save_orbits = QPushButton("Desar òrbites")
        self.btn_save_sats   = QPushButton("Desar satèl·lits")

        for btn in (self.btn_load_orbits, self.btn_load_sats,
                    self.btn_save_orbits, self.btn_save_sats):
            hbox.addWidget(btn)
        vbox.addLayout(hbox)

        tabs.addTab(cfg_tab, "Configuració")

        # --- Pestanya Visualització ---
        self.viewer = OrbitViewer()
        tabs.addTab(self.viewer, "Visualització")

        # Connexions
        self.btn_load_orbits.clicked.connect(lambda: load_orbits_only(self.space, self.viewer.ax, self.viewer.canvas))
        self.btn_load_sats.clicked.connect(lambda: load_sats_only(self.space, self.viewer.ax, self.viewer.canvas))
        self.btn_save_orbits.clicked.connect(lambda: save_orbits_only(self.space))
        self.btn_save_sats.clicked.connect(lambda: save_sats_only(self.space))

        # Actualitza gràfic inicial (sense dades)
        self.viewer.refresh(self.space)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
