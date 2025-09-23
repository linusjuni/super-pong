import customtkinter as ctk
from ui.colors import COLORS


class SetupCompletePage(ctk.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.controller = controller
        self.configure(fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark])

        # Success icon and title
        success_label = ctk.CTkLabel(
            self,
            text="🎉",
            font=ctk.CTkFont(size=80),
        )
        success_label.pack(pady=(50, 20))

        title = ctk.CTkLabel(
            self,
            text="Tournament Setup Complete!",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
        )
        title.pack(pady=(0, 10))

        subtitle = ctk.CTkLabel(
            self,
            text="Your teams are ready to compete",
            font=ctk.CTkFont(size=16),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        subtitle.pack(pady=(0, 50))

        # Action buttons
        start_games_btn = ctk.CTkButton(
            self,
            text="🎯 Start Games",
            width=250,
            height=50,
            corner_radius=25,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=[COLORS.green_primary, COLORS.green_secondary],
            hover_color=[COLORS.green_hover, COLORS.green_hover],
            text_color=COLORS.text_primary_light,
        )
        start_games_btn.pack(pady=20)

        back_btn = ctk.CTkButton(
            self,
            text="← Back to Setup",
            command=lambda: self.controller.show_frame("StartPage"),
            width=200,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=14),
            fg_color=[COLORS.grey_primary, COLORS.grey_secondary],
            hover_color=[COLORS.grey_hover, COLORS.grey_hover],
            text_color=COLORS.text_primary_light,
        )
        back_btn.pack(pady=10)
