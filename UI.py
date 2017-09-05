import sys
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from GrafADXL import Povezava

import time
import numpy as np

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class MainWindow(QtWidgets.QMainWindow):
    """ Podedovano glavno okno
    """

    def __init__(self):
        """ Konstruktor MainWindow objekta
        """
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('ADXL - UI')
        self.setWindowIcon(QtGui.QIcon("Logo.png"))
        self.setGeometry(50, 50, 600, 400)
        self.showMaximized()
        self.init_central_widget()
        self.init_actions()
        self.init_menus()
        self.statusBar()

    def init_central_widget(self):
        """ Vsebina centralnega okna
        """
        self.central_widget = QtWidgets.QWidget()
        self.buttons_widget = QtWidgets.QWidget()
        v_layout = QtWidgets.QVBoxLayout()
        h_layout = QtWidgets.QHBoxLayout()
        self.function_text = QtWidgets.QTextEdit()
        self.function_text.setFontPointSize(30)
        self.function_text.setText('Vnesite čas zajema [ms]')
        #self.submit_btn = QtWidgets.QPushButton('Prikaži')
        #self.submit_btn.pressed.connect(self.data_aq())
        self.animate_btn = QtWidgets.QPushButton('Zaženi meritev')
        self.animate_btn.pressed.connect(self.animate_figure)
        self.animate_btn.setCheckable(True)
        self.get_figure()

        self.central_widget.setLayout(v_layout)
        v_layout.addWidget(self.function_text)
        v_layout.addWidget(self.buttons_widget)
        v_layout.addWidget(self.canvas)
        v_layout.addWidget(self.canvas_toolbar)

        self.buttons_widget.setLayout(h_layout)
        h_layout.addStretch()
        h_layout.addWidget(self.animate_btn)
        #h_layout.addWidget(self.submit_btn)
        h_layout.addStretch()


        self.setCentralWidget(self.central_widget)

    def get_figure(self):
        self.fig = Figure(figsize=(600, 600), dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
        self.ax = self.fig.add_subplot(111)


        self.os, = self.ax.plot(np.linspace(0, 200, 10), np.random.randint(100, 140, 10))  # Začetno stanje
        #self.ax.set_ylim([100, 200])
        self.ax.set_xlabel('$t$ $[s]$', fontsize=24)
        self.ax.set_ylabel('$a$ $[m/s^2]$', fontsize=24)
        self.ax.tick_params(axis='both', which='major', labelsize=16)


        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_toolbar = NavigationToolbar(self.canvas, self)

    def init_menus(self):
        """ Pripravi menuje
        """
        self.file_menu = self.menuBar().addMenu('&Datoteka')

        self.file_menu.addAction(self.close_app_action)

    def close_app(self):
        choice = QtWidgets.QMessageBox.question(
            self,"Zapiranje",
            "Želite zapustiti aplikacijo?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if choice == QtWidgets.QMessageBox.Yes:
            print("Zapuščam aplikacijo.")
            sys.exit()
        else:
            pass

    def init_actions(self):
        """ Pripravi actions za menuje
        """
        self.close_app_action = QtWidgets.QAction(
            '&Izhod', self, shortcut=QtGui.QKeySequence.Cancel,
            statusTip="Izhod iz aplikacije", triggered=self.close_app)

    def animate_figure(self):

        try:
            tk = int(self.function_text.toPlainText())*1000
        except AttributeError:
            QtWidgets.QMessageBox.about(self, 'Napaka',
                                    'Vnesite čas zajema!')


        try:
            conn, add = Povezava()
        except:
            QtWidgets.QMessageBox.about(self, 'Napaka',
                                        'Povezava ni vzpostavljena!')

        dt = 10000 # Načeloma bi tukaj prišla komun. Pyt - Ard
        stp = 49
        i = 1

        t = np.array([], dtype=int)  # Prazen numerični seznam časov
        a = np.array([], dtype=int)  # Prazen numerični seznam pospeškov

        while i <= tk / (dt * stp):  # Prejemanje paketov
            paket = ""  # Prazen paket

            buf = conn.recv(4096)

            if len(buf) > 0:  # Se izpolni, ce paket ni prazen

                paket = buf.decode()

            tocke = paket.split("\n")  # Ločevanje točk
            for tocka in tocke:  # Ločevanje pospeška in časa
                if len(tocka) > 1:
                    y, x = tocka.split('\t')
                    t = np.append(t, float(x) / 1000000)  # Pripenjanje časov v skupno tabelo
                    a = np.append(a, int(y))  # Pripenjanje pospeškov v skupno tabelo

            self.os.set_data(t[(i - 1) * stp:(i - 1) * stp + stp] - t[0], a[(i - 1) * stp:(i - 1) * stp + stp])  # Osveževanje grafa
            self.ax.set_xlim(t[(i - 1) * stp] - t[0], t[(i - 1) * stp + stp] - t[0])  # Meje x osi
            self.canvas.draw()
            self.canvas.flush_events()

            i += 1  # Inkrement števca paketov

            # if self.animate_btn.isChecked() or self.animate_btn.isDown():
            #     self.timer.start(100)  # čez 100ms spet sproži to funkcijo
            # else:
            #     self.timer.stop()
            #self.animate_btn.setChecked(False)


if __name__ == '__main__':
    try:
        app = QtWidgets.QApplication(sys.argv)
        mainWindow = MainWindow()
        mainWindow.show()
        app.exec_()
        sys.exit(0)
    except SystemExit:
        print('Zapiram okno.')
    except:
        print(sys.exc_info())