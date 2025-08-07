class Timer:
    def __init__(self, work_duration=25*60, break_duration=20*60):
        self.work_duration = work_duration
        self.break_duration = break_duration
        self.time_left = work_duration
        self.is_work_mode = True
        self.is_running = False

    def start(self):
        self.is_running = True

    def pause(self):
        self.is_running = False

    def reset_to_work(self):
        self.is_work_mode = True
        self.time_left = self.work_duration
        self.is_running = False

    def reset_to_break(self):
        self.is_work_mode = False
        self.time_left = self.break_duration
        self.is_running = False

    def update(self):
        if self.is_running and self.time_left > 0:
            self.time_left -= 1
            return True
        return False

    def get_time_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        return f"{minutes:02d}:{seconds:02d}"

    def is_finished(self):
        return self.time_left <= 0

    def get_total_seconds(self):
        # Возвращает общее время для текущего режима (уже в секундах)
        return self.work_duration if self.is_work_mode else self.break_duration

    def get_seconds_left(self):
        # Возвращает оставшееся время в секундах
        return self.time_left