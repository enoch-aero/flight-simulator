import tkinter as tk
import math
import random

class RocketSimApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rocket Simulator")

        self.canvas_width = 1000
        self.canvas_height = 800
        self.graph_width = 800
        self.graph_height = 800

        self.gravity = tk.DoubleVar(value=9.8)
        self.thrust = tk.DoubleVar(value=150.0)
        self.mass = tk.DoubleVar(value=10.0)
        self.air_resistance = tk.DoubleVar(value=0.3)
        self.wind_speed = tk.DoubleVar(value=0.0)
        self.fuel = tk.DoubleVar(value=100.0)
        self.burn_rate = tk.DoubleVar(value=1.0)

        self.x_position = self.canvas_width / 2
        self.y_position = self.canvas_height - 100
        self.x_velocity = 0
        self.y_velocity = 0
        self.theta = 0  
        self.omega = 0  
        self.I = 20     
        self.torque = 0
        self.trajectory = []
        self.flying = False
        self.ground_bounce = tk.DoubleVar(value=0.2)
        self.dynamic_wind = False

        self.time_step = 0.05
        self.frame_delay = 20

        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="lightblue")
        self.canvas.grid(row=0, column=0)

        self.graph = tk.Canvas(root, width=self.graph_width, height=self.graph_height, bg="white")
        self.graph.grid(row=0, column=1)

        self.controls = tk.Frame(root)
        self.controls.grid(row=0, column=2, sticky="ns")

        self._add_slider("Gravity", self.gravity, 0, 20)
        self._add_slider("Thrust", self.thrust, 0, 300)
        self._add_slider("Mass", self.mass, 1, 100)
        self._add_slider("Air Resistance", self.air_resistance, 0, 2)
        self._add_slider("Wind Speed", self.wind_speed, -10, 10)
        self._add_slider("Fuel", self.fuel, 0, 500)
        self._add_slider("Burn Rate", self.burn_rate, 0, 10)
        self._add_slider("Ground Bounce", self.ground_bounce, 0, 1)

        self.launch_button = tk.Button(self.controls, text="Launch", command=self.start_simulation)
        self.launch_button.pack(pady=10)

        self.rocket = self.canvas.create_polygon(self._get_rotated_rocket_points(), fill="red")

    def _add_slider(self, label, variable, frm, to):
        tk.Label(self.controls, text=label).pack()
        tk.Scale(self.controls, from_=frm, to=to, resolution=0.1, orient="horizontal", variable=variable).pack()

    def _get_rotated_rocket_points(self):
        min_scale = 0.2
        max_scale = 1.0
        normalized_height = max(0, self.canvas_height - self.y_position) / self.canvas_height
        scale = max(min_scale, max_scale - normalized_height)

        w, h = 20 * scale, 40 * scale
        cx, cy = self.x_position, self.y_position
        angle = self.theta
        points = [(-w/2, h/2), (-w/2, -h/2), (0, h/2)]
        rotated = []
        for x, y in points:
            xr = cx + x * math.cos(angle) - y * math.sin(angle)
            yr = cy + x * math.sin(angle) + y * math.cos(angle)
            rotated.extend([xr, yr])
        return rotated

    def start_simulation(self):
        self.flying = True
        self.x_position = self.canvas_width / 2
        self.y_position = self.canvas_height - 10
        self.x_velocity = 0
        self.y_velocity = 0
        self.theta = 0
        self.omega = self.wind_speed.get()
        self.trajectory.clear()

        self.dynamic_wind = (self.wind_speed.get() == 0)

        self.update_simulation()

    def update_simulation(self):
        if not self.flying:
            return

        m = self.mass.get()
        g = self.gravity.get()
        thrust = self.thrust.get() if self.fuel.get() > 0 else 0
        drag = self.air_resistance.get()

        if self.dynamic_wind:
            wind = random.uniform(-1.0, 1.0)
        else:
            wind = self.wind_speed.get()

        if self.fuel.get() > 0:
            self.fuel.set(self.fuel.get() - self.burn_rate.get() * self.time_step)

        alpha = self.torque / self.I
        self.omega += alpha * self.time_step
        self.theta += self.omega * self.time_step
        self.theta %= (2 * math.pi)

        Fx = thrust * math.sin(self.theta)
        Fy = thrust * math.cos(self.theta)

        self.x_velocity += ((Fx / m) - drag * self.x_velocity + wind) * self.time_step
        self.y_velocity += ((-Fy / m) - drag * self.y_velocity + g) * self.time_step

        self.x_position += self.x_velocity * self.time_step * 20
        self.y_position += self.y_velocity * self.time_step * 20

        if self.y_position >= self.canvas_height - 10:
            self.y_position = self.canvas_height - 10
            self.y_velocity = -self.y_velocity * self.ground_bounce.get()

            if abs(self.y_velocity) < 1.0:
                self.y_velocity = 0
                self.flying = False


        self.canvas.delete(self.rocket)
        self.rocket = self.canvas.create_polygon(self._get_rotated_rocket_points(), fill="red")

        self.trajectory.append(self.canvas_height - self.y_position)
        self.draw_graph()

        if self.flying:
            self.root.after(self.frame_delay, self.update_simulation)

    def draw_graph(self):
        self.graph.delete("all")
        
        self.graph.create_line(0, self.graph_height - 20, self.graph_width, self.graph_height - 20, fill="green")
        self.graph.create_text(5, self.graph_height - 25, anchor="w", text="Time")

        if len(self.trajectory) < 2:
            return

        max_height = max(self.trajectory)
        scale_y = (self.graph_height - 40) / max(1, max_height)

        max_points = len(self.trajectory)
        scale_x = self.graph_width / max(1, max_points)

        for i in range(1, max_points):
            x1 = (i - 1) * scale_x
            y1 = self.graph_height - 20 - self.trajectory[i - 1] * scale_y
            x2 = i * scale_x
            y2 = self.graph_height - 20 - self.trajectory[i] * scale_y
            self.graph.create_line(x1, y1, x2, y2, fill="blue")


if __name__ == "__main__":
    root = tk.Tk()
    app = RocketSimApp(root)
    root.mainloop()
