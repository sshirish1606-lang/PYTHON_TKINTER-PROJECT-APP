import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import math
import time
import os
import webbrowser

# --- CustomTkinter Global Appearance ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# --- Warm Beige & Red Clinical SaaS Palette ---
BG_OBSIDIAN = "#FDFBF7"  # Soft warm beige background
SURFACE_CARD = "#F5F2EB"  # Clean ivory-beige card background
SURFACE_ELEVATED = "#EFECE4"  # Elevated warm surface
BORDER_SUBTLE = "#D9D4C7"  # Muted warm border
BORDER_GLOW = "#9B111E"  # Deep ruby red highlight
TEXT_PRIMARY = "#2C2A29"  # Dark charcoal primary text
TEXT_SECONDARY = "#615E5C"  # Muted dark stone text
TEXT_MUTED = "#8C8682"  # Dim secondary text
ACCENT_RED = "#D9384E"  # Primary Red Accent
ACCENT_BURGUNDY = "#9B111E"  # Deep Medical Burgundy
ACCENT_EMERALD = "#0D7A57"  # Safe status emerald
ACCENT_AMBER = "#B45309"  # Warning amber
ACCENT_INDIGO = "#4338CA"  # Distinct deep indigo

# Typography Helpers (Optimized for Windows 10/11)
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"


class ModernToastNotification(ctk.CTkFrame):
    """Floating modern web-style toast notification banner."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=SURFACE_ELEVATED, corner_radius=10,
                         border_width=1.5, border_color=ACCENT_RED, **kwargs)
        self.icon_lbl = ctk.CTkLabel(self, text="ℹ️", font=(FONT_FAMILY, 15))
        self.icon_lbl.pack(side=tk.LEFT, padx=(14, 8), pady=8)

        self.msg_lbl = ctk.CTkLabel(self, text="", font=(FONT_FAMILY, 13, "bold"), text_color=TEXT_PRIMARY)
        self.msg_lbl.pack(side=tk.LEFT, padx=(0, 16), pady=8)
        self.hide_timer = None

    def show(self, message, icon="✓", border_color=ACCENT_EMERALD, duration=2600):
        if self.hide_timer:
            try:
                self.after_cancel(self.hide_timer)
            except Exception:
                pass
        self.configure(border_color=border_color)
        self.icon_lbl.configure(text=icon)
        self.msg_lbl.configure(text=message)
        self.place(relx=0.5, rely=0.94, anchor="center")
        self.lift()
        self.hide_timer = self.after(duration, self.hide)

    def hide(self):
        try:
            self.place_forget()
        except Exception:
            pass
        self.hide_timer = None


class RadialRiskGauge(tk.Canvas):
    """Modern circular radial speedometer gauge (Web-SaaS dashboard style)."""

    def __init__(self, master, width=320, height=210, bg=SURFACE_ELEVATED, **kwargs):
        super().__init__(master, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.accent_color = ACCENT_AMBER

    def update_risk(self, pct, stage_title, color):
        self.accent_color = color
        self.render_gauge(pct)

    def render_gauge(self, pct):
        self.delete("all")
        cx, cy = self.width / 2, self.height - 35
        r = 92
        line_w = 16

        start_angle = 210
        extent = -240
        bbox = (cx - r, cy - r, cx + r, cy + r)

        self.create_arc(bbox, start=start_angle, extent=extent,
                        outline=BORDER_SUBTLE, width=line_w, style=tk.ARC)

        filled_extent = -(240.0 * (pct / 100.0))
        if abs(filled_extent) > 0.5:
            self.create_arc(bbox, start=start_angle, extent=filled_extent,
                            outline=self.accent_color, width=line_w, style=tk.ARC)

        for tick_p in [0, 25, 50, 75, 100]:
            angle_deg = 210 - (240 * (tick_p / 100.0))
            rad = math.radians(angle_deg)
            x1 = cx + (r - 14) * math.cos(rad)
            y1 = cy - (r - 14) * math.sin(rad)
            x2 = cx + (r - 22) * math.cos(rad)
            y2 = cy - (r - 22) * math.sin(rad)
            self.create_line(x1, y1, x2, y2, fill=TEXT_MUTED, width=1.5)

        tip_angle_deg = 210 - (240 * (pct / 100.0))
        tip_rad = math.radians(tip_angle_deg)
        tip_x = cx + r * math.cos(tip_rad)
        tip_y = cy - r * math.sin(tip_rad)
        self.create_oval(tip_x - 7, tip_y - 7, tip_x + 7, tip_y + 7,
                         fill=self.accent_color, outline=SURFACE_CARD, width=2)

        self.create_text(cx, cy - 28, text=f"{pct}%",
                         font=(FONT_FAMILY, 44, "bold"), fill=self.accent_color)
        self.create_text(cx, cy + 14, text="CARDIAC RISK PROBABILITY",
                         font=(FONT_MONO, 9, "bold"), fill=TEXT_SECONDARY)


class CardioPulseCommandCenterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CardioPulse Quantum Pro — Clinical AI Risk Stratification & Decision Support")

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = min(1440, max(1150, screen_w - 30))
        win_h = min(880, max(720, screen_h - 60))
        self.root.geometry(f"{win_w}x{win_h}")
        self.root.minsize(1100, 680)
        self.root.configure(fg_color=BG_OBSIDIAN)

        try:
            self.root.state('zoomed')
        except Exception:
            pass

        self.lr_weights = [0.345785, -0.002049, 0.002188, 0.085659, 0.073517, 0.922972, 0.104592, 0.336156, -0.073762,
                           -0.037769, -0.048789, -0.09171]
        self.lr_intercept = 0.02505
        self.scaler_mean = [53.274446, 1.348559, 164.432121, 73.916206, 27.377683, 126.614798, 81.292475, 1.364409,
                            1.224707, 0.087765, 0.053474, 0.803659]
        self.scaler_scale = [6.754973, 0.476514, 7.567921, 13.434024, 4.943527, 16.570829, 9.343005, 0.679425, 0.570678,
                             0.282953, 0.224976, 0.39723]

        self.patient_database = {"MRN-884925": "S SAI SHIRISH"}
        self.current_patient_record = {}

        self.create_command_header()
        self.create_tactical_tabs()

        self.toast = ModernToastNotification(self.root)

        self.compute_quantum_risk()
        self.update_live_clock()

        self.anim_offset = 0
        self.animate_ecg_waveform()

    def update_live_clock(self):
        try:
            if not self.root.winfo_exists():
                return
            curr_time = time.strftime("%H:%M:%S UTC")
            if hasattr(self, 'clock_lbl') and self.clock_lbl.winfo_exists():
                self.clock_lbl.configure(text=f"⏱ {curr_time}")
            self.root.after(1000, self.update_live_clock)
        except Exception:
            pass

    def animate_ecg_waveform(self):
        """Live scrolling thick red ECG oscilloscope pulse animation loop."""
        try:
            if not hasattr(self, 'ecg_canvas') or not self.ecg_canvas.winfo_exists():
                return
        except tk.TclError:
            return

        self.ecg_canvas.delete("all")
        width = self.root.winfo_width() or 1400

        points = []
        for x in range(0, width + 50, 12):
            y = 20
            rel_x = (x + self.anim_offset) % 320
            if 50 <= rel_x <= 75:
                y -= 8 * math.sin((rel_x - 50) * math.pi / 25)
            elif 110 <= rel_x <= 125:
                y -= 26
            elif 125 <= rel_x <= 140:
                y += 18
            elif 180 <= rel_x <= 210:
                y -= 10 * math.sin((rel_x - 180) * math.pi / 30)
            points.append((x, y))

        flat_coords = [c for pt in points for c in pt]
        # Thick red ECG trace line
        self.ecg_canvas.create_line(flat_coords, fill=ACCENT_RED, width=3, smooth=True)

        self.anim_offset = (self.anim_offset + 10) % 320
        self.root.after(40, self.animate_ecg_waveform)

    def create_command_header(self):
        header = ctk.CTkFrame(self.root, fg_color=SURFACE_CARD, height=64, corner_radius=0,
                              border_width=1, border_color=BORDER_SUBTLE)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.pack(side=tk.LEFT, padx=22, pady=10)

        icon_box = ctk.CTkFrame(brand_frame, fg_color=BG_OBSIDIAN, width=42, height=42,
                                corner_radius=8, border_width=1.5, border_color=ACCENT_RED)
        icon_box.pack(side=tk.LEFT, padx=(0, 12))
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="🫀", font=(FONT_FAMILY, 21)).place(relx=0.5, rely=0.5, anchor="center")

        title_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_box.pack(side=tk.LEFT)

        t_row = ctk.CTkFrame(title_box, fg_color="transparent")
        t_row.pack(anchor="w")
        ctk.CTkLabel(t_row, text="CARDIOPULSE", font=(FONT_FAMILY, 19, "bold"), text_color=TEXT_PRIMARY).pack(
            side=tk.LEFT)
        ctk.CTkLabel(t_row, text=" QUANTUM PRO", font=(FONT_FAMILY, 19, "bold"), text_color=ACCENT_RED).pack(
            side=tk.LEFT)

        badge_row = ctk.CTkFrame(title_box, fg_color="transparent")
        badge_row.pack(anchor="w")
        ctk.CTkLabel(badge_row, text="CLINICAL RISK STRATIFICATION & DECISION ENGINE", font=(FONT_MONO, 10, "bold"),
                     text_color=TEXT_SECONDARY).pack(side=tk.LEFT)
        ctk.CTkLabel(badge_row, text="• v3.2 ENTERPRISE", font=(FONT_MONO, 10), text_color=ACCENT_EMERALD).pack(
            side=tk.LEFT, padx=6)

        center_status = ctk.CTkFrame(header, fg_color=SURFACE_ELEVATED, height=34, corner_radius=17,
                                     border_width=1, border_color=BORDER_SUBTLE)
        center_status.pack(side=tk.LEFT, expand=True, padx=20)

        ctk.CTkLabel(center_status, text="●", font=(FONT_FAMILY, 13, "bold"), text_color=ACCENT_EMERALD).pack(
            side=tk.LEFT, padx=(14, 6))
        ctk.CTkLabel(center_status, text="AI INFERENCE ENGINE READY", font=(FONT_MONO, 11, "bold"),
                     text_color=TEXT_PRIMARY).pack(side=tk.LEFT, padx=(0, 10))

        self.clock_lbl = ctk.CTkLabel(center_status, text="⏱ 00:00:00 UTC", font=(FONT_MONO, 11),
                                      text_color=TEXT_SECONDARY)
        self.clock_lbl.pack(side=tk.LEFT, padx=(6, 14))

        right_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_frame.pack(side=tk.RIGHT, padx=22)

        ctk.CTkLabel(
            right_frame,
            text="● KAGGLE 67K MODEL: ACTIVE",
            font=(FONT_MONO, 11, "bold"),
            fg_color=SURFACE_ELEVATED,
            text_color=ACCENT_EMERALD,
            corner_radius=8,
            border_width=1,
            border_color=BORDER_SUBTLE,
            padx=12,
            pady=6
        ).pack(side=tk.LEFT, padx=4)

        # --- LIVE TELEMETRY ECG STRIP BANNER (Thick Red ECG) ---
        strip = ctk.CTkFrame(self.root, fg_color=SURFACE_CARD, height=42, corner_radius=0,
                             border_width=1, border_color=BORDER_SUBTLE)
        strip.pack(fill=tk.X, padx=0, pady=0)
        strip.pack_propagate(False)

        self.ecg_canvas = tk.Canvas(strip, height=38, bg=SURFACE_CARD, highlightthickness=0)
        self.ecg_canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=2)

    def create_tactical_tabs(self):
        """2 Modern Clean Tabs with High-Visibility Text Colors."""
        self.tabview = ctk.CTkTabview(
            self.root,
            fg_color=BG_OBSIDIAN,
            segmented_button_fg_color=SURFACE_CARD,
            segmented_button_selected_color=ACCENT_RED,
            segmented_button_selected_hover_color=ACCENT_BURGUNDY,
            segmented_button_unselected_color=SURFACE_CARD,
            segmented_button_unselected_hover_color=SURFACE_ELEVATED,
            text_color=TEXT_PRIMARY
        )
        self.tabview.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 14))

        self.tab_hud = self.tabview.add(" 🫀 Patient Biometrics & Neural Risk HUD ")
        self.tab_rx = self.tabview.add(" 📋 Clinical Prescription & AI Diet Engine ")

        self.build_hud_tab()
        self.build_prescription_tab()

    def build_hud_tab(self):
        container = ctk.CTkFrame(self.tab_hud, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        left_panel = ctk.CTkFrame(container, fg_color=SURFACE_CARD, corner_radius=14,
                                  border_width=1.5, border_color=BORDER_SUBTLE)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=2)

        left_scroll = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        left_scroll.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        lh_top = ctk.CTkFrame(left_scroll, fg_color="transparent")
        lh_top.pack(fill=tk.X, padx=16, pady=(10, 8))
        ctk.CTkLabel(lh_top, text="PATIENT REGISTRY & CLINICAL VITALS", font=(FONT_FAMILY, 15, "bold"),
                     text_color=ACCENT_RED).pack(side=tk.LEFT)
        ctk.CTkLabel(lh_top, text="● ID VERIFIED", font=(FONT_MONO, 10, "bold"), text_color=ACCENT_EMERALD,
                     fg_color=SURFACE_ELEVATED, corner_radius=6, padx=8, pady=3).pack(side=tk.RIGHT)

        info_card = ctk.CTkFrame(left_scroll, fg_color=SURFACE_ELEVATED, corner_radius=10,
                                 border_width=1, border_color=BORDER_SUBTLE)
        info_card.pack(fill=tk.X, padx=16, pady=(0, 8))

        grid_f = ctk.CTkFrame(info_card, fg_color="transparent")
        grid_f.pack(fill=tk.X, padx=14, pady=10)
        grid_f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(grid_f, text="Patient Full Name:", font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY).grid(
            row=0, column=0, sticky="w", padx=(4, 12), pady=4)
        self.name_var = ctk.StringVar(value="S SAI SHIRISH")
        name_entry = ctk.CTkEntry(grid_f, textvariable=self.name_var, font=(FONT_FAMILY, 12, "bold"),
                                  fg_color=BG_OBSIDIAN, border_color=BORDER_SUBTLE, text_color=TEXT_PRIMARY, height=32)
        name_entry.grid(row=0, column=1, sticky="ew", padx=(0, 4), pady=4)
        name_entry.bind("<KeyRelease>", lambda e: self.compute_quantum_risk())

        ctk.CTkLabel(grid_f, text="Medical Record (MRN):", font=(FONT_FAMILY, 12, "bold"),
                     text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=(4, 12), pady=4)
        self.id_var = ctk.StringVar(value="MRN-884925")
        id_entry = ctk.CTkEntry(grid_f, textvariable=self.id_var, font=(FONT_FAMILY, 12, "bold"),
                                fg_color=BG_OBSIDIAN, border_color=BORDER_SUBTLE, text_color=ACCENT_RED, height=32)
        id_entry.grid(row=1, column=1, sticky="ew", padx=(0, 4), pady=4)
        id_entry.bind("<KeyRelease>", lambda e: self.compute_quantum_risk())

        # Quick Presets
        preset_frame = ctk.CTkFrame(left_scroll, fg_color="transparent")
        preset_frame.pack(fill=tk.X, padx=16, pady=(0, 8))

        ctk.CTkLabel(preset_frame, text="Quick Vitals Presets:", font=(FONT_MONO, 10, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(0, 4))

        p_grid = ctk.CTkFrame(preset_frame, fg_color="transparent")
        p_grid.pack(fill=tk.X)
        p_grid.grid_columnconfigure(0, weight=1)
        p_grid.grid_columnconfigure(1, weight=1)

        presets = [
            ("🟢 Baseline (120/80)", lambda: self.apply_vitals_preset(52, 170, 75, 120, 80, 95, 0, 0), 0, 0),
            ("🟡 Pre-HTN (135/88)", lambda: self.apply_vitals_preset(56, 172, 78, 135, 88, 105, 0, 0), 0, 1),
            ("🔴 Elevated (175/105)", lambda: self.apply_vitals_preset(62, 168, 85, 175, 105, 145, 1, 0), 1, 0),
            ("🏃 Athlete (110/70)", lambda: self.apply_vitals_preset(32, 175, 68, 110, 70, 88, 0, 0), 1, 1),
        ]
        for p_name, p_cmd, r, c in presets:
            ctk.CTkButton(
                p_grid, text=p_name, font=(FONT_MONO, 10, "bold"), height=28,
                fg_color=SURFACE_ELEVATED, text_color=TEXT_PRIMARY, hover_color=BORDER_SUBTLE,
                border_width=1, border_color=BORDER_SUBTLE, command=p_cmd
            ).grid(row=r, column=c, sticky="ew", padx=3, pady=3)

        self.vars = {}
        self.val_labels = {}
        vitals_config = [
            ("Age (years)", "age", 52, 30, 80, "yrs"),
            ("Height (cm)", "height", 170, 140, 200, "cm"),
            ("Weight (kg)", "weight", 75, 40, 150, "kg"),
            ("Systolic BP (ap_hi)", "ap_hi", 130, 90, 220, "mmHg"),
            ("Diastolic BP (ap_lo)", "ap_lo", 85, 60, 140, "mmHg")
        ]

        vitals_box = ctk.CTkFrame(left_scroll, fg_color="transparent")
        vitals_box.pack(fill=tk.X, padx=16, pady=0)

        for label, key, default, vmin, vmax, unit in vitals_config:
            row = ctk.CTkFrame(vitals_box, fg_color="transparent")
            row.pack(fill=tk.X, pady=2)

            top_r = ctk.CTkFrame(row, fg_color="transparent")
            top_r.pack(fill=tk.X, pady=(0, 1))
            ctk.CTkLabel(top_r, text=label, font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY).pack(side=tk.LEFT)

            var = ctk.IntVar(value=default)
            self.vars[key] = var

            val_lbl = ctk.CTkLabel(top_r, text=f"{default} {unit}", font=(FONT_MONO, 11, "bold"),
                                   text_color=ACCENT_RED)
            val_lbl.pack(side=tk.RIGHT)
            self.val_labels[key] = (val_lbl, unit)

            slider = ctk.CTkSlider(
                row, from_=vmin, to=vmax, variable=var, height=14,
                fg_color=BG_OBSIDIAN, progress_color=ACCENT_RED,
                button_color=ACCENT_RED, button_hover_color=ACCENT_EMERALD,
                command=lambda v, k=key: self.on_slider_change(k)
            )
            slider.pack(fill=tk.X)

        # Blood Glucose Section
        glu_card = ctk.CTkFrame(left_scroll, fg_color=SURFACE_ELEVATED, corner_radius=10,
                                border_width=1.5, border_color=ACCENT_AMBER)
        glu_card.pack(fill=tk.X, padx=16, pady=(8, 8))

        glu_top_row = ctk.CTkFrame(glu_card, fg_color="transparent")
        glu_top_row.pack(fill=tk.X, padx=14, pady=(8, 4))

        ctk.CTkLabel(
            glu_top_row, text="🩸 Blood Glucose (mg/dL):",
            font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        self.glucose_var = ctk.StringVar(value="95")
        self.glu_entry = ctk.CTkEntry(
            glu_top_row, textvariable=self.glucose_var, font=(FONT_MONO, 14, "bold"),
            fg_color=BG_OBSIDIAN, border_color=ACCENT_RED, border_width=1.5,
            text_color=ACCENT_RED, width=90, height=32, justify="center"
        )
        self.glu_entry.pack(side=tk.RIGHT, padx=(6, 0))
        self.glu_entry.bind("<KeyRelease>", lambda e: self.on_glucose_entry())

        self.glu_status_badge = ctk.CTkLabel(
            glu_top_row, text="[Optimal: <100]", font=(FONT_MONO, 10, "bold"), text_color=ACCENT_EMERALD
        )
        self.glu_status_badge.pack(side=tk.RIGHT, padx=6)

        glu_bot_row = ctk.CTkFrame(glu_card, fg_color="transparent")
        glu_bot_row.pack(fill=tk.X, padx=14, pady=(0, 10))

        self.glu_slider_var = ctk.IntVar(value=95)
        self.glu_slider = ctk.CTkSlider(
            glu_bot_row, from_=60, to=250, variable=self.glu_slider_var, height=14,
            fg_color=BG_OBSIDIAN, progress_color=ACCENT_AMBER, button_color=ACCENT_AMBER,
            button_hover_color=ACCENT_EMERALD, command=self.on_glucose_slider
        )
        self.glu_slider.pack(fill=tk.X)

        # Lifestyle Toggle Switches
        life_box = ctk.CTkFrame(left_scroll, fg_color="transparent")
        life_box.pack(fill=tk.X, padx=16, pady=(4, 8))

        ctk.CTkLabel(life_box, text="Lifestyle & Clinical Risk Multipliers:", font=(FONT_MONO, 10, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w", pady=(0, 3))

        chk_row = ctk.CTkFrame(life_box, fg_color="transparent")
        chk_row.pack(fill=tk.X)

        self.smoker_var = ctk.IntVar(value=0)
        self.alcohol_var = ctk.IntVar(value=0)

        self.smoker_chk = ctk.CTkCheckBox(
            chk_row, text="Active Smoker Status", variable=self.smoker_var,
            font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY,
            fg_color=ACCENT_RED, hover_color=ACCENT_EMERALD, command=self.compute_quantum_risk
        )
        self.smoker_chk.pack(side=tk.LEFT, padx=(0, 24))

        self.alcohol_chk = ctk.CTkCheckBox(
            chk_row, text="Alcoholic Status", variable=self.alcohol_var,
            font=(FONT_FAMILY, 12, "bold"), text_color=TEXT_PRIMARY,
            fg_color=ACCENT_RED, hover_color=ACCENT_EMERALD, command=self.compute_quantum_risk
        )
        self.alcohol_chk.pack(side=tk.LEFT)

        # Action Buttons
        btn_row = ctk.CTkFrame(left_scroll, fg_color="transparent")
        btn_row.pack(fill=tk.X, padx=16, pady=(10, 14))
        btn_row.grid_columnconfigure(0, weight=3)
        btn_row.grid_columnconfigure(1, weight=1)

        save_btn = ctk.CTkButton(
            btn_row, text="💾 Save Record", font=(FONT_FAMILY, 12, "bold"),
            fg_color=ACCENT_EMERALD, text_color="#FFFFFF", hover_color=ACCENT_BURGUNDY,
            height=36, corner_radius=8, command=self.save_patient_changes
        )
        save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        reset_btn = ctk.CTkButton(
            btn_row, text="↺ Reset", font=(FONT_FAMILY, 12, "bold"),
            fg_color=SURFACE_ELEVATED, text_color=TEXT_SECONDARY, hover_color=BORDER_SUBTLE,
            height=36, corner_radius=8,
            command=lambda: self.apply_vitals_preset(52, 170, 75, 130, 85, 95, 0, 0)
        )
        reset_btn.grid(row=0, column=1, sticky="ew")

        # RIGHT PANEL: Neural Risk Stratification Matrix & Radial Gauge
        right_panel = ctk.CTkFrame(container, fg_color=SURFACE_CARD, corner_radius=14,
                                   border_width=1.5, border_color=BORDER_SUBTLE)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=2)

        rh_top = ctk.CTkFrame(right_panel, fg_color="transparent")
        rh_top.pack(fill=tk.X, padx=22, pady=(16, 6))
        ctk.CTkLabel(rh_top, text="NEURAL RISK STRATIFICATION MATRIX", font=(FONT_FAMILY, 16, "bold"),
                     text_color=ACCENT_RED).pack(side=tk.LEFT)
        ctk.CTkLabel(rh_top, text="● KAGGLE LOGISTIC MODEL", font=(FONT_MONO, 10, "bold"), text_color=ACCENT_EMERALD,
                     fg_color=SURFACE_ELEVATED, corner_radius=6, padx=8, pady=3).pack(side=tk.RIGHT)

        gauge_card = ctk.CTkFrame(right_panel, fg_color=SURFACE_ELEVATED, corner_radius=12,
                                  border_width=1, border_color=BORDER_SUBTLE)
        gauge_card.pack(fill=tk.X, padx=22, pady=(0, 10))

        self.radial_gauge = RadialRiskGauge(gauge_card, width=320, height=210, bg=SURFACE_ELEVATED)
        self.radial_gauge.pack(anchor="center", pady=(8, 0))

        self.status_lbl = ctk.CTkLabel(
            gauge_card, text="MODERATE RISK ALERT", font=(FONT_FAMILY, 13, "bold"),
            fg_color=ACCENT_AMBER, text_color="#FFFFFF", corner_radius=6, padx=16, pady=5
        )
        self.status_lbl.pack(anchor="center", pady=(0, 12))

        # Clinical Metrics & Breakdown (Different Colors for each metric card)
        breakdown_card = ctk.CTkFrame(right_panel, fg_color=SURFACE_ELEVATED, corner_radius=12,
                                      border_width=1, border_color=BORDER_SUBTLE)
        breakdown_card.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 16))

        ctk.CTkLabel(
            breakdown_card, text="CLINICAL VITAL METRICS & RISK INDICES",
            font=(FONT_MONO, 11, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(12, 8))

        indicators_grid = ctk.CTkFrame(breakdown_card, fg_color="transparent")
        indicators_grid.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 12))

        # Indicator 1: Blood Pressure & MAP (Crimson/Red)
        bp_bento = ctk.CTkFrame(indicators_grid, fg_color=BG_OBSIDIAN, corner_radius=8, border_width=1,
                                border_color=BORDER_SUBTLE)
        bp_bento.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(bp_bento, text="BLOOD PRESSURE / MAP", font=(FONT_MONO, 9, "bold"), text_color=TEXT_MUTED).pack(
            anchor="w", padx=10, pady=(8, 0))
        self.bp_display_lbl = ctk.CTkLabel(bp_bento, text="130 / 85 mmHg", font=(FONT_FAMILY, 16, "bold"),
                                           text_color=ACCENT_RED)
        self.bp_display_lbl.pack(anchor="w", padx=10)
        self.map_display_lbl = ctk.CTkLabel(bp_bento, text="MAP: 100 mmHg · Stage 1 HTN", font=(FONT_MONO, 10),
                                            text_color=TEXT_SECONDARY)
        self.map_display_lbl.pack(anchor="w", padx=10, pady=(0, 8))

        # Indicator 2: BMI (Deep Indigo)
        bmi_bento = ctk.CTkFrame(indicators_grid, fg_color=BG_OBSIDIAN, corner_radius=8, border_width=1,
                                 border_color=BORDER_SUBTLE)
        bmi_bento.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(bmi_bento, text="BODY MASS INDEX (BMI)", font=(FONT_MONO, 9, "bold"), text_color=TEXT_MUTED).pack(
            anchor="w", padx=10, pady=(8, 0))
        self.bmi_display_lbl = ctk.CTkLabel(bmi_bento, text="26.0 kg/m²", font=(FONT_FAMILY, 16, "bold"),
                                            text_color=ACCENT_INDIGO)
        self.bmi_display_lbl.pack(anchor="w", padx=10)
        self.bmi_sub_lbl = ctk.CTkLabel(bmi_bento, text="Overweight (170cm / 75kg)", font=(FONT_MONO, 10),
                                        text_color=TEXT_SECONDARY)
        self.bmi_sub_lbl.pack(anchor="w", padx=10, pady=(0, 8))

        # Indicator 3: Glycemic Control (Warm Amber)
        glu_bento = ctk.CTkFrame(indicators_grid, fg_color=BG_OBSIDIAN, corner_radius=8, border_width=1,
                                 border_color=BORDER_SUBTLE)
        glu_bento.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(glu_bento, text="GLYCEMIC INDEX", font=(FONT_MONO, 9, "bold"), text_color=TEXT_MUTED).pack(
            anchor="w", padx=10, pady=(8, 0))
        self.glu_display_lbl = ctk.CTkLabel(glu_bento, text="95 mg/dL", font=(FONT_FAMILY, 16, "bold"),
                                            text_color=ACCENT_AMBER)
        self.glu_display_lbl.pack(anchor="w", padx=10)
        self.glu_sub_lbl = ctk.CTkLabel(glu_bento, text="Optimal Fasting Range (<100)", font=(FONT_MONO, 10),
                                        text_color=ACCENT_EMERALD)
        self.glu_sub_lbl.pack(anchor="w", padx=10, pady=(0, 8))

        # Indicator 4: Clinical Guidance Link (Emerald/Burgundy)
        guide_bento = ctk.CTkFrame(indicators_grid, fg_color=BG_OBSIDIAN, corner_radius=8, border_width=1,
                                   border_color=BORDER_SUBTLE)
        guide_bento.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        ctk.CTkLabel(guide_bento, text="CLINICAL GUIDELINE STAGE", font=(FONT_MONO, 9, "bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", padx=10, pady=(8, 0))
        self.tier_display_lbl = ctk.CTkLabel(guide_bento, text="Below 50% Stage", font=(FONT_FAMILY, 15, "bold"),
                                             text_color=ACCENT_EMERALD)
        self.tier_display_lbl.pack(anchor="w", padx=10)
        ctk.CTkLabel(guide_bento, text="Review Prescriptions & Diet Tab ➔", font=(FONT_MONO, 10),
                     text_color=ACCENT_RED).pack(anchor="w", padx=10, pady=(0, 8))

        indicators_grid.grid_columnconfigure(0, weight=1)
        indicators_grid.grid_columnconfigure(1, weight=1)
        indicators_grid.grid_rowconfigure(0, weight=1)
        indicators_grid.grid_rowconfigure(1, weight=1)

    def on_slider_change(self, key):
        lbl, unit = self.val_labels[key]
        val = int(self.vars[key].get())
        lbl.configure(text=f"{val} {unit}")
        self.compute_quantum_risk()

    def on_glucose_entry(self):
        try:
            val = float(self.glucose_var.get())
            slider_val = max(60, min(250, int(val)))
            self.glu_slider_var.set(slider_val)
            self.update_glucose_badge(val)
        except ValueError:
            pass
        self.compute_quantum_risk()

    def on_glucose_slider(self, val):
        int_val = int(val)
        self.glucose_var.set(str(int_val))
        self.update_glucose_badge(int_val)
        self.compute_quantum_risk()

    def update_glucose_badge(self, val):
        if val <= 99:
            self.glu_status_badge.configure(text="[Optimal: <100]", text_color=ACCENT_EMERALD)
        elif val <= 125:
            self.glu_status_badge.configure(text="[Prediabetes: 100-125]", text_color=ACCENT_AMBER)
        else:
            self.glu_status_badge.configure(text="[Elevated: ≥126]", text_color=ACCENT_RED)

    def apply_vitals_preset(self, age, height, weight, ap_hi, ap_lo, glucose, smoker, alcohol):
        self.vars['age'].set(age)
        self.vars['height'].set(height)
        self.vars['weight'].set(weight)
        self.vars['ap_hi'].set(ap_hi)
        self.vars['ap_lo'].set(ap_lo)

        self.glucose_var.set(str(glucose))
        self.glu_slider_var.set(glucose)
        self.update_glucose_badge(glucose)

        self.smoker_var.set(smoker)
        self.alcohol_var.set(alcohol)

        for k in ['age', 'height', 'weight', 'ap_hi', 'ap_lo']:
            lbl, unit = self.val_labels[k]
            lbl.configure(text=f"{int(self.vars[k].get())} {unit}")

        self.toast.show(f"Vitals Preset Applied ({ap_hi}/{ap_lo} mmHg, {glucose} mg/dL)", icon="✓",
                        border_color=ACCENT_RED)
        self.compute_quantum_risk()

    def build_prescription_tab(self):
        container = ctk.CTkFrame(self.tab_rx, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        banner = ctk.CTkFrame(container, fg_color=SURFACE_CARD, corner_radius=12,
                              border_width=1.5, border_color=BORDER_SUBTLE)
        banner.pack(fill=tk.X, pady=(0, 10))

        top_b = ctk.CTkFrame(banner, fg_color="transparent")
        top_b.pack(fill=tk.X, padx=22, pady=(12, 6))

        ctk.CTkLabel(top_b, text="INDIVIDUALIZED CLINICAL PRESCRIPTION & DIET DIRECTIVE",
                     font=(FONT_FAMILY, 15, "bold"), text_color=ACCENT_RED).pack(side=tk.LEFT)

        btn_group = ctk.CTkFrame(top_b, fg_color="transparent")
        btn_group.pack(side=tk.RIGHT)

        ctk.CTkButton(
            btn_group, text="🌐 Export HTML Web Report", font=(FONT_FAMILY, 11, "bold"),
            fg_color=SURFACE_ELEVATED, text_color=ACCENT_RED, hover_color=BORDER_SUBTLE,
            border_width=1, border_color=ACCENT_RED, height=32, corner_radius=6,
            command=self.export_html_report
        ).pack(side=tk.LEFT, padx=(0, 6))

        ctk.CTkButton(
            btn_group, text="📋 Copy Summary", font=(FONT_FAMILY, 11, "bold"),
            fg_color=SURFACE_ELEVATED, text_color=TEXT_PRIMARY, hover_color=BORDER_SUBTLE,
            border_width=1, border_color=BORDER_SUBTLE, height=32, corner_radius=6,
            command=self.copy_summary_to_clipboard
        ).pack(side=tk.LEFT, padx=(0, 6))

        ctk.CTkButton(
            btn_group, text="📥 Download Report (.txt)", font=(FONT_FAMILY, 11, "bold"),
            fg_color=ACCENT_RED, text_color="#FFFFFF", hover_color=ACCENT_BURGUNDY,
            height=32, corner_radius=6, command=self.download_report_file
        ).pack(side=tk.LEFT)

        self.patient_summary_lbl = ctk.CTkLabel(
            banner, text="Patient: S SAI SHIRISH (MRN-884925)  |  Status: Initializing...",
            font=(FONT_MONO, 12, "bold"), text_color=TEXT_PRIMARY
        )
        self.patient_summary_lbl.pack(anchor="w", padx=22, pady=(0, 12))

        split_box = ctk.CTkFrame(container, fg_color="transparent")
        split_box.pack(fill=tk.BOTH, expand=True)

        rx_card = ctk.CTkFrame(split_box, fg_color=SURFACE_CARD, corner_radius=12,
                               border_width=1.5, border_color=BORDER_SUBTLE)
        rx_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        rx_h = ctk.CTkFrame(rx_card, fg_color="transparent")
        rx_h.pack(fill=tk.X, padx=20, pady=(14, 6))
        ctk.CTkLabel(rx_h, text="💊 Prescribed Medication Regimen", font=(FONT_FAMILY, 15, "bold"),
                     text_color=ACCENT_RED).pack(side=tk.LEFT)
        ctk.CTkLabel(rx_h, text="CLINICIAN-GOVERNED", font=(FONT_MONO, 10, "bold"), text_color=ACCENT_RED,
                     fg_color=SURFACE_ELEVATED, corner_radius=6, padx=8, pady=3).pack(side=tk.RIGHT)

        self.rx_scroll = ctk.CTkScrollableFrame(rx_card, fg_color="transparent")
        self.rx_scroll.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 14))

        self.rx_text = ctk.CTkLabel(
            self.rx_scroll, text="", font=(FONT_FAMILY, 12.5), text_color=TEXT_PRIMARY,
            justify=tk.LEFT, anchor="nw", wraplength=640
        )
        self.rx_text.pack(anchor="nw", fill=tk.BOTH, expand=True, padx=8, pady=8)

        diet_card = ctk.CTkFrame(split_box, fg_color=SURFACE_CARD, corner_radius=12,
                                 border_width=1.5, border_color=BORDER_SUBTLE)
        diet_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        diet_h = ctk.CTkFrame(diet_card, fg_color="transparent")
        diet_h.pack(fill=tk.X, padx=20, pady=(14, 6))
        ctk.CTkLabel(diet_h, text="🥗 Personalized Dietary Prescription & Support", font=(FONT_FAMILY, 15, "bold"),
                     text_color=ACCENT_AMBER).pack(side=tk.LEFT)
        ctk.CTkLabel(diet_h, text="EVIDENCE-BASED NUTRITION", font=(FONT_MONO, 10, "bold"), text_color=ACCENT_AMBER,
                     fg_color=SURFACE_ELEVATED, corner_radius=6, padx=8, pady=3).pack(side=tk.RIGHT)

        self.diet_scroll = ctk.CTkScrollableFrame(diet_card, fg_color="transparent")
        self.diet_scroll.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 14))

        self.diet_text = ctk.CTkLabel(
            self.diet_scroll, text="", font=(FONT_FAMILY, 12.5), text_color=TEXT_PRIMARY,
            justify=tk.LEFT, anchor="nw", wraplength=640
        )
        self.diet_text.pack(anchor="nw", fill=tk.BOTH, expand=True, padx=8, pady=8)

    def save_patient_changes(self):
        name = self.name_var.get().strip()
        mrn = self.id_var.get().strip()

        if mrn in self.patient_database and self.patient_database[mrn] != name:
            messagebox.showerror(
                "MRN Collision Error",
                f"The Patient ID / MRN '{mrn}' is already registered to another patient ('{self.patient_database[mrn]}').\n\n"
                f"Please change the ID to ensure a unique record for '{name}'."
            )
            return

        self.patient_database[mrn] = name
        self.current_patient_record.update({"name": name, "mrn": mrn})
        self.toast.show(f"Patient profile for '{name}' ({mrn}) synchronized!", icon="✓", border_color=ACCENT_EMERALD)
        messagebox.showinfo("Success",
                            f"Patient profile for '{name}' ({mrn}) successfully saved & synchronized with Clinical Engine!")

    def copy_summary_to_clipboard(self):
        try:
            name = self.name_var.get()
            mrn = self.id_var.get()
            summary = (
                f"CardioPulse Clinical Directives — {name} ({mrn})\n"
                f"Risk Tier: {self.current_patient_record.get('risk_tier', 'N/A')} ({self.current_patient_record.get('pct', 0)}%)\n\n"
                f"[MEDICATIONS]:\n{self.rx_text.cget('text')}\n\n"
                f"[DIET]:\n{self.diet_text.cget('text')}"
            )
            self.root.clipboard_clear()
            self.root.clipboard_append(summary)
            self.toast.show("Clinical summary copied to clipboard!", icon="📋", border_color=ACCENT_RED)
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Could not copy to clipboard: {e}")

    def download_report_file(self):
        name = self.name_var.get()
        mrn = self.id_var.get()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Report", "*.txt"), ("All Files", "*.*")],
            initialfile=f"CardioPulse_Report_{mrn}.txt"
        )
        if file_path:
            try:
                report_content = (
                    "====================================================\n"
                    "      CARDIOPULSE QUANTUM PRO - CLINICAL REPORT     \n"
                    "====================================================\n\n"
                    f"Patient Name : {name}\n"
                    f"Patient ID   : {mrn}\n"
                    f"Blood Glucose: {self.glucose_var.get()} mg/dL\n"
                    f"Risk Status  : {self.current_patient_record.get('risk_tier', 'N/A')} ({self.current_patient_record.get('pct', 0)}% Probability)\n"
                    f"Lifestyle    : Smoker: {'Yes' if self.smoker_var.get() else 'No'} | Alcoholic: {'Yes' if self.alcohol_var.get() else 'No'}\n\n"
                    "----------------------------------------------------\n"
                    "PRESCRIBED MEDICATION REGIMEN & TIMING REFERENCE:\n"
                    "----------------------------------------------------\n"
                    f"{self.rx_text.cget('text')}\n\n"
                    "----------------------------------------------------\n"
                    "DIETARY PLAN & COMMENT:\n"
                    "----------------------------------------------------\n"
                    f"{self.diet_text.cget('text')}\n\n"
                    "====================================================\n"
                    "Generated locally by CardioPulse Quantum Pro Command Center\n"
                    "Safety Notice: Unsafe to prescribe exact treatment months or schedules from a model percentage. Clinician-defined review required.\n"
                )
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(report_content)
                self.toast.show(f"Report saved: {os.path.basename(file_path)}", icon="💾", border_color=ACCENT_EMERALD)
                messagebox.showinfo("Export Successful", f"Clinical report successfully saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save file: {e}")

    def export_html_report(self):
        name = self.name_var.get()
        mrn = self.id_var.get()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("Modern Web Report", "*.html"), ("All Files", "*.*")],
            initialfile=f"CardioPulse_Clinical_Dashboard_{mrn}.html"
        )
        if not file_path:
            return

        try:
            pct = self.current_patient_record.get('pct', 0)
            tier = self.current_patient_record.get('risk_tier', 'N/A')
            glucose = self.glucose_var.get()
            bp_val = f"{self.vars['ap_hi'].get()} / {self.vars['ap_lo'].get()} mmHg"
            bmi_val = self.bmi_display_lbl.cget("text")
            smoker_val = "Active Smoker" if self.smoker_var.get() else "Non-Smoker"
            alcohol_val = "Alcoholic" if self.alcohol_var.get() else "Non-Alcoholic"

            rx_html = self.rx_text.cget('text').replace('\n', '<br>')
            diet_html = self.diet_text.cget('text').replace('\n', '<br>')

            html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CardioPulse Quantum Pro — Clinical Report: {mrn}</title>
    <style>
        :root {{
            --bg-obsidian: #fdfbf7;
            --surface-card: #f5f2eb;
            --surface-elevated: #efece4;
            --border: #d9d4c7;
            --accent-red: #d9384e;
            --accent-emerald: #0d7a57;
            --accent-amber: #b45309;
            --text-primary: #2c2a29;
            --text-secondary: #615e5c;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-obsidian);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            padding: 32px 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #f5f2eb 0%, #efece4 100%);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }}
        .brand-title {{ font-size: 24px; font-weight: 800; color: var(--text-primary); }}
        .brand-subtitle {{ font-size: 13px; color: var(--accent-red); font-weight: 600; letter-spacing: 1px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .kpi-card {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 18px;
        }}
        .kpi-title {{ font-size: 11px; text-transform: uppercase; color: var(--text-secondary); font-weight: 700; }}
        .kpi-val {{ font-size: 26px; font-weight: 800; color: var(--accent-red); margin-top: 4px; }}
        .kpi-sub {{ font-size: 12px; color: var(--text-secondary); }}
        .card-split {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
        @media (max-width: 768px) {{ .card-split {{ grid-template-columns: 1fr; }} }}
        .card {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 24px;
        }}
        .card-header {{
            font-size: 18px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;
            border-bottom: 1px solid var(--border); padding-bottom: 12px;
        }}
        .card-header.med {{ color: var(--accent-emerald); }}
        .card-header.diet {{ color: var(--accent-amber); }}
        .badge {{
            display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;
            background: rgba(217, 56, 78, 0.15); color: var(--accent-red); margin-right: 6px;
        }}
        .footer {{
            text-align: center; font-size: 12px; color: var(--text-secondary); margin-top: 40px;
            border-top: 1px solid var(--border); padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <div class="brand-title">🫀 CARDIOPULSE QUANTUM PRO</div>
                <div class="brand-subtitle">CLINICAL RISK STRATIFICATION & DECISION SUPPORT REPORT</div>
                <p style="margin-top: 8px; color: var(--text-secondary); font-size: 14px;">
                    Patient: <strong>{name}</strong> &nbsp;|&nbsp; MRN: <strong>{mrn}</strong> &nbsp;|&nbsp; Generated: {time.strftime('%Y-%m-%d %H:%M')}
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 38px; font-weight: 800; color: var(--accent-red);">
                    {pct}%
                </div>
                <span class="badge">{tier}</span>
            </div>
        </div>

        <div class="grid">
            <div class="kpi-card">
                <div class="kpi-title">Blood Pressure</div>
                <div class="kpi-val">{bp_val}</div>
                <div class="kpi-sub">Mean Arterial: {int((2 * int(self.vars['ap_lo'].get()) + int(self.vars['ap_hi'].get())) / 3)} mmHg</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Fasting Glucose</div>
                <div class="kpi-val">{glucose} mg/dL</div>
                <div class="kpi-sub">Lab Verified</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Body Mass Index</div>
                <div class="kpi-val">{bmi_val}</div>
                <div class="kpi-sub">Height: {self.vars['height'].get()} cm | Weight: {self.vars['weight'].get()} kg</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Lifestyle Multipliers</div>
                <div class="kpi-val" style="font-size: 16px; margin-top: 8px;">{smoker_val}</div>
                <div class="kpi-sub">{alcohol_val}</div>
            </div>
        </div>

        <div class="card-split">
            <div class="card">
                <div class="card-header med">💊 Prescribed Medication Regimen & Timing</div>
                <div style="font-size: 13.5px;">{rx_html}</div>
            </div>
            <div class="card">
                <div class="card-header diet">🥗 Personalized Dietary Plan & Directives</div>
                <div style="font-size: 13.5px;">{diet_html}</div>
            </div>
        </div>

        <div class="footer">
            Generated locally by CardioPulse Quantum Pro Command Center.<br>
            Safety Notice: Unsafe to prescribe exact treatment months or schedules from a model percentage. Clinician-defined review required.
        </div>
    </div>
</body>
</html>"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_code)
            self.toast.show(f"Modern Web Report saved: {os.path.basename(file_path)}", icon="🌐",
                            border_color=ACCENT_RED)

            if messagebox.askyesno("Report Exported",
                                   f"Modern Web Report successfully generated!\n\nWould you like to open it in your web browser right now?"):
                webbrowser.open(file_path)

        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export HTML report: {e}")

    def compute_quantum_risk(self):
        try:
            age = self.vars['age'].get()
            height = self.vars['height'].get()
            weight = self.vars['weight'].get()
            ap_hi = self.vars['ap_hi'].get()
            ap_lo = self.vars['ap_lo'].get()
            bmi = weight / ((height / 100) ** 2)

            try:
                glucose = float(self.glucose_var.get())
            except ValueError:
                glucose = 95.0

            smoker = self.smoker_var.get()
            alcoholic = self.alcohol_var.get()

            map_bp = int((2 * ap_lo + ap_hi) / 3)
            self.bp_display_lbl.configure(text=f"{ap_hi} / {ap_lo} mmHg")
            bp_tag = "Normal" if ap_hi < 120 and ap_lo < 80 else ("Elevated" if ap_hi < 130 and ap_lo < 80 else (
                "Stage 1 HTN" if ap_hi < 140 or ap_lo < 90 else "Stage 2 HTN"))
            self.map_display_lbl.configure(text=f"MAP: {map_bp} mmHg · {bp_tag}")

            self.bmi_display_lbl.configure(text=f"{bmi:.1f} kg/m²")
            bmi_tag = "Normal Range" if bmi < 25 else ("Overweight" if bmi < 30 else "Obese Class")
            self.bmi_sub_lbl.configure(text=f"{bmi_tag} ({height}cm / {weight}kg)")

            self.glu_display_lbl.configure(text=f"{int(glucose)} mg/dL")
            glu_tag = "Optimal Fasting (<100)" if glucose <= 99 else (
                "Prediabetes Range (100–125)" if glucose <= 125 else "Elevated Range (≥126)")
            self.glu_sub_lbl.configure(text=glu_tag, text_color=ACCENT_EMERALD if glucose <= 99 else (
                ACCENT_AMBER if glucose <= 125 else ACCENT_RED))

            glu_factor = max(0.0, (glucose - 100.0) / 25.0) * 0.15

            inputs_raw = [age, 1, height, weight, bmi, ap_hi, ap_lo, 1, 1, smoker, alcoholic, 1]
            z = self.lr_intercept + glu_factor
            for i, val in enumerate(inputs_raw):
                scaled = (val - self.scaler_mean[i]) / self.scaler_scale[i]
                z += scaled * self.lr_weights[i]

            prob = 1 / (1 + math.exp(-z))
            pct = round(prob * 100)

            if pct < 50:
                risk_tier = "Below 50% — General Preventive Plan"
                status_title = "PREVENTIVE HEALTH STAGE"
                status_color = ACCENT_EMERALD
                status_text_color = "#FFFFFF"
            elif pct <= 55:
                risk_tier = "Stage 1: 50-55% - Elevated Risk"
                status_title = "STAGE 1: ELEVATED RISK"
                status_color = ACCENT_EMERALD
                status_text_color = "#FFFFFF"
            elif pct <= 60:
                risk_tier = "Stage 2: 55-60% - Increased Risk"
                status_title = "STAGE 2: INCREASED RISK"
                status_color = ACCENT_RED
                status_text_color = "#FFFFFF"
            elif pct <= 65:
                risk_tier = "Stage 3: 60-65% - High Risk"
                status_title = "STAGE 3: HIGH RISK"
                status_color = ACCENT_RED
                status_text_color = "#FFFFFF"
            elif pct <= 70:
                risk_tier = "Stage 4: 65-70% - Significant Risk"
                status_title = "STAGE 4: SIGNIFICANT RISK"
                status_color = ACCENT_AMBER
                status_text_color = "#FFFFFF"
            elif pct <= 75:
                risk_tier = "Stage 5: 70-75% - Very High Risk"
                status_title = "STAGE 5: VERY HIGH RISK"
                status_color = ACCENT_AMBER
                status_text_color = "#FFFFFF"
            elif pct <= 80:
                risk_tier = "Stage 6: 75-80% - Advanced Risk"
                status_title = "STAGE 6: ADVANCED RISK"
                status_color = ACCENT_AMBER
                status_text_color = "#FFFFFF"
            elif pct <= 85:
                risk_tier = "Stage 7: 80-85% - Severe Risk Indicator"
                status_title = "STAGE 7: SEVERE RISK"
                status_color = ACCENT_RED
                status_text_color = "#FFFFFF"
            elif pct <= 90:
                risk_tier = "Stage 8: 85-90% - Critical Risk Indicator"
                status_title = "STAGE 8: CRITICAL RISK"
                status_color = ACCENT_RED
                status_text_color = "#FFFFFF"
            elif pct <= 95:
                risk_tier = "Stage 9: 90-95% - Extreme Risk Indicator"
                status_title = "STAGE 9: EXTREME RISK"
                status_color = ACCENT_RED
                status_text_color = "#FFFFFF"
            else:
                risk_tier = "Stage 10: 95-100% - Maximum Model Risk Indicator"
                status_title = "STAGE 10: MAXIMUM MODEL RISK"
                status_color = ACCENT_RED
                status_text_color = "#FFFFFF"

            self.radial_gauge.update_risk(pct, status_title, status_color)
            self.status_lbl.configure(text=status_title, fg_color=status_color, text_color=status_text_color)
            self.tier_display_lbl.configure(text=status_title, text_color=status_color)

            name = self.name_var.get()
            mrn = self.id_var.get()

            self.current_patient_record.update({"risk_tier": risk_tier, "pct": pct, "name": name, "mrn": mrn})
            self.update_prescription_and_diet(name, mrn, pct, risk_tier, smoker, alcoholic, glucose)

        except (AttributeError, ZeroDivisionError):
            pass

    def update_prescription_and_diet(self, name, mrn, pct, tier, smoker, alcoholic, glucose):
        lifestyle_note = []
        if smoker:
            lifestyle_note.append("Smoker")
        if alcoholic:
            lifestyle_note.append("Alcoholic")
        lifestyle_str = " | ".join(lifestyle_note) if lifestyle_note else "Non-Smoker / Non-Alcoholic"

        glu_status = "Normal" if glucose <= 99 else (
            "Prediabetes Range" if glucose <= 125 else "Elevated / Diabetes Range")
        self.patient_summary_lbl.configure(
            text=f"Patient: {name} ({mrn}) [{lifestyle_str}] | Glucose: {glucose} mg/dL ({glu_status}) | Risk: {pct}% [{tier}]")

        if pct < 50:
            rx_content = (
                "• General Preventive Medicines Note:\n"
                "There is no universal preventive medicine for everyone below 50%. Statins, antihypertensives and diabetes medicines should be considered only when clinically indicated after individual assessment.\n\n"
                "• Statin Information:\n"
                "Atorvastatin / Rosuvastatin: Lipid-lowering therapy. Indicated when clinically appropriate based on formal cardiovascular risk assessment and lipid profiling. Dosage: Clinician-directed. Timing: Usually once daily (evening preferred for some formulations). With/without food. Duration: Long-term when indicated.\n\n"
                "• Antihypertensive Information:\n"
                "Amlodipine / Telmisartan / Ramipril: Indicated only for confirmed hypertension. Dosage: Clinician-directed. Timing: Morning or evening, consistently. With/without food. Duration: Long-term when indicated.\n\n"
                "• Diabetes Medicine Information:\n"
                "Metformin: Indicated only for diagnosed diabetes or prediabetes under medical guidance. Dosage: Clinician-directed. Timing: With or after meals to minimize gastrointestinal discomfort. Duration: Long-term when indicated."
            )
            diet_content = (
                "🥗 General Preventive Dietary Plan & Directives:\n\n"
                "• Maintain a balanced dietary pattern emphasizing whole foods.\n"
                "• Include vegetables, whole grains, lean proteins, legumes, and nuts.\n"
                "• Minimize consumption of ultra-processed foods, refined carbohydrates, and sugary beverages.\n"
                "• Maintain moderate sodium intake (<2,300 mg/day).\n"
                "• Ensure adequate hydration and avoid excessive alcohol intake.\n\n"
                "💬 Comment:\n"
                "\"Maintaining a heart-healthy diet is a powerful foundation for long-term cardiovascular health. Keep up good lifestyle habits and have periodic routine evaluations with your physician.\""
            )
        elif pct <= 55:
            rx_content = (
                "💊 Stage 1 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• Atorvastatin: 10–20 mg | Timing: Once daily at night | Food: With or without food | Duration: Long-term ongoing evaluation\n"
                "• Telmisartan: 20–40 mg | Timing: Once daily, morning | Food: With or without food | Duration: Continuous review\n"
                "• Metformin: 500 mg | Timing: Once or twice daily | Food: With meals | Duration: Continuous review"
            )
            diet_content = (
                "🥗 Stage 1 Dietary Plan & Directives:\n\n"
                "• Emphasize fiber-rich legumes, oats, and leafy greens.\n"
                "• Limit saturated fats and dietary sodium.\n"
                "• Reduce refined sugars and sugary snacks.\n"
                "• Maintain consistent hydration throughout the day.\n\n"
                "💬 Comment:\n"
                "\"Your evaluation places you in a mildly elevated range. Simple, proactive lifestyle optimizations can make a profound positive impact. Work with your physician to stay on top of your numbers.\""
            )
        elif pct <= 60:
            rx_content = (
                "💊 Stage 2 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• Atorvastatin: 20 mg | Timing: Once daily at night | Food: With/without food | Duration: Long-term ongoing evaluation\n"
                "• Amlodipine: 5 mg | Timing: Once daily, morning | Food: With/without food | Duration: Long-term ongoing evaluation\n"
                "• Metformin: 500–850 mg | Timing: Twice daily | Food: With meals | Duration: Continuous review"
            )
            diet_content = (
                "🥗 Stage 2 Dietary Plan & Directives:\n\n"
                "• Incorporate omega-3 fatty acids from fish or flaxseed.\n"
                "• Limit processed and high-sodium pre-packaged foods.\n"
                "• Emphasize low glycemic index fruits like berries and apples.\n"
                "• Prioritize plant-based proteins and legumes.\n\n"
                "💬 Comment:\n"
                "\"Your heart health shows opportunities for proactive improvement. Moderate daily physical activity and a cardioprotective diet can help restore balanced risk levels.\""
            )
        elif pct <= 65:
            rx_content = (
                "💊 Stage 3 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• Rosuvastatin: 10–20 mg | Timing: Once daily | Food: With/without food | Duration: Long-term ongoing evaluation\n"
                "• Telmisartan + Amlodipine: Combination | Timing: Once daily, morning | Food: With/without food | Duration: Long-term ongoing evaluation\n"
                "• Metformin: 850–1000 mg | Timing: Twice daily | Food: With meals | Duration: Continuous review"
            )
            diet_content = (
                "🥗 Stage 3 Dietary Plan & Directives:\n\n"
                "• Follow a DASH-style dietary pattern strictly.\n"
                "• Restrict sodium intake strictly below 2,000 mg/day.\n"
                "• Consume potassium-rich vegetables (spinach, squash).\n"
                "• Eliminate trans fats and deep-fried items completely.\n\n"
                "💬 Comment:\n"
                "\"Your assessment indicates an important window for therapeutic intervention. Partner with your clinician to establish optimal lipid and blood pressure goals.\""
            )
        elif pct <= 70:
            rx_content = (
                "💊 Stage 4 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• Rosuvastatin: 20 mg | Timing: Once daily | Food: With/without food | Duration: Long-term ongoing evaluation\n"
                "• Aspirin: 75–100 mg | Timing: Once daily | Food: After food | Duration: Specialist-determined\n"
                "• Ramipril: 5–10 mg | Timing: Once daily, evening | Food: With/without food | Duration: Continuous review\n"
                "• Empagliflozin: 10 mg | Timing: Once daily, morning | Food: With/without food | Duration: Specialist-determined"
            )
            diet_content = (
                "🥗 Stage 4 Dietary Plan & Directives:\n\n"
                "• Adhere strictly to the Mediterranean or DASH diet pattern.\n"
                "• Strictly limit ultra-processed meats and cold cuts.\n"
                "• Replace saturated fats with extra virgin olive oil and avocados.\n"
                "• Restrict total sodium intake below 1,500–2,000 mg/day.\n\n"
                "💬 Comment:\n"
                "\"Consistent medical follow-up combined with targeted nutrition will protect your vascular system. Stay diligent and monitor your vitals closely.\""
            )
        elif pct <= 75:
            rx_content = (
                "💊 Stage 5 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• Atorvastatin: 40 mg | Timing: Once daily | Food: With/without food | Duration: Long-term ongoing evaluation\n"
                "• Clopidogrel: 75 mg (or Aspirin) | Timing: Once daily | Food: With/without food | Duration: Specialist-determined\n"
                "• Metoprolol Succinate: 25–50 mg | Timing: Once daily, morning | Food: With or immediately after food | Duration: Continuous review\n"
                "• Telmisartan: 40–80 mg | Timing: Once daily | Food: With/without food | Duration: Continuous review"
            )
            diet_content = (
                "🥗 Stage 5 Dietary Plan & Directives:\n\n"
                "• Prioritize antioxidant-dense berries, leafy crucifers, and dark leafy greens.\n"
                "• Strictly avoid high-glycemic sweetened foods and refined flours.\n"
                "• Monitor portion sizes and total carbohydrate intake.\n"
                "• Avoid added table salt and canned processed broths.\n\n"
                "💬 Comment:\n"
                "\"A focused clinical treatment strategy paired with daily healthy habits provides significant cardiovascular protection. Keep in close touch with your care provider.\""
            )
        elif pct <= 80:
            rx_content = (
                "💊 Stage 6 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• Rosuvastatin: 40 mg | Timing: Once daily | Food: With/without food | Duration: Long-term ongoing evaluation\n"
                "• Dual Antiplatelet / Specialist Regimen: As directed | Timing: As prescribed | Food: With meals | Duration: Time-limited specialist plan\n"
                "• Bisoprolol: 5 mg | Timing: Once daily, morning | Food: With/without food | Duration: Continuous review\n"
                "• Spironolactone: 25 mg | Timing: Once daily, morning | Food: With food | Duration: Regular electrolyte monitoring required"
            )
            diet_content = (
                "🥗 Stage 6 Dietary Plan & Directives:\n\n"
                "• Highly structured cardioprotective nutrition plan.\n"
                "• Restrict sodium to <1,500 mg daily.\n"
                "• Focus on easily digestible steamed vegetables and lean poultry/fish.\n"
                "• Fluid intake guidance as advised by your clinical team.\n\n"
                "💬 Comment:\n"
                "\"Your evaluation underscores the importance of adhering closely to medical recommendations. Timely medical supervision is vital to protecting your cardiac health.\""
            )
        elif pct <= 85:
            rx_content = (
                "💊 Stage 7 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• High-Intensity Statin (Atorvastatin 80 mg or Rosuvastatin 40 mg) | Timing: Once daily | Food: With/without food | Duration: Long term\n"
                "• Aspirin + P2Y12 Inhibitor: If clinically indicated | Timing: Once daily | Food: With food | Duration: Specialist plan\n"
                "• Sacubitril / Valsartan: If indicated | Timing: Twice daily | Food: With/without food | Duration: Specialist-supervised\n"
                "• Dapagliflozin: 10 mg | Timing: Once daily, morning | Food: With/without food | Duration: Continuous review"
            )
            diet_content = (
                "🥗 Stage 7 Dietary Plan & Directives:\n\n"
                "• Cardiac rehabilitation-approved clinical nutrition.\n"
                "• Eliminate all processed meats, commercial baked goods, and excess sodium.\n"
                "• Emphasize fiber-dense vegetables and heart-healthy legumes.\n"
                "• Strictly follow clinician instructions regarding fluid and electrolyte balances.\n\n"
                "💬 Comment:\n"
                "\"Please schedule a consultation with your cardiologist promptly. Modern clinical cardiology provides advanced tools to support and improve your health.\""
            )
        elif pct <= 90:
            rx_content = (
                "💊 Stage 8 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• Atorvastatin: 40–80 mg or Rosuvastatin 20–40 mg | Timing: Once daily | Food: With/without food | Duration: Long-term ongoing evaluation\n"
                "• Antiplatelet therapy: Aspirin or Clopidogrel | Timing: Once daily | Food: With/without food | Duration: Specialist-determined\n"
                "• Blood pressure therapy: ACEi / ARB or CCB | Timing: Once daily | Food: With/without food | Duration: Continuous review\n"
                "• Heart failure-specific therapy (SGLT2i / MRA / ARNI): If clinically indicated | Timing: As prescribed | Food: As directed | Duration: Specialist-managed"
            )
            diet_content = (
                "🥗 Stage 8 Dietary Plan & Directives:\n\n"
                "• Follow an individualized cardiology-approved diet.\n"
                "• Avoid excessive sodium and deep-fried foods.\n"
                "• Prefer fresh vegetables and appropriate protein.\n"
                "• Avoid excessive sugar.\n"
                "• Follow specific fluid restrictions only if prescribed.\n\n"
                "💬 Comment:\n"
                "\"Your assessment highlights the importance of receiving timely professional medical attention. Please remain calm and avoid making medication changes independently. Cardiovascular conditions can often be managed through appropriate medical interventions and continuous supervision. Your health and safety come first. Stay connected with your healthcare provider and follow the care plan recommended for you.\""
            )
        elif pct <= 95:
            rx_content = (
                "💊 Stage 9 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Long term if indicated\n"
                "• Clopidogrel / Aspirin | Timing: Once daily | Food: With/without food | Duration: Specialist-determined\n"
                "• Ticagrelor | Timing: Twice daily, ~12 hours apart | Food: With/without food | Duration: Time-limited post-ACS plan (default 12 months dual therapy if applicable)\n"
                "• Sacubitril/valsartan | Timing: Twice daily | Food: With/without food | Duration: Long term if indicated\n"
                "• Dapagliflozin | Timing: Once daily, morning | Food: With/without food | Duration: Long term if indicated"
            )
            diet_content = (
                "🥗 Stage 9 Dietary Plan & Directives:\n\n"
                "• Individualized clinical nutrition plan.\n"
                "• Avoid excessive salt and processed foods.\n"
                "• Avoid trans fats.\n"
                "• Follow clinician-directed fluid and nutritional restrictions.\n"
                "• Do not use food or supplements as substitutes for medical treatment.\n\n"
                "💬 Comment:\n"
                "\"Your results indicate that immediate professional review is important. Please remember that the percentage displayed is a model-generated estimate and does not independently establish a diagnosis or predict an imminent cardiac event. The most important step is to receive the appropriate medical assessment. You deserve proper care and support, and taking action now is a positive step towards protecting your health.\""
            )
        else:
            rx_content = (
                "💊 Stage 10 Medication Information & Administration Timing (Only when clinically indicated):\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Usually long-term\n"
                "• Aspirin / Clopidogrel / Ticagrelor | Timing: As prescribed | Food: Formulation-specific | Duration: Specialist-determined\n"
                "• Metoprolol | Timing: Formulation-dependent | Food: With/after food | Duration: Condition-dependent\n"
                "• Sacubitril/valsartan | Timing: Twice daily | Food: With/without food | Duration: Long term if indicated"
            )
            diet_content = (
                "🥗 Stage 10 Dietary Plan & Directives:\n\n"
                "• Obtain an individualized medical nutrition plan.\n"
                "• Avoid excess sodium and highly processed foods.\n"
                "• Follow prescribed fluid restrictions if applicable.\n"
                "• Maintain appropriate nutrition under medical supervision.\n"
                "• Do not delay medical assessment to follow a dietary plan.\n\n"
                "💬 Comment:\n"
                "\"Your assessment indicates that your cardiovascular health requires immediate professional attention. Please do not panic or make independent changes to your medication. A model-generated score is not a confirmed diagnosis, and appropriate medical evaluation is essential to understand your actual condition. You are taking an important step by paying attention to your health. Please seek the necessary medical support and allow your healthcare team to guide your next steps.\""
            )

        self.rx_text.configure(text=rx_content)
        self.diet_text.configure(text=diet_content)


if __name__ == "__main__":
    root = ctk.CTk()
    app = CardioPulseCommandCenterApp(root)
    root.mainloop()
