import tkinter as tk
from tkinter import Canvas, Frame
import time
import math
from dataclasses import dataclass
from typing import Optional, Dict
from PIL import Image, ImageTk, ImageEnhance

@dataclass
class VehicleState:
    """Stores the current state of the vehicle."""
    speed: float = 0.0
    rpm: float = 0.0
    temperature: float = 50.0
    fuel: float = 100.0
    gear: int = 1
    accelerating: bool = False

class WarningDot:
    """Represents a warning indicator dot."""
    def __init__(self, canvas: Canvas, x: int, y: int):
        self.canvas = canvas
        self.dot = canvas.create_oval(
            x, y, x + 10, y + 10,
            fill="red",
            state="hidden"
        )
        self.is_visible = False
        self.blinking = False

    def set_visibility(self, visible: bool):
        self.is_visible = visible
        self.canvas.itemconfig(
            self.dot,
            state="normal" if visible else "hidden"
        )

    def blink(self):
        if self.is_visible:
            current_state = self.canvas.itemcget(self.dot, "state")
            self.canvas.itemconfig(
                self.dot,
                state="hidden" if current_state == "normal" else "normal"
            )

class StatusIndicator:
    """Represents a status indicator with an icon and warning dot."""
    def __init__(self, canvas: Canvas, x: int, y: int, icon_path: str):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.icon_path = icon_path
        self.is_active = False
        
        # Load and create icon
        self.image = self._load_icon(False)
        self.icon = canvas.create_image(x, y, image=self.image, anchor="nw")
        
        # Create warning dot
        self.warning = WarningDot(canvas, x + 35, y + 5)

    def _load_icon(self, active: bool) -> ImageTk.PhotoImage:
        """Load and process the indicator icon."""
        image = Image.open(self.icon_path).resize((30, 30))
        enhancer = ImageEnhance.Brightness(image)
        return ImageTk.PhotoImage(enhancer.enhance(2 if active else 1))

    def set_state(self, active: bool):
        """Update the indicator's active state."""
        self.is_active = active
        self.image = self._load_icon(active)
        self.canvas.itemconfig(self.icon, image=self.image)

class ClockDisplay(Frame):
    """Displays the current time in a styled frame."""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            bg="black",
            highlightbackground="white",
            highlightthickness=2,
            padx=15,
            pady=8,
            **kwargs
        )

        self.time_label = tk.Label(
            self,
            text="",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="black"
        )
        self.time_label.pack()
        self._update_clock()

    def _update_clock(self):
        """Update the clock display every second."""
        current_time = time.strftime("%I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.after(1000, self._update_clock)

class GaugeDisplay:
    """Creates and manages a circular gauge display."""
    def __init__(
        self,
        canvas: Canvas,
        x: int,
        y: int,
        radius: int,
        start_angle: int,
        end_angle: int,
        max_value: float,
        label: str,
        units: str,
        danger_threshold: float,
        color: str = "white"
    ):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = radius
        self.angles = (start_angle, end_angle)
        self.max_value = max_value
        self.danger_threshold = danger_threshold
        self.color = color
        
        self._create_gauge(label, units)
        self.needle = None
        self.value_text = None

    def _create_gauge(self, label: str, units: str):
        """Create the gauge's visual elements."""
        # Background for danger indication
        self.background = self.canvas.create_arc(
            self.x - self.radius - 10,
            self.y - self.radius - 10,
            self.x + self.radius + 10,
            self.y + self.radius + 10,
            start=self.angles[0],
            extent=self.angles[1] - self.angles[0],
            fill="black",
            outline="black"
        )

        # Main gauge arc
        self.canvas.create_arc(
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius,
            start=self.angles[0],
            extent=self.angles[1] - self.angles[0],
            outline=self.color,
            width=3,
            style="arc"
        )

        # Create markers and labels
        self._add_markers()
        
        # Add main label and units
        self.canvas.create_text(
            self.x,
            self.y + self.radius // 2 + 20,
            text=label,
            fill=self.color,
            font=("Arial", 16, "bold")
        )
        
        self.canvas.create_text(
            self.x,
            self.y + self.radius // 2 + 45,
            text=units,
            fill=self.color,
            font=("Arial", 12)
        )

        # Value display
        self.value_text = self.canvas.create_text(
            self.x,
            self.y + 40,
            text="0",
            fill=self.color,
            font=("Arial", 28, "bold")
        )

    def _add_markers(self):
        """Add numeric markers around the gauge."""
        for i in range(0, int(self.max_value) + 1, int(self.max_value / 8)):
            angle = math.radians(
                self.angles[0] - (i / self.max_value) * 
                (self.angles[0] - self.angles[1])
            )
            marker_x = self.x + (self.radius - 20) * math.cos(angle)
            marker_y = self.y - (self.radius - 20) * math.sin(angle)
            
            self.canvas.create_text(
                marker_x,
                marker_y,
                text=str(i),
                fill=self.color,
                font=("Arial", 12)
            )

    def update(self, value: float):
        """Update the gauge with a new value."""
        # Remove old needle
        if self.needle:
            self.canvas.delete(self.needle)

        # Update danger background
        self.canvas.itemconfig(
            self.background,
            fill="#500000" if value >= self.danger_threshold else "black"
        )

        # Calculate needle angle
        angle = math.radians(
            self.angles[0] - (value / self.max_value) * 
            (self.angles[0] - self.angles[1])
        )
        
        # Draw new needle
        needle_x = self.x + (self.radius - 40) * math.cos(angle)
        needle_y = self.y - (self.radius - 40) * math.sin(angle)
        self.needle = self.canvas.create_line(
            self.x, self.y,
            needle_x, needle_y,
            fill="red",
            width=3
        )

        # Update value display
        self.canvas.itemconfig(self.value_text, text=f"{int(value)}")

class LevelBar:
    """Creates and manages a vertical level indicator bar."""
    def __init__(
        self,
        canvas: Canvas,
        x: int,
        y: int,
        width: int,
        height: int,
        label: str,
        colors: Dict[str, str]
    ):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colors = colors
        
        self._create_bar(label)

    def _create_bar(self, label: str):
        """Create the bar's visual elements."""
        # Border
        self.canvas.create_rectangle(
            self.x, self.y,
            self.x + self.width, self.y + self.height,
            outline="white",
            width=2
        )

        # Label
        self.canvas.create_text(
            self.x + self.width // 2,
            self.y + self.height + 20,
            text=label,
            fill="white",
            font=("Arial", 14, "bold")
        )

        # Fill bar
        self.fill = self.canvas.create_rectangle(
            self.x + 5,
            self.y + 5,
            self.x + self.width - 5,
            self.y + self.height - 5,
            fill=self.colors["normal"]
        )

    def update(self, value: float):
        """Update the bar's fill level and color."""
        fill_height = (value / 100) * (self.height - 10)
        color = (
            self.colors["low"] if value < 20
            else self.colors["medium"] if value < 50
            else self.colors["normal"]
        )
        
        self.canvas.coords(
            self.fill,
            self.x + 5,
            self.y + self.height - 5 - fill_height,
            self.x + self.width - 5,
            self.y + self.height - 5
        )
        self.canvas.itemconfig(self.fill, fill=color)

class CarDashboard:
    """Main dashboard application class."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Car Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="black")

        self.canvas = Canvas(
            self.root,
            width=1200,
            height=800,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill="both")

        # Initialize vehicle state
        self.vehicle = VehicleState()
        
        # Set up dashboard elements
        self._setup_dashboard()
        self._setup_controls()
        
        # Update rate (milliseconds)
        self.update_interval = 50

    def _setup_dashboard(self):
        """Initialize all dashboard components."""
        # Clock
        self.clock = ClockDisplay(self.root)
        self.clock.place(x=1000, y=20)

        # Gauges
        self.speedometer = GaugeDisplay(
            self.canvas, 400, 400, 150,
            225, -45, 200,
            "SPEED", "km/h", 160
        )
        
        self.tachometer = GaugeDisplay(
            self.canvas, 800, 400, 150,
            225, -45, 8000,
            "ENGINE", "RPM", 6400
        )

        # Status bars
        self.fuel_bar = LevelBar(
            self.canvas, 100, 300, 50, 300,
            "FUEL", {
                "normal": "#00ff00",
                "medium": "#ffff00",
                "low": "#ff0000"
            }
        )
        
        self.temp_bar = LevelBar(
            self.canvas, 1050, 300, 50, 300,
            "TEMP", {
                "normal": "#00ffff",
                "medium": "#ffa500",
                "low": "#ff0000"
            }
        )

        # Status indicators
        self.indicators = {
            "seatbelt": StatusIndicator(
                self.canvas, 100, 50,
                "Seat-Belt-Indicator.webp"
            ),
            "engine": StatusIndicator(
                self.canvas, 150, 50,
                "Check-Engine-Light.webp"
            ),
            "battery": StatusIndicator(
                self.canvas, 200, 50,
                "Battery-Charge-Warning-Light.webp"
            ),
            "lights": StatusIndicator(
                self.canvas, 250, 50,
                "Headlight-Range-Control.webp"
            ),
            "airbag": StatusIndicator(
                self.canvas, 300, 50,
                "Airbag-Indicator.webp"
            )
        }

    def _setup_controls(self):
        """Set up keyboard controls."""
        self.root.bind("<KeyPress-w>", lambda e: self._set_acceleration(True))
        self.root.bind("<KeyRelease-w>", lambda e: self._set_acceleration(False))
        
        # Indicator toggles
        for i, indicator in enumerate(self.indicators.values(), 1):
            self.root.bind(
                str(i),
                lambda e, ind=indicator: ind.set_state(not ind.is_active)
            )

    def _set_acceleration(self, accelerating: bool):
        """Update acceleration state."""
        self.vehicle.accelerating = accelerating

    def _update_vehicle_state(self):
        """Update vehicle parameters based on current state."""
        if self.vehicle.accelerating:
            self.vehicle.speed = min(200, self.vehicle.speed + 2)
            self.vehicle.rpm = min(8000, self.vehicle.rpm + 200)
            self.vehicle.temperature = min(100, self.vehicle.temperature + 0.5)
            self.vehicle.fuel = max(0, self.vehicle.fuel - 0.1)
        else:
            self.vehicle.speed = max(0, self.vehicle.speed - 1)
            self.vehicle.rpm = max(0, self.vehicle.rpm - 100)
            self.vehicle.temperature = max(50, self.vehicle.temperature - 0.2)

    def _check_warnings(self):
        """Check and update warning indicators."""
        warning_state = (
            self.vehicle.speed >= 160 or  # 80% of max speed
            self.vehicle.rpm >= 6400      # 80% of max RPM
        )
        
        for indicator in self.indicators.values():
            indicator.warning.set_visibility(warning_state)
            if warning_state:
                indicator.warning.blink()

    def update(self):
        """Main update loop."""
        self._update_vehicle_state()
        
        # Update displays
        self.speedometer.update(self.vehicle.speed)
        self.tachometer.update(self.vehicle.rpm)
        self.fuel_bar.update(self.vehicle.fuel)
        self.temp_bar.update(self.vehicle.temperature)
        
        # Check warning conditions
        self._check_warnings()
        
        # Schedule next update
        self.root.after(self.update_interval, self.update)

    def run(self):
        """Start the dashboard application."""
        self.update()
        self.root.mainloop()

if __name__ == "__main__":
    dashboard = CarDashboard()
    dashboard.run()