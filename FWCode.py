# LÖSUNG 1: Encoding-Fehler (cp1252) beheben
import os

os.environ['PYTHONUTF8'] = '1'

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import random

# Stellen Sie sicher, dass Sie "pip install pillow" ausgeführt haben
try:
    from PIL import Image, ImageDraw, ImageTk, ImageOps
except ImportError:
    print("Fehler: Die 'Pillow' Bibliothek wurde nicht gefunden.")
    print("Bitte installieren Sie sie mit: pip install pillow")
    exit()


def get_kontenplan():
    """
    Erstellt den Kontenplan basierend auf dem bereitgestellten PDF.
    Stark erweitert für MWST, AG und EU.
    """
    return {
        # Aktiven
        "1000": "Kasse", "1020": "Post", "1021": "Bankguthaben",
        "1100": "Forderungen aus Lieferungen und Leistungen (Debitoren)",
        "1170": "Vorsteuer MWST Material, Waren",
        "1171": "Vorsteuer MWST Investitionen",
        "1200": "Vorrat Handelswaren",
        "1510": "Mobiliar und Einrichtungen",

        # Passiven
        "2000": "Verbindlichkeiten aus Lieferungen und Leistungen (Kreditoren)",
        "2100": "Bankverbindlichkeiten",  # (Für Darlehen)
        "2200": "Verbindlichkeit MWST (Umsatzsteuer)",
        "2261": "Dividenden (Beschlossene Ausschüttung)",
        "2330": "Kurzfristige Rückstellungen",

        # Eigenkapital (AG / GmbH)
        "2800": "Aktienkapital (AG); Stammkapital (GmbH)",
        "2960": "Freiwillige Gewinnreserve",
        "2979": "Jahresgewinn oder Jahresverlust",

        # Eigenkapital (Einzelunternehmen)
        "2800.EU": "Eigenkapital (Einzelunternehmung)",
        "2850": "Privat (Einzelunternehmung)",
        "2891": "Jahresgewinn oder Jahresverlust (EU)",

        # Ertrag
        "3200": "Warenerlöse", "3400": "Dienstleistungserlöse",
        "3600": "Übrige Erlöse",

        # Aufwand
        "4000": "Materialaufwand",
        "4200": "Warenaufwand",
        "5000": "Lohnaufwand",
        "6000": "Raumaufwand",
        "6200": "Fahrzeugaufwand",
        "6500": "Verwaltungsaufwand",
        "6600": "Werbeaufwand",
        "6700": "Sonstiger Betriebsaufwand",
        "6900": "Finanzaufwand",  # (Für Zinsen)
    }


# --- HIER IST DIE NEUE, DYNAMISCHE GENERIERUNG ---
def generate_question(kontenplan, game_mode):
    """
    Generiert einen zufälligen Geschäftsfall dynamisch basierend auf Regeln.
    """

    # --- 1. Bausteine definieren ---

    # {Name: KontoNr}
    liquid_assets = {"Bank": "1021", "Post": "1020", "Kasse": "1000"}
    op_expenses = {"der Büromiete": "6000", "einer Werbekampagne": "6600", "der Tankrechnung": "6200",
                   "von Büromaterial": "6500"}
    material_expenses = {"Handelsgütern": "4200", "Rohmaterialien": "4000"}
    op_revenues = {"erbrachte Dienstleistungen": "3400", "verkaufte Waren": "3200"}
    investments = {"neues Mobiliar": "1510"}  # Könnte erweitert werden (z.B. Fahrzeuge 1530)

    # --- 2. Regelfunktionen definieren (Classic Modus) ---

    def rule_pay_expense_simple():
        # Zahle einfachen Aufwand (ohne MWST)
        exp_name, exp_acc = random.choice(list(op_expenses.items()))
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Bezahlung {exp_name} per {liq_name} (ohne VST)."
        return {'fall': fall, 'soll': [exp_acc], 'haben': [liq_acc]}

    def rule_customer_pays():
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Ein Kunde begleicht eine offene Rechnung per {liq_name}."
        return {'fall': fall, 'soll': [liq_acc], 'haben': ["1100"]}

    def rule_we_pay_supplier():
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Wir begleichen eine Lieferantenrechnung per {liq_name}."
        return {'fall': fall, 'soll': ["2000"], 'haben': [liq_acc]}

    def rule_cash_transfer():
        # Wähle zwei UNTERSCHIEDLICHE liquide Konten
        (liq1_name, liq1_acc), (liq2_name, liq2_acc) = random.sample(list(liquid_assets.items()), 2)
        fall = f"Übertrag von {liq1_name} auf {liq2_name}."
        return {'fall': fall, 'soll': [liq2_acc], 'haben': [liq1_acc]}

    def rule_buy_material_brutto():
        mat_name, mat_acc = random.choice(list(material_expenses.items()))
        fall = f"Eine Lieferantenrechnung für {mat_name} trifft ein. (Brutto, inkl. VST)."
        return {'fall': fall, 'soll': [mat_acc, "1170"], 'haben': ["2000"]}

    def rule_pay_expense_brutto():
        exp_name, exp_acc = random.choice(list(op_expenses.items()))
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Bezahlung {exp_name} per {liq_name} (Brutto, inkl. VST)."
        return {'fall': fall, 'soll': [exp_acc, "1170"], 'haben': [liq_acc]}

    def rule_sell_revenue_brutto():
        rev_name, rev_acc = random.choice(list(op_revenues.items()))
        fall = f"Wir stellen einem Kunden Rechnung für {rev_name}. (Brutto, inkl. UST)."
        return {'fall': fall, 'soll': ["1100"], 'haben': [rev_acc, "2200"]}

    def rule_sell_revenue_cash_brutto():
        rev_name, rev_acc = random.choice(list(op_revenues.items()))
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Ein Kunde bezahlt {rev_name} direkt per {liq_name}. (Brutto, inkl. UST)."
        return {'fall': fall, 'soll': [liq_acc], 'haben': [rev_acc, "2200"]}

    def rule_pay_mwst():
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Wir überweisen die geschuldete MWST-Abrechnung per {liq_name} an die ESTV."
        return {'fall': fall, 'soll': ["2200"], 'haben': [liq_acc]}

    def rule_buy_investment_brutto():
        inv_name, inv_acc = random.choice(list(investments.items()))
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Kauf von {inv_name} per {liq_name} (Brutto, inkl. VST Investitionen)."
        return {'fall': fall, 'soll': [inv_acc, "1171"], 'haben': [liq_acc]}

    def rule_pay_loan_combined():
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Die Bankrate für das Darlehen wird abgebucht (Zins UND Tilgung)."
        return {'fall': fall, 'soll': ["6900", "2100"], 'haben': [liq_acc]}

    def rule_provision_create():
        fall = "Bildung einer Rückstellung für einen Garantiefall."
        return {'fall': fall, 'soll': ["6700"], 'haben': ["2330"]}

    def rule_provision_use():
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Die effektive Garantieleistung (Rückstellung) wird per {liq_name} bezahlt."
        return {'fall': fall, 'soll': ["2330"], 'haben': [liq_acc]}

    def rule_provision_release():
        fall = "Eine nicht mehr benötigte Rückstellung wird erfolgswirksam aufgelöst."
        return {'fall': fall, 'soll': ["2330"], 'haben': ["3600"]}

    def rule_eu_deposit():
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Der Inhaber (Einzelunternehmen) legt {liq_name} als Privateinlage in die Firma ein."
        return {'fall': fall, 'soll': [liq_acc], 'haben': ["2850"]}

    def rule_eu_withdrawal():
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Der Inhaber (Einzelunternehmen) entnimmt Geld per {liq_name} für private Zwecke."
        return {'fall': fall, 'soll': ["2850"], 'haben': [liq_acc]}

    def rule_ag_create_capital():
        fall = "Gründung einer AG: Das Aktienkapital wird auf das Bankkonto einbezahlt."
        return {'fall': fall, 'soll': ["1021"], 'haben': ["2800"]}

    def rule_ag_decide_dividend():
        fall = "Die Generalversammlung beschliesst die Ausschüttung einer Dividende."
        return {'fall': fall, 'soll': ["2979"], 'haben': ["2261"]}

    def rule_ag_pay_dividend():
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Die beschlossene Dividende wird per {liq_name} an die Aktionäre ausbezahlt."
        return {'fall': fall, 'soll': ["2261"], 'haben': [liq_acc]}

    def rule_ag_allocate_profit():
        fall = "Der Jahresgewinn wird den freiwilligen Gewinnreserven zugewiesen."
        return {'fall': fall, 'soll': ["2979"], 'haben': ["2960"]}

    # --- 3. Regelfunktionen definieren (Pro Modus) ---

    def rule_buy_material_netto():
        mat_name, mat_acc = random.choice(list(material_expenses.items()))
        fall = f"{mat_name}-Einkauf auf Kredit (Netto). Buchen Sie Aufwand und Vorsteuer getrennt."
        return {'fall': fall, 'soll': [mat_acc, "1170"], 'haben': ["2000", "2000"]}

    def rule_pay_expense_netto():
        exp_name, exp_acc = random.choice(list(op_expenses.items()))
        liq_name, liq_acc = random.choice(list(liquid_assets.items()))
        fall = f"Bezahlung {exp_name} per {liq_name} (Netto). Buchen Sie Aufwand und Vorsteuer getrennt."
        return {'fall': fall, 'soll': [exp_acc, "1170"], 'haben': [liq_acc, liq_acc]}

    def rule_sell_revenue_netto():
        rev_name, rev_acc = random.choice(list(op_revenues.items()))
        fall = f"Verkauf von {rev_name} auf Kredit (Netto). Buchen Sie Ertrag und Umsatzsteuer getrennt."
        return {'fall': fall, 'soll': ["1100", "1100"], 'haben': [rev_acc, "2200"]}

    def rule_buy_investment_netto():
        inv_name, inv_acc = random.choice(list(investments.items()))
        fall = f"Kauf von {inv_name} auf Kredit (Netto). Buchen Sie Anlage und Vorsteuer Invest. getrennt."
        return {'fall': fall, 'soll': [inv_acc, "1171"], 'haben': ["2000", "2000"]}

    # --- 4. Regeln den Modi zuweisen ---

    classic_rules = [
        rule_pay_expense_simple, rule_customer_pays, rule_we_pay_supplier,
        rule_cash_transfer, rule_buy_material_brutto, rule_pay_expense_brutto,
        rule_sell_revenue_brutto, rule_sell_revenue_cash_brutto, rule_pay_mwst,
        rule_buy_investment_brutto, rule_pay_loan_combined,
        rule_provision_create, rule_provision_use, rule_provision_release,
        rule_eu_deposit, rule_eu_withdrawal, rule_ag_create_capital,
        rule_ag_decide_dividend, rule_ag_pay_dividend, rule_ag_allocate_profit
    ]

    pro_rules = [
        rule_buy_material_netto, rule_pay_expense_netto,
        rule_sell_revenue_netto, rule_buy_investment_netto
    ]
    # Füge einige einfache Regeln zum Pro-Modus hinzu, um die Variation zu erhöhen
    pro_rules.extend([
        rule_pay_loan_combined, rule_provision_create, rule_provision_use,
        rule_provision_release, rule_eu_deposit, rule_ag_decide_dividend,
        rule_ag_pay_dividend, rule_ag_allocate_profit
    ])

    # --- 5. Regel auswählen und ausführen ---
    if game_mode == "pro":
        chosen_rule = random.choice(pro_rules)
    else:
        chosen_rule = random.choice(classic_rules)

    return chosen_rule()


# --- ENDE DER NEUEN GENERIERUNGSFUNKTION ---


class AccountingGameApp:
    # --- UI-Konstanten (DARK MODE) ---
    BG_COLOR = "#2E2E2E"
    TEXT_COLOR = "#F5F5F5"
    PRIMARY_COLOR = "#007AFF"
    PRIMARY_LIGHT = "#409CFF"
    FIELD_BG_COLOR = "#3E3E3E"
    RED_COLOR = "#E57373"
    GREEN_COLOR = "#81C784"
    TIMER_TROUGH_COLOR = "#555555"

    # --- Spiel-Konstanten ---
    BASE_TIME_SECONDS = 25
    BONUS_TIME_SECONDS = 5
    START_LIVES = 3
    HIGHSCORE_FILE = "highscore.txt"

    # --- Timer-Konstanten ---
    TIMER_INTERVAL_MS = 50
    CIRCLE_TIMER_SIZE = 50
    CIRCLE_TIMER_WIDTH = 6
    UPSCALE_FACTOR = 4

    def __init__(self, root):
        self.root = root
        self.root.title("Buchhaltungs-Trainer Pro (Dark Mode)")
        self.root.geometry("600x580")  # Etwas höher für den neuen Knopf
        self.root.configure(bg=self.BG_COLOR)

        # --- Spiel-Variablen ---
        self.game_mode = "classic"  # NEU: Spielmodus
        self.kontenplan = get_kontenplan()
        self.highscore = self.load_highscore()
        self.score = 0
        self.streak = 0
        self.lives = self.START_LIVES
        self.current_question = {}

        self.auto_skip_timer = None
        self.question_timer = None
        self.current_time_limit = self.BASE_TIME_SECONDS

        self.timer_remaining_ms = 0
        self.last_displayed_seconds = -1

        self.soll_entries = []
        self.haben_entries = []
        self.MAX_ROWS = 3

        self.timer_photo_image = None
        self.kontenplan_window = None  # NEU: Referenz auf das Kontenplan-Fenster
        self.kontenplan_search_var = tk.StringVar()  # NEU: Suchvariable

        # --- Setup ausführen (AUFGERÄUMT) ---
        self._setup_styles()
        self._setup_kontenplan_lookup()
        self._create_widgets()

        # Spiel starten
        self.next_question()

    def _setup_styles(self):
        """Konfiguriert alle ttk-Styles."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Globale Styles
        self.style.configure('.', font=('Segoe UI', 11), background=self.BG_COLOR, foreground=self.TEXT_COLOR)
        self.style.configure('TFrame', background=self.BG_COLOR)
        self.style.configure('TLabel', background=self.BG_COLOR, foreground=self.TEXT_COLOR)

        # Spezifische Styles
        self.style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'))
        self.style.configure('Question.TLabel', font=('Segoe UI', 12, 'italic'))
        self.style.configure('Score.TLabel', font=('Segoe UI', 12))
        self.style.configure('TEntry', font=('Segoe UI', 12), fieldbackground=self.FIELD_BG_COLOR,
                             foreground=self.TEXT_COLOR)
        self.style.configure('InputHeader.TLabel', font=('Segoe UI', 12, 'bold'))

        # Button Style
        self.style.configure('TButton', font=('Segoe UI', 12, 'bold'), foreground=self.TEXT_COLOR,
                             background=self.PRIMARY_COLOR, relief='flat', padding=5)
        self.style.map('TButton', background=[('active', self.PRIMARY_LIGHT)])

        # Herzen-Styles
        self.style.configure('LiveHearts.TLabel', font=('Segoe UI', 14), background=self.BG_COLOR,
                             foreground=self.RED_COLOR)
        self.style.configure('DeadHearts.TLabel', font=('Segoe UI', 14), background=self.BG_COLOR,
                             foreground=self.TIMER_TROUGH_COLOR)

        # Style für Treeview (Kontenplan)
        self.style.configure("Treeview", rowheight=25, fieldbackground=self.FIELD_BG_COLOR,
                             background=self.FIELD_BG_COLOR, foreground=self.TEXT_COLOR)
        self.style.map("Treeview", background=[('selected', self.PRIMARY_COLOR)])
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), background=self.BG_COLOR,
                             foreground=self.TEXT_COLOR)

    def _setup_kontenplan_lookup(self):
        """Erstellt die Alias-Liste für Texteingaben."""
        self.kontenplan_lookup = {}
        for num, name in self.kontenplan.items():
            self.kontenplan_lookup[name.lower()] = num
            if "(" in name:
                try:
                    partial = name.split('(')[1].split(')')[0]
                    self.kontenplan_lookup[partial.lower()] = num
                except:
                    pass

        # Manuelle Aliase
        aliases = {
            "debitoren": "1100", "fll": "1100",
            "kreditoren": "2000", "vll": "2000",
            "bank": "1021", "bankguthaben": "1021",
            "post": "1020", "kasse": "1000",
            "miete": "6000", "raumaufwand": "6000",
            "warenaufwand": "4200", "wa": "4200",
            "warenerlös": "3200", "we": "3200",
            "löhne": "5000", "lohnaufwand": "5000",
            "vst": "1170", "vorsteuer": "1170",
            "vst invest": "1171", "vst inv": "1171", "vorsteuer investitionen": "1171",
            "ust": "2200", "umsatzsteuer": "2200",
            "mwst": "2200",
            "rückstellung": "2330", "rückstellungen": "2330",
            "privat": "2850",
            "eigenkapital": "2800.EU", "ek": "2800.EU",
            "aktienkapital": "2800", "ak": "2800",
            "dividende": "2261", "div": "2261",
            "gewinnreserve": "2960",
            "jahresgewinn": "2979", "jg": "2979",
            "jahresverlust": "2979", "jv": "2979",
            "jahresgewinn eu": "2891", "jg eu": "2891",
            "jahresverlust eu": "2891", "jv eu": "2891",
            "soba": "6700", "sonstiger betriebsaufwand": "6700",
            "mobiliar": "1510",
            "bankdarlehen": "2100", "bankschuld": "2100",
            "zinsaufwand": "6900", "finanzaufwand": "6900",
        }
        self.kontenplan_lookup.update(aliases)

    def _create_widgets(self):
        """Erstellt die Benutzeroberfläche."""

        # --- Header-Frame ---
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill='x')

        self.score_label = ttk.Label(header_frame, text="", style='Score.TLabel')
        self.score_label.pack(side='left', anchor='s')
        self.live_hearts_label = ttk.Label(header_frame, text="", style='LiveHearts.TLabel')
        self.live_hearts_label.pack(side='left', padx=(5, 0), anchor='s')
        self.dead_hearts_label = ttk.Label(header_frame, text="", style='DeadHearts.TLabel')
        self.dead_hearts_label.pack(side='left', anchor='s')
        self.highscore_label = ttk.Label(header_frame, text=f"Highscore: {self.highscore}", style='Score.TLabel')
        self.highscore_label.pack(side='right', anchor='s')

        # --- Frage-Frame ---
        question_frame = ttk.Frame(self.root, padding=10)
        question_frame.pack(fill='x')
        self.question_label = ttk.Label(question_frame, text="Geschäftsfall...", style='Question.TLabel',
                                        wraplength=550, anchor='center')
        self.question_label.pack(fill='x', pady=5)

        # --- Timer-Frame ---
        # Hält Timer-Text und Timer-Kreis
        self.timer_frame = ttk.Frame(self.root, padding="10 5")
        self.timer_frame.pack(fill='x')  # Wird in next_question() angezeigt/versteckt
        self.timer_label = ttk.Label(self.timer_frame, text=f"Zeit: {self.BASE_TIME_SECONDS}s", style='Score.TLabel')
        self.timer_label.pack(side='left', padx=5)
        self.timer_image_label = ttk.Label(self.timer_frame, background=self.BG_COLOR)
        self.timer_image_label.pack(side='right', padx=10)

        # --- Input-Frame ---
        self.input_frame = ttk.Frame(self.root, padding=10)  # Referenz speichern
        self.input_frame.pack(pady=5)
        ttk.Label(self.input_frame, text="Soll", style='InputHeader.TLabel').grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(self.input_frame, text="Haben", style='InputHeader.TLabel').grid(row=0, column=1, padx=10, pady=5)

        for i in range(self.MAX_ROWS):
            soll_entry = ttk.Entry(self.input_frame, font=('Segoe UI', 12), width=20)
            haben_entry = ttk.Entry(self.input_frame, font=('Segoe UI', 12), width=20)
            soll_entry.grid(row=i + 1, column=0, padx=5, pady=3)
            haben_entry.grid(row=i + 1, column=1, padx=5, pady=3)
            self.soll_entries.append(soll_entry)
            self.haben_entries.append(haben_entry)

        # --- Button-Frame ---
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(pady=10)
        self.check_button = ttk.Button(button_frame, text="Prüfen", command=self.check_answer)
        self.check_button.grid(row=0, column=0, padx=10)
        self.root.bind('<Return>', lambda event: self.check_answer())
        self.next_button = ttk.Button(button_frame, text="Nächste Frage", state="disabled")
        self.next_button.grid(row=0, column=1, padx=10)

        # Geänderter Button
        self.kontenplan_button = ttk.Button(self.root, text="Kontenplan anzeigen",
                                            command=self._toggle_kontenplan_window, style='TButton')
        self.kontenplan_button.pack(pady=5)

        # --- NEUER MODUS-KNOPF ---
        self.mode_toggle_button = ttk.Button(self.root, text="Modus: Klassisch (mit Zeitlimit)",
                                             command=self._toggle_game_mode, style='TButton')
        self.mode_toggle_button.pack(pady=5)
        # --- ENDE NEUER KNOPF ---

        self.feedback_label = ttk.Label(self.root, text="", font=('Segoe UI', 11, 'bold'), anchor='center')
        self.feedback_label.pack(pady=10, fill='x')

    # --- KONTENPLAN-FENSTER FUNKTIONEN ---

    def _toggle_kontenplan_window(self):
        """Öffnet oder schliesst das Kontenplan-Fenster."""
        if self.kontenplan_window and self.kontenplan_window.winfo_exists():
            self.kontenplan_window.destroy()
            self.kontenplan_window = None
        else:
            self._create_kontenplan_window()

    def _create_kontenplan_window(self):
        """Erstellt das Toplevel-Fenster für den Kontenplan."""
        self.kontenplan_window = tk.Toplevel(self.root)
        self.kontenplan_window.title("Kontenplan (KMU)")
        self.kontenplan_window.geometry("450x500")
        self.kontenplan_window.configure(bg=self.BG_COLOR)

        # Hält das Fenster im Vordergrund
        self.kontenplan_window.wm_attributes('-topmost', True)

        # Such-Frame
        search_frame = ttk.Frame(self.kontenplan_window, padding=5)
        search_frame.pack(fill='x')

        ttk.Label(search_frame, text="Suche:").pack(side='left', padx=5)
        search_entry = ttk.Entry(search_frame, textvariable=self.kontenplan_search_var)
        search_entry.pack(fill='x', expand=True)
        # Binde die Suchfunktion an jede Tastenänderung
        self.kontenplan_search_var.trace_add("write", self._filter_kontenplan)

        # Treeview-Frame (für Scrollbar)
        tree_frame = ttk.Frame(self.kontenplan_window)
        tree_frame.pack(fill='both', expand=True)

        # Treeview (Tabelle)
        self.kontenplan_tree = ttk.Treeview(tree_frame, columns=('Nummer', 'Name'), show='headings')
        self.kontenplan_tree.heading('Nummer', text='Nummer')
        self.kontenplan_tree.heading('Name', text='Kontenbezeichnung')
        self.kontenplan_tree.column('Nummer', width=80, anchor='w')
        self.kontenplan_tree.column('Name', width=350, anchor='w')

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.kontenplan_tree.yview)
        self.kontenplan_tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.kontenplan_tree.pack(side='left', fill='both', expand=True)

        # Fülle den Treeview
        self._filter_kontenplan()

        # Beim Schliessen des Fensters, setze nur die Referenz zurück
        self.kontenplan_window.protocol("WM_DELETE_WINDOW", self._on_kontenplan_close)

    def _on_kontenplan_close(self):
        """Wird aufgerufen, wenn das Kontenplan-Fenster geschlossen wird."""
        if self.kontenplan_window:
            self.kontenplan_window.destroy()
        self.kontenplan_window = None

    def _filter_kontenplan(self, *args):
        """Filtert den Treeview basierend auf der Sucheingabe."""
        if not self.kontenplan_window or not self.kontenplan_window.winfo_exists():
            return

        # Lösche alte Einträge
        for i in self.kontenplan_tree.get_children():
            self.kontenplan_tree.delete(i)

        # Hole Suchbegriff
        search_term = self.kontenplan_search_var.get().lower()

        # Füge passende Einträge hinzu
        for num, name in sorted(self.kontenplan.items()):
            if "EU" in num:  # Interne Konten überspringen
                continue

            if search_term in num.lower() or search_term in name.lower():
                self.kontenplan_tree.insert('', 'end', values=(num, name))

    # --- ENDE KONTENPLAN-FENSTER ---

    # --- NEUE FUNKTION ZUM MODUSWECHSEL ---
    def _toggle_game_mode(self):
        """Schaltet den Spielmodus um und startet das Spiel neu."""
        if self.game_mode == "classic":
            self.game_mode = "pro"
            self.mode_toggle_button.config(text="Modus: Pro (ohne Zeitlimit)")
        else:
            self.game_mode = "classic"
            self.mode_toggle_button.config(text="Modus: Klassisch (mit Zeitlimit)")
        self.restart_game()  # Startet das Spiel im neuen Modus

    def update_score_display(self):
        live_hearts_text = "❤️" * self.lives
        dead_hearts_text = "🖤" * (self.START_LIVES - self.lives)

        self.score_label.config(text=f"Score: {self.score} | Streak: {self.streak} 🔥 | Leben: ")
        self.live_hearts_label.config(text=live_hearts_text)
        self.dead_hearts_label.config(text=dead_hearts_text)
        self.highscore_label.config(text=f"Highscore: {self.highscore}")

    def load_highscore(self):
        try:
            with open(self.HIGHSCORE_FILE, 'r') as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0

    def save_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            try:
                with open(self.HIGHSCORE_FILE, 'w') as f:
                    f.write(str(self.highscore))
            except IOError:
                print("Fehler: Highscore konnte nicht gespeichert werden.")

    def _resolve_single_konto(self, input_str):
        """Wandelt Text (Name or Nummer) in die Kontonummer um. (Jetzt robuster)"""
        norm_input = input_str.strip().lower()
        if not norm_input: return None  # Leere Eingabe

        # 1. Ist es die Nummer? (Schnellster Check)
        if norm_input in self.kontenplan:
            return norm_input

        # 2. Ist es ein bekannter Name/Alias? (Zweitschnellster Check)
        if norm_input in self.kontenplan_lookup:
            return self.kontenplan_lookup[norm_input]

        # 3. Wort-basierter Match (Robuster als Substring)
        input_words = norm_input.split()
        if not input_words:
            return None

        for num, name in self.kontenplan.items():
            account_name_lower = name.lower()
            if all(word in account_name_lower for word in input_words):
                return num

        return None

    def stop_all_timers(self):
        """Stoppt sowohl den Auto-Skip als auch den Frage-Timer."""
        if self.auto_skip_timer:
            self.root.after_cancel(self.auto_skip_timer)
            self.auto_skip_timer = None
        if self.question_timer:
            self.root.after_cancel(self.question_timer)
            self.question_timer = None

    def update_timer_circle(self, progress_percent):
        """
        Zeichnet den Timer-Kreis mit Pillow (PIL) für Antialiasing.
        """
        size_up = self.CIRCLE_TIMER_SIZE * self.UPSCALE_FACTOR
        width_up = self.CIRCLE_TIMER_WIDTH * self.UPSCALE_FACTOR
        padding_up = width_up // 2

        img = Image.new('RGBA', (size_up, size_up), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        bbox = [padding_up, padding_up, size_up - padding_up, size_up - padding_up]

        # 1. Hintergrund-Kreis (Spur)
        draw.arc(bbox, start=-90, end=270, fill=self.TIMER_TROUGH_COLOR, width=width_up)

        # 2. Vordergrund-Kreis (Fortschritt)
        if progress_percent > 0:
            end_angle = (360 * progress_percent) - 90
            draw.arc(bbox, start=-90, end=end_angle, fill=self.PRIMARY_COLOR, width=width_up)

        # 3. Skaliere das Bild mit Antialiasing (LANCZOS) herunter
        img_down = img.resize((self.CIRCLE_TIMER_SIZE, self.CIRCLE_TIMER_SIZE), Image.Resampling.LANCZOS)

        # 4. In ein Tkinter-Foto-Image umwandeln
        self.timer_photo_image = ImageTk.PhotoImage(img_down)

        # 5. Im Label anzeigen
        self.timer_image_label.config(image=self.timer_photo_image)

    def start_question_timer(self):
        """Startet den Countdown für die Frage."""
        self.stop_all_timers()
        self.timer_remaining_ms = self.current_time_limit * 1000
        self.last_displayed_seconds = self.current_time_limit
        self.timer_label.config(text=f"Zeit: {self.current_time_limit}s")

        self.update_timer_circle(1.0)

        self.tick()

    def tick(self):
        """Führt einen Timer-Tick alle TIMER_INTERVAL_MS Millisekunden aus."""
        if self.timer_remaining_ms > 0:
            self.timer_remaining_ms -= self.TIMER_INTERVAL_MS

            current_display_seconds = (self.timer_remaining_ms + 999) // 1000
            if current_display_seconds != self.last_displayed_seconds:
                self.timer_label.config(text=f"Zeit: {current_display_seconds}s")
                self.last_displayed_seconds = current_display_seconds

            progress_percent = max(0, self.timer_remaining_ms / (self.current_time_limit * 1000))

            self.update_timer_circle(progress_percent)

            self.question_timer = self.root.after(self.TIMER_INTERVAL_MS, self.tick)
        else:
            self.update_timer_circle(0)
            self.check_answer(timed_out=True)

    def next_question(self):
        self.stop_all_timers()

        self.current_question = generate_question(self.kontenplan, self.game_mode)  # Modus übergeben
        self.question_label.config(text=self.current_question['fall'])

        correct_soll_list = self.current_question['soll']
        correct_haben_list = self.current_question['haben']

        # --- MODUS-LOGIK (ANZEIGE) ---
        if self.game_mode == "classic":
            # Timer anzeigen und Zeit berechnen
            self.timer_frame.pack(fill='x', before=self.input_frame)
            self.timer_image_label.pack(side='right', padx=10)  # Kreis anzeigen
            total_entries = len(correct_soll_list) + len(correct_haben_list)
            if total_entries > 2:
                self.current_time_limit = self.BASE_TIME_SECONDS + self.BONUS_TIME_SECONDS
            else:
                self.current_time_limit = self.BASE_TIME_SECONDS
            self.start_question_timer()
        else:  # Pro Modus
            # Timer-Kreis verstecken, Text auf "unendlich"
            self.timer_frame.pack(fill='x', before=self.input_frame)
            self.timer_image_label.pack_forget()
            self.timer_label.config(text="Zeit: ∞")
            self.stop_all_timers()
        # --- ENDE MODUS-LOGIK ---

        for i in range(self.MAX_ROWS):
            self.soll_entries[i].delete(0, 'end')
            self.haben_entries[i].delete(0, 'end')

            self.soll_entries[i].grid_remove() if i >= len(correct_soll_list) else self.soll_entries[i].grid()
            self.haben_entries[i].grid_remove() if i >= len(correct_haben_list) else self.haben_entries[i].grid()

        self.feedback_label.config(text="")
        self.check_button.config(state="normal")
        self.next_button.config(text="Nächste Frage", state="disabled")  # Deaktiviert für beide Modi

        self.soll_entries[0].focus()
        self.root.bind('<Return>', lambda event: self.check_answer())

        self.update_score_display()

    def check_answer(self, timed_out=False):
        if self.check_button['state'] == 'disabled' and not timed_out:
            return

        self.stop_all_timers()
        self.check_button.config(state="disabled")

        resolved_soll_list = [self._resolve_single_konto(self.soll_entries[i].get()) for i in
                              range(len(self.current_question['soll']))]
        resolved_haben_list = [self._resolve_single_konto(self.haben_entries[i].get()) for i in
                               range(len(self.current_question['haben']))]

        correct_soll_list = self.current_question['soll']
        correct_haben_list = self.current_question['haben']

        resolved_soll_list = ["2800" if x == "2800.EU" and "2800" in correct_soll_list else x for x in
                              resolved_soll_list]
        resolved_haben_list = ["2800" if x == "2800.EU" and "2800" in correct_haben_list else x for x in
                               resolved_haben_list]

        is_correct = set(resolved_soll_list) == set(correct_soll_list) and set(resolved_haben_list) == set(
            correct_haben_list)

        if is_correct:
            points = 10 + (self.streak * 5)
            self.score += points
            self.streak += 1
            self.feedback_label.config(text=f"✅ Richtig! +{points} Punkte!", foreground=self.GREEN_COLOR)
            self.auto_skip_timer = self.root.after(2000, self.next_question)
        else:
            self.streak = 0

            # Im Pro-Modus verliert man keine Leben (nur im Classic-Modus)
            if self.game_mode == "classic":
                self.lives -= 1

            correct_soll_names = [self.kontenplan.get(k, k) for k in correct_soll_list]
            correct_haben_names = [self.kontenplan.get(k, k) for k in correct_haben_list]

            correct_soll_str = ", ".join(correct_soll_list)
            correct_haben_str = ", ".join(correct_haben_list)

            correct_soll_names_str = ", ".join(correct_soll_names)
            correct_haben_names_str = ", ".join(correct_haben_names)

            if timed_out:
                feedback_text = f"⏰ Zeit abgelaufen! -1 Leben."
            else:
                feedback_text = f"❌ Falsch."
                if self.game_mode == "classic":
                    feedback_text += " -1 Leben."

            self.feedback_label.config(
                text=f"{feedback_text}\nKorrekt: {correct_soll_str} / {correct_haben_str}\n({correct_soll_names_str} / {correct_haben_names_str})",
                foreground=self.RED_COLOR
            )

            # --- MODUS-LOGIK (SKIP / NEXT BUTTON) ---
            if self.lives <= 0 and self.game_mode == "classic":
                self.game_over()
            else:
                if self.game_mode == "classic":
                    # Auto-Skip im Classic-Modus
                    self.auto_skip_timer = self.root.after(10000, self.next_question)
                else:
                    # Manueller "Next" Button im Pro-Modus
                    self.next_button.config(state="normal")
                    self.root.bind('<Return>', lambda event: self.next_question())
            # --- ENDE MODUS-LOGIK ---

        self.update_score_display()

    def game_over(self):
        """Behandelt das Spielende."""
        self.save_highscore()
        self.update_score_display()

        messagebox.showinfo("Game Over",
                            f"Keine Leben mehr!\n\nDein finaler Score: {self.score}\nHighscore: {self.highscore}")

        self.check_button.config(state="disabled")
        self.next_button.config(text="Neues Spiel", state="normal", command=self.restart_game)
        self.root.bind('<Return>', lambda event: self.restart_game())

    def restart_game(self):
        """Setzt das Spiel zurück."""
        self.score = 0
        self.streak = 0
        self.lives = self.START_LIVES
        self.highscore = self.load_highscore()  # Highscore neu laden

        # Update den Modus-Knopf-Text, falls er nicht schon korrekt ist
        if self.game_mode == "classic":
            self.mode_toggle_button.config(text="Modus: Klassisch (mit Zeitlimit)")
        else:
            self.mode_toggle_button.config(text="Modus: Pro (ohne Zeitlimit)")

        self.next_question()


if __name__ == "__main__":
    root = tk.Tk()
    app = AccountingGameApp(root)
    root.mainloop()