import sys, os
from PyQt4.Qt import *
from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL as S

import plistlib
plist_file = os.environ['HOME'] \
           + ('\\Application Data\\' if os.name == 'nt' else '/Library/') \
           + 'kmuttwifi.plist'
try:    reg = plistlib.readPlist(plist_file)
except: reg = dict(username='', password='', trayed=False)

class Window(QDialog):
    def __init__(self, auth):
        # initialize window
        QWidget.__init__(self)
        self.auth = auth
        self.setWindowTitle("KMUTT WiFi")
        self.setWindowIcon(QIcon('wifi.png'))

        # add controls
        self.username = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.save_button = QPushButton("&Log on", self)
        self.connect(self.save_button, S('clicked()'), self.save)
        self.cancel_button = QPushButton("&Cancel", self)
        self.connect(self.cancel_button, S('clicked()'), self.close)
        self.tray = Tray(self)
        if os.name == 'nt': # according to vista interface guideline
            self.resize(240, 128)
            self.username_label = QLabel("Username", self)
            self.password_label = QLabel("Password", self)
            self.username_label.setGeometry(11, 19, 55, 23)
            self.password_label.setGeometry(11, 49, 55, 23)
            self.username.setGeometry(73, 19, 156, 23)
            self.password.setGeometry(73, 49, 156, 23)
            self.save_button.setGeometry(73, 94, 75, 23)
            self.cancel_button.setGeometry(155, 94, 75, 23)
            self.setWindowFlags(Qt.WindowFlags(
                Qt.Sheet |
                Qt.WindowStaysOnTopHint |
                Qt.WindowSystemMenuHint |
                Qt.MSWindowsFixedSizeDialogHint))
        else: # according to aero human interface guideline
            self.resize(278, 128)
            self.username_label = QLabel("Username:", self)
            self.password_label = QLabel("Password:", self)
            self.username_label.setGeometry(20, 19, 70, 22)
            self.password_label.setGeometry(20, 51, 70, 22)
            self.username_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.password_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.username.setGeometry(98, 19, 160, 22)
            self.password.setGeometry(98, 51, 160, 22)
            self.save_button.setGeometry(179, 83, 85, 34)
            self.cancel_button.setGeometry(94, 83, 85, 34)
            self.setWindowFlags(Qt.WindowFlags(
                Qt.Sheet |
                Qt.WindowStaysOnTopHint))

        # give aero glass transparency
        self.dwm = False
        if os.name == 'nt':
            from ctypes import windll, c_int, byref
            dwm = c_int(0)
            try:
                windll.dwmapi.DwmIsCompositionEnabled(byref(dwm))
                self.dwm = bool(dwm)
            except: pass
            if self.dwm:
                self.setAttribute(Qt.WA_NoSystemBackground)
                windll.dwmapi.DwmExtendFrameIntoClientArea(
                    c_int(self.winId()), '\0\0\0\0\0\0\0\0\11\0\0\0\56\0\0\0')
                windll.dwmapi.DwmEnableBlurBehindWindow(
                    c_int(self.winId()), '\1\0\0\0\1\0\0\0')
                windll.UxTheme.SetWindowThemeAttribute(
                    c_int(self.winId()), 1, '\3\0\0\0\3\0\0\0', 8)

        # load registry settings
        self.auth.username = reg['username']
        self.auth.password = reg['password']
        self.trayed        = reg['trayed']
        if not self.trayed: self.show()

    def showEvent(self, event):
        "Reloads settings."
        self.username.setText(self.auth.username)
        self.password.setText(self.auth.password)
        self.username.setFocus()

    def closeEvent(self, event):
        if not self.trayed:
            self.tray.update_status("The program will continue to work in background.")
            self.trayed = True
            reg['trayed'] = True
            plistlib.writePlist(reg, plist_file)

    def paintEvent(self, event):
        "Paints white rectangle in the center."
        if self.dwm:
            paint = QPainter()
            paint.begin(self)
            paint.setPen(QPen(Qt.black, 0, 0))
            paint.setBrush(QColor(255, 255, 255, 128))
            paint.drawRect(0, 9, 240, 73)

    def mousePressEvent(self, event):
        "Enables drag anywhere. <3 windll."
        if os.name == 'nt':
            windll.user32.ReleaseCapture()
            windll.user32.SendMessageA(
                c_int(self.winId()), 0x0112, 0xF010 | 2, byref(c_int(-1)))

    def save(self):
        "Triggered by save button."
        self.auth.username = self.username.text()
        self.auth.password = self.password.text()
        self.close()
        reg['username'] = str(self.auth.username)
        reg['password'] = str(self.auth.password)
        plistlib.writePlist(reg, plist_file)

    def update_status(self, *args, **kwargs):
        self.tray.update_status(*args, **kwargs)

class Tray(QSystemTrayIcon):
    def __init__(self, win):
        QSystemTrayIcon.__init__(self, QIcon('wifi.png'))
        self.win = win
        self.update_status("Initializing", mute=True)
        self.show()
        if os.name == 'nt':
            sig = S('activated(QSystemTrayIcon::ActivationReason)')
            self.connect(self, sig, self._ontray)

        sig = S('triggered()')
        self.menu = QMenu()
        self.connect(self.menu.addAction("S&ettings"), sig, self.win.show)
        self.connect(self.menu.addAction("E&xit"), sig, app.quit)
        self.setContextMenu(self.menu)

    def update_status(self, status, description="", mute=False):
        if not mute: self.showMessage(status, description)
        self.setToolTip("KMUTT WiFi\n%s" % status)

    def _ontray(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.win.show() # TODO: show context menu here instead

app = QApplication(sys.argv)
