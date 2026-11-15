import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Cyberpunk / High-Tech Medical Theme Palette ---
BG_DARK = "#030712"
SURFACE = "#0F172A"
SURFACE_BORDER = "#1E293B"
TEXT_MAIN = "#F8FAFC"
TEXT_MUTED = "#94A3B8"
ACCENT_CYAN = "#06B6D4"
ACCENT_EMERALD = "#10B981"
ACCENT_ROSE = "#F43F5E"
ACCENT_AMBER = "#FBBF24"

# Configure Matplotlib for Dark Cyberpunk Theme
plt.style.use('dark_background')


class CardioPulseQuantumProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CardioPulse Quantum Pro — Clinical Triage & Prescription Engine")
        self.root.state('zoomed')
        self.root.configure(bg=BG_DARK)

        # Model weights & scalers (Kaggle baseline)[cite: 1]
        self.lr_weights = [0.345785, -0.002049, 0.002188, 0.085659, 0.073517, 0.922972, 0.104592, 0.336156, -0.073762,
                           -0.037769, -0.048789, -0.09171]
        self.lr_intercept = 0.02505
        self.scaler_mean = [53.274446, 1.348559, 164.432121, 73.916206, 27.377683, 126.614798, 81.292475, 1.364409,
                            1.224707, 0.087765, 0.053474, 0.803659]
        self.scaler_scale = [6.754973, 0.476514, 7.567921, 13.434024, 4.943527, 16.570829, 9.343005, 0.679425, 0.570678,
                             0.282953, 0.224976, 0.39723]

        # Patient Registry Database (Mapping MRN -> Name)
        self.patient_database = {}
        self.current_patient_record = {}

        self.setup_styles()
        self.create_header()
        self.create_main_notebook()

        # Pre-register default patient
        self.patient_database["MRN-884925"] = "S SAI SHIRISH"

        self.compute_quantum_risk()

        self.anim_offset = 0
        self.animate_ecg()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=SURFACE, foreground=TEXT_MUTED, padding=[28, 16],
                             font=("Space Grotesk", 18, "bold"))
        self.style.map("TNotebook.Tab",
                       background=[("selected", ACCENT_CYAN), ("active", SURFACE_BORDER)],
                       foreground=[("selected", BG_DARK), ("active", TEXT_MAIN)])

    def create_header(self):
        header = tk.Frame(self.root, bg=SURFACE, height=95)
        header.pack(fill=tk.X, padx=0, pady=(0, 2))
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=SURFACE)
        title_frame.pack(side=tk.LEFT, padx=32)

        tk.Label(title_frame, text="⚡", font=("Inter", 26), bg=SURFACE, fg=ACCENT_CYAN).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(title_frame, text="CARDIOPULSE QUANTUM PRO", font=("Space Grotesk", 24, "bold"), bg=SURFACE,
                 fg=TEXT_MAIN).pack(side=tk.LEFT, padx=(0, 14))

        badge = tk.Label(title_frame, text="CLINICAL HUD & PRESCRIPTION SUITE", font=("IBM Plex Mono", 13, "bold"),
                         bg=BG_DARK, fg=ACCENT_CYAN, padx=14, pady=6)
        badge.pack(side=tk.LEFT)

        self.ticker_lbl = tk.Label(header, text="SYSTEM STATUS: ONLINE · 67,510 RECORDS INDEXED[cite: 1]",
                                   font=("IBM Plex Mono", 13, "bold"), bg=SURFACE, fg=ACCENT_EMERALD)
        self.ticker_lbl.pack(side=tk.RIGHT, padx=32)

        self.ecg_canvas = tk.Canvas(self.root, height=45, bg=SURFACE, highlightthickness=0)
        self.ecg_canvas.pack(fill=tk.X)

    def animate_ecg(self):
        # Safe check to prevent callback errors when window is closed
        try:
            if not self.ecg_canvas.winfo_exists():
                return
        except tk.TclError:
            return

        self.ecg_canvas.delete("all")
        width = self.root.winfo_width() or 1400

        points = []
        for x in range(0, width + 50, 15):
            y = 22
            rel_x = (x + self.anim_offset) % 300
            if 60 <= rel_x <= 90:
                y -= 15 * math.sin((rel_x - 60) * math.pi / 30)
            elif 120 <= rel_x <= 135:
                y -= 28
            elif 135 <= rel_x <= 150:
                y += 22
            points.append((x, y))

        flat_points = [coord for pt in points for coord in pt]
        self.ecg_canvas.create_line(flat_points, fill=ACCENT_CYAN, width=3, smooth=True)

        self.anim_offset = (self.anim_offset + 8) % 300
        self.root.after(50, self.animate_ecg)

    def create_main_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=28, pady=24)

        self.tab_hud = ttk.Frame(self.notebook)
        self.tab_prescription = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_hud, text=" ⚡ Live Neural HUD & Predictor ")
        self.notebook.add(self.tab_prescription, text=" 📋 Patient Prescription & Diet Plan ")

        self.build_hud_tab()
        self.build_prescription_tab()

    def build_hud_tab(self):
        container = tk.Frame(self.tab_hud, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_panel = tk.Frame(container, bg=SURFACE, padx=32, pady=32, highlightbackground=SURFACE_BORDER,
                              highlightthickness=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))

        tk.Label(left_panel, text="PATIENT PROFILE & BIOMETRICS", font=("Space Grotesk", 20, "bold"), bg=SURFACE,
                 fg=ACCENT_CYAN).pack(anchor="w", pady=(0, 16))

        info_box = tk.Frame(left_panel, bg=SURFACE)
        info_box.pack(fill=tk.X, pady=(0, 8))

        tk.Label(info_box, text="Patient Name:", font=("Inter", 15, "bold"), bg=SURFACE, fg=TEXT_MAIN).grid(row=0,
                                                                                                            column=0,
                                                                                                            sticky="w",
                                                                                                            pady=4)
        self.name_var = tk.StringVar(value="S SAI SHIRISH")
        name_entry = tk.Entry(info_box, textvariable=self.name_var, font=("Inter", 15, "bold"), bg=BG_DARK,
                              fg=TEXT_MAIN, insertbackground=TEXT_MAIN, width=18)
        name_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=4)

        tk.Label(info_box, text="Patient ID / MRN:", font=("Inter", 15, "bold"), bg=SURFACE, fg=TEXT_MAIN).grid(row=1,
                                                                                                                column=0,
                                                                                                                sticky="w",
                                                                                                                pady=4)
        self.id_var = tk.StringVar(value="MRN-884925")
        id_entry = tk.Entry(info_box, textvariable=self.id_var, font=("Inter", 15, "bold"), bg=BG_DARK, fg=TEXT_MAIN,
                            insertbackground=TEXT_MAIN, width=18)
        id_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=4)

        separator = ttk.Separator(left_panel, orient='horizontal')
        separator.pack(fill=tk.X, pady=8)

        self.vars = {}
        vitals = [
            ("Age (years)", "age", 52, 30, 80),
            ("Height (cm)", "height", 170, 140, 200),
            ("Weight (kg)", "weight", 75, 40, 150),
            ("Systolic BP (ap_hi)", "ap_hi", 130, 90, 220),
            ("Diastolic BP (ap_lo)", "ap_lo", 85, 60, 140)
        ]

        for label, key, default, vmin, vmax in vitals:
            row = tk.Frame(left_panel, bg=SURFACE)
            row.pack(fill=tk.X, pady=2)

            lbl_row = tk.Frame(row, bg=SURFACE)
            lbl_row.pack(fill=tk.X, pady=(0, 1))
            tk.Label(lbl_row, text=label, font=("Inter", 15, "bold"), bg=SURFACE, fg=TEXT_MAIN).pack(side=tk.LEFT)

            var = tk.IntVar(value=default)
            self.vars[key] = var

            val_lbl = tk.Label(lbl_row, text=str(default), font=("IBM Plex Mono", 17, "bold"), bg=SURFACE,
                               fg=ACCENT_CYAN)
            val_lbl.pack(side=tk.RIGHT)

            scale = tk.Scale(row, variable=var, from_=vmin, to=vmax, orient=tk.HORIZONTAL, bg=SURFACE, fg=ACCENT_CYAN,
                             highlightthickness=0, troughcolor=BG_DARK, length=380,
                             command=lambda v, vl=val_lbl, vr=var: [vl.config(text=str(vr.get())),
                                                                    self.compute_quantum_risk()])
            scale.pack(fill=tk.X)

        # --- MANUAL BLOOD GLUCOSE INPUT FIELD ---
        glu_row = tk.Frame(left_panel, bg=SURFACE)
        glu_row.pack(fill=tk.X, pady=6)

        glu_lbl_frame = tk.Frame(glu_row, bg=SURFACE)
        glu_lbl_frame.pack(fill=tk.X, pady=(0, 2))
        tk.Label(glu_lbl_frame, text="Blood Glucose (mg/dL)", font=("Inter", 15, "bold"), bg=SURFACE,
                 fg=TEXT_MAIN).pack(side=tk.LEFT)

        tk.Label(glu_lbl_frame, text="[Best: 70–99 mg/dL Fasting]", font=("IBM Plex Mono", 11, "bold"), bg=SURFACE,
                 fg=ACCENT_EMERALD).pack(side=tk.RIGHT)

        glu_input_frame = tk.Frame(glu_row, bg=SURFACE)
        glu_input_frame.pack(fill=tk.X)

        self.glucose_var = tk.StringVar(value="95")
        glucose_entry = tk.Entry(glu_input_frame, textvariable=self.glucose_var, font=("IBM Plex Mono", 16, "bold"),
                                 bg=BG_DARK, fg=ACCENT_CYAN, insertbackground=TEXT_MAIN, width=12)
        glucose_entry.pack(side=tk.LEFT)
        glucose_entry.bind("<KeyRelease>", lambda e: self.compute_quantum_risk())

        tk.Label(glu_input_frame, text="  (Type manual hospital report value)", font=("Inter", 11), bg=SURFACE,
                 fg=TEXT_MUTED).pack(side=tk.LEFT)

        # --- LIFESTYLE OPTIONS ---
        lifestyle_frame = tk.Frame(left_panel, bg=SURFACE, padx=2, pady=4)
        lifestyle_frame.pack(fill=tk.X, pady=(4, 2))

        tk.Label(lifestyle_frame, text="Lifestyle Factors:", font=("Space Grotesk", 15, "bold"), bg=SURFACE,
                 fg=ACCENT_CYAN).pack(anchor="w", pady=(0, 4))

        toggle_box = tk.Frame(lifestyle_frame, bg=SURFACE)
        toggle_box.pack(anchor="w")

        self.smoker_var = tk.IntVar(value=0)
        self.alcohol_var = tk.IntVar(value=0)

        smoker_chk = tk.Checkbutton(toggle_box, text="Smoker Status", variable=self.smoker_var,
                                    font=("Inter", 13, "bold"), bg=SURFACE, fg=TEXT_MAIN, selectcolor=BG_DARK,
                                    activebackground=SURFACE, activeforeground=TEXT_MAIN,
                                    command=self.compute_quantum_risk)
        smoker_chk.pack(side=tk.LEFT, padx=(0, 20))

        alcohol_chk = tk.Checkbutton(toggle_box, text="Alcoholic Status", variable=self.alcohol_var,
                                     font=("Inter", 13, "bold"), bg=SURFACE, fg=TEXT_MAIN, selectcolor=BG_DARK,
                                     activebackground=SURFACE, activeforeground=TEXT_MAIN,
                                     command=self.compute_quantum_risk)
        alcohol_chk.pack(side=tk.LEFT)

        # --- SAVE CHANGES BUTTON ---
        save_btn = tk.Button(left_panel, text="💾 Save Changes & Store Patient Record",
                             font=("Space Grotesk", 15, "bold"), bg=ACCENT_EMERALD, fg=BG_DARK,
                             activebackground=ACCENT_CYAN, activeforeground=BG_DARK, padx=14, pady=8, relief="flat",
                             command=self.save_patient_changes)
        save_btn.pack(fill=tk.X, pady=(10, 2))

        # --- RIGHT PANEL: COMPACT & FULLY VISIBLE RISK MONITOR ---
        right_panel = tk.Frame(container, bg=SURFACE, padx=24, pady=20, highlightbackground=SURFACE_BORDER,
                               highlightthickness=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(16, 0))

        tk.Label(right_panel, text="QUANTUM RISK STRATIFICATION", font=("Space Grotesk", 18, "bold"), bg=SURFACE,
                 fg=ACCENT_EMERALD).pack(anchor="w", pady=(0, 10))

        prob_box = tk.Frame(right_panel, bg=BG_DARK, padx=16, pady=10, highlightbackground=ACCENT_EMERALD,
                            highlightthickness=2)
        prob_box.pack(fill=tk.X, pady=(0, 10))

        tk.Label(prob_box, text="PREDICTED CARDIAC RISK PROBABILITY", font=("IBM Plex Mono", 11, "bold"), bg=BG_DARK,
                 fg=TEXT_MUTED).pack(anchor="center")

        self.prob_lbl = tk.Label(prob_box, text="48%", font=("Space Grotesk", 50, "bold"), bg=BG_DARK, fg=ACCENT_AMBER)
        self.prob_lbl.pack(anchor="center", pady=2)

        self.status_lbl = tk.Label(prob_box, text="MODERATE RISK ALERT", font=("Inter", 14, "bold"), bg=ACCENT_AMBER,
                                   fg=BG_DARK, padx=14, pady=4)
        self.status_lbl.pack(anchor="center", pady=(2, 0))

        self.fig, self.ax = plt.subplots(figsize=(5.5, 2.6), facecolor=SURFACE)
        self.ax.set_facecolor(SURFACE)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(6, 0))

    def build_prescription_tab(self):
        container = tk.Frame(self.tab_prescription, bg=BG_DARK)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        banner = tk.Frame(container, bg=SURFACE, padx=28, pady=22, highlightbackground=SURFACE_BORDER,
                          highlightthickness=2)
        banner.pack(fill=tk.X, pady=(0, 18))

        top_banner_row = tk.Frame(banner, bg=SURFACE)
        top_banner_row.pack(fill=tk.X, pady=(0, 8))

        tk.Label(top_banner_row, text="INDIVIDUALIZED CLINICAL PRESCRIPTION & DIET DIRECTIVE",
                 font=("Space Grotesk", 20, "bold"), bg=SURFACE, fg=ACCENT_CYAN).pack(side=tk.LEFT)

        download_btn = tk.Button(top_banner_row, text="📥 Download Clinical Report", font=("Space Grotesk", 16, "bold"),
                                 bg=ACCENT_CYAN, fg=BG_DARK, activebackground=ACCENT_EMERALD, activeforeground=BG_DARK,
                                 padx=20, pady=8, relief="flat", command=self.download_report_file)
        download_btn.pack(side=tk.RIGHT)

        self.patient_summary_lbl = tk.Label(banner,
                                            text="Patient: S SAI SHIRISH (MRN-884925)  |  Status: Initializing...",
                                            font=("IBM Plex Mono", 15, "bold"), bg=SURFACE, fg=TEXT_MAIN)
        self.patient_summary_lbl.pack(anchor="w")

        split_box = tk.Frame(container, bg=BG_DARK)
        split_box.pack(fill=tk.BOTH, expand=True)

        rx_card = tk.Frame(split_box, bg=SURFACE, padx=28, pady=28, highlightbackground=SURFACE_BORDER,
                           highlightthickness=2)
        rx_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        tk.Label(rx_card, text="💊 Prescribed Medication Regimen", font=("Space Grotesk", 35, "bold"), bg=SURFACE,
                 fg=ACCENT_EMERALD).pack(anchor="w", pady=(0, 16))

        self.rx_text = tk.Label(rx_card, text="", font=("Inter", 25), bg=SURFACE, fg=TEXT_MAIN, justify=tk.LEFT,
                                anchor="nw", wraplength=850)
        self.rx_text.pack(anchor="nw", fill=tk.BOTH, expand=True)

        diet_card = tk.Frame(split_box, bg=SURFACE, padx=28, pady=28, highlightbackground=SURFACE_BORDER,
                             highlightthickness=2)
        diet_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(12, 0))

        tk.Label(diet_card, text="🥗 Personalized Dietary Prescription & Support", font=("Space Grotesk", 35, "bold"),
                 bg=SURFACE, fg=ACCENT_AMBER).pack(anchor="w", pady=(0, 16))

        self.diet_text = tk.Label(diet_card, text="", font=("Inter", 25), bg=SURFACE, fg=TEXT_MAIN, justify=tk.LEFT,
                                  anchor="nw", wraplength=850)
        self.diet_text.pack(anchor="nw", fill=tk.BOTH, expand=True)

    def save_patient_changes(self):
        name = self.name_var.get().strip()
        mrn = self.id_var.get().strip()

        if mrn in self.patient_database and self.patient_database[mrn] != name:
            messagebox.showerror(
                "MRN Collision Error",
                f"The Patient ID / MRN '{mrn}' is already registered to another patient ('{self.patient_database[mrn]}').\n\n"
                f"Please change the last two or three digits of the ID to ensure a unique patient record for '{name}'."
            )
            return

        self.patient_database[mrn] = name

        age = self.vars['age'].get()
        height = self.vars['height'].get()
        weight = self.vars['weight'].get()
        ap_hi = self.vars['ap_hi'].get()
        ap_lo = self.vars['ap_lo'].get()
        smoker = bool(self.smoker_var.get())
        alcoholic = bool(self.alcohol_var.get())

        try:
            glucose = float(self.glucose_var.get())
        except ValueError:
            glucose = 95.0

        self.current_patient_record = {
            "name": name,
            "mrn": mrn,
            "age": age,
            "height": height,
            "weight": weight,
            "ap_hi": ap_hi,
            "ap_lo": ap_lo,
            "glucose": glucose,
            "smoker": smoker,
            "alcoholic": alcoholic
        }

        self.compute_quantum_risk()
        messagebox.showinfo("Success",
                            f"Patient profile for '{name}' ({mrn}) successfully saved, validated, and synchronized with prescription engine!")

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
                    "Generated locally by CardioPulse Quantum Pro HUD System\n"
                    "Safety Notice: Unsafe to prescribe exact treatment months or schedules from a model percentage. Clinician-defined review required[cite: 21].\n"
                )
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(report_content)
                messagebox.showinfo("Export Successful", f"Clinical report successfully saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save file: {e}")

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

            glu_factor = max(0.0, (glucose - 100.0) / 25.0) * 0.15

            inputs_raw = [age, 1, height, weight, bmi, ap_hi, ap_lo, 1, 1, smoker, alcoholic, 1]
            z = self.lr_intercept + glu_factor
            for i, val in enumerate(inputs_raw):
                scaled = (val - self.scaler_mean[i]) / self.scaler_scale[i]
                z += scaled * self.lr_weights[i]

            prob = 1 / (1 + math.exp(-z))
            pct = round(prob * 100)

            self.prob_lbl.config(text=f"{pct}%")

            # --- 10-STAGE RISK STRATIFICATION ---
            if pct < 50:
                risk_tier = "Below 50% — General Preventive Plan"
                self.status_lbl.config(text="PREVENTIVE HEALTH STAGE", bg=ACCENT_EMERALD, fg=BG_DARK)
                self.prob_lbl.config(fg=ACCENT_EMERALD)
            elif pct <= 55:
                risk_tier = "Stage 1: 50-55% - Elevated Risk"
                self.status_lbl.config(text="STAGE 1: ELEVATED RISK", bg=ACCENT_EMERALD, fg=BG_DARK)
                self.prob_lbl.config(fg=ACCENT_EMERALD)
            elif pct <= 60:
                risk_tier = "Stage 2: 55-60% - Increased Risk"
                self.status_lbl.config(text="STAGE 2: INCREASED RISK", bg=ACCENT_CYAN, fg=BG_DARK)
                self.prob_lbl.config(fg=ACCENT_CYAN)
            elif pct <= 65:
                risk_tier = "Stage 3: 60-65% - High Risk"
                self.status_lbl.config(text="STAGE 3: HIGH RISK", bg=ACCENT_CYAN, fg=BG_DARK)
                self.prob_lbl.config(fg=ACCENT_CYAN)
            elif pct <= 70:
                risk_tier = "Stage 4: 65-70% - Significant Risk"
                self.status_lbl.config(text="STAGE 4: SIGNIFICANT RISK", bg=ACCENT_AMBER, fg=BG_DARK)
                self.prob_lbl.config(fg=ACCENT_AMBER)
            elif pct <= 75:
                risk_tier = "Stage 5: 70-75% - Very High Risk"
                self.status_lbl.config(text="STAGE 5: VERY HIGH RISK", bg=ACCENT_AMBER, fg=BG_DARK)
                self.prob_lbl.config(fg=ACCENT_AMBER)
            elif pct <= 80:
                risk_tier = "Stage 6: 75-80% - Advanced Risk"
                self.status_lbl.config(text="STAGE 6: ADVANCED RISK", bg=ACCENT_AMBER, fg=BG_DARK)
                self.prob_lbl.config(fg=ACCENT_AMBER)
            elif pct <= 85:
                risk_tier = "Stage 7: 80-85% - Severe Risk Indicator"
                self.status_lbl.config(text="STAGE 7: SEVERE RISK", bg=ACCENT_ROSE, fg=TEXT_MAIN)
                self.prob_lbl.config(fg=ACCENT_ROSE)
            elif pct <= 90:
                risk_tier = "Stage 8: 85-90% - Critical Risk Indicator"
                self.status_lbl.config(text="STAGE 8: CRITICAL RISK", bg=ACCENT_ROSE, fg=TEXT_MAIN)
                self.prob_lbl.config(fg=ACCENT_ROSE)
            elif pct <= 95:
                risk_tier = "Stage 9: 90-95% - Extreme Risk Indicator"
                self.status_lbl.config(text="STAGE 9: EXTREME RISK", bg=ACCENT_ROSE, fg=TEXT_MAIN)
                self.prob_lbl.config(fg=ACCENT_ROSE)
            else:
                risk_tier = "Stage 10: 95-100% - Maximum Model Risk Indicator"
                self.status_lbl.config(text="STAGE 10: MAXIMUM MODEL RISK", bg=ACCENT_ROSE, fg=TEXT_MAIN)
                self.prob_lbl.config(fg=ACCENT_ROSE)

            self.ax.clear()
            self.ax.set_facecolor(SURFACE)
            features = ['Systolic BP', 'Age', 'Glucose', 'Lifestyle']
            weights = [ap_hi * 0.35, age * 0.20, min(glucose * 0.25, 40), (smoker * 12 + alcoholic * 8)]

            bar_color = ACCENT_ROSE if pct >= 65 else (ACCENT_AMBER if pct >= 50 else ACCENT_EMERALD)
            self.ax.barh(features, weights, color=bar_color, height=0.55)
            self.ax.set_title("Neural Feature Attribution Weights", fontsize=12, color=TEXT_MAIN, fontweight="bold")
            self.ax.tick_params(colors=TEXT_MUTED, labelsize=11)
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            self.fig.tight_layout()
            self.canvas.draw()

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
        self.patient_summary_lbl.config(
            text=f"Patient: {name} ({mrn}) [{lifestyle_str}] | Glucose: {glucose} mg/dL ({glu_status}) | Risk: {pct}% [{tier}]")

        if pct < 50:
            rx_content = (
                "• General Preventive Medicines Note:\n"
                "There is no universal preventive medicine for everyone below 50%[cite: 19]. Statins, antihypertensives and diabetes medicines should be considered only when clinically indicated after individual assessment[cite: 19]."
            )
            diet_content = (
                "🥗 General Preventive Dietary Plan (Below 50%):\n\n"
                "• Breakfast: Oats, idli or vegetable upma[cite: 19].\n"
                "• Mid-morning: Apple, guava or papaya[cite: 19].\n"
                "• Lunch: Brown rice, dal, vegetables and curd[cite: 19].\n"
                "• Evening: Unsalted almonds, walnuts or roasted chana[cite: 19].\n"
                "• Dinner: Chapati, vegetables and lentils[cite: 19].\n"
                "• Hydration: Water according to individual needs and any clinician-directed fluid plan[cite: 19].\n\n"
                "💬 Comment:\n"
                "\"Great job taking an interest in your cardiovascular health! Your current assessment provides an opportunity to maintain healthy habits and protect your long-term well-being. Continue eating balanced meals, staying physically active, sleeping well and attending routine health check-ups. Prevention is always a valuable investment in your future. Keep up the excellent work!\"[cite: 19]"
            )
        elif pct <= 55:
            rx_content = (
                "💊 Stage 1 Medication Information & Administration Timing (Only when clinically indicated)[cite: 11, 22]:\n\n"
                "• Atorvastatin\n"
                "  - Timing: Once daily; any consistent time[cite: 22]\n"
                "  - Food: With or without food[cite: 22]\n"
                "  - Duration: Often long term, sometimes lifelong, if indicated; review lipids, tolerance and interactions[cite: 22]\n\n"
                "• Rosuvastatin\n"
                "  - Timing: Once daily; any consistent time[cite: 22]\n"
                "  - Food: With or without food[cite: 22]\n"
                "  - Duration: Often long term, sometimes lifelong, if indicated; review response and adverse effects[cite: 22]\n\n"
                "• Amlodipine\n"
                "  - Timing: Once daily; same time[cite: 22]\n"
                "  - Food: Before or after food[cite: 22]\n"
                "  - Duration: Often long term for hypertension/angina; review BP, ankle swelling and dizziness[cite: 22]\n\n"
                "• Telmisartan\n"
                "  - Timing: Once daily; same time[cite: 22]\n"
                "  - Food: With or without food[cite: 22]\n"
                "  - Duration: Often ongoing for hypertension/selected indications; monitor BP, kidney function and potassium[cite: 22]"
            )
            diet_content = (
                "🥗 Stage 1 Dietary Plan & Directives:\n\n"
                "• Breakfast: Oatmeal, almonds and an apple[cite: 11].\n"
                "• Mid-morning: Guava or papaya[cite: 11].\n"
                "• Lunch: Brown rice, dal, spinach and curd[cite: 11].\n"
                "• Evening: Unsalted walnuts[cite: 11].\n"
                "• Dinner: Whole-wheat chapati with vegetables[cite: 11].\n"
                "• Core Rule: Include whole grains, fruits and vegetables; reduce excess salt and fried foods[cite: 11].\n\n"
                "💬 Comment:\n"
                "\"Your cardiovascular indicators suggest that some attention to your heart health may be beneficial. The good news is that this is an opportunity to establish healthier habits before further complications develop. Consistent physical activity, balanced nutrition and regular health monitoring can make a meaningful difference. Small improvements made today can contribute to a healthier tomorrow. Keep going!\"[cite: 11]"
            )
        elif pct <= 60:
            rx_content = (
                "💊 Stage 2 Medication Information & Administration Timing (Only when clinically indicated)[cite: 11, 22]:\n\n"
                "• Atorvastatin | Timing: Once daily (any time) | Food: With/without food | Duration: Often long term[cite: 22]\n"
                "• Rosuvastatin | Timing: Once daily (any time) | Food: With/without food | Duration: Often long term[cite: 22]\n"
                "• Ezetimibe | Timing: Once daily (same time) | Food: With/without food | Duration: Continued while clinically needed; review LDL[cite: 22]\n"
                "• Amlodipine | Timing: Once daily (same time) | Food: Before/after food | Duration: Often long term[cite: 22]\n"
                "• Losartan | Timing: Once daily (same time) | Food: With/without food | Duration: Often long term; review BP, kidney function and potassium[cite: 22]"
            )
            diet_content = (
                "🥗 Stage 2 Dietary Plan & Directives:\n\n"
                "• Breakfast: Vegetable oats or idli with sambar[cite: 11].\n"
                "• Mid-morning: Orange or apple[cite: 11].\n"
                "• Lunch: Brown rice, dal and green vegetables[cite: 11].\n"
                "• Evening: Roasted chana or unsalted almonds[cite: 11].\n"
                "• Dinner: Chapati with vegetable curry[cite: 11].\n"
                "• Core Rule: Increase fibre; avoid packaged snacks and sugary beverages; reduce excessive salt[cite: 11].\n\n"
                "💬 Comment:\n"
                "\"Your results indicate that your cardiovascular health deserves additional attention. However, this is also an excellent opportunity to make positive changes. Your heart responds to consistent care, and improvements in nutrition, activity and blood pressure management can support better long-term health. Stay motivated and remember that every healthy decision counts!\"[cite: 11, 12]"
            )
        elif pct <= 65:
            rx_content = (
                "💊 Stage 3 Medication Information & Administration Timing (Only when clinically indicated)[cite: 12, 22]:\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Long term if indicated[cite: 22]\n"
                "• Ezetimibe | Timing: Once daily | Food: With/without food | Duration: As prescribed[cite: 22]\n"
                "• Telmisartan / Losartan | Timing: Once daily | Food: With/without food | Duration: Ongoing / long term[cite: 22]\n"
                "• Ramipril | Timing: Once/twice daily (first dose bedtime if advised) | Food: With/without food | Duration: Often long term; monitor cough/angioedema[cite: 22]\n"
                "• Amlodipine | Timing: Once daily | Food: Before/after food | Duration: Usually ongoing[cite: 22]"
            )
            diet_content = (
                "🥗 Stage 3 Dietary Plan & Directives:\n\n"
                "• Breakfast: Oats with chia seeds and fruit[cite: 12].\n"
                "• Mid-morning: Papaya[cite: 12].\n"
                "• Lunch: Brown rice, dal, broccoli and vegetables[cite: 12].\n"
                "• Evening: Unsalted almonds[cite: 12].\n"
                "• Dinner: Whole-wheat chapati with lentils[cite: 12].\n"
                "• Core Rule: Prefer steaming, boiling and grilling; reduce saturated fats; avoid processed meats; monitor portions[cite: 12].\n\n"
                "💬 Comment:\n"
                "\"Your current indicators suggest that your heart health requires more focused attention. The encouraging part is that several important cardiovascular risk factors can be managed through appropriate medical care and lifestyle improvements. With regular follow-ups, a heart-friendly diet and a consistent routine, you can actively work towards improving your health. Stay positive and take one step at a time!\"[cite: 12]"
            )
        elif pct <= 70:
            rx_content = (
                "💊 Stage 4 Medication Information & Administration Timing (Only when clinically indicated)[cite: 13, 22]:\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Long term if prescribed[cite: 22]\n"
                "• Ezetimibe | Timing: Once daily | Food: With/without food | Duration: As prescribed[cite: 22]\n"
                "• Amlodipine / Telmisartan | Timing: Once daily | Food: Before/after food | Duration: Usually ongoing[cite: 22]\n"
                "• Bisoprolol / Metoprolol | Timing: Once daily, commonly morning | Food: Per product leaflet; keep timing consistent | Duration: Long term for selected cardiac indications; do not stop abruptly[cite: 22]"
            )
            diet_content = (
                "🥗 Stage 4 Dietary Plan & Directives:\n\n"
                "• Breakfast: Vegetable oats with low-fat milk[cite: 13].\n"
                "• Mid-morning: Apple or guava[cite: 13].\n"
                "• Lunch: Moderate portion of rice, dal and leafy vegetables[cite: 13].\n"
                "• Evening: Unsalted nuts[cite: 13].\n"
                "• Dinner: Chapati with steamed vegetables[cite: 13].\n"
                "• Core Rule: Limit sodium; avoid deep-fried foods and processed/high-fat meats; individualize restrictions for kidney or heart disease[cite: 13].\n\n"
                "💬 Comment:\n"
                "\"Your cardiovascular assessment indicates that taking proactive steps is particularly important at this stage. Remember that a higher risk indicator does not mean that improvement is impossible. With appropriate medical supervision, consistent monitoring and healthier daily choices, you can take meaningful steps towards protecting your heart. Your commitment to your health is an important part of your progress!\"[cite: 13]"
            )
        elif pct <= 75:
            rx_content = (
                "💊 Stage 5 Medication Information & Administration Timing (Only when clinically indicated)[cite: 13, 22]:\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Usually long-term if indicated[cite: 22]\n"
                "• Ramipril / Telmisartan | Timing: Once/twice daily | Food: With/without food | Duration: Condition-dependent / ongoing[cite: 22]\n"
                "• Metoprolol | Timing: Formulation-dependent | Food: With/immediately after food | Duration: Condition-dependent[cite: 22]\n"
                "• Empagliflozin | Timing: Once daily, usually morning | Food: With or without food | Duration: Often long term for appropriate indications; monitor hydration[cite: 22]"
            )
            diet_content = (
                "🥗 Stage 5 Dietary Plan & Directives:\n\n"
                "• Breakfast: Oats with fruit[cite: 13].\n"
                "• Mid-morning: Guava[cite: 14].\n"
                "• Lunch: Dal, vegetables and a controlled portion of whole grains[cite: 14].\n"
                "• Evening: Unsalted nuts[cite: 14].\n"
                "• Dinner: Vegetable soup and chapati[cite: 14].\n"
                "• Core Rule: Reduce sodium and saturated fat; avoid processed food; prefer plant protein; obtain professional dietary advice[cite: 14].\n\n"
                "💬 Comment:\n"
                "\"Your results indicate that your cardiovascular health needs careful attention and consistent medical supervision. Although this stage requires greater commitment, you are not without options. Appropriate treatment, regular monitoring and a personalized nutrition plan can help manage important risk factors. Stay encouraged, follow your healthcare professional's advice and remember that your health journey is built one day at a time!\"[cite: 14]"
            )
        elif pct <= 80:
            rx_content = (
                "💊 Stage 6 Medication Information & Administration Timing (Only when clinically indicated)[cite: 14, 22]:\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Long term if prescribed[cite: 22]\n"
                "• Evolocumab | Timing: Injection every 2 weeks or monthly | Food: No meal timing applies | Duration: Continued while indication and benefit remain[cite: 22]\n"
                "• Sacubitril/valsartan | Timing: Usually twice daily, spaced evenly | Food: With or without food | Duration: Long term in eligible heart failure patients if tolerated[cite: 22, 23]\n"
                "• Bisoprolol | Timing: Once daily (morning) | Food: Follow leaflet | Duration: Long term if tolerated[cite: 22]\n"
                "• Empagliflozin | Timing: Once daily, morning | Food: With/without food | Duration: Long term if indicated[cite: 22]"
            )
            diet_content = (
                "🥗 Stage 6 Dietary Plan & Directives:\n\n"
                "• Breakfast: Unsweetened oatmeal[cite: 14].\n"
                "• Mid-morning: Small fruit portion[cite: 14].\n"
                "• Lunch: Vegetable dal and controlled portions of whole grains[cite: 14].\n"
                "• Evening: Unsalted nuts[cite: 14].\n"
                "• Dinner: Chapati with vegetables and suitable protein[cite: 14].\n"
                "• Core Rule: Reduce excess sodium; avoid processed meats; fluid and potassium restrictions only when clinically advised[cite: 14].\n\n"
                "💬 Comment:\n"
                "\"Your cardiovascular indicators suggest that your heart deserves closer attention and a carefully managed healthcare plan. It is important to remain hopeful while taking your medical recommendations seriously. Consistent follow-ups, appropriate treatment and personalized lifestyle changes can support your overall health. Every effort you make towards better health matters. Stay strong and keep working towards your recovery goals!\"[cite: 14]"
            )
        elif pct <= 85:
            rx_content = (
                "💊 Stage 7 Medication Information & Administration Timing (Only when clinically indicated)[cite: 15, 22, 23]:\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Long term if indicated[cite: 22]\n"
                "• Evolocumab | Timing: Bi-weekly/monthly injection | Food: No meal timing | Duration: Ongoing while indicated[cite: 22]\n"
                "• Sacubitril/valsartan | Timing: Twice daily, spaced evenly | Food: With/without food | Duration: Long term if tolerated[cite: 23]\n"
                "• Metoprolol succinate | Timing: Formulation-dependent | Food: With/after food | Duration: Long term if indicated[cite: 22]\n"
                "• Dapagliflozin | Timing: Once daily, morning | Food: With/without food | Duration: Long term if indicated[cite: 22]"
            )
            diet_content = (
                "🥗 Stage 7 Dietary Plan & Directives:\n\n"
                "• Breakfast: Oatmeal[cite: 15].\n"
                "• Mid-morning: Fresh fruit if appropriate[cite: 15].\n"
                "• Lunch: Vegetables, dal and a suitable grain portion[cite: 15].\n"
                "• Evening: Unsalted nuts in appropriate portions[cite: 15].\n"
                "• Dinner: Light vegetable-based meal with suitable protein[cite: 15].\n"
                "• Core Rule: Avoid excess sodium and processed foods; follow a cardiologist-approved plan; individualize fluid intake[cite: 15].\n\n"
                "💬 Comment:\n"
                "\"Your current assessment indicates that professional cardiovascular evaluation is particularly important. Please remember that a risk score is not a prediction of your immediate future. With the right medical guidance, careful monitoring and a personalized care plan, there are meaningful ways to manage cardiovascular health. Stay hopeful, seek timely support and prioritize your well-being.\"[cite: 15]"
            )
        elif pct <= 90:
            rx_content = (
                "💊 Stage 8 Medication Information & Administration Timing (Only when clinically indicated)[cite: 15, 22, 23]:\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Long term if indicated[cite: 22]\n"
                "• Clopidogrel | Timing: Once daily at consistent time | Food: With/without food | Duration: Weeks/months to long term per diagnosis and bleeding risk[cite: 22]\n"
                "• Aspirin (low-dose) | Timing: Consistent time | Food: Take with/after food if stomach upset | Duration: Clinician-determined[cite: 22]\n"
                "• Sacubitril/valsartan | Timing: Twice daily | Food: With/without food | Duration: Long term if indicated[cite: 23]\n"
                "• Empagliflozin | Timing: Once daily, morning | Food: With/without food | Duration: Long term if indicated[cite: 22]"
            )
            diet_content = (
                "🥗 Stage 8 Dietary Plan & Directives:\n\n"
                "• Follow an individualized cardiology-approved diet[cite: 15].\n"
                "• Avoid excessive sodium and deep-fried foods[cite: 15].\n"
                "• Prefer fresh vegetables and appropriate protein[cite: 15].\n"
                "• Avoid excessive sugar[cite: 15].\n"
                "• Follow specific fluid restrictions only if prescribed[cite: 15].\n\n"
                "💬 Comment:\n"
                "\"Your assessment highlights the importance of receiving timely professional medical attention. Please remain calm and avoid making medication changes independently. Cardiovascular conditions can often be managed through appropriate medical interventions and continuous supervision. Your health and safety come first. Stay connected with your healthcare provider and follow the care plan recommended for you.\"[cite: 15, 16]"
            )
        elif pct <= 95:
            rx_content = (
                "💊 Stage 9 Medication Information & Administration Timing (Only when clinically indicated)[cite: 17, 22, 23]:\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Long term if indicated[cite: 22]\n"
                "• Clopidogrel / Aspirin | Timing: Once daily | Food: With/without food | Duration: Specialist-determined[cite: 22]\n"
                "• Ticagrelor | Timing: Twice daily, ~12 hours apart | Food: With/without food | Duration: Time-limited post-ACS plan (default 12 months dual therapy if applicable)[cite: 22]\n"
                "• Sacubitril/valsartan | Timing: Twice daily | Food: With/without food | Duration: Long term if indicated[cite: 23]\n"
                "• Dapagliflozin | Timing: Once daily, morning | Food: With/without food | Duration: Long term if indicated[cite: 22]"
            )
            diet_content = (
                "🥗 Stage 9 Dietary Plan & Directives:\n\n"
                "• Individualized clinical nutrition plan[cite: 17].\n"
                "• Avoid excessive salt and processed foods[cite: 17].\n"
                "• Avoid trans fats[cite: 17].\n"
                "• Follow clinician-directed fluid and nutritional restrictions[cite: 17].\n"
                "• Do not use food or supplements as substitutes for medical treatment[cite: 17].\n\n"
                "💬 Comment:\n"
                "\"Your results indicate that immediate professional review is important. Please remember that the percentage displayed is a model-generated estimate and does not independently establish a diagnosis or predict an imminent cardiac event. The most important step is to receive the appropriate medical assessment. You deserve proper care and support, and taking action now is a positive step towards protecting your health.\"[cite: 17]"
            )
        else:
            rx_content = (
                "💊 Stage 10 Medication Information & Administration Timing (Only when clinically indicated)[cite: 17, 22, 23]:\n\n"
                "• Atorvastatin / Rosuvastatin | Timing: Once daily | Food: With/without food | Duration: Usually long-term[cite: 22]\n"
                "• Aspirin / Clopidogrel / Ticagrelor | Timing: As prescribed | Food: Formulation-specific | Duration: Specialist-determined[cite: 22]\n"
                "• Metoprolol | Timing: Formulation-dependent | Food: With/after food | Duration: Condition-dependent[cite: 22]\n"
                "• Sacubitril/valsartan | Timing: Twice daily | Food: With/without food | Duration: Long term if indicated[cite: 23]"
            )
            diet_content = (
                "🥗 Stage 10 Dietary Plan & Directives:\n\n"
                "• Obtain an individualized medical nutrition plan[cite: 17].\n"
                "• Avoid excess sodium and highly processed foods[cite: 17, 18].\n"
                "• Follow prescribed fluid restrictions if applicable[cite: 18].\n"
                "• Maintain appropriate nutrition under medical supervision[cite: 18].\n"
                "• Do not delay medical assessment to follow a dietary plan[cite: 18].\n\n"
                "💬 Comment:\n"
                "\"Your assessment indicates that your cardiovascular health requires immediate professional attention. Please do not panic or make independent changes to your medication. A model-generated score is not a confirmed diagnosis, and appropriate medical evaluation is essential to understand your actual condition. You are taking an important step by paying attention to your health. Please seek the necessary medical support and allow your healthcare team to guide your next steps.\"[cite: 18]"
            )

        self.rx_text.config(text=rx_content)
        self.diet_text.config(text=diet_content)


if __name__ == "__main__":
    root = tk.Tk()
    app = CardioPulseQuantumProApp(root)
    root.mainloop()