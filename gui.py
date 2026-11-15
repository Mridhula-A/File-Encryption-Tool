import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path
import hashlib
import hmac


# ==============================
# COLORS
# ==============================

BG = "#F5F7FB"
CARD = "#FFFFFF"

PRIMARY = "#2563EB"
PURPLE = "#7C3AED"

TEXT = "#172033"
MUTED = "#64748B"

SUCCESS = "#16A34A"
BORDER = "#DCE3EE"

# Encrypted files created by this version begin with this marker
# inside the authenticated Fernet-encrypted payload.
PAYLOAD_MARKER = b"FET1"
HASH_LENGTH = 32  # SHA-256 produces 32 bytes


class FileEncryptionApp:

    # ==============================
    # APPLICATION SETUP
    # ==============================

    def __init__(self, root):
        self.root = root
        self.root.title("File Encryption & Decryption Tool")
        self.root.geometry("900x780")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.file_path = tk.StringVar()
        self.key_value = tk.StringVar()

        self.status = tk.StringVar(
            value="Ready — Select a file to begin"
        )

        self.file_name = tk.StringVar(value="No file selected")
        self.file_type = tk.StringVar(value="-")
        self.file_size = tk.StringVar(value="-")

        self.key_visible = False

        self.create_widgets()

    # ==============================
    # UI DESIGN
    # ==============================

    def create_widgets(self):

        # Header
        header = tk.Frame(self.root, bg=PRIMARY, height=110)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="🔐  FILE ENCRYPTION & DECRYPTION TOOL",
            font=("Arial", 22, "bold"),
            bg=PRIMARY,
            fg="white"
        ).pack(pady=(22, 5))

        tk.Label(
            header,
            text="Secure your files with authenticated encryption",
            font=("Arial", 11),
            bg=PRIMARY,
            fg="#DBEAFE"
        ).pack()

        # Main container
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=55, pady=20)

        # File selection card
        file_card = tk.Frame(
            main,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        file_card.pack(fill="x", pady=(0, 12))

        tk.Label(
            file_card,
            text="📁  Select File",
            font=("Arial", 13, "bold"),
            bg=CARD,
            fg=TEXT
        ).pack(anchor="w", padx=20, pady=(15, 8))

        file_row = tk.Frame(file_card, bg=CARD)
        file_row.pack(fill="x", padx=20, pady=(0, 12))

        tk.Entry(
            file_row,
            textvariable=self.file_path,
            font=("Arial", 10),
            relief="solid",
            bd=1
        ).pack(side="left", fill="x", expand=True, ipady=7)

        tk.Button(
            file_row,
            text="Browse 📁",
            command=self.browse_file,
            bg="#E8EEFF",
            fg=PRIMARY,
            activebackground="#DDE7FF",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=18,
            pady=7,
            cursor="hand2"
        ).pack(side="right", padx=(12, 0))

        # File information
        info_frame = tk.Frame(file_card, bg="#F8FAFC")
        info_frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            info_frame,
            text="📄 File Information",
            font=("Arial", 10, "bold"),
            bg="#F8FAFC",
            fg=TEXT
        ).pack(anchor="w", padx=12, pady=(8, 5))

        details = tk.Frame(info_frame, bg="#F8FAFC")
        details.pack(fill="x", padx=12, pady=(0, 8))

        tk.Label(
            details, text="Name:", font=("Arial", 9, "bold"),
            bg="#F8FAFC", fg=MUTED
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))

        tk.Label(
            details, textvariable=self.file_name,
            font=("Arial", 9), bg="#F8FAFC", fg=TEXT
        ).grid(row=0, column=1, sticky="w")

        tk.Label(
            details, text="Type:", font=("Arial", 9, "bold"),
            bg="#F8FAFC", fg=MUTED
        ).grid(row=1, column=0, sticky="w", padx=(0, 5))

        tk.Label(
            details, textvariable=self.file_type,
            font=("Arial", 9), bg="#F8FAFC", fg=TEXT
        ).grid(row=1, column=1, sticky="w")

        tk.Label(
            details, text="Size:", font=("Arial", 9, "bold"),
            bg="#F8FAFC", fg=MUTED
        ).grid(row=2, column=0, sticky="w", padx=(0, 5))

        tk.Label(
            details, textvariable=self.file_size,
            font=("Arial", 9), bg="#F8FAFC", fg=TEXT
        ).grid(row=2, column=1, sticky="w")

        # Secret key card
        key_card = tk.Frame(
            main,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        key_card.pack(fill="x", pady=(0, 12))

        tk.Label(
            key_card,
            text="🔑  Secret Encryption Key",
            font=("Arial", 13, "bold"),
            bg=CARD,
            fg=TEXT
        ).pack(anchor="w", padx=20, pady=(15, 8))

        key_row = tk.Frame(key_card, bg=CARD)
        key_row.pack(fill="x", padx=20)

        self.key_entry = tk.Entry(
            key_row,
            textvariable=self.key_value,
            font=("Arial", 10),
            show="•",
            relief="solid",
            bd=1
        )
        self.key_entry.pack(side="left", fill="x", expand=True, ipady=7)

        tk.Button(
            key_row,
            text="Generate",
            command=self.generate_key,
            bg="#EDE9FE",
            fg=PURPLE,
            activebackground="#DDD6FE",
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            key_row,
            text="👁",
            command=self.toggle_key_visibility,
            bg="#F1F5F9",
            relief="flat",
            width=4,
            cursor="hand2"
        ).pack(side="right", padx=(8, 0))

        # Key management buttons
        key_buttons = tk.Frame(key_card, bg=CARD)
        key_buttons.pack(pady=15)

        tk.Button(
            key_buttons,
            text="📋 Copy Key",
            command=self.copy_key,
            bg="#F1F5F9",
            fg=TEXT,
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).pack(side="left", padx=6)

        tk.Button(
            key_buttons,
            text="💾 Save Key",
            command=self.save_key,
            bg="#F1F5F9",
            fg=TEXT,
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).pack(side="left", padx=6)

        tk.Button(
            key_buttons,
            text="📂 Load Key",
            command=self.load_key,
            bg="#F1F5F9",
            fg=TEXT,
            relief="flat",
            padx=15,
            pady=7,
            cursor="hand2"
        ).pack(side="left", padx=6)

        # Action buttons
        action_frame = tk.Frame(main, bg=BG)
        action_frame.pack(fill="x", pady=10)

        tk.Button(
            action_frame,
            text="🔒  ENCRYPT FILE",
            command=self.encrypt_file,
            bg=PRIMARY,
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            pady=13,
            cursor="hand2"
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Button(
            action_frame,
            text="🔓  DECRYPT FILE",
            command=self.decrypt_file,
            bg=PURPLE,
            fg="white",
            activebackground="#6D28D9",
            activeforeground="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            pady=13,
            cursor="hand2"
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Reset button
        tk.Button(
            main,
            text="↻  RESET",
            command=self.reset_app,
            bg="#F1F5F9",
            fg=TEXT,
            font=("Arial", 10, "bold"),
            relief="flat",
            pady=9,
            cursor="hand2"
        ).pack(fill="x", pady=(0, 10))

        # Progress bar
        progress_frame = tk.Frame(main, bg=BG)
        progress_frame.pack(fill="x", pady=(0, 10))

        self.progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100
        )
        self.progress.pack(fill="x")
        self.progress["value"] = 0

        # Status card
        status_card = tk.Frame(
            main,
            bg="#ECFDF5",
            highlightbackground="#BBF7D0",
            highlightthickness=1
        )
        status_card.pack(fill="x", pady=(0, 10))

        tk.Label(
            status_card,
            textvariable=self.status,
            font=("Arial", 10, "bold"),
            bg="#ECFDF5",
            fg=SUCCESS
        ).pack(pady=10)

        # Security information
        security_card = tk.Frame(
            main,
            bg="#EFF6FF",
            highlightbackground="#BFDBFE",
            highlightthickness=1
        )
        security_card.pack(fill="x")

        tk.Label(
            security_card,
            text="🛡️  SECURITY INFORMATION",
            font=("Arial", 11, "bold"),
            bg="#EFF6FF",
            fg=PRIMARY
        ).pack(anchor="w", padx=18, pady=(10, 4))

        tk.Label(
            security_card,
            text=(
                "• Files are protected using Fernet authenticated encryption\n"
                "• SHA-256 fingerprints are checked after decryption\n"
                "• The same secret key is required to decrypt a file\n"
                "• Keep your .key file safe — losing it may prevent recovery"
            ),
            justify="left",
            font=("Arial", 9),
            bg="#EFF6FF",
            fg=TEXT
        ).pack(anchor="w", padx=20, pady=(0, 10))

    # ==============================
    # UI FUNCTIONS
    # ==============================

    def update_progress(self, value, message=None):
        self.progress["value"] = value

        if message:
            self.status.set(message)

        self.root.update_idletasks()

    def toggle_key_visibility(self):
        if self.key_visible:
            self.key_entry.config(show="•")
            self.key_visible = False
        else:
            self.key_entry.config(show="")
            self.key_visible = True

    def browse_file(self):
        filename = filedialog.askopenfilename()

        if filename:
            file_path = Path(filename)

            try:
                size = file_path.stat().st_size
            except OSError as error:
                messagebox.showerror("File Error", str(error))
                return

            self.file_path.set(filename)
            self.file_name.set(file_path.name)

            if file_path.suffix:
                self.file_type.set(file_path.suffix.upper() + " File")
            else:
                self.file_type.set("Unknown")

            self.file_size.set(self.format_file_size(size))
            self.progress["value"] = 0
            self.status.set("📁 File selected successfully")

    def format_file_size(self, size):
        if size < 1024:
            return f"{size} Bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        return f"{size / (1024 * 1024 * 1024):.2f} GB"

    def reset_app(self):
        self.file_path.set("")
        self.key_value.set("")
        self.file_name.set("No file selected")
        self.file_type.set("-")
        self.file_size.set("-")
        self.key_entry.config(show="•")
        self.key_visible = False
        self.progress["value"] = 0
        self.status.set("Ready — Select a file to begin")

    # ==============================
    # KEY FUNCTIONS
    # ==============================

    def generate_key(self):
        key = Fernet.generate_key().decode("utf-8")
        self.key_value.set(key)
        self.status.set("🔑 New key generated — save it safely!")

    def copy_key(self):
        key = self.key_value.get()

        if not key:
            messagebox.showwarning(
                "No Key",
                "Please generate or load a key first."
            )
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(key)
        self.root.update()
        self.status.set("📋 Key copied to clipboard")

    def save_key(self):
        key = self.key_value.get()

        if not key:
            messagebox.showwarning(
                "No Key",
                "Please generate or enter a key first."
            )
            return

        try:
            Fernet(key.encode("utf-8"))

            filename = filedialog.asksaveasfilename(
                title="Save Encryption Key",
                defaultextension=".key",
                filetypes=[
                    ("Key Files", "*.key"),
                    ("All Files", "*.*")
                ]
            )

            if filename:
                with open(filename, "w", encoding="utf-8") as key_file:
                    key_file.write(key)

                self.status.set("💾 Encryption key saved successfully")

        except Exception:
            messagebox.showerror(
                "Invalid Key",
                "The encryption key is invalid."
            )

    def load_key(self):
        filename = filedialog.askopenfilename(
            title="Load Encryption Key",
            filetypes=[
                ("Key Files", "*.key"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as key_file:
                    key = key_file.read().strip()

                Fernet(key.encode("utf-8"))
                self.key_value.set(key)
                self.status.set("🔑 Encryption key loaded successfully")

            except Exception:
                messagebox.showerror(
                    "Invalid Key",
                    "The selected file does not contain "
                    "a valid encryption key."
                )

    # ==============================
    # SHARED VALIDATION
    # ==============================

    def get_cipher(self):
        key = self.key_value.get().strip()

        if not key:
            messagebox.showerror(
                "Missing Key",
                "Please generate or load a secret key first."
            )
            return None

        try:
            return Fernet(key.encode("utf-8"))
        except Exception:
            messagebox.showerror(
                "Invalid Key",
                "Please enter or load a valid Fernet key."
            )
            return None

    def choose_output_path(self, title, initial_name, encrypted=False):
        filetypes = (
            [("Encrypted Files", "*.enc"), ("All Files", "*.*")]
            if encrypted else
            [("All Files", "*.*")]
        )

        output_path = filedialog.asksaveasfilename(
            title=title,
            initialfile=initial_name,
            defaultextension=".enc" if encrypted else "",
            filetypes=filetypes
        )

        if not output_path:
            self.update_progress(0, "Operation cancelled")
            return None

        if Path(output_path).exists():
            overwrite = messagebox.askyesno(
                "File Already Exists",
                f"The file already exists:\n\n{output_path}\n\n"
                "Do you want to overwrite it?"
            )
            if not overwrite:
                self.update_progress(
                    0,
                    "Operation cancelled — file not overwritten"
                )
                return None

        return output_path

    # ==============================
    # ENCRYPTION WITH SHA-256
    # ==============================

    def encrypt_file(self):
        try:
            self.update_progress(10, "🔄 Preparing encryption...")

            selected_path = self.file_path.get().strip()
            if not selected_path:
                messagebox.showerror("Error", "Please select a file.")
                self.update_progress(0, "❌ No file selected")
                return

            file_path = Path(selected_path)

            if not file_path.is_file():
                messagebox.showerror(
                    "Error",
                    "Please select a valid file."
                )
                self.update_progress(0, "❌ No valid file selected")
                return

            cipher = self.get_cipher()
            if cipher is None:
                self.update_progress(0, "❌ Encryption key unavailable")
                return

            output_path = self.choose_output_path(
                "Save Encrypted File",
                file_path.name + ".enc",
                encrypted=True
            )
            if not output_path:
                return

            self.update_progress(30, "📖 Reading file...")
            with open(file_path, "rb") as source_file:
                data = source_file.read()

            self.update_progress(45, "🔍 Calculating SHA-256 hash...")
            original_hash = hashlib.sha256(data).digest()

            # Payload layout: marker (4 bytes) + SHA-256 (32 bytes) + file data.
            # Fernet encrypts and authenticates the entire payload.
            payload = PAYLOAD_MARKER + original_hash + data

            self.update_progress(65, "🔐 Encrypting file...")
            encrypted_data = cipher.encrypt(payload)

            self.update_progress(85, "💾 Saving encrypted file...")
            with open(output_path, "wb") as output_file:
                output_file.write(encrypted_data)

            self.update_progress(100, "✅ File encrypted successfully!")

            messagebox.showinfo(
                "Encryption Successful",
                "🔒 File encrypted successfully!\n\n"
                f"Saved as:\n{output_path}\n\n"
                f"SHA-256:\n{original_hash.hex()}\n\n"
                "⚠️ Keep your encryption key safe."
            )

        except Exception as error:
            self.update_progress(0, "❌ Encryption failed")
            messagebox.showerror("Encryption Error", str(error))

    # ==============================
    # DECRYPTION WITH SHA-256
    # ==============================

    def decrypt_file(self):
        try:
            self.update_progress(10, "🔄 Preparing decryption...")

            selected_path = self.file_path.get().strip()
            if not selected_path:
                messagebox.showerror(
                    "Error",
                    "Please select an encrypted file."
                )
                self.update_progress(0, "❌ No file selected")
                return

            file_path = Path(selected_path)

            if not file_path.is_file():
                messagebox.showerror(
                    "Error",
                    "Please select a valid encrypted file."
                )
                self.update_progress(0, "❌ No valid file selected")
                return

            cipher = self.get_cipher()
            if cipher is None:
                self.update_progress(0, "❌ Decryption key unavailable")
                return

            if file_path.name.endswith(".enc"):
                default_name = file_path.name[:-4]
            else:
                default_name = file_path.name + ".decrypted"

            output_path = self.choose_output_path(
                "Save Decrypted File",
                default_name,
                encrypted=False
            )
            if not output_path:
                return

            self.update_progress(30, "📖 Reading encrypted file...")
            with open(file_path, "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()

            self.update_progress(55, "🔓 Decrypting file...")
            decrypted_payload = cipher.decrypt(encrypted_data)

            self.update_progress(75, "🛡️ Verifying SHA-256 integrity...")

            if decrypted_payload.startswith(PAYLOAD_MARKER):
                # New format: marker + 32-byte stored hash + original bytes.
                if len(decrypted_payload) < len(PAYLOAD_MARKER) + HASH_LENGTH:
                    raise ValueError(
                        "Encrypted payload is incomplete. "
                        "The file cannot be verified."
                    )

                hash_start = len(PAYLOAD_MARKER)
                hash_end = hash_start + HASH_LENGTH

                stored_hash = decrypted_payload[hash_start:hash_end]
                decrypted_data = decrypted_payload[hash_end:]

                calculated_hash = hashlib.sha256(decrypted_data).digest()

                if not hmac.compare_digest(stored_hash, calculated_hash):
                    raise ValueError(
                        "SHA-256 integrity verification failed. "
                        "The decrypted data does not match its stored hash."
                    )

                integrity_message = (
                    "SHA-256 Integrity: VERIFIED\n"
                    "Original and decrypted file hashes match."
                )
                hash_display = calculated_hash.hex()

            else:
                # Backward compatibility: files encrypted before SHA-256
                # metadata was added can still be decrypted, but their
                # original hash cannot be compared.
                decrypted_data = decrypted_payload
                calculated_hash = hashlib.sha256(decrypted_data).digest()

                integrity_message = (
                    "Legacy encrypted file detected.\n"
                    "File decrypted, but no original SHA-256 hash "
                    "was stored for comparison."
                )
                hash_display = calculated_hash.hex()

            # Do not write the output until decryption and verification finish.
            self.update_progress(90, "💾 Saving verified decrypted file...")
            with open(output_path, "wb") as output_file:
                output_file.write(decrypted_data)

            self.update_progress(100, "✅ Decryption and verification complete!")

            messagebox.showinfo(
                "Decryption Successful",
                "🔓 File decrypted successfully!\n\n"
                f"Saved as:\n{output_path}\n\n"
                f"{integrity_message}\n\n"
                f"SHA-256:\n{hash_display}"
            )

        except InvalidToken:
            self.update_progress(
                0,
                "❌ Decryption failed — invalid key or damaged file"
            )
            messagebox.showerror(
                "Decryption Failed",
                "Invalid key or corrupted encrypted file.\n\n"
                "Please use the same key that was used for encryption."
            )

        except Exception as error:
            self.update_progress(0, "❌ Decryption or verification failed")
            messagebox.showerror(
                "Decryption Error",
                str(error)
            )


# ==============================
# START APPLICATION
# ==============================

if __name__ == "__main__":
    root = tk.Tk()
    app = FileEncryptionApp(root)
    root.mainloop()
