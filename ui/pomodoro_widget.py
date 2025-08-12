"""
Fullscreen Pomodoro Timer Widget (keyboard-only).

Controls:
- Space / Enter: Pause/Resume
- S: Skip to next phase
- R: Reset current phase's timer
- Esc / Q: Exit timer
"""

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QWidget, QHBoxLayout, QApplication, QSizePolicy
)

try:
    from config.settings import THEME, FONTS
except Exception:
    THEME = {
        'background': '#0a0a0a',
        'primary': '#00ffff',
        'secondary': '#8a2be2',
        'text_primary': '#ffffff',
        'text_secondary': '#b0b0b0',
        'success': '#00ff00',
        'warning': '#ffa500',
        'error': '#ff4444',
    }
    FONTS = {
        'time_display': ('Arial', 48, 'bold'),
        'date_display': ('Arial', 24, 'normal'),
        'event_title': ('Arial', 20, 'bold'),
        'event_time': ('Arial', 18, 'bold'),
        'notification_title': ('Arial', 28, 'bold'),
        'notification_text': ('Arial', 22, 'normal')
    }


def _fmt_time(seconds: int) -> str:
    seconds = max(0, int(seconds))
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"


class PomodoroWidget(QDialog):
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self.setObjectName("pomodoro_timer")
        self.setWindowTitle("Pomodoro Timer")
        # Fullscreen overlay, stays on top, no frame
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setModal(True)
        self.setWindowModality(Qt.ApplicationModal)
        self._service = service

        self._build_ui()
        self._apply_styles()
        self._wire_signals()

        # Ensure keystrokes go here
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        try:
            # Size/position to fully cover the main window or the primary screen
            if self.parent() is not None:
                self.setGeometry(self.parent().geometry())
            else:
                screen = QApplication.primaryScreen()
                if screen:
                    self.setGeometry(screen.availableGeometry())
            # Ensure fullscreen and focus for keyboard-only control
            try:
                self.setMinimumSize(self.geometry().size())
            except Exception:
                pass
            self.showFullScreen()
            self.raise_()
            self.activateWindow()
            self.setFocus()
        except Exception:
            self.showMaximized()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30)
        root.setSpacing(12)
        root.setAlignment(Qt.AlignCenter)

        # Phase label
        self.phase_label = QLabel("FOCUS")
        self.phase_label.setObjectName("pomodoro_phase")
        self.phase_label.setAlignment(Qt.AlignCenter)

        # Time display (big)
        self.time_label = QLabel("25:00")
        self.time_label.setObjectName("pomodoro_time")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Round info
        self.round_label = QLabel("Round 1 of 4")
        self.round_label.setObjectName("pomodoro_round")
        self.round_label.setAlignment(Qt.AlignCenter)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(12)

        # Hints
        self.hint_label = QLabel("Space/Enter: Pause/Resume  •  S: Skip  •  R: Reset  •  Esc/Q: Exit")
        self.hint_label.setObjectName("pomodoro_hint")
        self.hint_label.setAlignment(Qt.AlignCenter)

        # Assemble
        root.addWidget(self.phase_label)
        root.addWidget(self.time_label)
        root.addWidget(self.round_label)
        root.addWidget(self.progress)
        root.addSpacing(8)
        root.addWidget(self.hint_label)

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QDialog#pomodoro_timer {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 0, 0, 0.95),
                    stop:1 rgba(0, 255, 255, 0.08));
                color: {THEME['text_primary']};
                border: 3px solid {THEME['primary']};
            }}
            QLabel#pomodoro_phase {{
                color: {THEME['secondary']};
                font-family: {FONTS['notification_title'][0]};
                font-size: {max(22, FONTS['notification_title'][1]-2)}px;
                font-weight: bold;
                margin: 8px 0;
            }}
            QLabel#pomodoro_time {{
                color: {THEME['primary']};
                font-family: {FONTS['time_display'][0]};
                font-size: {max(64, FONTS['time_display'][1] + 16)}px;
                font-weight: bold;
                padding: 8px;
            }}
            QLabel#pomodoro_round {{
                color: {THEME['text_secondary']};
                font-family: {FONTS['event_time'][0]};
                font-size: {FONTS['event_time'][1]}px;
                margin: 4px 0 10px 0;
            }}
            QProgressBar {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {THEME['primary']},
                    stop:1 {THEME['secondary']});
                border-radius: 6px;
            }}
            QLabel#pomodoro_hint {{
                color: {THEME['text_secondary']};
                font-size: 14px;
            }}
        """)

    def _wire_signals(self):
        self._service.tick.connect(self._on_tick)
        self._service.phase_changed.connect(self._on_phase_changed)
        self._service.finished.connect(self._on_finished)

    # ----- Slots -----

    @pyqtSlot(int, str, int)
    def _on_tick(self, remaining_seconds: int, phase: str, round_index: int):
        # Update time text
        self.time_label.setText(_fmt_time(remaining_seconds))
        # Update round display
        self.round_label.setText(f"Round {round_index} of {self._service.total_rounds}")
        # Update progress: progress within current phase
        total = self._service._focus_seconds if phase == "focus" else self._service._break_seconds
        total = max(1, int(total))
        pct = int(100 * (total - max(0, remaining_seconds)) / total)
        self.progress.setValue(max(0, min(100, pct)))

    @pyqtSlot(str, int)
    def _on_phase_changed(self, phase: str, round_index: int):
        self.phase_label.setText("FOCUS" if phase == "focus" else "BREAK")
        # Reset progress to start of new phase
        self.progress.setValue(0)

    @pyqtSlot()
    def _on_finished(self):
        # Close the dialog when finished
        self.accept()

    # ----- Keyboard handling -----

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self._service.toggle_pause()
            return
        if key == Qt.Key_S:
            self._service.skip()
            return
        if key == Qt.Key_R:
            self._service.reset()
            return
        if key in (Qt.Key_Escape, Qt.Key_Q):
            # Stop and close
            try:
                self._service.stop()
            except Exception:
                pass
            self.accept()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        try:
            if self._service and self._service.is_running:
                self._service.stop()
        except Exception:
            pass
        event.accept()
