import customtkinter as ctk
from ui.colors import COLORS


class GamePlayPage(ctk.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.controller = controller
        self.configure(fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark])

        # Track current shot in the turn (1 or 2)
        self.current_shot = 1
        self.shot_history = []  # Store shots for current turn

        # Main container with padding
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)

        # ===== GAME INFO SECTION =====
        self.create_game_info_section(main_container)

        # ===== SHOT INPUT FORM (Main Focus) =====
        self.create_shot_input_form(main_container)

        # ===== TURN RESULTS SECTION =====
        self.create_turn_results_section(main_container)

        # ===== NAVIGATION BUTTONS =====
        self.create_navigation_buttons(main_container)

    def create_game_info_section(self, parent):
        """Display current game information with team scores."""
        info_frame = ctk.CTkFrame(
            parent,
            fg_color=[COLORS.bg_secondary_light, COLORS.bg_secondary_dark],
            corner_radius=12,
            border_width=2,
            border_color=[COLORS.grey_primary, COLORS.grey_secondary],
        )
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        info_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Team 1 Info
        team1_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        team1_container.grid(row=0, column=0, padx=15, pady=12)

        self.team1_name_label = ctk.CTkLabel(
            team1_container,
            text="Team Alpha",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
        )
        self.team1_name_label.pack()

        self.team1_players_label = ctk.CTkLabel(
            team1_container,
            text="Player 1 & Player 2",
            font=ctk.CTkFont(size=11),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        self.team1_players_label.pack(pady=(3, 5))

        self.team1_cups_label = ctk.CTkLabel(
            team1_container,
            text="🥤 10",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=[COLORS.green_primary, COLORS.green_secondary],
        )
        self.team1_cups_label.pack()

        # VS Divider
        vs_label = ctk.CTkLabel(
            info_frame,
            text="VS",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        vs_label.grid(row=0, column=1, padx=15, pady=12)

        # Team 2 Info
        team2_container = ctk.CTkFrame(info_frame, fg_color="transparent")
        team2_container.grid(row=0, column=2, padx=15, pady=12)

        self.team2_name_label = ctk.CTkLabel(
            team2_container,
            text="Team Beta",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
        )
        self.team2_name_label.pack()

        self.team2_players_label = ctk.CTkLabel(
            team2_container,
            text="Player 3 & Player 4",
            font=ctk.CTkFont(size=11),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        self.team2_players_label.pack(pady=(3, 5))

        self.team2_cups_label = ctk.CTkLabel(
            team2_container,
            text="🥤 10",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=[COLORS.green_primary, COLORS.green_secondary],
        )
        self.team2_cups_label.pack()

    def create_shot_input_form(self, parent):
        """Main shot tracking form - the core functionality."""
        form_frame = ctk.CTkFrame(
            parent,
            fg_color=[COLORS.bg_secondary_light, COLORS.bg_secondary_dark],
            corner_radius=18,
            border_width=3,
            border_color=[COLORS.blue_primary, COLORS.blue_secondary],
        )
        form_frame.grid(row=1, column=0, sticky="ew", pady=15)
        form_frame.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(
            form_frame,
            fg_color=[COLORS.blue_primary, COLORS.blue_secondary],
            corner_radius=15,
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=3, pady=3)

        self.shot_header_label = ctk.CTkLabel(
            header_frame,
            text="📝 Recording Shot 1 of 2",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS.text_primary_light,
        )
        self.shot_header_label.pack(pady=15)

        # Form content container
        content_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=(10, 25))
        content_frame.grid_columnconfigure(1, weight=1)

        # ===== TEAM SELECTION =====
        team_label = ctk.CTkLabel(
            content_frame,
            text="Shooting Team:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
            anchor="w",
        )
        team_label.grid(row=0, column=0, sticky="w", pady=(10, 5))

        self.team_var = ctk.StringVar(value="Team 1")
        self.team_selector = ctk.CTkSegmentedButton(
            content_frame,
            values=["Team 1", "Team 2"],
            variable=self.team_var,
            command=self.on_team_selected,
            height=40,
            corner_radius=10,
            fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
            selected_color=[COLORS.blue_primary, COLORS.blue_secondary],
            selected_hover_color=[COLORS.blue_hover, COLORS.blue_hover],
            unselected_color=[COLORS.grey_primary, COLORS.grey_secondary],
            unselected_hover_color=[COLORS.grey_hover, COLORS.grey_hover],
            text_color=COLORS.text_primary_light,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.team_selector.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # ===== PLAYER SELECTION =====
        player_label = ctk.CTkLabel(
            content_frame,
            text="Player:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
            anchor="w",
        )
        player_label.grid(row=2, column=0, sticky="w", pady=(10, 5))

        self.player_var = ctk.StringVar(value="")  # Start with no selection
        self.player_selector = ctk.CTkSegmentedButton(
            content_frame,
            values=["Player 1", "Player 2"],
            variable=self.player_var,
            height=40,
            corner_radius=10,
            fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
            selected_color=[COLORS.blue_primary, COLORS.blue_secondary],
            selected_hover_color=[COLORS.blue_hover, COLORS.blue_hover],
            unselected_color=[COLORS.grey_primary, COLORS.grey_secondary],
            unselected_hover_color=[COLORS.grey_hover, COLORS.grey_hover],
            text_color=COLORS.text_primary_light,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.player_selector.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # ===== SHOT TYPE SELECTION =====
        shot_type_label = ctk.CTkLabel(
            content_frame,
            text="Shot Type:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
            anchor="w",
        )
        shot_type_label.grid(row=4, column=0, sticky="w", pady=(10, 5))

        self.shot_type_var = ctk.StringVar(value="Normal")
        shot_type_selector = ctk.CTkSegmentedButton(
            content_frame,
            values=["Normal", "Bounce", "Trickshot"],
            variable=self.shot_type_var,
            command=self.on_shot_type_changed,
            height=40,
            corner_radius=10,
            fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
            selected_color=[COLORS.green_primary, COLORS.green_secondary],
            selected_hover_color=[COLORS.green_hover, COLORS.green_hover],
            unselected_color=[COLORS.grey_primary, COLORS.grey_secondary],
            unselected_hover_color=[COLORS.grey_hover, COLORS.grey_hover],
            text_color=COLORS.text_primary_light,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        shot_type_selector.grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )
        
        # ===== BOUNCE COUNT SELECTION (only shown for bounce shots) =====
        self.bounce_count_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        self.bounce_count_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.bounce_count_frame.grid_remove()  # Hide by default
        
        bounce_count_label = ctk.CTkLabel(
            self.bounce_count_frame,
            text="Number of Bounces:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
            anchor="w",
        )
        bounce_count_label.pack(side="left", padx=(0, 15))
        
        self.bounce_count_var = ctk.StringVar(value="1")
        bounce_count_menu = ctk.CTkOptionMenu(
            self.bounce_count_frame,
            values=["1", "2", "3", "4", "5"],
            variable=self.bounce_count_var,
            width=100,
            height=35,
            corner_radius=10,
            fg_color=[COLORS.green_primary, COLORS.green_secondary],
            button_color=[COLORS.green_secondary, COLORS.green_primary],
            button_hover_color=[COLORS.green_hover, COLORS.green_hover],
            dropdown_fg_color=[COLORS.bg_secondary_light, COLORS.bg_secondary_dark],
            text_color=COLORS.text_primary_light,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        bounce_count_menu.pack(side="left")

        # ===== OUTCOME SELECTION =====
        outcome_label = ctk.CTkLabel(
            content_frame,
            text="Outcome:",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
            anchor="w",
        )
        outcome_label.grid(row=7, column=0, sticky="w", pady=(10, 5))

        self.outcome_var = ctk.StringVar(value="Miss")

        # Outcome buttons in a grid
        outcome_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        outcome_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        outcome_frame.grid_columnconfigure((0, 1, 2), weight=1)

        hit_btn = ctk.CTkButton(
            outcome_frame,
            text="✅ Hit",
            command=lambda: self.outcome_var.set("Hit"),
            height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=[COLORS.green_primary, COLORS.green_secondary],
            hover_color=[COLORS.green_hover, COLORS.green_hover],
            text_color=COLORS.text_primary_light,
            border_width=3,
            border_color=[COLORS.green_primary, COLORS.green_secondary],
        )
        hit_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        miss_btn = ctk.CTkButton(
            outcome_frame,
            text="❌ Miss",
            command=lambda: self.outcome_var.set("Miss"),
            height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=[COLORS.red_primary, COLORS.red_secondary],
            hover_color=[COLORS.red_hover, COLORS.red_hover],
            text_color=COLORS.text_primary_light,
            border_width=3,
            border_color=[COLORS.red_primary, COLORS.red_secondary],
        )
        miss_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        rim_btn = ctk.CTkButton(
            outcome_frame,
            text="🎯 Rim",
            command=lambda: self.outcome_var.set("Rim"),
            height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=[COLORS.grey_primary, COLORS.grey_secondary],
            hover_color=[COLORS.grey_hover, COLORS.grey_hover],
            text_color=COLORS.text_primary_light,
            border_width=3,
            border_color=[COLORS.grey_primary, COLORS.grey_secondary],
        )
        rim_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Store button references to update border colors
        self.outcome_buttons = {
            "Hit": hit_btn,
            "Miss": miss_btn,
            "Rim": rim_btn,
        }        # Add trace to update button appearances
        self.outcome_var.trace_add("write", self.update_outcome_buttons)

        # ===== RECORD SHOT BUTTON =====
        self.record_btn = ctk.CTkButton(
            content_frame,
            text="📊 Record Shot",
            command=self.record_shot,
            height=50,
            corner_radius=25,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=[COLORS.green_primary, COLORS.green_secondary],
            hover_color=[COLORS.green_hover, COLORS.green_hover],
            text_color=COLORS.text_primary_light,
        )
        self.record_btn.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def create_turn_results_section(self, parent):
        """Display the results of recorded shots in the current turn."""
        results_frame = ctk.CTkFrame(
            parent,
            fg_color=[COLORS.bg_secondary_light, COLORS.bg_secondary_dark],
            corner_radius=18,
            border_width=3,
            border_color=[COLORS.blue_primary, COLORS.blue_secondary],
        )
        results_frame.grid(row=2, column=0, sticky="nsew", pady=15)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)

        # Header with more prominent styling
        header_container = ctk.CTkFrame(
            results_frame,
            fg_color=[COLORS.blue_primary, COLORS.blue_secondary],
            corner_radius=15,
        )
        header_container.grid(row=0, column=0, sticky="ew", padx=3, pady=3)
        
        results_header = ctk.CTkLabel(
            header_container,
            text="📋 Current Turn Summary",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS.text_primary_light,
        )
        results_header.pack(pady=15, padx=20)

        # Scrollable results container with minimum height
        self.results_container = ctk.CTkScrollableFrame(
            results_frame,
            fg_color=[COLORS.bg_primary_light, COLORS.bg_primary_dark],
            corner_radius=12,
            scrollbar_button_color=[COLORS.grey_primary, COLORS.grey_secondary],
            scrollbar_button_hover_color=[COLORS.grey_hover, COLORS.grey_hover],
            height=200,  # Set minimum height to make it visible
        )
        self.results_container.grid(
            row=1, column=0, sticky="nsew", padx=20, pady=(10, 20)
        )

        # Initial empty state
        self.empty_state_label = ctk.CTkLabel(
            self.results_container,
            text="No shots recorded yet\nRecord your first shot above!",
            font=ctk.CTkFont(size=14),
            text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
        )
        self.empty_state_label.pack(pady=40)

    def create_navigation_buttons(self, parent):
        """Navigation and action buttons."""
        nav_frame = ctk.CTkFrame(parent, fg_color="transparent")
        nav_frame.grid(row=3, column=0, sticky="ew", pady=(15, 0))

        # Submit Turn button (visible when 2 shots recorded)
        self.submit_turn_btn = ctk.CTkButton(
            nav_frame,
            text="✅ Submit Turn",
            command=self.submit_turn,
            width=250,
            height=50,
            corner_radius=25,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=[COLORS.blue_primary, COLORS.blue_secondary],
            hover_color=[COLORS.blue_hover, COLORS.blue_hover],
            text_color=COLORS.text_primary_light,
            state="disabled",
        )
        self.submit_turn_btn.pack(side="left", padx=(0, 10))

        # Clear Turn button
        clear_turn_btn = ctk.CTkButton(
            nav_frame,
            text="🔄 Clear Turn",
            command=self.clear_turn,
            width=200,
            height=50,
            corner_radius=25,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=[COLORS.grey_primary, COLORS.grey_secondary],
            hover_color=[COLORS.grey_hover, COLORS.grey_hover],
            text_color=COLORS.text_primary_light,
        )
        clear_turn_btn.pack(side="left", padx=10)

        # Back button
        back_btn = ctk.CTkButton(
            nav_frame,
            text="← Back",
            command=lambda: self.controller.show_frame("SetupCompletePage"),
            width=150,
            height=50,
            corner_radius=25,
            font=ctk.CTkFont(size=14),
            fg_color=[COLORS.red_primary, COLORS.red_secondary],
            hover_color=[COLORS.red_hover, COLORS.red_hover],
            text_color=COLORS.text_primary_light,
        )
        back_btn.pack(side="right")

    # ===== EVENT HANDLERS =====

    def on_team_selected(self, team_name):
        """Update player options when team is selected."""
        game = self.controller.app_state.game
        if not game:
            return
        
        # Find the selected team by name
        selected_team = game.team1 if team_name == game.team1.name else game.team2
        self.update_player_selector_for_team(selected_team)
    
    def update_player_selector_for_team(self, team):
        """Update player selector with the given team's players."""
        player_names = [team.player1.name, team.player2.name]
        self.player_selector.configure(values=player_names)
        # Clear player selection so user must choose
        self.player_var.set("")
    
    def on_shot_type_changed(self, shot_type):
        """Show/hide bounce count selector based on shot type."""
        if shot_type == "Bounce":
            self.bounce_count_frame.grid()
        else:
            self.bounce_count_frame.grid_remove()
    
    def update_outcome_buttons(self, *args):
        """Update button borders to show which outcome is selected."""
        selected = self.outcome_var.get()
        
        # Color mapping for unselected state
        default_colors = {
            "Hit": [COLORS.green_primary, COLORS.green_secondary],
            "Miss": [COLORS.red_primary, COLORS.red_secondary],
            "Rim": [COLORS.grey_primary, COLORS.grey_secondary],
        }
        
        for outcome, button in self.outcome_buttons.items():
            if outcome == selected:
                # Highlight selected button with white border
                button.configure(border_color=COLORS.text_primary_light)
            else:
                # Reset border to match button color (less prominent)
                button.configure(border_color=default_colors[outcome])

    def record_shot(self):
        """Record a single shot and update the UI."""
        # Validate all required fields are filled
        if not self.player_var.get():
            self.show_error_message("Please select a player!")
            return
        if not self.shot_type_var.get():
            self.show_error_message("Please select a shot type!")
            return
        if not self.outcome_var.get():
            self.show_error_message("Please select an outcome!")
            return
        
        shot_data = {
            "shot_number": self.current_shot,
            "team": self.team_var.get(),
            "player": self.player_var.get(),
            "shot_type": self.shot_type_var.get(),
            "outcome": self.outcome_var.get(),
            "bounces": int(self.bounce_count_var.get()) if self.shot_type_var.get() == "Bounce" else None,
        }

        self.shot_history.append(shot_data)
        self.update_results_display()

        # Move to next shot or enable submit
        if self.current_shot == 1:
            self.current_shot = 2
            self.shot_header_label.configure(text="📝 Recording Shot 2 of 2")
            self.record_btn.configure(text="📊 Record Final Shot")
        else:
            # Both shots recorded, enable submit
            self.record_btn.configure(state="disabled")
            self.submit_turn_btn.configure(state="normal")
            self.shot_header_label.configure(
                text="✅ Turn Complete - Ready to Submit",
                text_color=[COLORS.green_primary, COLORS.green_secondary],
            )

    def update_results_display(self):
        """Update the turn results display with recorded shots."""
        # Clear existing content
        for widget in self.results_container.winfo_children():
            widget.destroy()

        if not self.shot_history:
            self.empty_state_label = ctk.CTkLabel(
                self.results_container,
                text="No shots recorded yet\nRecord your first shot above!",
                font=ctk.CTkFont(size=14),
                text_color=[COLORS.text_secondary_dark, COLORS.text_secondary_light],
            )
            self.empty_state_label.pack(pady=40)
            return

        # Display each recorded shot
        for shot in self.shot_history:
            shot_frame = ctk.CTkFrame(
                self.results_container,
                fg_color=[COLORS.bg_secondary_light, COLORS.bg_secondary_dark],
                corner_radius=12,
                border_width=2,
                border_color=[COLORS.blue_primary, COLORS.blue_secondary],
            )
            shot_frame.pack(fill="x", padx=10, pady=8)

            # Shot number badge
            badge_color = (
                [COLORS.blue_primary, COLORS.blue_secondary]
                if shot["shot_number"] == 1
                else [COLORS.green_primary, COLORS.green_secondary]
            )
            shot_badge = ctk.CTkLabel(
                shot_frame,
                text=f"Shot {shot['shot_number']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=badge_color,
                corner_radius=8,
                text_color=COLORS.text_primary_light,
                width=80,
                height=40,
            )
            shot_badge.pack(side="left", padx=15, pady=15)

            # Shot details
            shot_type_text = shot['shot_type']
            if shot['shot_type'] == "Bounce" and shot.get('bounces'):
                shot_type_text = f"{shot['shot_type']} ({shot['bounces']}x)"
            details_text = f"{shot['team']} - {shot['player']} | {shot_type_text} shot"
            outcome_icon = (
                "✅"
                if shot["outcome"] == "Hit"
                else "❌"
                if shot["outcome"] == "Miss"
                else "🎯"
            )

            details_label = ctk.CTkLabel(
                shot_frame,
                text=f"{outcome_icon} {details_text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=[COLORS.text_primary_dark, COLORS.text_primary_light],
                anchor="w",
            )
            details_label.pack(side="left", padx=10, pady=15, fill="x", expand=True)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                shot_frame,
                text="🗑️",
                command=lambda s=shot: self.delete_shot(s),
                width=40,
                height=40,
                corner_radius=8,
                font=ctk.CTkFont(size=16),
                fg_color=[COLORS.red_primary, COLORS.red_secondary],
                hover_color=[COLORS.red_hover, COLORS.red_hover],
                text_color=COLORS.text_primary_light,
            )
            delete_btn.pack(side="right", padx=(5, 15), pady=15)
            
            # Outcome badge
            outcome_colors = {
                "Hit": [COLORS.green_primary, COLORS.green_secondary],
                "Miss": [COLORS.red_primary, COLORS.red_secondary],
                "Rim": [COLORS.grey_primary, COLORS.grey_secondary],
            }
            outcome_badge = ctk.CTkLabel(
                shot_frame,
                text=shot['outcome'],
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=outcome_colors.get(shot['outcome'], [COLORS.grey_primary, COLORS.grey_secondary]),
                corner_radius=8,
                text_color=COLORS.text_primary_light,
                width=60,
                height=30,
            )
            outcome_badge.pack(side="right", padx=5, pady=15)

    def delete_shot(self, shot):
        """Delete a specific shot from the current turn."""
        if shot in self.shot_history:
            self.shot_history.remove(shot)
            
            # Renumber remaining shots
            for idx, s in enumerate(self.shot_history, start=1):
                s["shot_number"] = idx
            
            # Update current shot counter
            self.current_shot = len(self.shot_history) + 1
            
            # Update UI state
            if len(self.shot_history) == 0:
                # No shots left
                self.shot_header_label.configure(
                    text="📝 Recording Shot 1 of 2",
                    text_color=[COLORS.text_primary_light, COLORS.text_primary_light],
                )
                self.record_btn.configure(state="normal", text="📊 Record Shot")
                self.submit_turn_btn.configure(state="disabled")
            elif len(self.shot_history) == 1:
                # One shot left
                self.shot_header_label.configure(
                    text="📝 Recording Shot 2 of 2",
                    text_color=[COLORS.text_primary_light, COLORS.text_primary_light],
                )
                self.record_btn.configure(state="normal", text="📊 Record Final Shot")
                self.submit_turn_btn.configure(state="disabled")
            
            # Refresh display
            self.update_results_display()

    def submit_turn(self):
        """Submit the completed turn to the game engine."""
        if len(self.shot_history) != 2:
            self.show_error_message("Need 2 shots to submit turn!")
            return
        
        game = self.controller.app_state.game
        engine = self.controller.app_state.engine
        
        if not game or not engine:
            self.show_error_message("Game not initialized!")
            return
        
        # Get the actual Player objects from the game
        shot1_data = self.shot_history[0]
        shot2_data = self.shot_history[1]
        
        # Find player objects by name
        player1 = self._get_player_by_name(shot1_data['player'])
        player2 = self._get_player_by_name(shot2_data['player'])
        
        if not player1 or not player2:
            self.show_error_message("Invalid player selection!")
            return
        
        # Import ShotData from game_engine
        from models.game_engine import ShotData
        from models.game import ShotType, ShotOutcome
        
        # Map UI shot type names to enum values
        shot_type_mapping = {
            'NORMAL': ShotType.NORMAL,
            'BOUNCE': ShotType.BOUNCE,
            'TRICKSHOT': ShotType.TRICKSHOT
        }
        
        # Create ShotData objects
        shot1 = ShotData(
            player=player1,
            shot_type=shot_type_mapping.get(shot1_data['shot_type'].upper(), ShotType.NORMAL),
            outcome=ShotOutcome[shot1_data['outcome'].upper()],
            elbow_violation=False,  # TODO: Connect to elbow tracking
            cup_position=None,
            bounces=shot1_data.get('bounces')
        )
        
        shot2 = ShotData(
            player=player2,
            shot_type=shot_type_mapping.get(shot2_data['shot_type'].upper(), ShotType.NORMAL),
            outcome=ShotOutcome[shot2_data['outcome'].upper()],
            elbow_violation=False,  # TODO: Connect to elbow tracking
            cup_position=None,
            bounces=shot2_data.get('bounces')
        )
        
        # Process the turn through the game engine
        result = engine.process_turn(shot1, shot2)
        
        if result.success:
            # Update cup counts in UI
            self.team1_cups_label.configure(text=f"🥤 {result.team1_cups_remaining}")
            self.team2_cups_label.configure(text=f"🥤 {result.team2_cups_remaining}")
            
            # Build success message
            message = f"Turn recorded! {result.total_cups_removed} cups removed."
            if result.balls_back:
                message += " 🔥 BALLS BACK!"
            if result.two_balls_one_cup:
                message += " 🎯 TWO BALLS ONE CUP!"
            if result.game_over:
                message += f"\n🏆 {result.winner_name} WINS!"
            
            self.show_success_message(message)
            
            # Update team selector to next team
            if result.next_team_name:
                self.team_var.set(result.next_team_name)
                self.on_team_selected(result.next_team_name)
        else:
            self.show_error_message(f"Error: {result.error_message}")
        
        # Reset for next turn
        self.clear_turn()
    
    def _get_player_by_name(self, player_name):
        """Find a player object by name from the current game."""
        game = self.controller.app_state.game
        if not game:
            return None
        
        # Check all players in both teams
        all_players = [
            game.team1.player1,
            game.team1.player2,
            game.team2.player1,
            game.team2.player2
        ]
        
        for player in all_players:
            if player.name == player_name:
                return player
        
        return None

    def clear_turn(self):
        """Clear all recorded shots and reset the form."""
        self.shot_history = []
        self.current_shot = 1
        self.shot_header_label.configure(
            text="📝 Recording Shot 1 of 2",
            text_color=[COLORS.text_primary_light, COLORS.text_primary_light],
        )
        self.record_btn.configure(state="normal", text="📊 Record Shot")
        self.submit_turn_btn.configure(state="disabled")
        self.outcome_var.set("Miss")
        self.update_outcome_buttons()
        self.update_results_display()

    def show_success_message(self, message):
        """Show a success message overlay."""
        success_frame = ctk.CTkFrame(
            self,
            fg_color=[COLORS.green_primary, COLORS.green_secondary],
            corner_radius=15,
            border_width=2,
            border_color=[COLORS.green_secondary, COLORS.green_primary],
        )
        success_frame.place(relx=0.5, rely=0.5, anchor="center")

        success_label = ctk.CTkLabel(
            success_frame,
            text=f"✅ {message}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS.text_primary_light,
        )
        success_label.pack(padx=40, pady=25)

        # Auto-dismiss after 1.5 seconds
        self.after(1500, success_frame.destroy)
    
    def show_error_message(self, message):
        """Show an error message overlay."""
        error_frame = ctk.CTkFrame(
            self,
            fg_color=[COLORS.red_primary, COLORS.red_secondary],
            corner_radius=15,
            border_width=2,
            border_color=[COLORS.red_secondary, COLORS.red_primary],
        )
        error_frame.place(relx=0.5, rely=0.5, anchor="center")

        error_label = ctk.CTkLabel(
            error_frame,
            text=f"⚠️ {message}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS.text_primary_light,
        )
        error_label.pack(padx=40, pady=25)

        # Auto-dismiss after 2 seconds
        self.after(2000, error_frame.destroy)

    def on_show(self):
        """Called when the page is shown."""
        self.load_game_data()
        self.clear_turn()

    def load_game_data(self):
        """Load current game data from app_state and update UI."""
        game = self.controller.app_state.game
        engine = self.controller.app_state.engine
        
        if not game or not engine:
            print("Warning: No game or engine found in app_state")
            return
        
        # Start the game if not already started
        from models.game import GameState
        if game.state == GameState.NOT_STARTED:
            engine.start_game()
            print(f"Game started: {game.team1.name} vs {game.team2.name}")
        
        # Update team names
        self.team1_name_label.configure(text=game.team1.name)
        self.team2_name_label.configure(text=game.team2.name)
        
        # Update player names
        self.team1_players_label.configure(
            text=f"{game.team1.player1.name} & {game.team1.player2.name}"
        )
        self.team2_players_label.configure(
            text=f"{game.team2.player1.name} & {game.team2.player2.name}"
        )
        
        # Update cup counts
        self.team1_cups_label.configure(text=f"🥤 {game.team1_cups_remaining}")
        self.team2_cups_label.configure(text=f"🥤 {game.team2_cups_remaining}")
        
        # Update team selector values with actual team names
        self.team_selector.configure(values=[game.team1.name, game.team2.name])
        
        # Set current team as default
        self.team_var.set(game.current_team.name)
        
        # Update player selector with current team's players
        self.update_player_selector_for_team(game.current_team)
