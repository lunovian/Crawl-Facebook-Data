from datetime import datetime
from colorama import Fore, Style, init
from tqdm import tqdm
import os

init()

class Logger:
    def __init__(self, log_file="crawler.log"):
        self.log_file = log_file
        self.progress_bars = {}
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        self.log_file = os.path.join("logs", log_file)

    def _write_log(self, level, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def info(self, message):
        print(f"{Fore.BLUE}[{datetime.now().strftime('%H:%M:%S')}] ℹ {message}{Style.RESET_ALL}")
        self._write_log("INFO", message)

    def success(self, message):
        print(f"{Fore.GREEN}[{datetime.now().strftime('%H:%M:%S')}] ✓ {message}{Style.RESET_ALL}")
        self._write_log("SUCCESS", message)

    def error(self, message):
        print(f"{Fore.RED}[{datetime.now().strftime('%H:%M:%S')}] ✗ {message}{Style.RESET_ALL}")
        self._write_log("ERROR", message)

    def warning(self, message):
        print(f"{Fore.YELLOW}[{datetime.now().strftime('%H:%M:%S')}] ⚠ {message}{Style.RESET_ALL}")
        self._write_log("WARNING", message)

    def create_progress_bar(self, name, total, desc=None):
        self.progress_bars[name] = tqdm(
            total=total,
            desc=desc or name,
            bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Style.RESET_ALL)
        )
        return self.progress_bars[name]

    def update_progress(self, name, n=1):
        if name in self.progress_bars:
            self.progress_bars[name].update(n)

    def close_progress(self, name):
        if name in self.progress_bars:
            self.progress_bars[name].close()
            del self.progress_bars[name]

    def section(self, title):
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}  {title}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}\n")
