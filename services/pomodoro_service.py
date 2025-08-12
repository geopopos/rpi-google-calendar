"""
Pomodoro timing service using QTimer.

Manages focus/break phases and round progression; emits signals for UI updates.
"""

from PyQt5.QtCore import QObject, QTimer, pyqtSignal


class PomodoroService(QObject):
    """
    Pomodoro timer service.

    Signals:
        tick(remaining_seconds: int, phase: str, round_index: int)
        phase_changed(phase: str, round_index: int)
        finished()
    """
    tick = pyqtSignal(int, str, int)
    phase_changed = pyqtSignal(str, int)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # 1 second
        self._timer.timeout.connect(self._on_timeout)

        # Configuration
        self._focus_seconds = 25 * 60
        self._break_seconds = 5 * 60
        self._total_rounds = 4

        # State
        self._phase = "focus"  # "focus" | "break"
        self._round_index = 1  # 1-based
        self._remaining_seconds = self._focus_seconds
        self._running = False
        self._paused = False

    # --------- Public API ---------

    def start(self, focus_minutes: int, break_minutes: int, rounds: int) -> None:
        """
        Start a new pomodoro session with the given configuration.
        """
        # Basic validation and clamping to sensible ranges
        focus_minutes = max(1, min(int(focus_minutes), 180))
        break_minutes = max(1, min(int(break_minutes), 60))
        rounds = max(1, min(int(rounds), 24))

        self._focus_seconds = focus_minutes * 60
        self._break_seconds = break_minutes * 60
        self._total_rounds = rounds

        self._round_index = 1
        self._phase = "focus"
        self._remaining_seconds = self._focus_seconds
        self._paused = False
        self._running = True

        self.phase_changed.emit(self._phase, self._round_index)
        # Emit initial tick so UI can render immediately
        self.tick.emit(self._remaining_seconds, self._phase, self._round_index)

        self._timer.start()

    def pause(self) -> None:
        if not self._running or self._paused:
            return
        self._paused = True
        self._timer.stop()

    def resume(self) -> None:
        if not self._running or not self._paused:
            return
        self._paused = False
        self._timer.start()

    def toggle_pause(self) -> None:
        if self._paused:
            self.resume()
        else:
            self.pause()

    def skip(self) -> None:
        """
        Skip to the next phase immediately.
        """
        if not self._running:
            return
        # Force remaining to 0 and let phase transition perform in the next step
        self._remaining_seconds = 0
        self._advance_phase()

    def reset(self) -> None:
        """
        Reset current phase countdown to its initial duration.
        """
        if not self._running:
            return
        if self._phase == "focus":
            self._remaining_seconds = self._focus_seconds
        else:
            self._remaining_seconds = self._break_seconds
        # Inform UI
        self.tick.emit(self._remaining_seconds, self._phase, self._round_index)

    def stop(self) -> None:
        """
        Stop the session entirely and emit finished.
        """
        if self._timer.isActive():
            self._timer.stop()
        self._running = False
        self._paused = False
        self.finished.emit()

    # --------- Properties ---------

    @property
    def phase(self) -> str:
        return self._phase

    @property
    def round_index(self) -> int:
        return self._round_index

    @property
    def total_rounds(self) -> int:
        return self._total_rounds

    @property
    def remaining_seconds(self) -> int:
        return self._remaining_seconds

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    # --------- Internals ---------

    def _on_timeout(self) -> None:
        if not self._running or self._paused:
            return

        self._remaining_seconds = max(0, self._remaining_seconds - 1)
        self.tick.emit(self._remaining_seconds, self._phase, self._round_index)

        if self._remaining_seconds == 0:
            self._advance_phase()

    def _advance_phase(self) -> None:
        """
        Move to the next phase or round; stop if all rounds completed.
        """
        if self._phase == "focus":
            # Move to break within the same round
            self._phase = "break"
            self._remaining_seconds = self._break_seconds
            self.phase_changed.emit(self._phase, self._round_index)
            # Emit initial tick for the new phase
            self.tick.emit(self._remaining_seconds, self._phase, self._round_index)
        else:
            # Completed break; proceed to next round or finish
            if self._round_index >= self._total_rounds:
                self.stop()
                return
            self._round_index += 1
            self._phase = "focus"
            self._remaining_seconds = self._focus_seconds
            self.phase_changed.emit(self._phase, self._round_index)
            self.tick.emit(self._remaining_seconds, self._phase, self._round_index)
