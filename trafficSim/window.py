import pygame
from pygame import gfxdraw
import numpy as np

class Window:
    def __init__(self, sim, config={}):
        # Simulation to draw
        self.sim = sim

        # Set default configurations
        self.set_default_config()

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)
        
    def set_default_config(self):
        """Set default configuration"""
        self.width = 1400
        self.height = 900
        self.bg_color = (250, 250, 250)

        self.fps = 60
        self.zoom = 5
        self.offset = (0, 0)

        self.mouse_last = (0, 0)
        self.mouse_down = False

        # flip x axis
        self.flip_x = True


    def loop(self, loop=None):
        """Shows a window visualizing the simulation and runs the loop function."""
        
        # Create a pygame window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.flip()

        # Fixed fps
        clock = pygame.time.Clock()

        # To draw text
        pygame.font.init()
        self.text_font = pygame.font.SysFont('Lucida Console', 16)
        pygame.display.set_caption("Simulador de Tráfico Independencia - Revolución")

        # Draw loop
        running = True
        while running:
            # Update simulation
            if loop: loop(self.sim)

            # Draw simulation
            self.draw()

            # Update window
            pygame.display.update()
            clock.tick(self.fps)

            # Handle all events
            for event in pygame.event.get():
                # Quit program if window is closed
                if event.type == pygame.QUIT:
                    running = False
                # Handle mouse events
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # If mouse button down
                    if event.button == 1:
                        # Left click
                        x, y = pygame.mouse.get_pos()
                        x0, y0 = self.offset
                        self.mouse_last = (x-x0*self.zoom, y-y0*self.zoom)
                        self.mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False           

    def run(self, steps_per_update=1):
        """Runs the simulation by updating in every loop."""
        def loop(sim):
            sim.run(steps_per_update)
        self.loop(loop)

    def convert(self, x, y=None):
        """Converts simulation coordinates to screen coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(self.width/2 + (x + self.offset[0])*self.zoom),
            int(self.height/2 + (y + self.offset[1])*self.zoom)
        )

    def inverse_convert(self, x, y=None):
        """Converts screen coordinates to simulation coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(-self.offset[0] + (x - self.width/2)/self.zoom),
            int(-self.offset[1] + (y - self.height/2)/self.zoom)
        )


    def background(self, r, g, b):
        """Fills screen with one color."""
        self.screen.fill((r, g, b))

    def line(self, start_pos, end_pos, color):
        gfxdraw.line(
            self.screen,
            *start_pos,
            *end_pos,
            color
        )

    def rect(self, pos, size, color):
        gfxdraw.rectangle(self.screen, (*pos, *size), color)

    def box(self, pos, size, color):
        gfxdraw.box(self.screen, (*pos, *size), color)

    def circle(self, pos, radius, color, filled=True):
        gfxdraw.aacircle(self.screen, *pos, radius, color)
        if filled:
            gfxdraw.filled_circle(self.screen, *pos, radius, color)



    def polygon(self, vertices, color, filled=True):
        gfxdraw.aapolygon(self.screen, vertices, color)
        if filled:
            gfxdraw.filled_polygon(self.screen, vertices, color)

    def rotated_box(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255), filled=True):
        """Draws a rectangle center at *pos* with size *size* rotated anti-clockwise by *angle*."""
        x, y = pos
        l, h = size

        if angle:
            cos, sin = np.cos(angle), np.sin(angle)
        
        vertex = lambda e1, e2: (
            x + (e1*l*cos + e2*h*sin)/2,
            y + (e1*l*sin - e2*h*cos)/2
        )

        if centered:
            vertices = self.convert(
                [vertex(*e) for e in [(-1,-1), (-1, 1), (1,1), (1,-1)]]
            )
        else:
            vertices = self.convert(
                [vertex(*e) for e in [(0,-1), (0, 1), (2,1), (2,-1)]]
            )

        self.polygon(vertices, color, filled=filled)

    def rotated_rect(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255)):
        self.rotated_box(pos, size, angle=angle, cos=cos, sin=sin, centered=centered, color=color, filled=False)

    def arrow(self, pos, size, angle=None, cos=None, sin=None, color=(150, 150, 190)):
        if angle:
            cos, sin = np.cos(angle), np.sin(angle)
        
        self.rotated_box(
            pos,
            size,
            cos=(cos - sin) / np.sqrt(2),
            sin=(cos + sin) / np.sqrt(2),
            color=color,
            centered=False
        )

        self.rotated_box(
            pos,
            size,
            cos=(cos + sin) / np.sqrt(2),
            sin=(sin - cos) / np.sqrt(2),
            color=color,
            centered=False
        )


    def draw_axes(self, color=(100, 100, 100)):
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)


        self.line(
            self.convert((0, y_start)),
            self.convert((0, y_end)),
            color
        )
        self.line(
            self.convert((x_start, 0)),
            self.convert((x_end, 0)),
            color
        )

    def draw_grid(self, unit=50, color=(150,150,150)):
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit)+1
        m_y = int(y_end / unit)+1

        for i in range(n_x, m_x):
            self.line(
                self.convert((unit*i, y_start)),
                self.convert((unit*i, y_end)),
                color
            )
        for i in range(n_y, m_y):
            self.line(
                self.convert((x_start, unit*i)),
                self.convert((x_end, unit*i)),
                color
            )

    def draw_roads(self):
        for road in self.sim.roads:
            # Draw road background
            self.rotated_box(
                road.start,
                (road.length, 3.7),
                cos=road.angle_cos,
                sin=road.angle_sin,
                color=(180, 180, 220),
                centered=False
            )

            # Draw road arrow
            if road.length > 5: 
                for i in np.arange(-0.5*road.length, 0.5*road.length, 10):
                    pos = (
                        road.start[0] + (road.length/2 + i + 3) * road.angle_cos,
                        road.start[1] + (road.length/2 + i + 3) * road.angle_sin
                    )

                    self.arrow(
                        pos,
                        (-1.25, 0.2),
                        cos=road.angle_cos,
                        sin=road.angle_sin
                    )

        text_surface1 = self.text_font.render("Revolución", True, (0, 0, 0))
        text_rect = text_surface1.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 1000, 530)
        self.screen.blit(text_surface1, text_rect)

        text_surface2 = self.text_font.render("Revolución", True, (0, 0, 0))
        text_rect = text_surface2.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 1000, 355)
        self.screen.blit(text_surface2, text_rect) 

        text_surface3 = self.text_font.render("Av. A. López Mateos", True, (0, 0, 0))
        text_rect = text_surface3.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 250, 530)
        self.screen.blit(text_surface3, text_rect) 

        text_surface4 = self.text_font.render("Av. A. López Mateos", True, (0, 0, 0))
        text_rect = text_surface4.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 250, 355)
        self.screen.blit(text_surface4, text_rect)

        text_surface5 = self.text_font.render("Av. Independencia", True, (0, 0, 0))
        rotated_text_surface = pygame.transform.rotate(text_surface5, 90)  # 90 degrees to make it vertical
        text_rect = rotated_text_surface.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 605, 675)  # Adjust the y-coordinate as needed
        self.screen.blit(rotated_text_surface, text_rect)

        text_surface6 = self.text_font.render("Av. Independencia", True, (0, 0, 0))
        rotated_text_surface = pygame.transform.rotate(text_surface6, 90)  # 90 degrees to make it vertical
        text_rect = rotated_text_surface.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 784, 675)  # Adjust the y-coordinate as needed
        self.screen.blit(rotated_text_surface, text_rect)

        text_surface7 = self.text_font.render("Av. Independencia", True, (0, 0, 0))
        rotated_text_surface = pygame.transform.rotate(text_surface7, 90)  # 90 degrees to make it vertical
        text_rect = rotated_text_surface.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 605, 80)  # Adjust the y-coordinate as needed
        self.screen.blit(rotated_text_surface, text_rect)

        text_surface8 = self.text_font.render("Av. Independencia", True, (0, 0, 0))
        rotated_text_surface = pygame.transform.rotate(text_surface8, 90)  # 90 degrees to make it vertical
        text_rect = rotated_text_surface.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 784, 80)  # Adjust the y-coordinate as needed
        self.screen.blit(rotated_text_surface, text_rect)

        text_surface9 = self.text_font.render("Chedraui 1", True, (0, 0, 0))
        text_rect = text_surface9.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 1000, 700)
        self.screen.blit(text_surface9, text_rect)

        text_surface10 = self.text_font.render("Pollo Guerrero", True, (0, 0, 0))
        text_rect = text_surface10.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 300, 700)
        self.screen.blit(text_surface10, text_rect)

        text_surface11 = self.text_font.render("Caja popular Mexicana", True, (0, 0, 0))
        text_rect = text_surface11.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 1000, 150)
        self.screen.blit(text_surface11, text_rect)

        text_surface12 = self.text_font.render("Pollo feliz", True, (0, 0, 0))
        text_rect = text_surface12.get_rect()
        text_rect.topleft = (self.width - text_rect.width - 300, 150)
        self.screen.blit(text_surface12, text_rect)

    def draw_commercial_space(self, pos, size, color):
        """
        Draws a rectangle representing a commercial space.

        Parameters:
        pos (tuple): The (x, y) position of the top-left corner of the rectangle.
        size (tuple): The (width, height) of the rectangle.
        color (tuple): The (R, G, B) color of the rectangle.
        """
        pygame.draw.rect(self.screen, color, (*pos, *size))
        pygame.draw.rect(self.screen, color, (*pos, *size))
        pygame.draw.rect(self.screen, color, (*pos, *size))
        pygame.draw.rect(self.screen, color, (*pos, *size))



    def draw_vehicle(self, vehicle, road):
        l, h = vehicle.l,  vehicle.h
        sin, cos = road.angle_sin, road.angle_cos

        x = road.start[0] + cos * vehicle.x 
        y = road.start[1] + sin * vehicle.x 

        self.rotated_box((x, y), (l, h), cos=cos, sin=sin, color=vehicle.color, centered=True)

    def draw_vehicles(self):
        for road in self.sim.roads:
            # Draw vehicles
            for vehicle in road.vehicles:
                self.draw_vehicle(vehicle, road)

    def draw_signals(self):
        for signal in self.sim.traffic_signals:
            for i in range(len(signal.roads)):
                color = (0, 255, 0) if signal.current_cycle[i] else (255, 0, 0)
                for road in signal.roads[i]:
                    a = 0.165
                    position = (
                        (1-a)*road.end[0] + a*road.start[0],        
                        (1-a)*road.end[1] + a*road.start[1]
                    )
                    self.rotated_box(
                        position,
                        (1, 3),
                        cos=road.angle_cos, sin=road.angle_sin,
                        color=color)
                    

    def draw_status(self):
        text_fps = self.text_font.render(f't={self.sim.t:.5}', False, (0, 0, 0))
        text_frc = self.text_font.render(f'n={self.sim.frame_count}', False, (0, 0, 0))
        vehicles_passed = int(self.sim.vehiclesPassed)
        text_total_vehicles = self.text_font.render(f'Total vehículos={vehicles_passed + self.sim.vehiclesPresent}', False, (0, 0, 0))

        #add white rectangle
        self.screen.fill((255, 255, 255), (0, 0, 1400, 40))
        self.screen.blit(text_fps, (0, 0))
        self.screen.blit(text_frc, (100, 0))
        self.screen.blit(text_total_vehicles, (0, 20))
        

    def draw(self):
        # Fill background
        self.background(*self.bg_color)

        # Major and minor grid and axes
        self.draw_grid(10, (220,220,220))
        self.draw_grid(100, (200,200,200))
        self.draw_axes()

        commercial_pos = self.convert((-78, 18))  # Convert to screen coordinates
        commercial_size = (600, 300)  # Width and height of the rectangle
        commercial_color = (255, 120, 0)  # Color of the rectangle (blue)
        self.draw_commercial_space(commercial_pos, commercial_size, commercial_color)

        commercial_pos1 = self.convert((18, 18))  # Convert to screen coordinates
        commercial_size1 = (300, 300)  # Width and height of the rectangle
        commercial_color1 = (230, 0, 50)  # Color of the rectangle (blue)
        self.draw_commercial_space(commercial_pos1, commercial_size1, commercial_color1)

        commercial_pos2 = self.convert((-78, -48))  # Convert to screen coordinates
        commercial_size2 = (600, 300)  # Width and height of the rectangle
        commercial_color2 = (50, 230, 0)  # Color of the rectangle (blue)
        self.draw_commercial_space(commercial_pos2, commercial_size2, commercial_color2)

        commercial_pos3 = self.convert((18, -48))  # Convert to screen coordinates
        commercial_size3 = (600, 300)  # Width and height of the rectangle
        commercial_color3 = (255, 100, 100)  # Color of the rectangle (blue)
        self.draw_commercial_space(commercial_pos3, commercial_size3, commercial_color3)

        self.draw_roads()
        self.draw_vehicles()
        self.draw_signals()

        # Draw status info
        self.draw_status()

        