import os
import re
import json
import subprocess
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from core.config import BASE_DIR

CONTACTS_FILE = BASE_DIR / "contacts.json"

DEFAULT_CONTACTS = {
    "papa": {"name": "Papa", "phone": "+919876543210"},
    "mummy": {"name": "Mummy", "phone": "+919876543211"},
    "bhai": {"name": "Bhai", "phone": "+919876543212"},
    "sister": {"name": "Sister", "phone": "+919876543213"},
    "rohit": {"name": "Rohit", "phone": "+919876543214"},
    "aman": {"name": "Aman", "phone": "+919876543215"},
    "boss": {"name": "Boss", "phone": "+919876543216"}
}

class ContactManager:
    """Manages address book, telephone calling, and text messaging for Jarvis."""

    def __init__(self):
        self.contacts: Dict[str, Dict[str, str]] = {}
        self._load_contacts()

    def _load_contacts(self):
        if not CONTACTS_FILE.exists():
            self.contacts = DEFAULT_CONTACTS.copy()
            self._save_contacts()
        else:
            try:
                with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
                    self.contacts = json.load(f)
            except Exception:
                self.contacts = DEFAULT_CONTACTS.copy()

    def _save_contacts(self):
        try:
            with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.contacts, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def add_contact(self, name: str, phone: str) -> str:
        """Adds or updates a contact."""
        key = name.strip().lower()
        clean_phone = re.sub(r'[^0-9+]', '', phone.strip())
        self.contacts[key] = {"name": name.strip().title(), "phone": clean_phone}
        self._save_contacts()
        return f"Contact '{name.strip().title()}' saved with phone number {clean_phone}, sir."

    def find_contact(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Finds contact by name, alias, or returns cleaned phone number.
        Returns: (display_name, phone_number)
        """
        q = query.strip().lower()
        
        # Check if direct phone number (7 to 15 digits)
        digits_only = re.sub(r'[^0-9+]', '', q)
        if len(digits_only) >= 7:
            return digits_only, digits_only

        # Check exact key match
        if q in self.contacts:
            info = self.contacts[q]
            return info.get("name", q.title()), info.get("phone")

        # Fuzzy / partial match
        for key, info in self.contacts.items():
            if key in q or q in key or q in info.get("name", "").lower():
                return info.get("name", key.title()), info.get("phone")

        return None, None

    def make_call(self, target: str) -> str:
        """Initiates a phone call / FaceTime audio call on macOS."""
        if not target or not target.strip():
            return "Sir, please specify who you would like to call."

        name, phone = self.find_contact(target)
        
        # If not found in local contacts, attempt direct dialing or open FaceTime
        if not phone:
            # Check if digits in target
            digits = re.sub(r'[^0-9+]', '', target)
            if len(digits) >= 7:
                phone = digits
                name = digits
            else:
                # Open native Contacts app to let user pick
                subprocess.Popen(["open", "-a", "Contacts"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Could not find phone number for '{target}', sir. I have opened your macOS Contacts app."

        clean_phone = re.sub(r'[^0-9+]', '', phone)
        
        # 1. Trigger macOS native telephone call (FaceTime / iPhone Cellular Relay)
        try:
            subprocess.Popen(["open", f"tel:{clean_phone}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            try:
                subprocess.Popen(["open", f"facetime-audio:{clean_phone}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

        return f"Initiating call to {name} at {phone}, sir. Connecting via FaceTime audio."

    def send_text(self, target: str, message: str, platform: str = "messages") -> str:
        """Sends or drafts an SMS / iMessage or WhatsApp message."""
        if not target or not target.strip():
            return "Sir, please specify who you would like to message."

        if not message or not message.strip():
            message = "Hello, please call me when you are free."

        name, phone = self.find_contact(target)
        if not phone:
            digits = re.sub(r'[^0-9+]', '', target)
            if len(digits) >= 7:
                phone = digits
                name = digits
            else:
                return f"Could not find contact details for '{target}', sir."

        clean_phone = re.sub(r'[^0-9+]', '', phone)
        encoded_msg = urllib.parse.quote(message.strip())

        # WhatsApp mode
        if platform.lower() == "whatsapp" or "whatsapp" in platform.lower():
            # WhatsApp requires country code without +
            wa_num = clean_phone.replace("+", "")
            if len(wa_num) == 10:
                wa_num = "91" + wa_num  # default to India if 10 digits
            
            wa_url = f"https://web.whatsapp.com/send?phone={wa_num}&text={encoded_msg}"
            try:
                subprocess.Popen(["open", f"whatsapp://send?phone={wa_num}&text={encoded_msg}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            subprocess.Popen(["open", wa_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opening WhatsApp to transmit message to {name}: '{message}', sir."

        # Default: Apple Messages / SMS
        # Try native AppleScript for direct instant send
        apple_script = f'''
        tell application "Messages"
            try
                set targetService to 1st service whose service type = iMessage
                set targetBuddy to participant "{clean_phone}" of targetService
                send "{message}" to targetBuddy
            on error
                open location "sms:{clean_phone}&body={encoded_msg}"
            end try
        end tell
        '''
        try:
            res = subprocess.run(["osascript", "-e", apple_script], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return f"Message dispatched to {name} ({clean_phone}): '{message}', sir."
        except Exception:
            pass

        # Fallback: open sms URL scheme directly
        subprocess.Popen(["open", f"sms:{clean_phone}&body={encoded_msg}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Prepared message for {name} ({clean_phone}): '{message}', sir."

contacts_mgr = ContactManager()
