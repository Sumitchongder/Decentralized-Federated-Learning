class TrainingReporter:
    """
    Report training metrics and progress
    """
    def __init__(self):
        self.logs = []

    def log_round(self, round_number, metrics: dict):
        log_entry = {"round": round_number, **metrics}
        self.logs.append(log_entry)
        print(f"[Reporter] Round {round_number}: {metrics}")

    def get_history(self):
        return self.logs
