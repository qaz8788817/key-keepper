# 🔒 KeyVault Desktop - Secure Password Manager

> **A Secure, Locally-Encrypted Desktop Password Vault Powered by Python, CustomTkinter, and Cryptography.**

KeyVault Desktop is a localized credentials safe designed for developers and users who refuse to trust cloud-based password syncs. Built with zero-knowledge architectural principles, it secures your accounts, passwords, and sensitive keys entirely on your offline machine. Combining modern macaron-palette aesthetics with rigorous cryptographic standards, KeyVault balances impenetrable protection with an ultra-smooth desktop user experience.

---

## ✨ Key Features

* **🛡️ AES-128 Localized Encryption**: Leverages `cryptography.fernet` symmetric key architecture to ensure that even if your storage file (`vault.json`) is physically stolen, your raw data looks like unintelligible gibberish.
* **🔑 Master Password Protection**: Employs structural hashing safeguards. Your Master Password is never saved anywhere in plain text, making it immune to basic string-extraction memory leaks.
* **👁️ Instant Masking & One-Click Copy**: Built with elegant on-screen masking (hiding items behind `******` patterns). Features seamless click-to-copy capabilities to speed up log-in workflows without exposing items to trailing shoulder surfers.
* **🎨 Anti-Fatigue Micro-Dashboard**: Houses a custom dual-pane layout utilizing a custom handwriting-font stack (*StayHomeWriting*) to make security look pleasant rather than intimidating.

---

## 🔒 Cryptographic Blueprint

KeyVault Desktop handles data streams through a strict localized isolation cycle:

1. **Initialization**: Derives an absolute 32-byte URL-safe base64 encryption token from your Master Password setup block.
2. **Persistence Processing**: Serializes data records (`Platform`, `Username`, `Password`, `Updated_At`) into a dynamic JSON packet, instantly piping it through the symmetric Fernet cipher block before hitting the hard drive.
3. **Memory Flush**: Clears intermediate plain-text credential variables out of active loop tracking upon successful database write-backs.

---

## 🛠️ Tech Stack & Dependencies

* **GUI Interface Engine**: `CustomTkinter` (Python 3.10+)
* **Encryption Kernel**: `cryptography` (Advanced Symmetric Fernet Recipes)
* **Storage Backend**: Native lightweight `JSON` flat-file serialization wrapper

---

## 🚀 Getting Started

### Prerequisites

Deploy the mandatory interface structures and industry-standard security binaries into your current sandbox shell:

```bash
pip install customtkinter cryptography
```
## 介面
<img width="846" height="906" alt="image" src="https://github.com/user-attachments/assets/ecf3932b-e2bd-4990-a1ff-13de2487c60c" />
<img width="510" height="567" alt="image" src="https://github.com/user-attachments/assets/ba0665e8-96c6-442c-9803-97eca31b0e19" />
