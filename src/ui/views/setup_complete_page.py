import customtkinter as ctk


class SetupCompletePage(ctk.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.controller = controller
        self.configure(fg_color=["#f8fafc", "#0f172a"])

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
            text_color=["#1e293b", "#f1f5f9"],
        )
        title.pack(pady=(0, 10))

        subtitle = ctk.CTkLabel(
            self,
            text="Your teams are ready to compete",
            font=ctk.CTkFont(size=16),
            text_color=["#64748b", "#94a3b8"],
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
            fg_color=["#10b981", "#059669"],
            hover_color=["#059669", "#047857"],
            text_color="white",
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
            fg_color=["#6b7280", "#4b5563"],
            hover_color=["#4b5563", "#374151"],
            text_color="white",
        )
        back_btn.pack(pady=10)
