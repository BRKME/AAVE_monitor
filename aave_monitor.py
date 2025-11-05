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
    '0x4e7240952C21C811d9e1237a328b927685a21418',
    '0x3c2c34B9bB0b00145142FFeE68475E1AC01C92bA'
]

# Short names для вывода
SHORT_NAMES = {
    '0x17e6d71d30d260e30bb7721c63539694ab02b036': '1F_MMW',
    '0x91dad140af2800b2d660e530b9f42500eee474a0': '2F_MMS',
    '0x4e7240952c21c811d9e1237a328b927685a21418': '3F_BNB',
    '0x3c2c34b9bb0b00145142ffee68475e1ac01c92ba': '4F_Exodus',
}

# Telegram config (из env для GitHub Actions)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8442392037:AAEiM_b4QfdFLqbmmc1PXNvA99yxmFVLEp8')
CHAT_ID = os.environ.get('CHAT_ID', '350766421')

# AAVE V3 Pool на Arbitrum
POOL_ADDRESS = '0x794a61358D6845594F94dc1DB02A252b5b4814aD'
RPC_URL = 'https://arb1.arbitrum.io/rpc'

# Полный ABI_POOL
ABI_POOL = [
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "getUserAccountData",
        "outputs": [
            {"internalType": "uint256", "name": "totalCollateralBase", "type": "uint256"},
            {"internalType": "uint256", "name": "totalDebtBase", "type": "uint256"},
            {"internalType": "uint256", "name": "availableBorrowsBase", "type": "uint256"},
            {"internalType": "uint256", "name": "currentLiquidationThreshold", "type": "uint256"},
            {"internalType": "uint256", "name": "ltv", "type": "uint256"},
            {"internalType": "uint256", "name": "healthFactor", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getReservesList",
        "outputs": [{"internalType": "address[]", "name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
        "name": "getUserConfigurationData",
        "outputs": [
            {"internalType": "DataTypes.UserConfigurationMap", "name": "", "type": "tuple"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "address", "name": "user", "type": "address"}
        ],
        "name": "getUserReserveData",
        "outputs": [
            {"internalType": "uint256", "name": "currentATokenBalance", "type": "uint256"},
            {"internalType": "uint256", "name": "currentStableDebt", "type": "uint256"},
            {"internalType": "uint256", "name": "currentVariableDebt", "type": "uint256"},
            {"internalType": "uint256", "name": "principalStableDebt", "type": "uint256"},
            {"internalType": "uint256", "name": "scaledVariableDebt", "type": "uint256"},
            {"internalType": "uint256", "name": "stableBorrowRate", "type": "uint256"},
            {"internalType": "uint256", "name": "liquidityRate", "type": "uint256"},
            {"internalType": "uint40", "name": "stableRateLastUpdated", "type": "uint40"},
            {"internalType": "bool", "name": "usageAsCollateralEnabled", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# ABI для ERC20
ABI_ERC20 = [
    {"inputs": [], "name": "symbol", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "decimals", "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"}
]

def get_eth_price():
    """Цена ETH в USD"""
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd', timeout=10)
        response.raise_for_status()
        return response.json()['ethereum']['usd']
    except Exception as e:
        print(f"Ошибка цены ETH: {e}")
        return None

def get_token_price(symbol):
    """Цена токена в USD"""
    if not symbol or symbol == 'ETH':
        return get_eth_price()
    try:
        response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd', timeout=10)
        response.raise_for_status()
        data = response.json()
        return list(data.values())[0]['usd'] if data else None
    except Exception as e:
        print(f"Ошибка цены {symbol}: {e}")
        return None

def send_telegram_message(message):
    """Отправка в TG"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
        print("TG-отчёт отправлен.")
    except Exception as e:
        print(f"TG ошибка: {e}")

def get_token_details(w3, reserve_address):
    """Детали токена: symbol, decimals"""
    try:
        erc20 = w3.eth.contract(address=Web3.to_checksum_address(reserve_address), abi=ABI_ERC20)
        symbol = erc20.functions.symbol().call()
        decimals = erc20.functions.decimals().call()
        return symbol, decimals
    except Exception as e:
        print(f"Ошибка деталей токена: {e}")
        return 'UNKNOWN', 18

def get_hf_status(health_factor):
    """Определяет эмодзи и статус для Health Factor"""
    if health_factor < 1.3:
        return '🔴', 'Опасно'
    elif health_factor < 1.45:
        return '🟡', 'Нейтрально'
    else:
        return '🟢', 'Безопасно'

def monitor_aave_positions():
    """Основной мониторинг"""
    print("Запуск мониторинга...")  # Debug для Actions
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Ошибка RPC.")
        return None
    
    pool = w3.eth.contract(address=Web3.to_checksum_address(POOL_ADDRESS), abi=ABI_POOL)
    reserves_list = pool.functions.getReservesList().call()
    
    eth_price = get_eth_price()
    
    # Новый заголовок с датой
    now = datetime.now()
    days_ru = {
        'Monday': 'понедельник',
        'Tuesday': 'вторник',
        'Wednesday': 'среда',
        'Thursday': 'четверг',
        'Friday': 'пятница',
        'Saturday': 'суббота',
        'Sunday': 'воскресенье'
    }
    months_ru = {
        1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля',
        5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
        9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'
    }
    
    day_name = days_ru.get(now.strftime('%A'), 'день')
    day_num = now.day
    month_name = months_ru.get(now.month, '')
    week_num = now.isocalendar()[1]
    
    header = f"#Крипта #AAVE\n{day_name.capitalize()} {day_num} {month_name}, неделя {week_num}"
    
    report = f"<b>{header}</b>\n\n"
    console_report = f"\n=== {header} ===\n"
    
    low_hf_warning = False
    
    for addr in ADDRESSES:
        short_name = SHORT_NAMES.get(addr.lower(), addr[:8] + '...')
        console_name = short_name
        tg_name = short_name
        
        try:
            # Общие метрики (всегда работают)
            result = pool.functions.getUserAccountData(Web3.to_checksum_address(addr)).call()
            total_collateral_base = result[0] / 1e8
            total_debt_base = result[1] / 1e8
            available_borrows_base = result[2] / 1e8
            liq_threshold = result[3] / 1e4
            ltv = result[4] / 1e4
            health_factor_raw = result[5]
            health_factor = health_factor_raw / 1e18
            
            # HF обработка с эмодзи и статусом
            MAX_UINT256 = 2**256 - 1
            if health_factor_raw == MAX_UINT256:
                hf_display = '∞'
                emoji = '🟢'
                status = 'Безопасно (нет долга)'
            else:
                hf_display = "{0:.2f}".format(health_factor)
                emoji, status = get_hf_status(health_factor)
                
                if health_factor < 1.3:
                    low_hf_warning = True
            
            console_section = f"\n--- {console_name} ---\n"
            console_section += f"{emoji} Health Factor: {hf_display} ({status})\n"
            console_section += f"Коллатерал: ${total_collateral_base:,.0f} USD\n"
            console_section += f"Долг: ${total_debt_base:,.0f} USD\n"
            
            tg_section = f"<b>{tg_name}</b>\n"
            tg_section += f"{emoji} HF: <code>{hf_display}</code> ({status})\n"
            tg_section += f"Коллатерал: <code>${total_collateral_base:,.0f}</code>\n"
            tg_section += f"Долг: <code>${total_debt_base:,.0f}</code>\n"
            
            # Детали токенов: только если есть активность
            active_reserves = []
            details_console = ""
            details_tg = ""
            if total_collateral_base > 0 or total_debt_base > 0:
                try:
                    user_config = pool.functions.getUserConfigurationData(Web3.to_checksum_address(addr)).call()
                    config_map = user_config[0]  # uint256 bitmask
                    
                    for i, reserve_addr in enumerate(reserves_list):
                        if (config_map & (1 << i)) != 0:  # Активен
                            try:
                                user_reserve = pool.functions.getUserReserveData(reserve_addr, Web3.to_checksum_address(addr)).call()
                                a_balance = user_reserve[0]
                                stable_debt = user_reserve[1]
                                variable_debt = user_reserve[2]
                                if a_balance > 0 or stable_debt > 0 or variable_debt > 0:
                                    symbol, decimals = get_token_details(w3, reserve_addr)
                                    price = get_token_price(symbol)
                                    bal = a_balance / (10 ** decimals)
                                    debt = (stable_debt + variable_debt) / (10 ** decimals)
                                    a_usd = bal * price if price else 0
                                    d_usd = debt * price if price else 0
                                    active_reserves.append((symbol, bal, debt, a_usd, d_usd))
                            except Exception:
                                pass  # Skip bad reserve
                except Exception as config_e:
                    pass
                
                # Сортировка и вывод топ-5
                if active_reserves:
                    active_reserves.sort(key=lambda x: x[3], reverse=True)
                    details_console = "Детали активов:\n"
                    details_tg = "Активы:\n"
                    for sym, bal, debt, a_usd, d_usd in active_reserves[:5]:
                        details_console += f"  - {sym}: Баланс {bal:.0f} (${a_usd:.0f}), Долг {debt:.0f} (${d_usd:.0f})\n"
                        details_tg += f"• <code>{sym}</code>: {bal:.0f} (${a_usd:.0f}) | Долг: {debt:.0f} (${d_usd:.0f})\n"
            
            # Добавляем детали только если они есть
            if details_console or details_tg:
                console_section += details_console
                tg_section += details_tg
            
            console_report += console_section
            report += tg_section + "\n"
            
        except Exception as e:
            error_msg = "Общая ошибка: {0}".format(e)
            console_report += f"\n--- {console_name} ---\n{error_msg}\n"
            report += f"<b>{tg_name}</b>: {error_msg}\n\n"
    
    console_report += "\n"
    
    print(console_report)
    
    # TG отправка
    if low_hf_warning:
        report = "🚨 <b>ВНИМАНИЕ: Опасный HF у некоторых позиций!</b>\n\n" + report
    send_telegram_message(report)
    
    return console_report

# Запуск
if __name__ == "__main__":
    try:
        monitor_aave_positions()
    except KeyboardInterrupt:
        print("\nОстановлено.")
        sys.exit(0)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)
