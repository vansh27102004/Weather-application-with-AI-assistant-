import customtkinter as ctk
import requests
from PIL import Image, ImageTk
import tkinter as tk
import datetime
import threading
import sys

class AnimatedGIFLabel(tk.Label):
    def __init__(self, master, gif_path):
        super().__init__(master)
        self.master = master
        self.gif_path = gif_path
        self.original_frames = []
        self.resized_frames = []
        self.photo_frames = []
        self.current_frame = 0
        self.animation_id = None
        self.is_animating = False
        self.resize_after_id = None
        self.master.bind("<Configure>", self.on_resize)
        threading.Thread(target=self.load_frames_thread, daemon=True).start()

    def load_frames_thread(self):
        img = Image.open(self.gif_path)
        frames = []
        try:
            while True:
                frames.append(img.copy())
                img.seek(len(frames))
        except EOFError:
            pass
        self.original_frames = frames
        self.master.after(0, self.resize_frames_main_thread)

    def resize_frames_main_thread(self):
        w = self.master.winfo_width() or 1
        h = self.master.winfo_height() or 1
        self.resized_frames = [f.resize((w, h), Image.LANCZOS) for f in self.original_frames]
        self.photo_frames = [ImageTk.PhotoImage(img) for img in self.resized_frames]
        if not self.is_animating:
            self.start_animation()

    def animate(self):
        if not self.is_animating or not self.photo_frames or not self.winfo_exists():
            return
        self.config(image=self.photo_frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.photo_frames)
        self.animation_id = self.after(100, self.animate)

    def start_animation(self):
        self.is_animating = True
        self.animate()

    def on_resize(self, event):
        if self.resize_after_id:
            self.after_cancel(self.resize_after_id)
        self.resize_after_id = self.after(200, self.resize_frames_main_thread)

    def stop_animation(self):
        self.is_animating = False
        if self.animation_id:
            self.after_cancel(self.animation_id)

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Weather App")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.bg_label = AnimatedGIFLabel(root, "weather_bg.gif")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.city_name = ctk.StringVar()


#################################################################


        if len(sys.argv) > 1:
            self.city_name.set(sys.argv[1])
            self.data_get()



        # Make the main frame transparent-like by setting fg_color=None
        self.frame = ctk.CTkFrame(root, fg_color=None, corner_radius=0)
        # Small frame in middle, no bg color to keep transparency illusion
        self.frame.place(relx=0.35, rely=0.15, relwidth=0.3, relheight=0.7)

        # Title Label - Black, bold, larger font
        title = ctk.CTkLabel(
            self.frame,
            text="🌦 Weather App",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="black",
            fg_color=None,
        )
        title.pack(pady=(20, 10))

        # ComboBox - text black, transparent background
        self.combo = ctk.CTkComboBox(
            self.frame,
            variable=self.city_name,
            values=["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata"],
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=None,
            dropdown_fg_color="white",
            dropdown_text_color="black",
            text_color="black",
            width=260,
        )
        self.combo.pack(pady=(0, 15))

        # Button - black bg with white text, no border/background behind frame
        self.button = ctk.CTkButton(
            self.frame,
            text="Get Weather",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self.data_get,
            fg_color="black",
            text_color="white",
            hover_color="#222222",
            border_width=0,
            corner_radius=8,
        )
        self.button.pack(pady=(0, 20))

        # Icon Label (for weather icon)
        self.icon_label = ctk.CTkLabel(self.frame, text="", fg_color=None)
        self.icon_label.pack(pady=(0, 15))

        # Data Frame to hold weather info labels, transparent
        self.data_frame = ctk.CTkFrame(self.frame, fg_color=None)
        self.data_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))

        self.result_labels = {}
        self.fields = [
            "Weather",
            "Description",
            "Temperature",
            "Pressure",
            "Humidity",
            "Wind Speed",
            "Sunrise",
            "Sunset",
        ]

        label_font = ctk.CTkFont(size=16, weight="bold")

        for i, field in enumerate(self.fields):
            label_text = f"{field}:"
            # Label on left (black text, transparent bg)
            label = ctk.CTkLabel(
                self.data_frame,
                text=label_text,
                font=label_font,
                text_color="black",
                fg_color=None,
            )
            label.grid(row=i, column=0, sticky="w", pady=5, padx=(0, 10))

            # Value label on right (black text, transparent bg)
            value_label = ctk.CTkLabel(
                self.data_frame,
                text="---",
                font=label_font,
                text_color="black",
                fg_color=None,
            )
            value_label.grid(row=i, column=1, sticky="w", pady=5)
            self.result_labels[field] = value_label

        self.data_frame.grid_columnconfigure(1, weight=1)

    def data_get(self):
        city = self.city_name.get()
        if not city:
            return

        def fetch_weather():
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=2894fe5fb6d0d510ab4faa71f8bd8913"
                data = requests.get(url).json()

                weather = data["weather"][0]["main"].capitalize()
                desc = data["weather"][0]["description"].capitalize()
                temp = int(data["main"]["temp"] - 273.15)
                pressure = data["main"]["pressure"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]

                sunrise_unix = data["sys"]["sunrise"]
                sunset_unix = data["sys"]["sunset"]
                sunrise_time = datetime.datetime.fromtimestamp(sunrise_unix).strftime("%I:%M %p")
                sunset_time = datetime.datetime.fromtimestamp(sunset_unix).strftime("%I:%M %p")

                icon_code = data["weather"][0]["icon"]
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                icon_response = requests.get(icon_url, stream=True)
                icon_img_pil = Image.open(icon_response.raw).copy()

                def update_ui():
                    self.result_labels["Weather"].configure(text=weather)
                    self.result_labels["Description"].configure(text=desc)
                    self.result_labels["Temperature"].configure(text=f"{temp} °C")
                    self.result_labels["Pressure"].configure(text=f"{pressure} hPa")
                    self.result_labels["Humidity"].configure(text=f"{humidity}%")
                    self.result_labels["Wind Speed"].configure(text=f"{wind_speed} m/s")
                    self.result_labels["Sunrise"].configure(text=sunrise_time)
                    self.result_labels["Sunset"].configure(text=sunset_time)

                    icon_img = ImageTk.PhotoImage(icon_img_pil)
                    self.icon_label.configure(image=icon_img)
                    self.icon_label.image = icon_img

                self.root.after(0, update_ui)

            except Exception:
                def update_error():
                    for lbl in self.result_labels.values():
                        lbl.configure(text="Error fetching data")
                    self.icon_label.configure(image="")
                self.root.after(0, update_error)

        threading.Thread(target=fetch_weather, daemon=True).start()



if __name__ == "__main__":
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()
