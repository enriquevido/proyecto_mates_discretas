import random

class TrafficSignal:
    def __init__(self, roads, config={}, wait_times=None):
        # Initialize roads
        self.roads = roads
        # Set default configuration
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)
        # Calculate properties
        self.init_properties()
        
        # Set wait times
        self.wait_times = wait_times if wait_times else [self.cycle_length] * len(self.cycle)
        self.last_t = 0
        self.yellow_time = 10

    def set_default_config(self):
        self.cycle = [(False, False, False, True), (True, False, True, False), (False, True, False, False), (True, False, True, False)]
        self.slow_distance = 100
        self.slow_factor = 0.35
        self.stop_distance = 20
        self.cycle_length = 6

        self.current_cycle_index = 0

    def init_properties(self):
        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)

    @property
    def current_cycle(self):
        return self.cycle[self.current_cycle_index]
    
    def update(self, sim):
        # Use specific wait times for each traffic light
        if sim.t >= self.last_t + self.wait_times[self.current_cycle_index]:
            self.last_t = sim.t
            self.current_cycle_index = (self.current_cycle_index + 1) % len(self.cycle)
            
            # If less than 4 roads, ensure the cycle index is valid
            if len(self.roads) < 4 and self.current_cycle_index >= len(self.roads):
                self.current_cycle_index = len(self.roads) - 1
            # Cambiar el estado del semáforo a amarillo antes de cambiar a rojo
            if self.current_cycle == (False, False, False, True):  # Si el semáforo está en rojo
                # Cambiar a amarillo
                self.current_cycle_index = (self.current_cycle_index + 1) % len(self.cycle)
                sim.t += self.yellow_time  # Añadir tiempo amarillo al tiempo simulado

