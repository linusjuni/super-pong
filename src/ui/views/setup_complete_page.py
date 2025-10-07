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
        success_label.pack(pady=(30, 20))

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
        subtitle.pack(pady=(0, 20))

        # Action buttons
        start_games_btn = ctk.CTkButton(
            self,
            text="🎯 Start Games",
            command=lambda: self.controller.show_frame("GamePlayPage"),
            width=250,
            height=50,
            corner_radius=25,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=[COLORS.green_primary, COLORS.green_secondary],
            hover_color=[COLORS.green_hover, COLORS.green_hover],
            text_color=COLORS.text_primary_light,
        )
        start_games_btn.pack(pady=10)

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
        back_btn.pack(pady=(10,20))

        # Container for the round-robin schedule
        self.rounds_container = ctk.CTkScrollableFrame(
            self,
            fg_color=[COLORS.bg_secondary_light, COLORS.bg_secondary_dark],
            width=650,
            height=350,
            corner_radius=18,
            scrollbar_button_color=[COLORS.grey_primary, COLORS.grey_secondary],
            scrollbar_button_hover_color=[COLORS.grey_hover, COLORS.grey_hover],
        )
        self.rounds_container.pack(fill="both", expand=True, padx=40, pady=(20, 40))

    def on_show(self):
        self.render_schedule()

    def render_schedule(self):
        """Render the scheduled round-robin games."""
        for widget in self.rounds_container.winfo_children():
            widget.destroy()

        tournament = self.controller.app_state.tournament

        for round_index, games in enumerate(tournament.rounds, start=1):
            round_card = ctk.CTkFrame(
                self.rounds_container,
                fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
                corner_radius=16,
                border_width=2,
                border_color=[COLORS.grey_primary, COLORS.grey_secondary],
            )
            round_card.pack(fill="x", padx=20, pady=(10, 20))

            header = ctk.CTkLabel(
                round_card,
                text=f"Round {round_index}",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
                anchor="center",
            )
            header.pack(fill="x", padx=20, pady=(20, 0))

            if not games:
                bye_label = ctk.CTkLabel(
                    round_card,
                    text="Bye round",
                    font=ctk.CTkFont(size=14),
                    text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
                )
                bye_label.pack(padx=20, pady=(0, 20))
                continue

            for idx, game in enumerate(games):
                matchup_label = ctk.CTkLabel(
                    round_card,
                    text=f"{game.team1.name} VS {game.team2.name}",
                    font=ctk.CTkFont(size=16),
                    text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
                    anchor="center",
                )
                if idx == len(games)-1:
                    matchup_label.pack(fill="x", padx=30, pady=(0,20))
                else:
                    matchup_label.pack(fill="x", padx=30, pady=(0,0))
