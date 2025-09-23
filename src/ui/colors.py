from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPalette:
    # Background colors
    bg_primary_light: str = "#f8fafc"
    bg_primary_dark: str = "#0f172a"

    bg_secondary_light: str = "#f1f5f9"
    bg_secondary_dark: str = "#1e293b"

    # Text colors
    text_primary_light: str = "#f1f5f9"
    text_primary_dark: str = "#1e293b"

    text_secondary_light: str = "#94a3b8"
    text_secondary_dark: str = "#64748b"

    # Action colors
    blue_primary: str = "#3b82f6"
    blue_secondary: str = "#215ad3"
    blue_hover: str = "#0b3898"

    green_primary: str = "#10b981"
    green_secondary: str = "#059669"
    green_hover: str = "#045D44"

    red_primary: str = "#fa7676"
    red_secondary: str = "#dc2626"
    red_hover: str = "#b91c1c"

    grey_primary: str = "#6b7280"
    grey_secondary: str = "#4b5563"
    grey_hover: str = "#374151"

    # Error colors
    error_bg_light: str = "#fef2f2"
    error_bg_dark: str = "#7f1d1d"
    error_border_light: str = "#fca5a5"
    error_border_dark: str = "#ef4444"


COLORS = ColorPalette()
