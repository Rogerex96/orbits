from space import (load_orbits, load_satellites,save_orbits, save_satellites,update_all_positions, Space, get_orbit)
from orbit import Orbit
from satellite import Satellite
from PySide6.QtWidgets import (QApplication, QSlider, QMainWindow, QWidget, QFrame, QTabWidget,QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,QPushButton, QFileDialog, QMessageBox,QGroupBox, QFormLayout, QLineEdit)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation

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

class OrbitViewer(QWidget):
    def __init__(self):
        super().__init__()

        # ── Layout principal: 3 columnes ────────────────────────────────
        layout = QHBoxLayout(self)
        left_container   = QWidget(self)
        left_layout      = QGridLayout(left_container)
        center_layout    = QVBoxLayout()
        right_layout     = QVBoxLayout()

        # ── Canvas de la simulació ─────────────────────────────────────
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        # ── Frame del timer ─────────────────────────────────────────────
        timer_frame = QFrame(self)
        timer_frame.setFrameShape(QFrame.StyledPanel)
        timer_frame.setStyleSheet("QFrame { background: #222; border-radius: 6px; }")
        tf_layout = QVBoxLayout(timer_frame)
        tf_layout.setContentsMargins(8, 8, 8, 8)
        self.time = 0
        self.time_label = QLabel("Temps: 0 s", self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font: bold 14px; color: #fff;")
        tf_layout.addWidget(self.time_label)

        # ── Frame de l’accelerador ──────────────────────────────────────
        acc_frame = QFrame(self)
        acc_frame.setFrameShape(QFrame.StyledPanel)
        acc_frame.setStyleSheet("QFrame { background: #333; border-radius: 6px; }")
        af_layout = QVBoxLayout(acc_frame)
        af_layout.setContentsMargins(8, 8, 8, 8)
        self.speed = 1
        self.speed_label = QLabel("x1", self)
        self.speed_label.setAlignment(Qt.AlignCenter)
        self.speed_label.setStyleSheet("font: 13px; color: #ddd;")
        af_layout.addWidget(self.speed_label)
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setRange(0, 3)      # 0→x1, 1→x2, 2→x4, 3→x8
        self.speed_slider.setValue(0)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 6px; background: #555; border-radius: 3px; }
            QSlider::handle:horizontal { width: 14px; background: #ff5722; border-radius: 7px; margin: -4px 0; }
        """)
        self.speed_slider.valueChanged.connect(self._on_speed_change)
        af_layout.addWidget(self.speed_slider)

        # ── Posa timer i accelerador en una quadrícula (un sota l’altre) ──
        left_layout.addWidget(timer_frame, 0, 0)
        left_layout.addWidget(acc_frame,   1, 0)
        left_layout.setRowStretch(2, 1)  # empenta l’espai restant cap avall

        # ── Columna central amb el plot ─────────────────────────────────
        center_layout.addWidget(self.canvas, stretch=1)

        # ── Afegeix columnes al layout principal ────────────────────────
        layout.addWidget(left_container,   0)
        layout.addLayout(center_layout,    1)
        layout.addLayout(right_layout,     0)

        # ── Configura el temporitzador (s’iniciarà en carregar dades) ─
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)

        # ── Animació d’aparició del slider ─────────────────────────────
        anim = QPropertyAnimation(acc_frame, b"windowOpacity", self)
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()

    def _on_speed_change(self, val: int):
        self.speed = 2 ** val
        self.speed_label.setText(f"x{self.speed}")

    def refresh(self, space, t=0):
        update_all_positions(space, t)
        self.ax.clear()
        plot(space, self.ax)
        self.canvas.draw()

    def _update_time(self):
        self.time += self.speed
        self.time_label.setText(f"Temps: {self.time} s")
        if hasattr(self, 'space'):
            self.refresh(self.space, self.time)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oorbit")
        self.resize(1200, 800)
        
        # Espai orbital
        self.space = Space()

        # Pestanyes
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # --- Pestanya Configuració ---
        cfg_tab = QWidget()
        cfg_layout = QHBoxLayout(cfg_tab)

        # Placeholder esquerre
        left_placeholder = QLabel("")
        cfg_layout.addWidget(left_placeholder, 1)

        # Panell dret amb grid 3×2
        right_panel = QWidget()
        grid = QGridLayout(right_panel)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(15)

        # 1) Unic botó: Carregar dades (òrbitas + satèl·lits)
        self.btn_load_data = QPushButton("Carregar dades")
        grid.addWidget(self.btn_load_data, 0, 0, 1, 2)

        # 2 & 3) Botons de desar
        self.btn_save_orbits = QPushButton("Desar òrbites")
        self.btn_save_sats = QPushButton("Desar satèl·lits")
        grid.addWidget(self.btn_save_orbits, 1, 0)
        grid.addWidget(self.btn_save_sats,   1, 1)

        # 4) Formularis agrupats (spanning 2 columnes)
        forms_container = QWidget()
        forms_layout = QVBoxLayout(forms_container)
        forms_layout.setSpacing(20)

        # 4a) Formulari nou òrbita
        orbit_box = QGroupBox("Nou Òrbita")
        form_orbit = QFormLayout(orbit_box)
        self.orbit_name_edit    = QLineEdit()
        self.orbit_period_edit  = QLineEdit()
        self.orbit_epsilon_edit = QLineEdit()
        self.orbit_a_edit       = QLineEdit()
        form_orbit.addRow("Nom",       self.orbit_name_edit)
        form_orbit.addRow("Període",   self.orbit_period_edit)
        form_orbit.addRow("Epsilon",   self.orbit_epsilon_edit)
        form_orbit.addRow("Semi-eix",  self.orbit_a_edit)
        self.add_orbit_btn = QPushButton("Afegeix Òrbita")
        form_orbit.addWidget(self.add_orbit_btn)
        forms_layout.addWidget(orbit_box)

        # 4b) Formulari nou satèl·lit
        sat_box = QGroupBox("Nou Satèl·lit")
        form_sat = QFormLayout(sat_box)
        self.sat_name_edit       = QLineEdit()
        self.sat_orbitname_edit  = QLineEdit()
        self.sat_mass_edit       = QLineEdit()
        self.sat_fuel_edit       = QLineEdit()
        form_sat.addRow("Nom",    self.sat_name_edit)
        form_sat.addRow("Òrbita", self.sat_orbitname_edit)
        form_sat.addRow("Massa",  self.sat_mass_edit)
        form_sat.addRow("Fuel",   self.sat_fuel_edit)
        self.add_sat_btn = QPushButton("Afegeix Satèl·lit")
        form_sat.addWidget(self.add_sat_btn)
        forms_layout.addWidget(sat_box)

        grid.addWidget(forms_container, 2, 0, 1, 2)

        cfg_layout.addWidget(right_panel, 0)
        tabs.addTab(cfg_tab, "Configuració")

        # --- Pestanya Visualització ---
        self.viewer = OrbitViewer()
        self.viewer.space = self.space
        tabs.addTab(self.viewer, "Visualització")

        # Connexions
        self.btn_load_data.clicked.connect(self._load_both)
        self.btn_save_orbits.clicked.connect(self._save_orbits)
        self.btn_save_sats.clicked.connect(self._save_sats)
        self.add_orbit_btn.clicked.connect(self._add_orbit)
        self.add_sat_btn.clicked.connect(self._add_sat)

        # Dibuix inicial
        self.viewer.refresh(self.space)

    def _load_both(self):
        # 1) Fitxer d'òrbites
        orbit_file, _ = QFileDialog.getOpenFileName(self, "Selecciona fitxer d'òrbites", "", "Text Files (*.txt);;All Files (*)")
        if not orbit_file:
            return
        # 2) Fitxer de satèl·lits
        sat_file, _ = QFileDialog.getOpenFileName(self, "Selecciona fitxer de satèl·lits", "", "Text Files (*.txt);;All Files (*)")
        if not sat_file:
            return

        load_orbits(self.space, orbit_file)
        load_satellites(self.space, sat_file)
        update_all_positions(self.space, 0)
        self.viewer.refresh(self.space)
        self.viewer.time = 0
        self.viewer.time_label.setText("Temps: 0 s")
        self.viewer.timer.start(1000)

    def _save_orbits(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Desar òrbites", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            save_orbits(self.space, fname)
            QMessageBox.information(self, "✔", "Òrbites desades.")

    def _save_sats(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Desar satèl·lits", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            save_satellites(self.space, fname)
            QMessageBox.information(self, "✔", "Satèl·lits desats.")

    def _add_orbit(self):
        try:
            orbit = Orbit(self.orbit_name_edit.text().strip(),float(self.orbit_period_edit.text()),float(self.orbit_epsilon_edit.text()),float(self.orbit_a_edit.text()))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Dades d'òrbita no vàlides.\n{e}")
            return
        self.space.orbits.append(orbit)
        self.viewer.refresh(self.space)
        QMessageBox.information(self, "✔", f"Òrbita «{orbit.name}» afegida.")

    def _add_sat(self):
        name      = self.sat_name_edit.text().strip()
        orbitname = self.sat_orbitname_edit.text().strip()
        orbit     = get_orbit(self.space, orbitname)
        if not orbit:
            QMessageBox.warning(self, "Error", f"Òrbita «{orbitname}» no trobada.")
            return
        try:
            sat = Satellite(name,orbit,float(self.sat_mass_edit.text()),float(self.sat_fuel_edit.text()))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Dades de satèl·lit no vàlides.\n{e}")
            return
        self.space.satellites.append(sat)
        self.viewer.refresh(self.space)
        QMessageBox.information(self, "✔", f"Satèl·lit «{sat.name}» afegit.")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
