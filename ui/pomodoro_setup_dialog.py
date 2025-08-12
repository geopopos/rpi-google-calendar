"""
Keyboard-only Pomodoro Setup Dialog.

Allows user to input focus minutes, break minutes, and number of rounds.
"""

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox,
    QSpinBox, QLabel, QShortcut
)

try:
    from config.settings import THEME, FONTS
except Exception:
    THEME = {
        'background': '#0a0a0a',
        'primary': '#00ffff',
        'text_primary': '#ffffff',
        'text_secondary': '#b0b0b0',
    }
    FONTS = {
        'event_title': ('Arial', 20, 'bold'),
        'notification_text': ('Arial', 22, 'normal'),
    }


class PomodoroSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pomodoro_setup_dialog")
        self.setWindowTitle("Pomodoro Setup")
        self.setModal(True)
        self.setWindowFlag(Qt.FramelessWindowHint, False)
        self._build_ui()
        self._apply_styles()
        self.setFocusPolicy(Qt.StrongFocus)
        # Ensure Enter/Return always accept, regardless of child focus (e.g., QSpinBox editor)
        self._sc_return = QShortcut(QKeySequence(Qt.Key_Return), self)
        self._sc_return.activated.connect(self.accept)
        self._sc_enter = QShortcut(QKeySequence(Qt.Key_Enter), self)
        self._sc_enter.activated.connect(self.accept)
        self._sc_escape = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self._sc_escape.activated.connect(self.reject)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Pomodoro Setup")
        title.setObjectName("pomodoro_setup_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form.setSpacing(12)

        self.focus_spin = QSpinBox()
        self.focus_spin.setRange(5, 180)
        self.focus_spin.setValue(25)
        self.focus_spin.setSuffix(" min")
        self.focus_spin.setFocusPolicy(Qt.StrongFocus)

        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setValue(5)
        self.break_spin.setSuffix(" min")
        self.break_spin.setFocusPolicy(Qt.StrongFocus)

        self.rounds_spin = QSpinBox()
        self.rounds_spin.setRange(1, 24)
        self.rounds_spin.setValue(4)
        self.rounds_spin.setSuffix(" rounds")
        self.rounds_spin.setFocusPolicy(Qt.StrongFocus)

        form.addRow("Focus interval:", self.focus_spin)
        form.addRow("Break interval:", self.break_spin)
        form.addRow("Number of rounds:", self.rounds_spin)

        layout.addLayout(form)

        # Enter on any spinbox should accept immediately (one-press)
        for _w in (self.focus_spin, self.break_spin, self.rounds_spin):
            _w.installEventFilter(self)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # Keyboard: Enter activates Start by default, Esc triggers reject
        ok_button = self.buttons.button(QDialogButtonBox.Ok)
        if ok_button:
            ok_button.setText("Start")
            ok_button.setDefault(True)
            ok_button.setAutoDefault(True)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addWidget(self.buttons)

        hint = QLabel("Use Tab/Shift+Tab to navigate. Enter to Start. Esc to Cancel.")
        hint.setObjectName("pomodoro_setup_hint")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        self.focus_spin.setFocus()

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QDialog#pomodoro_setup_dialog {{
                background-color: {THEME['background']};
                color: {THEME['text_primary']};
                border: 2px solid {THEME['primary']};
                border-radius: 10px;
            }}
            QLabel#pomodoro_setup_title {{
                color: {THEME['primary']};
                font-family: {FONTS.get('event_title', ('Arial', 20, 'bold'))[0]};
                font-size: {FONTS.get('event_title', ('Arial', 20, 'bold'))[1]}px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            QLabel#pomodoro_setup_hint {{
                color: {THEME['text_secondary']};
                font-size: 14px;
                margin-top: 8px;
            }}
            QSpinBox {{
                background: rgba(255, 255, 255, 0.06);
                color: {THEME['text_primary']};
                border: 1px solid {THEME['primary']};
                border-radius: 6px;
                padding: 6px 10px;
                min-width: 140px;
            }}
            QDialogButtonBox QPushButton {{
                background: rgba(255, 255, 255, 0.06);
                color: {THEME['primary']};
                border: 1px solid {THEME['primary']};
                border-radius: 6px;
                padding: 8px 18px;
                margin: 6px;
                font-weight: bold;
            }}
            QDialogButtonBox QPushButton:default {{
                background: rgba(0, 255, 255, 0.18);
            }}
            QDialogButtonBox QPushButton:hover {{
                background: rgba(0, 255, 255, 0.28);
            }}
        """)

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.accept()
                return True
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
            return
        if key == Qt.Key_Escape:
            self.reject()
            return
        super().keyPressEvent(event)

    def get_values(self):
        return self.focus_spin.value(), self.break_spin.value(), self.rounds_spin.value()
