import tkinter as tk
from tkinter import ttk, messagebox
import json
import re
from pathlib import Path
from datetime import datetime

# ============================================================
# STADIUM PRO — Modern Stadium Ticket Manager
# Python 3.10+ | Tkinter only | No MySQL required
# Saves bookings to tickets.txt beside this script.
# ============================================================

DATA_FILE = Path(__file__).with_name("tickets.txt")
TICKET_TYPES = {"VIP": 150.00, "Premium": 90.00, "Standard": 40.00}
VALID_SEAT_PATTERN = re.compile(r"^[ABCDF](?:[1-9]|10)$")
SEATS = [f"{row}{number}" for row in "ABCDF" for number in range(1, 11)]


def load_tickets():
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        raise ValueError("The file must contain a list of tickets.")
    except (json.JSONDecodeError, OSError, ValueError) as error:
        messagebox.showerror(
            "Storage Error",
            f"Could not read {DATA_FILE.name}.\n\n{error}\n\n"
            "Back up the file before attempting to repair it."
        )
        return []


def save_tickets(tickets):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(tickets, file, indent=4, ensure_ascii=False)
        return True
    except OSError as error:
        messagebox.showerror("Save Error", f"Could not save your bookings.\n\n{error}")
        return False


class StadiumProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STADIUM PRO  |  Ticket Management")
        self.root.geometry("1240x800")
        self.root.minsize(900, 650)
        self.root.configure(bg="#F3F6FC")

        self.colors = {
            "navy": "#101A35",
            "navy2": "#17264A",
            "blue": "#4F6BFF",
            "blue_hover": "#3C55E6",
            "purple": "#855CF8",
            "green": "#10A878",
            "orange": "#F59E0B",
            "red": "#E34D68",
            "bg": "#F3F6FC",
            "card": "#FFFFFF",
            "text": "#17213A",
            "muted": "#7D879E",
            "line": "#E5EAF4",
            "softblue": "#EDF1FF",
            "softgreen": "#E6F8F1",
            "softorange": "#FFF4DF",
            "softred": "#FFF0F2",
        }

        self.tickets = load_tickets()
        self.next_id = max(
            (int(t.get("ticket_id", 0)) for t in self.tickets), default=0
        ) + 1

        self.customer_var = tk.StringVar()
        self.match_var = tk.StringVar()
        self.seat_var = tk.StringVar()
        self.type_var = tk.StringVar(value="VIP")
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready • Changes save automatically")

        self._setup_styles()
        self._build_ui()
        self.refresh_all()

    # ---------- General UI helpers ----------
    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Pro.Treeview",
            background=self.colors["card"],
            foreground=self.colors["text"],
            fieldbackground=self.colors["card"],
            rowheight=38,
            borderwidth=0,
            font=("Segoe UI", 10),
        )
        style.configure(
            "Pro.Treeview.Heading",
            background="#F0F3FA",
            foreground="#59647B",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(9, 12),
        )
        style.map(
            "Pro.Treeview",
            background=[("selected", "#E2E8FF")],
            foreground=[("selected", self.colors["text"])],
        )
        style.configure(
            "Pro.Vertical.TScrollbar",
            background="#DCE3F0",
            troughcolor="#F5F7FB",
            bordercolor="#F5F7FB",
            arrowsize=13,
        )
        style.configure(
            "Pro.TCombobox",
            padding=9,
            font=("Segoe UI", 10),
            fieldbackground="#F8FAFE",
            background="#F8FAFE",
        )

    def _button(self, parent, text, command, bg, fg="#FFFFFF", compact=False):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=self.colors["blue_hover"] if bg == self.colors["blue"] else bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=12 if compact else 16,
            pady=8 if compact else 11,
        )
        if bg in (self.colors["blue"], self.colors["purple"], self.colors["green"], self.colors["red"]):
            btn.bind("<Enter>", lambda _e: btn.configure(bg=self.colors["blue_hover"] if bg == self.colors["blue"] else bg))
            btn.bind("<Leave>", lambda _e: btn.configure(bg=bg))
        return btn

    def _card(self, parent, **kwargs):
        return tk.Frame(
            parent,
            bg=kwargs.get("bg", self.colors["card"]),
            highlightbackground=self.colors["line"],
            highlightthickness=1,
            bd=0,
        )

    def _label(self, parent, text, size=10, color=None, bold=False, bg=None):
        return tk.Label(
            parent,
            text=text,
            bg=bg or self.colors["card"],
            fg=color or self.colors["text"],
            font=("Segoe UI", size, "bold" if bold else "normal"),
        )

    def _field(self, parent, label, variable):
        self._label(parent, label.upper(), 8, "#69758D", True).pack(
            anchor="w", padx=18, pady=(10, 5)
        )
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=("Segoe UI", 10),
            bg="#F8FAFE",
            fg=self.colors["text"],
            insertbackground=self.colors["blue"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors["line"],
            highlightcolor=self.colors["blue"],
        )
        entry.pack(fill="x", padx=18, ipady=9)
        return entry

    # ---------- Main layout ----------
    def _build_ui(self):
        # Sidebar stays visible; main area resizes with the window.
        self.sidebar = tk.Frame(self.root, bg=self.colors["navy"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo = tk.Frame(self.sidebar, bg=self.colors["navy"])
        logo.pack(fill="x", padx=20, pady=(25, 32))
        logo_icon = tk.Label(
            logo, text="S", bg=self.colors["blue"], fg="#FFFFFF",
            font=("Segoe UI", 19, "bold"), width=2, height=1
        )
        logo_icon.pack(side="left", padx=(0, 10))
        logo_text = tk.Frame(logo, bg=self.colors["navy"])
        logo_text.pack(side="left")
        self._label(logo_text, "STADIUM", 15, "#FFFFFF", True, self.colors["navy"]).pack(anchor="w")
        self._label(logo_text, "PRO MANAGEMENT", 7, "#9CAAD0", True, self.colors["navy"]).pack(anchor="w", pady=(2, 0))

        self._label(self.sidebar, "WORKSPACE", 8, "#7786B2", True, self.colors["navy"]).pack(anchor="w", padx=22, pady=(0, 10))
        self._nav_item("▦", "Dashboard", active=True)
        self._nav_item("＋", "Book a ticket")
        self._nav_item("▤", "All bookings")

        # Sidebar bottom storage badge
        bottom = tk.Frame(self.sidebar, bg=self.colors["navy"])
        bottom.pack(side="bottom", fill="x", padx=15, pady=20)
        badge = tk.Frame(bottom, bg="#1D3157", padx=12, pady=12)
        badge.pack(fill="x")
        self._label(badge, "●  LOCAL STORAGE", 8, "#71E0B4", True, "#1D3157").pack(anchor="w")
        self._label(badge, "Your bookings stay on this PC.", 8, "#B8C4E1", False, "#1D3157").pack(anchor="w", pady=(7, 0))
        self._label(bottom, "STADIUM PRO  •  v2.0", 8, "#7180A8", True, self.colors["navy"]).pack(anchor="center", pady=(15, 0))

        # Right content shell
        self.main = tk.Frame(self.root, bg=self.colors["bg"])
        self.main.pack(side="left", fill="both", expand=True)

        # Top bar
        topbar = tk.Frame(self.main, bg="#FFFFFF", height=66, highlightbackground=self.colors["line"], highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        self._label(topbar, "Ticket operations", 11, "#46516A", True, "#FFFFFF").pack(side="left", padx=25)
        tk.Label(
            topbar, text="●  SYSTEM ONLINE", bg="#FFFFFF", fg=self.colors["green"],
            font=("Segoe UI", 9, "bold")
        ).pack(side="right", padx=25)

        # Scrollable main content: on short screens the user can scroll to all buttons.
        self.canvas = tk.Canvas(self.main, bg=self.colors["bg"], highlightthickness=0, bd=0)
        self.v_scroll = ttk.Scrollbar(self.main, orient="vertical", command=self.canvas.yview, style="Pro.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=self.v_scroll.set)
        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(self.canvas, bg=self.colors["bg"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_linux_scroll_up)
        self.canvas.bind_all("<Button-5>", self._on_linux_scroll_down)

        self._build_content()

    def _nav_item(self, icon, text, active=False):
        bg = "#263B70" if active else self.colors["navy"]
        fg = "#FFFFFF" if active else "#B5C1E0"
        row = tk.Frame(self.sidebar, bg=bg, cursor="hand2")
        row.pack(fill="x", padx=12, pady=3)
        tk.Label(row, text=icon, bg=bg, fg="#AFC0FF" if active else "#8999C3", width=3,
                 font=("Segoe UI Symbol", 12, "bold")).pack(side="left", padx=(7, 2), pady=11)
        tk.Label(row, text=text, bg=bg, fg=fg, font=("Segoe UI", 10, "bold" if active else "normal")).pack(side="left", pady=11)
        for widget in (row, *row.winfo_children()):
            widget.bind("<Button-1>", lambda _e, name=text: self._nav_action(name))
            widget.bind("<Enter>", lambda _e, r=row, a=active: r.configure(bg="#1A2B50" if not a else "#263B70"))
            widget.bind("<Leave>", lambda _e, r=row, b=bg: r.configure(bg=b))

    def _nav_action(self, name):
        if name == "Book a ticket":
            self.customer_entry.focus_set()
            self.canvas.yview_moveto(0)
        elif name == "All bookings":
            self.search_entry.focus_set()
            self.canvas.yview_moveto(1)
        else:
            self.canvas.yview_moveto(0)

    def _on_content_configure(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        # Scroll only when the pointer is over the main content area.
        x_root, y_root = self.root.winfo_pointerxy()
        widget = self.root.winfo_containing(x_root, y_root)
        if widget and self._is_descendant(widget, self.canvas):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_linux_scroll_up(self, event):
        self.canvas.yview_scroll(-1, "units")

    def _on_linux_scroll_down(self, event):
        self.canvas.yview_scroll(1, "units")

    def _is_descendant(self, widget, parent):
        while widget is not None:
            if widget == parent:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _build_content(self):
        pad = tk.Frame(self.content, bg=self.colors["bg"])
        pad.pack(fill="both", expand=True, padx=24, pady=22)

        title_row = tk.Frame(pad, bg=self.colors["bg"])
        title_row.pack(fill="x", pady=(0, 18))
        title_text = tk.Frame(title_row, bg=self.colors["bg"])
        title_text.pack(side="left")
        self._label(title_text, "Good day 👋", 10, self.colors["muted"], False, self.colors["bg"]).pack(anchor="w")
        self._label(title_text, "Stadium dashboard", 22, self.colors["text"], True, self.colors["bg"]).pack(anchor="w", pady=(2, 0))
        self._label(title_row, datetime.now().strftime("%A, %d %B %Y"), 9, self.colors["muted"], False, self.colors["bg"]).pack(side="right", anchor="s", pady=5)

        # Four colourful stat cards
        stat_row = tk.Frame(pad, bg=self.colors["bg"])
        stat_row.pack(fill="x", pady=(0, 18))
        for col in range(4):
            stat_row.grid_columnconfigure(col, weight=1, uniform="stat")
        self.stat_total = self._stat_card(stat_row, 0, "TOTAL BOOKINGS", "0", "▤", self.colors["blue"], self.colors["softblue"])
        self.stat_revenue = self._stat_card(stat_row, 1, "TOTAL REVENUE", "₹0.00", "₹", self.colors["green"], self.colors["softgreen"])
        self.stat_seats = self._stat_card(stat_row, 2, "SEATS OCCUPIED", "0 / 50", "▦", self.colors["purple"], "#F1EBFF")
        self.stat_matches = self._stat_card(stat_row, 3, "MATCHES", "0", "⚑", self.colors["orange"], self.colors["softorange"])

        # Main two-column section
        grid = tk.Frame(pad, bg=self.colors["bg"])
        grid.pack(fill="x", expand=False)
        grid.grid_columnconfigure(0, weight=0, minsize=300)
        grid.grid_columnconfigure(1, weight=1)

        # Booking form
        form = self._card(grid)
        form.grid(row=0, column=0, sticky="new", padx=(0, 16))
        form_head = tk.Frame(form, bg=self.colors["card"])
        form_head.pack(fill="x", padx=18, pady=(18, 3))
        tk.Label(form_head, text="✦", bg=self.colors["softblue"], fg=self.colors["blue"],
                 font=("Segoe UI", 13, "bold"), width=2, pady=3).pack(side="left", padx=(0, 9))
        self._label(form_head, "Create booking", 13, self.colors["text"], True).pack(side="left", pady=3)
        self._label(form, "Fill in the details to reserve a seat.", 9, self.colors["muted"]).pack(anchor="w", padx=18, pady=(3, 7))

        self.customer_entry = self._field(form, "Customer name", self.customer_var)
        self._field(form, "Match name", self.match_var)

        self._label(form, "SEAT NUMBER", 8, "#69758D", True).pack(anchor="w", padx=18, pady=(12, 5))
        self.seat_combo = ttk.Combobox(form, textvariable=self.seat_var, values=SEATS, state="normal", style="Pro.TCombobox")
        self.seat_combo.pack(fill="x", padx=18, ipady=3)
        self.seat_combo.bind("<KeyRelease>", lambda _e: self.seat_var.set(self.seat_var.get().upper()))

        self._label(form, "TICKET CATEGORY", 8, "#69758D", True).pack(anchor="w", padx=18, pady=(12, 5))
        self.type_combo = ttk.Combobox(form, textvariable=self.type_var, values=list(TICKET_TYPES), state="readonly", style="Pro.TCombobox")
        self.type_combo.pack(fill="x", padx=18, ipady=3)
        self.type_combo.bind("<<ComboboxSelected>>", self._update_price)

        self.price_banner = tk.Frame(form, bg=self.colors["softblue"])
        self.price_banner.pack(fill="x", padx=18, pady=14)
        tk.Label(self.price_banner, text="TICKET PRICE", bg=self.colors["softblue"], fg="#6875B7",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=12, pady=11)
        self.price_value = tk.Label(self.price_banner, text="₹150.00", bg=self.colors["softblue"],
                                    fg=self.colors["blue"], font=("Segoe UI", 14, "bold"))
        self.price_value.pack(side="right", padx=12, pady=7)

        self._button(form, "＋   CONFIRM BOOKING", self.book_ticket, self.colors["blue"]).pack(fill="x", padx=18, pady=(0, 9))
        self._button(form, "Clear form", self.clear_form, "#EEF1F7", self.colors["text"]).pack(fill="x", padx=18, pady=(0, 18))

        # Bookings table
        table = self._card(grid)
        table.grid(row=0, column=1, sticky="new")
        table_head = tk.Frame(table, bg=self.colors["card"])
        table_head.pack(fill="x", padx=18, pady=(18, 10))
        head_left = tk.Frame(table_head, bg=self.colors["card"])
        head_left.pack(side="left")
        self._label(head_left, "Booking records", 14, self.colors["text"], True).pack(anchor="w")
        self._label(head_left, "Review and manage all tickets", 9, self.colors["muted"]).pack(anchor="w", pady=(3, 0))

        search_row = tk.Frame(table, bg=self.colors["card"])
        search_row.pack(fill="x", padx=18, pady=(0, 12))
        tk.Label(search_row, text="⌕", bg="#F7F9FD", fg=self.colors["muted"],
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=(9, 0), ipady=1)
        self.search_entry = tk.Entry(
            search_row, textvariable=self.search_var, font=("Segoe UI", 10),
            bg="#F7F9FD", fg=self.colors["text"], insertbackground=self.colors["blue"],
            relief="flat", bd=0
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(6, 8))
        self.search_entry.bind("<KeyRelease>", lambda _e: self.populate_table())
        self._button(search_row, "Refresh", self.refresh_all, "#EDF1F8", self.colors["text"], compact=True).pack(side="right")

        table_frame = tk.Frame(table, bg=self.colors["card"])
        table_frame.pack(fill="both", expand=True, padx=14, pady=(0, 10))
        columns = ("id", "customer", "match", "seat", "type", "price")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", style="Pro.Treeview", height=10)
        column_info = {
            "id": ("ID", 42),
            "customer": ("CUSTOMER", 120),
            "match": ("MATCH", 120),
            "seat": ("SEAT", 54),
            "type": ("TYPE", 75),
            "price": ("PRICE", 76),
        }
        for col, (heading, width) in column_info.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=40, anchor="w" if col in ("customer", "match") else "center", stretch=True)
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview, style="Pro.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        self.tree.tag_configure("odd", background="#FFFFFF")
        self.tree.tag_configure("even", background="#F6F8FD")

        actions = tk.Frame(table, bg=self.colors["card"])
        actions.pack(fill="x", padx=18, pady=(0, 18))
        self._button(actions, "✕  Cancel selected ticket", self.cancel_ticket, self.colors["red"], compact=True).pack(side="left")
        self._label(actions, "Select a row first", 8, self.colors["muted"]).pack(side="right", pady=9)

        # Recent activity / guidance strip below the table. It is reachable by scrolling.
        info = self._card(pad)
        info.pack(fill="x", pady=(18, 0))
        info_inner = tk.Frame(info, bg=self.colors["card"])
        info_inner.pack(fill="x", padx=18, pady=14)
        tk.Label(info_inner, text="ℹ", bg=self.colors["softgreen"], fg=self.colors["green"],
                 font=("Segoe UI", 12, "bold"), width=3, pady=4).pack(side="left", padx=(0, 12))
        note = tk.Frame(info_inner, bg=self.colors["card"])
        note.pack(side="left", fill="x", expand=True)
        self._label(note, "Your data is saved locally", 10, self.colors["text"], True).pack(anchor="w")
        self._label(note, f"Bookings are stored in {DATA_FILE.name}. Keep that file with this application to preserve records.", 9, self.colors["muted"]).pack(anchor="w", pady=(3, 0))

        # Footer inside scrollable content
        self._label(pad, "STADIUM PRO  •  A simple, local ticket management solution", 8, "#9AA4B8", False, self.colors["bg"]).pack(anchor="center", pady=(18, 0))

    def _stat_card(self, parent, column, title, value, icon, accent, soft):
        card = self._card(parent)
        card.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 7, 7 if column < 3 else 0))
        top = tk.Frame(card, bg=self.colors["card"])
        top.pack(fill="x", padx=14, pady=(14, 4))
        tk.Label(top, text=icon, bg=soft, fg=accent, font=("Segoe UI", 12, "bold"), width=3, pady=5).pack(side="left")
        tk.Label(top, text=title, bg=self.colors["card"], fg=self.colors["muted"],
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(9, 0))
        value_label = tk.Label(card, text=value, bg=self.colors["card"], fg=self.colors["text"],
                               font=("Segoe UI", 19, "bold"))
        value_label.pack(anchor="w", padx=15, pady=(3, 15))
        return value_label

    # ---------- Booking logic ----------
    def _update_price(self, _event=None):
        price = TICKET_TYPES.get(self.type_var.get(), 0)
        self.price_value.config(text=f"₹{price:.2f}")

    def clear_form(self):
        self.customer_var.set("")
        self.match_var.set("")
        self.seat_var.set("")
        self.type_var.set("VIP")
        self._update_price()
        self.customer_entry.focus_set()
        self.status_var.set("Form cleared")

    def book_ticket(self):
        customer = self.customer_var.get().strip()
        match = self.match_var.get().strip()
        seat = self.seat_var.get().strip().upper()
        ticket_type = self.type_var.get()

        if not customer or not match or not seat:
            messagebox.showwarning("Missing details", "Please enter customer name, match name, and seat number.")
            return
        if len(customer) > 100 or len(match) > 100:
            messagebox.showwarning("Input too long", "Customer and match names must be 100 characters or fewer.")
            return
        if not VALID_SEAT_PATTERN.fullmatch(seat):
            messagebox.showwarning("Invalid seat", "Use A1–A10, B1–B10, C1–C10, D1–D10, or F1–F10.")
            return
        if ticket_type not in TICKET_TYPES:
            messagebox.showwarning("Invalid category", "Please choose a valid ticket category.")
            return

        for old in self.tickets:
            if (
                old.get("match_name", "").casefold() == match.casefold()
                and old.get("seat_number", "").upper() == seat
            ):
                messagebox.showerror("Seat unavailable", f"Seat {seat} is already booked for {old.get('match_name')}.")
                return

        ticket = {
            "ticket_id": self.next_id,
            "customer_name": customer,
            "match_name": match,
            "seat_number": seat,
            "ticket_type": ticket_type,
            "price": TICKET_TYPES[ticket_type],
            "booked_at": datetime.now().isoformat(timespec="seconds"),
        }
        self.tickets.append(ticket)
        if not save_tickets(self.tickets):
            self.tickets.pop()
            return

        self.next_id += 1
        self.refresh_all()
        self.clear_form()
        self.status_var.set(f"Booking #{ticket['ticket_id']} saved successfully")
        messagebox.showinfo(
            "Booking confirmed",
            f"Booking confirmed successfully!\n\n"
            f"Ticket ID: {ticket['ticket_id']}\nCustomer: {customer}\n"
            f"Match: {match}\nSeat: {seat}\nCategory: {ticket_type}\n"
            f"Total: ₹{ticket['price']:.2f}",
        )

    def cancel_ticket(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a ticket", "Select a booking row from the table before cancelling.")
            return
        values = self.tree.item(selected[0], "values")
        ticket_id = int(values[0])
        ticket = next((t for t in self.tickets if int(t.get("ticket_id", -1)) == ticket_id), None)
        if ticket is None:
            messagebox.showerror("Ticket not found", "That booking could not be found. Refresh and try again.")
            return

        if not messagebox.askyesno(
            "Confirm cancellation",
            f"Cancel booking #{ticket_id}?\n\n{ticket['customer_name']} • {ticket['match_name']} • Seat {ticket['seat_number']}"
        ):
            return

        old_tickets = self.tickets[:]
        self.tickets = [t for t in self.tickets if int(t.get("ticket_id", -1)) != ticket_id]
        if save_tickets(self.tickets):
            self.refresh_all()
            self.status_var.set(f"Booking #{ticket_id} cancelled")
            messagebox.showinfo("Cancelled", f"Booking #{ticket_id} has been cancelled.")
        else:
            self.tickets = old_tickets

    # ---------- Dashboard refresh ----------
    def populate_table(self):
        if not hasattr(self, "tree"):
            return
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().strip().casefold()
        records = sorted(self.tickets, key=lambda t: int(t.get("ticket_id", 0)), reverse=True)
        visible = []
        for ticket in records:
            text = " ".join(
                str(ticket.get(key, ""))
                for key in ("ticket_id", "customer_name", "match_name", "seat_number", "ticket_type")
            ).casefold()
            if not query or query in text:
                visible.append(ticket)

        for index, ticket in enumerate(visible):
            self.tree.insert(
                "", "end",
                values=(
                    ticket.get("ticket_id", ""),
                    ticket.get("customer_name", ""),
                    ticket.get("match_name", ""),
                    ticket.get("seat_number", ""),
                    ticket.get("ticket_type", ""),
                    f"₹{float(ticket.get('price', 0)):.2f}",
                ),
                tags=("even" if index % 2 == 0 else "odd",),
            )

    def refresh_all(self):
        self.stat_total.config(text=str(len(self.tickets)))
        revenue = sum(float(t.get("price", 0)) for t in self.tickets)
        self.stat_revenue.config(text=f"₹{revenue:,.2f}")
        occupied = len({
            (t.get("match_name", "").casefold(), t.get("seat_number", "").upper())
            for t in self.tickets
        })
        self.stat_seats.config(text=f"{occupied} / 50")
        matches = len({t.get("match_name", "").casefold() for t in self.tickets if t.get("match_name")})
        self.stat_matches.config(text=str(matches))
        self.populate_table()


def main():
    root = tk.Tk()
    app = StadiumProApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
