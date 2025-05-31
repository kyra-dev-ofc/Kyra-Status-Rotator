import requests
import time
import json
import os
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

if os.name == "nt":
    os.system('title KYRA Status Rotator')
else:
    print("\033]0;KYRA Status Rotator\a", end="", flush=True)

def show_kyra_banner():
    print(f"""
{Fore.MAGENTA}
  ██╗  ██╗██╗   ██╗██████╗  █████╗ 
  ██║ ██╔╝╚██╗ ██╔╝██╔══██╗██╔══██╗
  █████╔╝  ╚████╔╝ ██████╔╝███████║
  ██╔═██╗   ╚██╔╝  ██╔══██╗██╔══██║
  ██║  ██╗   ██║   ██║  ██║██║  ██║
  ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
{Fore.CYAN}
  ┌───────────────────────────────┐
  │      {Fore.WHITE}KYRA STATUS ROTATOR{Fore.CYAN}      │
  └───────────────────────────────┘
{Fore.RESET}
""")

def load_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            print(f"{Fore.GREEN}✓ Configuration loaded successfully{Fore.RESET}\n")
            return config
    except Exception as e:
        print(f"{Fore.RED}✗ Error loading config.json: {e}{Fore.RESET}\n")
        exit()

def read_file_lines(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            print(f"{Fore.GREEN}✓ Loaded {len(lines)} items from {filename}{Fore.RESET}\n")
            return lines
    except FileNotFoundError:
        print(f"{Fore.RED}✗ {filename} not found.{Fore.RESET}")
        exit()

def get_user_info(token):
    headers = {"authorization": token}
    try:
        response = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data["username"], data["discriminator"], True
        return "Unknown", "0000", False
    except Exception:
        return "Unknown", "0000", False

def change_status(token, message, emoji_name, emoji_id, status):
    headers = {"authorization": token}
    payload = {
        "custom_status": {
            "text": message,
            "emoji_name": emoji_name,
            "emoji_id": emoji_id or None
        },
        "status": status.lower()
    }

    try:
        response = requests.patch(
            "https://discord.com/api/v10/users/@me/settings",
            headers=headers,
            json=payload
        )
        return response.status_code == 200
    except Exception:
        return False

def display_status_update(token, username, discriminator, status_text, emoji_name, status_mode):
    timestamp = datetime.now().strftime("%H:%M:%S")
    masked_token = f"{token[:6]}...{token[-4:]}" if len(token) > 10 else token
    
    print(f"{Fore.BLUE}┌── {Fore.CYAN}Status Update {Fore.BLUE}───{'─' * max(0, 30 - len(status_text))}")
    print(f"{Fore.BLUE}│ {Fore.YELLOW}• Time: {Fore.GREEN}{timestamp}")
    print(f"{Fore.BLUE}│ {Fore.YELLOW}• Account: {Fore.GREEN}{username}")
    print(f"{Fore.BLUE}│ {Fore.YELLOW}• Token: {Fore.GREEN}{masked_token}")
    print(f"{Fore.BLUE}│ {Fore.YELLOW}• Status: {Fore.CYAN}{status_text}")
    print(f"{Fore.BLUE}│ {Fore.YELLOW}• Emoji: {Fore.CYAN}{emoji_name}")
    print(f"{Fore.BLUE}│ {Fore.YELLOW}• Mode: {Fore.CYAN}{status_mode}")
    print(f"{Fore.BLUE}└───────────────────────────────────────┘{Fore.RESET}")

def main():
    show_kyra_banner()
    config = load_config()
    
    token = config["token"]
    status_sequence = config["status_sequence"]
    clear_enabled = config["clear_enabled"]
    clear_interval = config["clear_interval"]
    speed_rotator = config["speed_rotator"]
    
    statuses = read_file_lines("text.txt")
    emojis = read_file_lines("emojis.txt")
    
    status_index = emoji_index = 0
    cycle_count = 0
    
    try:
        while True:
            status_mode = status_sequence[status_index % len(status_sequence)]
            status_text = statuses[status_index % len(statuses)]
            emoji_line = emojis[emoji_index % len(emojis)]
            
            emoji_parts = emoji_line.split(":")
            emoji_name = emoji_parts[0]
            emoji_id = emoji_parts[1] if len(emoji_parts) == 2 else None
            
            username, discriminator, token_valid = get_user_info(token)
            
            if change_status(token, status_text, emoji_name, emoji_id, status_mode):
                display_status_update(token, username, discriminator, 
                                    status_text, emoji_name, status_mode)
            else:
                print(f"{Fore.RED}✗ Failed to update status{Fore.RESET}")
            
            status_index += 1
            emoji_index += 1
            cycle_count += 1
            
            time.sleep(speed_rotator)
            
            if clear_enabled and cycle_count % clear_interval == 0:
                os.system('cls' if os.name == 'nt' else 'clear')
                show_kyra_banner()
                
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}✨ Thank you for using KYRA Status Rotator! ✨{Fore.RESET}")

if __name__ == "__main__":
    main()