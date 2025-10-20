from web3 import Web3
import requests
import os
import time
from datetime import datetime
import sys

# Твои адреса
ADDRESSES = [
    '0x17e6D71D30d260e30BB7721C63539694aB02b036',
    '0x91dad140AF2800B2D660e530B9F42500Eee474a0',
    '0x4e7240952C21C811d9e1237a328b927685A21418',
    '0x3c2c34B9bB0b00145142FFeE68475E1AC01C92bA',
    '0x5A51f62D86F5CCB8C7470Cea2AC982762049c53c'
]

# Short names для вывода
SHORT_NAMES = {
    '0x17e6d71d30d260e30bb7721c63539694ab02b036': 'Papa Dont drink alcohol today',
    '0x91dad140af2800b2d660e530b9f42500eee474a0': '2F_MMS',
    '0x4e7240952c21c811d9e1237a328b927685a21418': '3F_NH',
    '0x3c2c34b9bb0b00145142ffee68475e1ac01c92ba': '4F_Exodus',
    '0x5a51f62d86f5ccb8c7470cea2ac982762049c53c': '5F_BNB'
}

# Telegram config (из env для GitHub Actions)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8442392037:AAEiM_b4QfdFLqbmmc1PXNvA99yxmFVLEp8')
CHAT_ID = os.environ.get('CHAT_ID', '350766421')

# AAVE V3 Pool на Arbitrum
POOL_ADDRESS = '0x794a61358D6845594F94dc1DB02A252b5b4814aD'
RPC_URL = 'https://arb1.arbitrum.io/rpc'

# ABI_POOL и ABI_ERC20 (как раньше, без изменений)
ABI_POOL = [
    # ... (вставь полный ABI_POOL из предыдущего кода, чтобы не повторять)
]

ABI_ERC20 = [
    {"inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"}
]

# Функции get_eth_price, get_token_price, send_telegram_message, get_token_details (как раньше)

def monitor_aave_positions():
    # ... (основная логика как раньше, с изменениями в status)

            # HF обработка с эмодзи
            MAX_UINT256 = 2**256 - 1
            if health_factor_raw == MAX_UINT256:
                hf_display = '∞'
                status = '🟢 Безопасно (нет долга)'
            else:
                hf_display = "{0:.2f}".format(health_factor)
                if health_factor > 1.45:
                    emoji = '🟢'
                else:
                    emoji = '🔴'
                base_status = 'РИСК ЛИКВИДАЦИИ!' if health_factor < 1 else 'Безопасно'
                status = f"{emoji} {base_status}"
                if health_factor < 1.2:
                    low_hf_warning = True

            # В print и tg_section: используй status как есть

# ... (остальной код как в предыдущей версии)

if __name__ == "__main__":
    try:
        monitor_aave_positions()
    except KeyboardInterrupt:
        print("\nОстановлено.")
        sys.exit(0)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)
