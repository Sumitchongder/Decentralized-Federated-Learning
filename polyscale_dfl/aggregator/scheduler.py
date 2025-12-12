class RoundScheduler:
    """
    Simple round scheduler for FL training
    """
    def __init__(self, num_rounds, clients_per_round):
        self.num_rounds = num_rounds
        self.clients_per_round = clients_per_round
        self.current_round = 0

    def next_round(self):
        if self.current_round >= self.num_rounds:
            return None
        self.current_round += 1
        return self.current_round

    def sample_clients(self, clients_list):
        import random
        return random.sample(clients_list, min(len(clients_list), self.clients_per_round))
