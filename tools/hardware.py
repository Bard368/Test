import psutil
import datetime
import subprocess
import platform
import socket
from core.logger import logger

# --- WINDOWS HELPERS ---
def get_windows_wmi_data(command: str) -> list:
    try:
        cmd = f'powershell -NoProfile -Command "{command}"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    except:
        return []

def get_windows_temperature() -> str:
    output = get_windows_wmi_data("Get-WmiObject MSAcpi_ThermalZoneTemperature -Namespace 'root/wmi' | Select-Object -ExpandProperty CurrentTemperature")
    temps = [round((int(val) / 10) - 273.15, 1) for val in output if val.isdigit() and 0 < ((int(val) / 10) - 273.15) < 120]
    return f"\n🔥 Макс. температура (ACPI): {max(temps)}°C" if temps else "\n🔥 Температура: Прихована на рівні драйверів (OEM)"

# --- MACOS HELPERS ---
def get_mac_cpu_name() -> str:
    try:
        # Утиліта sysctl віддає точну назву процесора на Mac (напр., Apple M2 Pro)
        res = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], capture_output=True, text=True)
        return res.stdout.strip() if res.stdout else platform.processor()
    except:
        return platform.processor()

def get_mac_gpu_name() -> str:
    try:
        # system_profiler сканує апаратне забезпечення Mac
        res = subprocess.run(['system_profiler', 'SPDisplaysDataType'], capture_output=True, text=True)
        gpus = [line.split(":")[1].strip() for line in res.stdout.split('\n') if "Chipset Model:" in line or "Renderer:" in line]
        return "\n".join([f"  - {gpu}" for gpu in gpus]) if gpus else "  - GPU не визначено"
    except:
        return "  - GPU не визначено"

# --- MAIN SCANNER ---
async def get_system_status() -> str:
    """Кросплатформне глибоке сканування апаратного забезпечення (Windows, macOS, Linux)."""
    logger.info("[bold cyan]💻 Запуск кросплатформного апаратного сканування...[/bold cyan]")
    
    try:
        current_os = platform.system()
        os_info = f"{current_os} {platform.release()} ({platform.architecture()[0]})"
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
        except:
            local_ip = "Невідомо"

        # 1. Процесор (CPU)
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_cores_phys = psutil.cpu_count(logical=False)
        cpu_cores_log = psutil.cpu_count(logical=True)
        
        # Визначаємо назву CPU залежно від ОС
        if current_os == "Windows":
            cpu_names = get_windows_wmi_data("Get-WmiObject Win32_Processor | Select-Object -ExpandProperty Name")
            cpu_name = cpu_names[0] if cpu_names else platform.processor()
        elif current_os == "Darwin": # Darwin = macOS
            cpu_name = get_mac_cpu_name()
        else:
            cpu_name = platform.processor()

        # 2. Відеокарта (GPU)
        if current_os == "Windows":
            gpu_names = get_windows_wmi_data("Get-WmiObject Win32_VideoController | Select-Object -ExpandProperty Name")
            gpu_info = "\n".join([f"  - {gpu}" for gpu in gpu_names]) if gpu_names else "  - Інтегрована або не знайдена"
        elif current_os == "Darwin":
            gpu_info = get_mac_gpu_name()
        else:
            gpu_info = "  - Сканування GPU підтримується лише для Windows та macOS"

        # 3. Оперативна пам'ять
        memory = psutil.virtual_memory()
        ram_total = round(memory.total / (1024**3), 2)
        ram_used = round(memory.used / (1024**3), 2)

        # 4. Диски
        disks_info = ""
        for partition in psutil.disk_partitions():
            if 'cdrom' in partition.opts or partition.fstype == '':
                continue
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                free = round(usage.free / (1024**3), 2)
                total = round(usage.total / (1024**3), 2)
                disks_info += f"\n  - Диск {partition.mountpoint}: Вільно {free} ГБ з {total} ГБ"
            except PermissionError:
                continue

        # 5. Батарея
        battery_info = ""
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                plugged = "🔌 Мережа" if battery.power_plugged else "🔋 Батарея"
                battery_info = f"\n🔋 Живлення: {battery.percent}% ({plugged})"

        # 6. Аптайм та Температура
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
        
        temp_info = ""
        if current_os == "Windows":
            temp_info = get_windows_temperature()
        elif current_os == "Darwin":
            temp_info = "\n🔥 Температура: Apple Silicon приховує датчики (потрібні права sudo powermetrics)"

        # Формуємо звіт
        report = (
            f"Глибокий аналіз системи ({hostname}):\n"
            f"🖥️ ОС: {os_info} | Локальний IP: {local_ip}\n"
            f"⏱️ Аптайм: {uptime.days} дн. {int(uptime.total_seconds() // 3600) % 24} год.\n\n"
            f"🧠 Процесор (CPU):\n  - Модель: {cpu_name}\n  - Ядра: {cpu_cores_phys} фіз. / {cpu_cores_log} лог.\n  - Завантаження: {cpu_percent}%\n\n"
            f"🎮 Відеокарта (GPU):\n{gpu_info}\n\n"
            f"💾 RAM: {ram_used} ГБ / {ram_total} ГБ ({memory.percent}%)\n"
            f"💽 Накопичувачі:{disks_info}"
            f"{battery_info}"
            f"{temp_info}"
        )
        return report

    except Exception as e:
        logger.error(f"[bold red]❌ Помилка зчитування системи:[/bold red] {str(e)}")
        return "Не вдалося отримати детальні дані про систему."