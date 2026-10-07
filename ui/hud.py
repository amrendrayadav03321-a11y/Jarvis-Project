import time
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import box
from core.config import Config

console = Console()

ARC_REACTOR_FRAMES = [
r"""
             .---''''---.
           .'    \  /    '.
          /       \/       \
         |   <---(●)--->   |
          \       /\       /
           '.    /  \    .'
             '---....---'
""",
r"""
             .---''''---.
           .'     ||     '.
          /    \  ||  /    \
         |   ===( ◈ )===   |
          \    /  ||  \    /
           '.     ||     .'
             '---....---'
""",
r"""
             .---''''---.
           .'    //\\    '.
          /     //  \\     \
         |   --- (◎) ---   |
          \     \\  //     /
           '.    \\//    .'
             '---....---'
"""
]

JARVIS_HEADER = r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
    [ STARK INDUSTRIES - MARK 85 AI ASSISTANT ]
    [ DESIGN AND BUILT BY SATYAA YADAV ]
"""

class JarvisHUD:
    @staticmethod
    def play_boot_sound():
        """Plays triumphant power-up sound."""
        try:
            subprocess.Popen(["afplay", "/System/Library/Sounds/Hero.aiff"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    @staticmethod
    def run_boot_sequence():
        """Cinematic Iron Man Mark-style terminal boot animation."""
        if not Config.SHOW_BOOT_ANIMATION:
            return

        console.clear()
        
        # Audio power-up
        JarvisHUD.play_boot_sound()
        
        # Typewriter intro
        intro = Text("STARK INDUSTRIES PROTOCOL INITIALIZATION...\nSYSTEM: MARK LXXXV OS (v9.4-APPLE_SILICON)", style="bold bright_cyan")
        console.print(intro)
        time.sleep(0.3)
        
        # Reactor animation frames
        for frame in ARC_REACTOR_FRAMES:
            console.clear()
            console.print(Text("INITIALIZING ARC REACTOR CORE...", style="bold yellow"), justify="center")
            console.print(Text(frame, style="bold cyan"), justify="center")
            time.sleep(0.18)

        # High-tech loading bars
        with Progress(
            SpinnerColumn(spinner_name="dots12", style="bold bright_cyan"),
            TextColumn("[bold bright_white]{task.description}"),
            BarColumn(bar_width=40, style="blue", complete_style="bold bright_cyan"),
            TextColumn("[bold green]{task.percentage:>3.0f}%"),
            console=console,
            transient=True
        ) as progress:
            t1 = progress.add_task("[cyan]Booting Neural Language Core...", total=100)
            t2 = progress.add_task("[yellow]Calibrating Acoustic Sensors & Mic...", total=100)
            t3 = progress.add_task("[bright_blue]Linking macOS Automation Subsystems...", total=100)

            while not progress.finished:
                progress.update(t1, advance=25)
                progress.update(t2, advance=30)
                progress.update(t3, advance=35)
                time.sleep(0.08)

        console.clear()

    @staticmethod
    def show_banner(brain_status: str, voice_status: str):
        console.clear()
        
        banner_text = Text(JARVIS_HEADER, style="bold cyan")
        console.print(banner_text, justify="center")
        
        # Holographic HUD Table
        table = Table(box=box.HEAVY_EDGE, show_header=False, expand=True, border_style="bright_cyan")
        table.add_column("Telemetry", style="bold yellow", width=22)
        table.add_column("Diagnostics", style="bold white")
        
        table.add_row("⚡ REACTOR CORE", "[bold green]100% OPTIMAL (ARM64 HIGH-PERFORMANCE)[/bold green]")
        table.add_row("🤖 ASSISTANT", f"[bold bright_cyan]{Config.ASSISTANT_NAME}[/bold bright_cyan] (Voice of Stark Industries)")
        table.add_row("👤 PROTOCOL USER", f"[bold bright_white]{Config.USER_NAME}[/bold bright_white]")
        table.add_row("🛡️ NOISE FILTER SHIELD", "[bold green]ACTIVE (Ignoring background music/songs until 'Hey Jarvis')[/bold green]" if Config.WAKE_WORD_REQUIRED else "[yellow]OFF (Continuous Listening)[/yellow]")
        table.add_row("🧠 AI INTELLIGENCE", brain_status)
        table.add_row("🔊 ACOUSTIC OUTPUT", voice_status)
        table.add_row("🎙️ MICROPHONE SENSORS", "[bold green]ACTIVE (Auto-Calibrated & Clamped)[/bold green]")
        table.add_row("💡 ACTIVATION EXAMPLES", "'Hey Jarvis play Kesariya', 'Jarvis what time is it', 'जार्विस यूट्यूब खोलो', 'Who developed you'")
        
        panel = Panel(
            table,
            title="[bold yellow]⚡ J.A.R.V.I.S TACTICAL HUD ⚡[/bold yellow]",
            subtitle="[italic bright_black]Say 'exit', 'bye', or press Ctrl+C to terminate[/italic bright_black]",
            border_style="bright_cyan"
        )
        console.print(panel)
        console.print()

    @staticmethod
    def show_standby_listening():
        """Shows standby listening state awaiting wake word."""
        console.print(
            "\n[dim bright_cyan]🛡️  STANDBY SHIELD[/dim bright_cyan] "
            "[bold cyan]ılı.lıllılı.ıllı.[/bold cyan] "
            f"[dim italic white]Background noise blocked. Say '[bold yellow]Hey Jarvis[/bold yellow]' or '[bold yellow]Jarvis[/bold yellow]'...[/dim italic white]",
            end="\r"
        )

    @staticmethod
    def show_active_listening():
        """Shows active listening state after wake word has been acknowledged."""
        console.print(
            "\n[bold bright_green]⚡ PROTOCOL ENGAGED[/bold bright_green] "
            "[bold green]ılı.lıllılı.ıllı.[/bold green] "
            f"[bold white]Listening for your command, {Config.USER_NAME}...[/bold white]",
            end="\r"
        )

    @staticmethod
    def show_noise_filtered(text: str):
        """Discretely informs user that ambient chatter/song was filtered out."""
        cleaned = text.strip()[:40]
        console.print(f"[dim grey50]● [Ambient song/noise filtered: '{cleaned}...'][/dim grey50]", end="\r")

    @staticmethod
    def show_listening_wave():
        """Shows dynamic acoustic wave visualization while listening."""
        console.print(
            "\n[bold bright_cyan]🎙️  LISTENING[/bold bright_cyan] "
            "[bold green]ılı.lıllılı.ıllı.[/bold green] "
            "[italic bright_white]Speak your command now (or press Enter to type)...[/italic bright_white]",
            end="\r"
        )

    @staticmethod
    def print_user(text: str):
        panel = Panel(
            Text(text, style="bold bright_white"),
            title="[bold green]👤 COMMAND RECEIVED[/bold green]",
            border_style="green",
            box=box.ROUNDED
        )
        console.print(panel)

    @staticmethod
    def print_jarvis(text: str):
        panel = Panel(
            Text(text, style="bold bright_cyan"),
            title=f"[bold bright_cyan]🤖 {Config.ASSISTANT_NAME}[/bold bright_cyan]",
            border_style="bright_cyan",
            box=box.ROUNDED
        )
        console.print(panel)

hud = JarvisHUD()
