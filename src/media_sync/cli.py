"""CLI entry point for media-sync."""

import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(package_name="media-sync")
def main():
    """Media Sync - synchronize metadata between media servers and Obsidian."""
    pass


@main.command()
def healthcheck():
    """Test connectivity to all configured services."""
    console.print("[yellow]Healthcheck not implemented yet[/yellow]")
    console.print("This will test Jellyfin, Sonarr, Radarr, and Obsidian connections.")
    sys.exit(0)


@main.command()
@click.option("--dry-run", is_flag=True, help="Show what would be changed without writing files")
@click.option("--source", type=click.Choice(["jellyfin", "sonarr", "radarr", "all"]), default="all", help="Which source to sync")
def sync(dry_run: bool, source: str):
    """Synchronize media libraries to Obsidian vault."""
    try:
        from media_sync.config_loader import ConfigLoader
        from media_sync.sync import SyncEngine

        console.print("[cyan]Loading configuration...[/cyan]")
        loader = ConfigLoader()
        engine = SyncEngine(loader)

        console.print(f"[cyan]Starting synchronization from {source}...[/cyan]")
        if dry_run:
            console.print("[yellow]DRY RUN mode - no files will be written[/yellow]")

        with console.status("[bold green]Processing media items..."):
            if source == "jellyfin":
                stats = engine.sync_jellyfin(dry_run=dry_run)
            elif source == "sonarr":
                stats = engine.sync_sonarr(dry_run=dry_run)
            elif source == "radarr":
                stats = engine.sync_radarr(dry_run=dry_run)
            else:  # all
                stats = engine.sync_all(dry_run=dry_run)

        console.print("[bold green]✓ Sync completed[/bold green]")
        if source == "all":
            for src_name, src_stats in stats.items():
                if src_stats:
                    console.print(f"[cyan]{src_name.capitalize()}[/cyan]: Movies {src_stats.get('movies',0)}, Series {src_stats.get('series',0)}")
                    console.print(f" Created: {src_stats.get('created',0)}, Skipped: {src_stats.get('skipped',0)}, Errors: {src_stats.get('errors',0)}")
        else:
            console.print(f"Movies: {stats.get('movies',0)}, Series: {stats.get('series',0)}")
            console.print(f"Created: {stats.get('created',0)}, Skipped: {stats.get('skipped',0)}, Errors: {stats.get('errors',0)}")
        if dry_run:
            console.print("[yellow]This was a dry run. No files were modified.[/yellow]")
    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        console.print("Please run [cyan]media-sync config-init[/cyan] and edit the config file.")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        raise click.Abort()


@main.command()
def config_init():
    """Initialize configuration file."""
    config_path = Path.home() / ".config" / "media-sync" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        console.print(f"[yellow]Config already exists: {config_path}[/yellow]")
        return
    config_path.write_text(
        """jellyfin:
  url: "http://localhost:8096"
  api_key: "YOUR_JELLYFIN_API_KEY"

obsidian:
  vault_path: "/path/to/your/vault"
  template: "templates/media_note.md"

# Uncomment and configure if you use Sonarr/Radarr
# sonarr:
#   url: "http://localhost:8989"
#   api_key: "YOUR_SONARR_API_KEY"
#
# radarr:
#   url: "http://localhost:7878"
#   api_key: "YOUR_RADARR_API_KEY"
"""
    )
    console.print(f"[green]Created config at {config_path}[/green]")
    console.print("Please edit it with your actual credentials.")


if __name__ == "__main__":
    main()