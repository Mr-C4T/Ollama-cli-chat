#!/usr/bin/env python3

import json
import urllib.request
import urllib.error

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live

console = Console()


console.print(""" 
                         -
                        .@
                        .@.
                   ...#@@@.
              ..#@@@@@@@@@
             .@@@@@..   @@.
               .+@@.    @@
                 ..@@: .@@
                   .:@@@@@.
                .@@@@:..@@=
             .@@@@@.   .@@*
             ..@@@@@   .@@%
                 .@@@@@.@@%
                    :@@@@@%.
                      .@@@@@@.
                       .@@*@@@@-
                       .@@=  .@@@@..
                       .@@.     :@@@%
                       .@@.    .@@@@.
                        @@.  *@@#.
                        @@..@@#.
                        =@   .@@.
                       ..@.    .@%
                        .@.      .@.
                         @.        .%
                         .           ..     
""", style="bold green")

HOST = "http://localhost:11434"
MODEL = "phi4-mini"

messages = []


def chat(prompt):
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": MODEL,
        "messages": messages,
        "stream": True
    }

    request = urllib.request.Request(
        f"{HOST}/api/chat",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}
    )

    answer = ""

    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            with Live(
                Markdown(""),
                console=console,
                refresh_per_second=10
            ) as live:

                for line in response:
                    if not line:
                        continue

                    chunk = json.loads(line)

                    content = chunk.get("message", {}).get("content", "")
                    answer += content

                    live.update(Markdown(answer))

    except urllib.error.URLError as e:
        console.print(f"[red]Connection error: {e}[/red]")
        messages.pop()
        return

    messages.append({"role": "assistant", "content": answer})


def main():
    global MODEL

    console.print(Panel(
        "[bold cyan]Ollama Interactive Chat[/bold cyan]\n"
        f"Model: {MODEL}\n"
        "Commands: /clear, /model NAME, exit",
        title="Local AI"
    ))

    while True:
        try:
            prompt = console.input("\n[bold green]You > [/bold green]").strip()

            if not prompt:
                continue

            if prompt.lower() in ("exit", "quit"):
                console.print("[yellow]Goodbye![/yellow]")
                break

            if prompt == "/clear":
                messages.clear()
                console.clear()
                console.print("[green]Conversation cleared.[/green]")
                continue

            if prompt.startswith("/model "):
                MODEL = prompt.split(" ", 1)[1].strip()
                messages.clear()
                console.print(f"[cyan]Model changed to {MODEL}[/cyan]")
                continue

            console.print(f"\n[bold cyan]{MODEL} >[/bold cyan]")
            chat(prompt)

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted.[/yellow]")
            break


if __name__ == "__main__":
    main()


