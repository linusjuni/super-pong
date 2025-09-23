import customtkinter as ctk
from models.player import Player
from models.team import Team
from models.tournament import Tournament
from ui.colors import COLORS


class StartPage(ctk.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.controller = controller

        self.configure(fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark])

        # Title
        title = ctk.CTkLabel(
            self,
            text="🏆 Super Pong Tournament Setup",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
        )
        title.pack(pady=(30, 20))

        # Subtitle
        subtitle = ctk.CTkLabel(
            self,
            text="Create your teams and get ready to compete!",
            font=ctk.CTkFont(size=16),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        subtitle.pack(pady=(0, 30))

        # Scrollable container
        self.team_container = ctk.CTkScrollableFrame(
            self,
            fg_color=[COLORS.bg_secondary_light, COLORS.bg_secondary_dark],
            width=750,
            height=450,
            corner_radius=20,
            scrollbar_button_color=[COLORS.grey_primary, COLORS.grey_secondary],
            scrollbar_button_hover_color=[COLORS.grey_hover, COLORS.grey_hover],
        )
        self.team_container.pack(fill="both", expand=True, padx=30, pady=20)

        # Button container
        button_frame = ctk.CTkFrame(self, fg_color="transparent", height=120)
        button_frame.pack(fill="x", padx=30, pady=(0, 30))

        # Styled buttons
        add_team_btn = ctk.CTkButton(
            button_frame,
            text="➕ Add Team",
            command=self.add_team,
            width=200,
            height=45,
            corner_radius=25,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=[COLORS.blue_primary, COLORS.blue_secondary],
            hover_color=[COLORS.blue_hover, COLORS.blue_hover],
            text_color=COLORS.text_primary_light,
        )
        add_team_btn.pack(side="left", padx=(0, 15))

        start_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Start Tournament",
            command=self.start_tournament,
            width=220,
            height=45,
            corner_radius=25,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=[COLORS.green_primary, COLORS.green_secondary],
            hover_color=[COLORS.green_hover, COLORS.green_hover],
            text_color=COLORS.text_primary_light,
        )
        start_btn.pack(side="left", padx=15)

        reset_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Reset",
            command=self.reset_fields,
            width=200,
            height=45,
            corner_radius=25,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=[COLORS.red_primary, COLORS.red_secondary],
            hover_color=[COLORS.red_hover, COLORS.red_hover],
            text_color=COLORS.text_primary_light,
        )
        reset_btn.pack(side="left", padx=(15, 0))

        # Track the number of teams
        self.team_count = 0
        self.team_entries = []

    def add_team(self):
        """Add a new team entry section."""
        self.team_count += 1

        # Create a card-style frame for the team
        team_frame = ctk.CTkFrame(
            self.team_container,
            fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
            corner_radius=15,
            border_width=2,
            border_color=[COLORS.grey_primary, COLORS.grey_secondary],
        )
        team_frame.pack(fill="x", pady=15, padx=20)
        team_frame.grid_columnconfigure(1, weight=1)

        # Team header
        header_frame = ctk.CTkFrame(
            team_frame, fg_color=[COLORS.bg_secondary_light, COLORS.bg_secondary_dark], corner_radius=10, height=40
        )
        header_frame.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 15)
        )

        team_header = ctk.CTkLabel(
            header_frame,
            text=f"Team {self.team_count}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
        )
        team_header.pack(pady=8)

        # Team name entry
        team_label = ctk.CTkLabel(
            team_frame,
            text="Team Name:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        team_label.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="w")

        team_name_entry = ctk.CTkEntry(
            team_frame,
            width=300,
            height=35,
            corner_radius=10,
            border_width=2,
            border_color=[COLORS.grey_primary, COLORS.grey_secondary],
            fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
            placeholder_text="Enter team name...",
            font=ctk.CTkFont(size=14),
        )
        team_name_entry.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="ew")

        # Player 1 entry
        player1_label = ctk.CTkLabel(
            team_frame,
            text="Player 1:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        player1_label.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="w")

        player1_entry = ctk.CTkEntry(
            team_frame,
            width=300,
            height=35,
            corner_radius=10,
            border_width=2,
            border_color=[COLORS.grey_primary, COLORS.grey_secondary],
            fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
            placeholder_text="Enter player 1 name...",
            font=ctk.CTkFont(size=14),
        )
        player1_entry.grid(row=2, column=1, padx=(10, 20), pady=10, sticky="ew")

        # Player 2 entry
        player2_label = ctk.CTkLabel(
            team_frame,
            text="Player 2:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        player2_label.grid(row=3, column=0, padx=(20, 10), pady=10, sticky="w")

        player2_entry = ctk.CTkEntry(
            team_frame,
            width=300,
            height=35,
            corner_radius=10,
            border_width=2,
            border_color=[COLORS.grey_primary, COLORS.grey_secondary],
            fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
            placeholder_text="Enter player 2 name...",
            font=ctk.CTkFont(size=14),
        )
        player2_entry.grid(row=3, column=1, padx=(10, 20), pady=10, sticky="ew")

        # Lock-in toggle frame
        toggle_frame = ctk.CTkFrame(team_frame, fg_color="transparent")
        toggle_frame.grid(row=4, column=0, columnspan=2, pady=(15, 25))

        # Lock-in status label
        status_label = ctk.CTkLabel(
            toggle_frame,
            text="Team Status:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        status_label.pack(side="left", padx=(0, 10))

        # Lock-in toggle switch
        lock_toggle = ctk.CTkSwitch(
            toggle_frame,
            text="🔒 Lock In Team",
            command=lambda: self.toggle_team_lock(
                team_frame,
                team_name_entry,
                player1_entry,
                player2_entry,
                lock_toggle,
                status_indicator,
            ),
            width=120,
            font=ctk.CTkFont(size=14, weight="bold"),
            progress_color=[COLORS.green_primary, COLORS.green_secondary],
            button_color=[COLORS.grey_primary, COLORS.grey_secondary],
            button_hover_color=[COLORS.grey_hover, COLORS.grey_hover],
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        lock_toggle.pack(side="left", padx=10)

        # Status indicator
        status_indicator = ctk.CTkLabel(
            toggle_frame,
            text="🔓 Not Locked",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=[COLORS.red_secondary, COLORS.red_primary],
        )
        status_indicator.pack(side="left", padx=(10, 0))

        # Store the entries and frame for later use
        self.team_entries.append(
            {
                "frame": team_frame,
                "team_name": team_name_entry,
                "player1": player1_entry,
                "player2": player2_entry,
                "lock_toggle": lock_toggle,
                "status_indicator": status_indicator,
                "locked": False,
            }
        )

    def toggle_team_lock(self, team_frame, team_name_entry, player1_entry, player2_entry, lock_toggle, status_indicator):
        """Handle the team lock toggle."""
        is_locked = lock_toggle.get()
        
        # Find the team entry
        team_entry = None
        for entry in self.team_entries:
            if entry["lock_toggle"] == lock_toggle:
                team_entry = entry
                break
        
        if not team_entry:
            return
        
        # Validate fields before locking
        if is_locked:
            team_name = team_name_entry.get().strip()
            player1_name = player1_entry.get().strip()
            player2_name = player2_entry.get().strip()
            
            if not team_name or not player1_name or not player2_name:
                # Reset toggle and show error
                lock_toggle.deselect()
                self.show_error("Please fill in all fields before locking!")
                return
        
        if is_locked:
            # Lock the team
            team_name_entry.configure(state="disabled")
            player1_entry.configure(state="disabled")
            player2_entry.configure(state="disabled")
            
            # Change frame appearance to locked state
            team_frame.configure(
                fg_color=["#dcfce7", "#1f2937"],
                border_color=[COLORS.green_primary, COLORS.green_secondary],
            )
            
            # Update status indicator
            status_indicator.configure(
                text="🔒 Locked In",
                text_color=["#15803d", "#22c55e"]
            )
            
            # Update toggle text
            lock_toggle.configure(text="🔓 Unlock Team")
            
        else:
            # Unlock the team
            team_name_entry.configure(state="normal")
            player1_entry.configure(state="normal")
            player2_entry.configure(state="normal")
            
            # Reset frame appearance
            team_frame.configure(
                fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
                border_color=[COLORS.grey_primary, COLORS.grey_secondary],
            )
            
            # Update status indicator
            status_indicator.configure(
                text="🔓 Not Locked",
                text_color=[COLORS.red_secondary, COLORS.red_primary]
            )
            
            # Update toggle text
            lock_toggle.configure(text="🔒 Lock In Team")
        
        # Update the stored state
        team_entry["locked"] = is_locked

    def start_tournament(self):
        """Start the tournament with proper team creation."""
        teams_data = []
        locked_teams = 0

        for team in self.team_entries:
            team_name = team["team_name"].get().strip()
            player1_name = team["player1"].get().strip()
            player2_name = team["player2"].get().strip()

            if team_name and player1_name and player2_name:
                teams_data.append({
                    "team_name": team_name,
                    "player1_name": player1_name,
                    "player2_name": player2_name,
                    "locked": team["locked"],
                })
                if team["locked"]:
                    locked_teams += 1

        if len(teams_data) < 2:
            self.show_error("Need at least 2 teams to start tournament!")
            return

        if locked_teams != len(teams_data):
            self.show_error("Please lock in all teams before starting!")
            return

        # Create the tournament
        tournament = Tournament("Super Pong Tournament")
        
        # Create Player and Team objects
        created_teams = []
        for team_data in teams_data:
            # Create player objects
            player1 = Player(team_data["player1_name"])
            player2 = Player(team_data["player2_name"])
            
            # Create team object
            team = Team(player1, player2, team_data["team_name"])
            created_teams.append(team)
            
            # Add team to tournament
            tournament.add_team(team)

        # Start the tournament
        tournament.start_tournament()
        
        # Store in app state
        self.controller.app_state.tournament = tournament

        print(f"Successfully created tournament with {len(created_teams)} teams:")
        for team in created_teams:
            print(f"  Team: {team.name}")
            print(f"    Players: {team.player1.name}, {team.player2.name}")

        # Navigate to the next page    
        self.controller.show_frame("SetupCompletePage")

    def show_error(self, message):
        """Show an error message with modern styling."""
        error_frame = ctk.CTkFrame(
            self,
            fg_color=[COLORS.error_bg_light, COLORS.error_bg_dark],
            corner_radius=15,
            border_width=2,
            border_color=[COLORS.error_border_light, COLORS.error_border_dark],
        )
        error_frame.place(relx=0.5, rely=0.5, anchor="center")

        error_label = ctk.CTkLabel(
            error_frame,
            text=f"⚠️ {message}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=[COLORS.red_secondary, COLORS.red_primary],
        )
        error_label.pack(padx=30, pady=20)

        # Auto-dismiss after 2 seconds
        self.after(2000, error_frame.destroy)

    def reset_fields(self):
        """Reset all fields and remove all dynamic team entries."""
        for widget in self.team_container.winfo_children():
            widget.destroy()
        self.team_entries = []
        self.team_count = 0
