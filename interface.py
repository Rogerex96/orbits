from space import (load_orbits, load_satellites,save_orbits, save_satellites,update_all_positions, Space, get_orbit)
from orbit import Orbit
from satellite import Satellite, change_orbit
from PySide6.QtWidgets import (QApplication, QSlider, QComboBox, QMainWindow, QWidget, QFrame, QTabWidget,QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,QPushButton, QFileDialog, QMessageBox,QGroupBox, QFormLayout, QLineEdit)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
import math

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

        layout = QHBoxLayout(self)
        left_container   = QWidget(self)
        left_layout      = QGridLayout(left_container)
        center_layout    = QVBoxLayout()
        right_layout     = QVBoxLayout()

        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)

        #Timer
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

        #Accelerador
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
        self.speed_slider.setRange(0, 3)
        self.speed_slider.setValue(0)
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.setStyleSheet("""QSlider::groove:horizontal { height: 6px; background: #555; border-radius: 3px; }QSlider::handle:horizontal { width: 14px; background: #ff5722; border-radius: 7px; margin: -4px 0; }""")
        self.speed_slider.valueChanged.connect(self._on_speed_change)
        af_layout.addWidget(self.speed_slider)

        left_layout.addWidget(timer_frame, 0, 0)
        left_layout.addWidget(acc_frame,   1, 0)
        left_layout.setRowStretch(2, 1)

        center_layout.addWidget(self.canvas, stretch=1)

        layout.addWidget(left_container,   0)
        layout.addLayout(center_layout,    1)
        layout.addLayout(right_layout,     0)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_time)

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
        
        self.space = Space()

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        cfg_tab = QWidget()
        cfg_layout = QHBoxLayout(cfg_tab)

        left_placeholder = QLabel("")
        cfg_layout.addWidget(left_placeholder, 1)

        right_panel = QWidget()
        grid = QGridLayout(right_panel)
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(15)

        self.btn_load_data = QPushButton("Carregar dades")
        grid.addWidget(self.btn_load_data, 0, 0, 1, 2)

        self.btn_save_orbits = QPushButton("Desar òrbites")
        self.btn_save_sats = QPushButton("Desar satèl·lits")
        grid.addWidget(self.btn_save_orbits, 1, 0)
        grid.addWidget(self.btn_save_sats,   1, 1)

        change_box = QGroupBox("Canvi d'òrbita")
        form_co = QFormLayout(change_box)

        self.co_sat_combo = QComboBox()
        self.co_dest_combo = QComboBox()
        self.co_change_btn = QPushButton("Canvia")

        form_co.addRow("Satèl·lit", self.co_sat_combo)
        self.co_period_edit = QLineEdit(); self.co_period_edit.setReadOnly(True)
        self.co_eps_edit = QLineEdit(); self.co_eps_edit.setReadOnly(True)
        self.co_a_edit = QLineEdit(); self.co_a_edit.setReadOnly(True)
        form_co.addRow("Òrbita destí", self.co_dest_combo)
        form_co.addRow("Període", self.co_period_edit)
        form_co.addRow("Epsilon", self.co_eps_edit)
        form_co.addRow("Semi-eix", self.co_a_edit)
        self.co_dv_edit = QLineEdit(); self.co_dv_edit.setReadOnly(True)
        form_co.addRow("Δv (m/s)", self.co_dv_edit)
        self.co_dv_avail_edit = QLineEdit(); self.co_dv_avail_edit.setReadOnly(True)
        form_co.addRow("Δv disponible", self.co_dv_avail_edit)
        form_co.addRow(self.co_change_btn)

        forms_container = QWidget()
        forms_layout = QVBoxLayout(forms_container)
        forms_layout.setSpacing(20)

        orbit_box = QGroupBox("Nova Òrbita")
        form_orbit = QFormLayout(orbit_box)
        self.orbit_name_edit = QLineEdit()
        self.orbit_period_edit = QLineEdit()
        self.orbit_epsilon_edit = QLineEdit()
        self.orbit_a_edit = QLineEdit()
        form_orbit.addRow("Nom", self.orbit_name_edit)
        form_orbit.addRow("Període", self.orbit_period_edit)
        form_orbit.addRow("Epsilon", self.orbit_epsilon_edit)
        form_orbit.addRow("Semi-eix", self.orbit_a_edit)
        self.add_orbit_btn = QPushButton("Afegeix Òrbita")
        form_orbit.addWidget(self.add_orbit_btn)
        forms_layout.addWidget(orbit_box)

        sat_box = QGroupBox("Nou Satèl·lit")
        form_sat = QFormLayout(sat_box)
        self.sat_name_edit = QLineEdit()
        self.sat_orbitname_edit = QLineEdit()
        self.sat_mass_edit = QLineEdit()
        self.sat_fuel_edit = QLineEdit()
        form_sat.addRow("Nom", self.sat_name_edit)
        form_sat.addRow("Òrbita", self.sat_orbitname_edit)
        form_sat.addRow("Massa", self.sat_mass_edit)
        form_sat.addRow("Fuel", self.sat_fuel_edit)
        self.add_sat_btn = QPushButton("Afegeix Satèl·lit")
        form_sat.addWidget(self.add_sat_btn)
        forms_layout.addWidget(sat_box)

        #Posicions
        grid.addWidget(change_box, 0, 0, 3, 1)
        grid.addWidget(self.btn_load_data, 0, 1, 1, 2)
        grid.addWidget(self.btn_save_orbits, 1, 1)
        grid.addWidget(self.btn_save_sats, 1, 2)
        grid.addWidget(forms_container, 2, 1, 1, 2)

        cfg_layout.addWidget(right_panel, 0)
        tabs.addTab(cfg_tab, "Configuració")

        self.viewer = OrbitViewer()
        self.viewer.space = self.space
        tabs.addTab(self.viewer, "Visualització")

        self.btn_load_data.clicked.connect(self._load_both)
        self.btn_save_orbits.clicked.connect(self._save_orbits)
        self.btn_save_sats.clicked.connect(self._save_sats)
        self.add_orbit_btn.clicked.connect(self._add_orbit)
        self.add_sat_btn.clicked.connect(self._add_sat)
        self.co_dest_combo.currentIndexChanged.connect(self._update_dest_params)
        self.co_dest_combo.currentIndexChanged.connect(self._update_dv)
        self.co_sat_combo.currentIndexChanged.connect(self._update_dv)
        self.co_change_btn.clicked.connect(self._change_orbit)


        self._refresh_selectors()
        self.viewer.refresh(self.space)

    def _load_both(self):
        orbit_file, _ = QFileDialog.getOpenFileName(self, "Selecciona fitxer d'òrbites", "", "Text Files (*.txt);;All Files (*)")
        if not orbit_file:
            return
        sat_file, _ = QFileDialog.getOpenFileName(self, "Selecciona fitxer de satèl·lits", "", "Text Files (*.txt);;All Files (*)")
        if not sat_file:
            return

        load_orbits(self.space, orbit_file)
        load_satellites(self.space, sat_file)
        update_all_positions(self.space, 0)
        self._refresh_selectors()
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
        self._refresh_selectors()
        QMessageBox.information(self, "✔", f"Òrbita «{orbit.name}» afegida.")

    def _add_sat(self):
        name  = self.sat_name_edit.text().strip()
        orbitname = self.sat_orbitname_edit.text().strip()
        orbit = get_orbit(self.space, orbitname)
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
        self._refresh_selectors()
        QMessageBox.information(self, "✔", f"Satèl·lit «{sat.name}» afegit.")

    def _change_orbit(self):
        sat_name  = self.co_sat_combo.currentText()
        dest_name = self.co_dest_combo.currentText()
        sat  = next((s for s in self.space.satellites if s.name == sat_name), None)
        dest = get_orbit(self.space, dest_name)
        if not (sat and dest):
            QMessageBox.warning(self, "Error", "Selecció no vàlida.")
            return
        if change_orbit(sat, dest):
            self.viewer.refresh(self.space)
            self._update_dv()
            QMessageBox.information(self, "✔", f"{sat.name} → {dest.name}")
        else:
            QMessageBox.warning(self, "Combustible insuficient",
                                f"{sat.name} no pot arribar a {dest.name}.")

    def _update_dest_params(self):
        name = self.co_dest_combo.currentText()
        orbit = get_orbit(self.space, name)
        if orbit:
            self.co_period_edit.setText(f"{orbit.period:.0f}")
            self.co_eps_edit.setText(f"{orbit.epsilon:.6f}")
            self.co_a_edit.setText(f"{orbit.a:.0f} km")
        else:
            for w in (self.co_period_edit, self.co_eps_edit, self.co_a_edit):
                w.clear()

    def _refresh_selectors(self):
        self.co_sat_combo.clear()
        self.co_dest_combo.clear()

        self.co_sat_combo.addItems([s.name for s in self.space.satellites])
        self.co_dest_combo.addItems([o.name for o in self.space.orbits])

        self._update_dest_params()
        self._update_dv() 

    def _update_dv(self):
        sat_name  = self.co_sat_combo.currentText()
        dest_name = self.co_dest_combo.currentText()
        sat  = next((s for s in self.space.satellites if s.name == sat_name), None)
        dest = get_orbit(self.space, dest_name)

        if not (sat and dest):
            self.co_dv_edit.clear()
            self.co_dv_avail_edit.clear()
            return

        MU  = 3.986e14
        ISP = 450
        G0  = 9.80665

        # Δv necessari (Hohmann)
        a1 = sat.orbit.a * 1_000
        a2 = dest.a      * 1_000
        if abs(a1 - a2) < 1e-3:
            dv_need = 0.0
        else:
            dv1 = math.sqrt(MU/a1) * (math.sqrt(2*a2/(a1+a2)) - 1)
            dv2 = math.sqrt(MU/a2) * (1 - math.sqrt(2*a1/(a1+a2)))
            dv_need = abs(dv1) + abs(dv2)

        # Δv disponible amb el fuel restant
        m0   = sat.mass
        fuel = sat.fuel
        dv_avail = 0.0
        if fuel > 0 and m0 > fuel:
            m_dry = m0 - fuel
            dv_avail = ISP * G0 * math.log(m0 / m_dry)

        self.co_dv_edit.setText(f"{dv_need:.1f}")
        self.co_dv_avail_edit.setText(f"{dv_avail:.1f}")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
