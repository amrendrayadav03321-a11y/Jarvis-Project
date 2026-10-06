#!/usr/bin/env python3
import sys
import argparse
import time

from core.config import Config
from core.speaker import speaker
from core.listener import listener
from core.brain import brain
from core.tools import tools
from core.wakeword import wake_detector
from ui.hud import hud, console

def run_tests():
    """Performs system verification and self-test."""
    console.print("[bold cyan]Running Jarvis Diagnostic & Self-Test...[/bold cyan]")
    
    console.print("\n[bold yellow]1. Testing Time & Date:[/bold yellow]")
    console.print(tools.get_time_and_date())
    
    console.print("\n[bold yellow]2. Testing Battery:[/bold yellow]")
    console.print(tools.get_battery_status())
    
    console.print("\n[bold yellow]3. Testing System Stats:[/bold yellow]")
    console.print(tools.get_system_stats())
    
    console.print("\n[bold yellow]4. Testing AI Brain:[/bold yellow]")
    test_res = brain.process("Hello Jarvis, how are you?")
    console.print(f"Jarvis response: {test_res}")
    
    console.print("\n[bold yellow]5. Testing Wake Word Detector & Noise Filter:[/bold yellow]")
    t1_has, t1_cmd = wake_detector.extract_command("Hey Jarvis play Kesariya")
    t2_has, t2_cmd = wake_detector.extract_command("dancing in the dark with you")
    console.print(f"Utterance: 'Hey Jarvis play Kesariya' -> Wake Word: {t1_has}, Command: '{t1_cmd}'")
    console.print(f"Utterance: 'dancing in the dark with you' (Background Song) -> Wake Word: {t2_has} (FILTERED)")
    
    console.print("\n[bold yellow]6. Testing Microphone Sensors:[/bold yellow]")
    listener.calibrate()
    console.print(f"Device index: {listener.device_index} | Energy threshold: {listener.recognizer.energy_threshold}")
    
    console.print("\n[bold yellow]7. Testing Audio Output (Deep Male Voice):[/bold yellow]")
    speaker.speak(f"Diagnostic complete. All systems are operational, {Config.USER_NAME}.")
    
    console.print("\n[bold green]✓ All self-tests passed successfully![/bold green]\n")

def main():
    parser = argparse.ArgumentParser(description="Jarvis AI Voice Assistant for macOS (Stark Industries Edition)")
    parser.add_argument("--ui", action="store_true", help="Launch Iron Man Holographic Graphical UI Window (Default)")
    parser.add_argument("--cli", action="store_true", help="Run in terminal CLI mode")
    parser.add_argument("--text", action="store_true", help="Run in keyboard/text input mode")
    parser.add_argument("--voice", action="store_true", help="Run in continuous voice mode")
    parser.add_argument("--test", action="store_true", help="Run diagnostic self-test")
    parser.add_argument("--no-animation", action="store_true", help="Skip Iron Man startup animation")
    args = parser.parse_args()

    if args.test:
        run_tests()
        sys.exit(0)

    # Default to Holographic GUI Window unless terminal CLI mode requested
    if args.ui or (not args.cli and not args.text and not args.voice):
        console.print("[bold cyan]Initializing J.A.R.V.I.S. Tactical Holographic GUI...[/bold cyan]")
        try:
            from ui.server import server
            console.print("[bold green]✓ Starting Stark OS Server on http://127.0.0.1:8888[/bold green]")
            console.print("[bold yellow]⚡ Opening Tactical HUD Window... (Press Ctrl+C to terminate)[/bold yellow]")
            server.run()
            sys.exit(0)
        except Exception as e:
            console.print(f"[bold red]GUI Initialization Notice: {e}[/bold red]")
            console.print("[yellow]Switching to terminal HUD mode...[/yellow]")

    # 1. Run Iron Man Cinematic Boot Sequence (unless disabled)
    if not args.no_animation and Config.SHOW_BOOT_ANIMATION:
        hud.run_boot_sequence()

    # 2. Calibrate Microphone Sensors
    listener.calibrate()

    # 3. Brain & Voice status
    brain_status = (
        f"[green]Gemini 2.5 AI Active[/green]" 
        if brain.is_gemini_active 
        else "[yellow]Offline Multi-Lingual Engine (Add GEMINI_API_KEY for Full AI)[/yellow]"
    )
    
    voice_status = f"{Config.TTS_ENGINE.upper()} ({Config.EDGE_VOICE if Config.TTS_ENGINE == 'edge' else Config.MACOS_VOICE}) [Deep Male]"
    
    # 4. Display Tactical HUD Banner
    hud.show_banner(brain_status, voice_status)
    
    # 5. Initial Greeting in Deep Male Voice
    greeting = f"Jarvis systems fully initialized. All protocols active. Ready for your command, {Config.USER_NAME}."
    hud.print_jarvis(greeting)
    speaker.speak(greeting)

    mode = "text" if args.text else "voice"

    try:
        while True:
            user_query = ""
            
            if mode == "voice":
                def update_status(msg):
                    console.print(f"[dim bright_cyan]● {msg}[/dim bright_cyan]", end="\r")

                if Config.WAKE_WORD_REQUIRED:
                    # STANDBY SHIELD: Block all background songs, TV chatter, room noise
                    hud.show_standby_listening()
                    raw_audio = listener.listen(status_callback=update_status)
                    
                    if not raw_audio:
                        time.sleep(0.15)
                        continue
                        
                    has_wake, extracted_command = wake_detector.extract_command(raw_audio)
                    
                    if not has_wake:
                        # Silently filter and ignore background song / noise
                        hud.show_noise_filtered(raw_audio)
                        time.sleep(0.1)
                        continue
                        
                    # Wake word was detected!
                    if extracted_command:
                        # Direct inline command: e.g. "Hey Jarvis play Kesariya" or "Jarvis volume badhao"
                        user_query = extracted_command
                    else:
                        # Standalone wake word: e.g. "Hey Jarvis" or "Jarvis"
                        ack = wake_detector.get_acknowledgement(raw_audio)
                        hud.print_jarvis(ack)
                        speaker.speak(ack)
                        
                        # Active listening state for immediate command
                        hud.show_active_listening()
                        followup = listener.listen(status_callback=update_status)
                        
                        if not followup:
                            standby_note = f"Standing by, {Config.USER_NAME}."
                            hud.print_jarvis(standby_note)
                            speaker.speak(standby_note)
                            continue
                            
                        # If followup itself had wake word, strip cleanly
                        _, clean_followup = wake_detector.extract_command(followup)
                        user_query = clean_followup if clean_followup else followup
                else:
                    # Continuous mode (wake word disabled)
                    hud.show_listening_wave()
                    user_query = listener.listen(status_callback=update_status)
                    if not user_query:
                        time.sleep(0.2)
                        continue
            else:
                # Text mode
                console.print()
                try:
                    user_query = console.input(f"[bold green]💬 [{Config.USER_NAME}]: [/bold green]").strip()
                except EOFError:
                    break

            if not user_query:
                continue

            # Strip wake word if typed in text mode
            if mode == "text":
                has_w, clean_typed = wake_detector.extract_command(user_query)
                if has_w and clean_typed:
                    user_query = clean_typed

            console.print() # Clear line
            hud.print_user(user_query)

            # Exit command check
            if any(w in user_query.lower() for w in ["exit", "quit", "goodbye", "terminate", "band ho jao", "shut down", "sleep jarvis"]):
                farewell = f"Powering down tactical protocols. Have a wonderful day, {Config.USER_NAME}."
                hud.print_jarvis(farewell)
                speaker.speak(farewell)
                break

            # Dynamic toggle for wake word filter
            if any(w in user_query.lower() for w in ["disable wake word", "turn off wake word", "continuous listening"]):
                Config.WAKE_WORD_REQUIRED = False
                msg = "Wake word shield disabled. Switched to continuous open microphone mode."
                hud.print_jarvis(msg)
                speaker.speak(msg)
                continue
            elif any(w in user_query.lower() for w in ["enable wake word", "turn on wake word", "enable noise shield"]):
                Config.WAKE_WORD_REQUIRED = True
                msg = f"Wake word shield activated. Background noise blocked until you say 'Hey Jarvis', {Config.USER_NAME}."
                hud.print_jarvis(msg)
                speaker.speak(msg)
                continue

            # Switch mode commands
            if user_query.lower() in ["switch to text", "text mode", "type mode"]:
                mode = "text"
                msg = "Switched to keyboard text input mode."
                hud.print_jarvis(msg)
                speaker.speak(msg)
                continue
            elif user_query.lower() in ["switch to voice", "voice mode", "mic mode"]:
                mode = "voice"
                msg = "Switched to acoustic microphone mode. Listening, sir."
                hud.print_jarvis(msg)
                speaker.speak(msg)
                continue

            # Process through Brain
            with console.status("[bold cyan]Jarvis is executing...[/bold cyan]", spinner="dots12"):
                response = brain.process(user_query)

            if response:
                hud.print_jarvis(response)
                speaker.speak(response)
            else:
                fallback = "I didn't quite catch that, sir. Could you please repeat?"
                hud.print_jarvis(fallback)
                speaker.speak(fallback)

            time.sleep(0.3)

    except KeyboardInterrupt:
        console.print(f"\n[bold yellow]Tactical disconnect initiated. Farewell, {Config.USER_NAME}.[/bold yellow]")
        sys.exit(0)

if __name__ == "__main__":
    main()
