import customtkinter as ctk
from ui.app_state import AppState
from ui.views.start_page import StartPage
from ui.views.setup_complete_page import SetupCompletePage


class SuperPongApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🏓 Super Pong Tournament")
        self.geometry("900x900")
        self.resizable(True, True)
        self.minsize(800, 700)

        # Background
        self.configure(fg_color=["#f8fafc", "#0f172a"])

        # Central application state
        self.app_state = AppState()

        # Container for all frames
        container = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, SetupCompletePage):
            name = F.__name__
            frame = F(container, controller=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[name] = frame

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    app = SuperPongApp()
    app.mainloop()
