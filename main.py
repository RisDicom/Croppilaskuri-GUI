# -*- coding: utf-8 -*-
"""
Sovelluksen käynnistyspiste.
Luo QApplication-instanssin ja EclipseHelperApp-pääikkunan ja näyttää sen.
"""
import sys
from PyQt5.QtWidgets import QApplication

# Oletetaan, että app.py on samassa hakemistossa
from app import EclipseHelperApp

if __name__ == '__main__':
    app_instance = QApplication(sys.argv)
    eclipse_helper_window = EclipseHelperApp()
    eclipse_helper_window.show()
    sys.exit(app_instance.exec_())