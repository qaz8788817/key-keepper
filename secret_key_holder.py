import customtkinter as ctk
from tkinter import messagebox, simpledialog
import json
import os
import base64
import platform
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

if platform.system() == "Windows":
    main_font_family = "Segoe UI"
elif platform.system() == "Darwin":
    main_font_family = "PingFang TC"
else:
    main_font_family = "Arial"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# =====================================================================
# 🔒 核心加密後台引擎
# =====================================================================
class EncryptionEngine:
    def __init__(self):
        self.salt = b'\xaa\xbb\xcc\xdd\x11\x22\x33\x44'

    def _generate_key(self, master_password: str) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = kdf.derive(master_password.encode('utf-8'))
        return base64.urlsafe_b64encode(key)

    def encrypt_data(self, data_dict: dict, master_password: str) -> str:
        key = self._generate_key(master_password)
        fernet = Fernet(key)
        json_str = json.dumps(data_dict, ensure_ascii=False)
        encrypted_bytes = fernet.encrypt(json_str.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')

    def decrypt_data(self, encrypted_str: str, master_password: str) -> dict:
        key = self._generate_key(master_password)
        fernet = Fernet(key)
        decrypted_bytes = fernet.decrypt(encrypted_str.encode('utf-8'))
        return json.loads(decrypted_bytes.decode('utf-8'))


# =====================================================================
# 🎨 前台介面與業務邏輯
# =====================================================================
class KeyVaultDesktopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("KeyVault Pro - Secure Token & Password Manager")
        self.geometry("680x700")

        # 專屬色調設定
        self.primary_purple = "#7F56D9"
        self.hover_purple = "#6941C6"
        self.light_purple = "#D6BBFB"
        self.text_yellow = "#FDFDC9"
        self.card_bg = "#1A1A24"

        self.title_font = ctk.CTkFont(family=main_font_family, size=20, weight="bold")
        self.body_font = ctk.CTkFont(family=main_font_family, size=13)
        self.btn_font = ctk.CTkFont(family=main_font_family, size=13, weight="bold")

        self.db_file = "vault.enc"
        self.crypt_engine = EncryptionEngine()
        self.master_password = ""
        self.vault_data = {"api_keys": [], "web_accounts": []}
        
        self.visible_secrets = set() 

        # ✨ 關鍵修正：不要用 withdraw()，改在主視窗內縮最小化或直接就地呼叫
        # 讓視窗先更新一下底層架構，防止焦點遺失
        self.update_idletasks()
        
        # 使用 after 延遲 100 毫秒呼叫，確保主視窗完全建立好，再彈出密碼框，徹底解決閃退！
        self.after(100, self.trigger_login_or_init)

    # --- 🔐 登入與資料初始化防線 ---
    def trigger_login_or_init(self):
        if not os.path.exists(self.db_file):
            messagebox.showinfo("Welcome 🎉", "Welcome to KeyVault! Please setup your Master Password first.\nThis password cannot be recovered if lost!", parent=self)
            new_password = simpledialog.askstring("Setup Vault", "Set your Master Password:", show="*", parent=self)
            if not new_password or len(new_password.strip()) < 4:
                messagebox.showerror("Error", "Invalid password! Password must be at least 4 characters.", parent=self)
                self.destroy()
                return
            
            self.master_password = new_password.strip()
            self.save_vault_to_disk()
            messagebox.showinfo("Success", "Vault initialized successfully! Welcome aboard.", parent=self)
        else:
            attempt = simpledialog.askstring("Unlock Vault 🔓", "Enter Master Password to decrypt database:", show="*", parent=self)
            if attempt is None:
                self.destroy()
                return
                
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    encrypted_content = f.read()
                self.vault_data = self.crypt_engine.decrypt_data(encrypted_content, attempt)
                self.master_password = attempt
            except Exception:
                messagebox.showerror("Access Denied ❌", "Invalid Master Password! Decryption failed.", parent=self)
                self.destroy()
                return

        # 驗證成功後，才正式把主畫面的元件生出來
        self.setup_main_ui()
        self.refresh_vault_ui()

    def save_vault_to_disk(self):
        try:
            encrypted_str = self.crypt_engine.encrypt_data(self.vault_data, self.master_password)
            with open(self.db_file, "w", encoding="utf-8") as f:
                f.write(encrypted_str)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save encrypted data: {e}", parent=self)

    # --- 🎨 主畫面佈局 ---
    def setup_main_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 5))
        
        ctk.CTkLabel(header_frame, text="🔒 KeyVault Secure Dashboard", font=self.title_font).pack(side="left")
        
        btn_add = ctk.CTkButton(
            header_frame, text="＋ Add New Secret", 
            font=self.btn_font, fg_color=self.primary_purple, hover_color=self.hover_purple,
            command=self.open_add_secret_dialog, width=140, height=32
        )
        btn_add.pack(side="right")

        self.tabview = ctk.CTkTabview(self, corner_radius=15)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self.tab_api = self.tabview.add("🔑 API Keys & Tokens")
        self.tab_web = self.tabview.add("🌐 Web Accounts")

        self.scroll_api = ctk.CTkScrollableFrame(self.tab_api, fg_color="transparent")
        self.scroll_api.pack(fill="both", expand=True, padx=5, pady=5)
        self.scroll_api._scrollbar.configure(width=0) 
        self.scroll_api._scrollbar.pack_forget()

        self.scroll_web = ctk.CTkScrollableFrame(self.tab_web, fg_color="transparent")
        self.scroll_web.pack(fill="both", expand=True, padx=5, pady=5)
        self.scroll_web._scrollbar.configure(width=0)
        self.scroll_web._scrollbar.pack_forget()

    # --- 🔄 UI 即時重繪與卡片渲染 ---
    def refresh_all_ui(self):
        self.refresh_vault_ui()

    def refresh_vault_ui(self):
        for widget in self.scroll_api.winfo_children(): widget.destroy()
        for widget in self.scroll_web.winfo_children(): widget.destroy()

        if not self.vault_data.get("api_keys"):
            ctk.CTkLabel(self.scroll_api, text="No API Keys saved yet.", font=self.body_font, text_color="gray").pack(pady=30)
        else:
            for idx, item in enumerate(self.vault_data["api_keys"]):
                self.create_secret_card(self.scroll_api, "api_keys", idx, item)

        if not self.vault_data.get("web_accounts"):
            ctk.CTkLabel(self.scroll_web, text="No Website Accounts saved yet.", font=self.body_font, text_color="gray").pack(pady=30)
        else:
            for idx, item in enumerate(self.vault_data["web_accounts"]):
                self.create_secret_card(self.scroll_web, "web_accounts", idx, item)

    def create_secret_card(self, container, category_key, index, item):
        card = ctk.CTkFrame(container, fg_color=self.card_bg, corner_radius=12, border_width=1, border_color="#2A2A35")
        card.pack(fill="x", pady=6, padx=2)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        lbl_title = ctk.CTkLabel(info_frame, text=item["title"], font=ctk.CTkFont(family=main_font_family, size=15, weight="bold"), text_color=self.light_purple)
        lbl_title.pack(anchor="w")
        
        sub_text = f"Account: {item['account']}" if item.get('account') else f"Note: {item.get('note', '')}"
        lbl_sub = ctk.CTkLabel(info_frame, text=sub_text, font=self.body_font, text_color="gray")
        lbl_sub.pack(anchor="w", pady=(2, 0))

        unique_id = f"{category_key}_{index}"
        is_visible = unique_id in self.visible_secrets
        display_text = item["secret_key"] if is_visible else "••••••••••••••••"
        eye_icon = "👁 聞" if is_visible else "👁 密" 

        secret_frame = ctk.CTkFrame(card, fg_color="transparent")
        secret_frame.pack(side="right", padx=15)

        lbl_secret = ctk.CTkLabel(secret_frame, text=display_text, font=self.body_font, text_color=self.text_yellow, width=150, anchor="e")
        lbl_secret.pack(side="left", padx=10)

        btn_eye = ctk.CTkButton(
            secret_frame, text=eye_icon, width=45, height=26, fg_color="#2E2E3A", hover_color="#3E3E4A",
            command=lambda k=category_key, i=index: self.toggle_secret_visibility(k, i)
        )
        btn_eye.pack(side="left", padx=2)

        btn_copy = ctk.CTkButton(
            secret_frame, text="📋 Copy", width=55, height=26, fg_color=self.primary_purple, hover_color=self.hover_purple,
            font=self.btn_font, command=lambda val=item["secret_key"]: self.copy_to_clipboard(val)
        )
        btn_copy.pack(side="left", padx=2)

        btn_del = ctk.CTkButton(
            secret_frame, text="🗑", width=30, height=26, fg_color="#E74C3C", hover_color="#C0392b",
            command=lambda k=category_key, i=index: self.delete_secret_item(k, i)
        )
        btn_del.pack(side="left", padx=2)

    def toggle_secret_visibility(self, category_key, index):
        unique_id = f"{category_key}_{index}"
        if unique_id in self.visible_secrets:
            self.visible_secrets.remove(unique_id)
        else:
            self.visible_secrets.add(unique_id)
        self.refresh_vault_ui()

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied 📋", "Secret has been copied to your clipboard safely!", parent=self)

    def delete_secret_item(self, category_key, index):
        item = self.vault_data[category_key][index]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item['title']}'?", parent=self):
            self.vault_data[category_key].pop(index)
            uid = f"{category_key}_{index}"
            if uid in self.visible_secrets: self.visible_secrets.remove(uid)
            self.save_vault_to_disk()
            self.refresh_vault_ui()

    def open_add_secret_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Secret Entry")
        dialog.geometry("400x420")
        dialog.grab_set()  
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog, text="🔒 Add New Credentials", font=ctk.CTkFont(family=main_font_family, size=16, weight="bold")).pack(pady=15)

        ctk.CTkLabel(dialog, text="Vault Category:", font=self.body_font).pack(anchor="w", padx=30)
        cbo_cat = ctk.CTkOptionMenu(dialog, values=["🔑 API Keys & Tokens", "🌐 Web Accounts"], width=340, fg_color="#34495e")
        cbo_cat.pack(pady=(2, 12))

        ctk.CTkLabel(dialog, text="Title / Service Name (e.g. Gemini API):", font=self.body_font).pack(anchor="w", padx=30)
        ent_title = ctk.CTkEntry(dialog, placeholder_text="e.g. GitHub Token, Netflix", width=340)
        ent_title.pack(pady=(2, 12))

        ctk.CTkLabel(dialog, text="Account Username / Owner (Optional):", font=self.body_font).pack(anchor="w", padx=30)
        ent_acc = ctk.CTkEntry(dialog, placeholder_text="e.g. vivian@email.com", width=340)
        ent_acc.pack(pady=(2, 12))

        ctk.CTkLabel(dialog, text="Secret Password / Key String:", font=self.body_font).pack(anchor="w", padx=30)
        ent_key = ctk.CTkEntry(dialog, placeholder_text="Paste your secret payload here...", width=340, show="*")
        ent_key.pack(pady=(2, 12))

        def save_new_entry():
            cat_choice = cbo_cat.get()
            title = ent_title.get().strip()
            account = ent_acc.get().strip()
            secret_key = ent_key.get().strip()

            if not title or not secret_key:
                messagebox.showwarning("Warning", "Title and Secret Key fields are required!", parent=dialog)
                return

            new_item = {
                "title": title,
                "account": account,
                "secret_key": secret_key
            }

            target_key = "api_keys" if "API" in cat_choice else "web_accounts"
            self.vault_data[target_key].append(new_item)
            
            self.save_vault_to_disk()
            self.refresh_vault_ui()
            dialog.destroy()
            messagebox.showinfo("Saved 🚀", f"'{title}' has been safely encrypted and saved!", parent=self)

        btn_save = ctk.CTkButton(
            dialog, text="Encrypt and Save Entry 📥", font=self.btn_font,
            fg_color=self.primary_purple, hover_color=self.hover_purple,
            height=40, command=save_new_entry
        )
        btn_save.pack(pady=20, fill="x", padx=30)


if __name__ == "__main__":
    app = KeyVaultDesktopApp()
    app.mainloop()