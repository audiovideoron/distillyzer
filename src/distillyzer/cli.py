"""Distillyzer CLI - Personal learning accelerator."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from . import db, harvest as harv, transcribe, embed, query as q

app = typer.Typer(help="Distillyzer - Harvest knowledge, query it, use it.")
console = Console()


@app.command()
def search(query: str, limit: int = 10):
    """Search YouTube for videos on a topic."""
    console.print(f"[yellow]Searching YouTube for:[/yellow] {query}\n")

    try:
        videos = harv.search_youtube(query, limit=limit)
        if not videos:
            console.print("[dim]No results found[/dim]")
            return

        table = Table(show_header=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="cyan", no_wrap=False)
        table.add_column("Channel", style="green")
        table.add_column("Duration", style="yellow", justify="right")

        for i, video in enumerate(videos, 1):
            duration = video.get("duration")
            if duration:
                duration = int(duration)
                duration_str = f"{duration // 60}:{duration % 60:02d}"
            else:
                duration_str = "?"
            table.add_row(
                str(i),
                video["title"][:60] + ("..." if len(video.get("title", "")) > 60 else ""),
                video.get("channel", "?")[:20],
                duration_str,
            )

        console.print(table)
        console.print("\n[dim]To harvest a video:[/dim] dz harvest <url>")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def harvest(
    url: str,
    skip_transcribe: bool = typer.Option(False, "--skip-transcribe", help="Skip transcription"),
):
    """Harvest a YouTube video or GitHub repo."""
    console.print(f"[yellow]Harvesting:[/yellow] {url}\n")

    try:
        # Detect URL type
        if "github.com" in url:
            # GitHub repo
            console.print("[cyan]Detected GitHub repo[/cyan]")
            result = harv.harvest_repo(url)

            if result["status"] == "already_exists":
                console.print(f"[yellow]Already harvested:[/yellow] {result['name']}")
                return

            console.print(f"[green]Cloned:[/green] {result['name']}")
            console.print(f"[green]Files indexed:[/green] {result['files_indexed']}")

            # TODO: Embed code files
            console.print("[dim]Code embedding not yet implemented[/dim]")

        elif "youtube.com" in url or "youtu.be" in url:
            # YouTube video
            console.print("[cyan]Detected YouTube video[/cyan]")
            result = harv.harvest_video(url)

            if result["status"] == "already_exists":
                console.print(f"[yellow]Already harvested:[/yellow] {result['title']}")
                return

            console.print(f"[green]Downloaded:[/green] {result['title']}")
            console.print(f"[dim]Channel:[/dim] {result['channel']}")
            dur = int(result['duration']) if result.get('duration') else 0
            console.print(f"[dim]Duration:[/dim] {dur // 60}:{dur % 60:02d}")

            if not skip_transcribe:
                console.print("\n[yellow]Transcribing...[/yellow]")
                transcript = transcribe.transcribe_audio(result["audio_path"])
                console.print(f"[green]Transcribed:[/green] {len(transcript['text'])} characters")

                # Convert to timed chunks and embed
                console.print("[yellow]Embedding...[/yellow]")
                timed_chunks = transcribe.segments_to_timed_chunks(transcript["segments"])
                num_chunks = embed.embed_transcript_chunks(result["item_id"], timed_chunks)
                console.print(f"[green]Stored:[/green] {num_chunks} chunks")

                # Cleanup audio file
                Path(result["audio_path"]).unlink(missing_ok=True)
        else:
            console.print("[red]Unknown URL type.[/red] Supported: YouTube, GitHub")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise


@app.command("harvest-channel")
def harvest_channel(
    channel_url: str,
    limit: int = typer.Option(10, "--limit", "-l", help="Max videos to list"),
):
    """List videos from a YouTube channel (for selective harvesting)."""
    console.print(f"[yellow]Fetching channel videos:[/yellow] {channel_url}\n")

    try:
        videos = harv.harvest_channel(channel_url, limit=limit)

        table = Table(show_header=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="cyan")
        table.add_column("URL", style="dim")

        for i, video in enumerate(videos, 1):
            table.add_row(str(i), video["title"][:50], video["url"])

        console.print(table)
        console.print("\n[dim]To harvest a video:[/dim] dz harvest <url>")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def query(
    question: str,
    sources: int = typer.Option(5, "--sources", "-s", help="Number of sources to retrieve"),
):
    """Query your knowledge base."""
    console.print(f"[yellow]Querying:[/yellow] {question}\n")

    try:
        result = q.ask(question, num_sources=sources)

        # Display answer
        console.print(Panel(Markdown(result["answer"]), title="Answer", border_style="green"))

        # Display sources
        if result["sources"]:
            console.print("\n[dim]Sources:[/dim]")
            for i, src in enumerate(result["sources"], 1):
                title = src["item_title"][:50]
                ts = q.format_timestamp(src.get("timestamp_start"))
                ts_str = f" @ {ts}" if ts else ""
                sim = f"{src['similarity']:.2f}"
                console.print(f"  {i}. [cyan]{title}[/cyan]{ts_str} [dim](sim: {sim})[/dim]")

        console.print(f"\n[dim]Tokens used: {result['tokens_used']}[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def chat():
    """Interactive chat with your knowledge base."""
    console.print("[yellow]Starting chat...[/yellow]")
    console.print("[dim]Type 'quit' or 'exit' to end. Press Ctrl+C to cancel.[/dim]\n")

    history = []

    try:
        while True:
            question = console.input("[bold blue]You:[/bold blue] ")

            if question.lower() in ("quit", "exit", "q"):
                console.print("[yellow]Goodbye![/yellow]")
                break

            if not question.strip():
                continue

            result = q.chat_turn(question, history, num_sources=5)

            # Display answer
            console.print(f"\n[bold green]Assistant:[/bold green] {result['answer']}\n")

            # Update history
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": result["answer"]})

            # Keep history manageable
            if len(history) > 20:
                history = history[-20:]

    except KeyboardInterrupt:
        console.print("\n[yellow]Chat ended.[/yellow]")


@app.command()
def stats():
    """Show statistics about your knowledge base."""
    console.print("[yellow]Knowledge base stats[/yellow]\n")

    try:
        s = db.get_stats()
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green", justify="right")

        table.add_row("Sources (channels, repos)", str(s["sources"]))
        table.add_row("Items (videos, files)", str(s["items"]))
        table.add_row("Chunks (searchable)", str(s["chunks"]))

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    app()
