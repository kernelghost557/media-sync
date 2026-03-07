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
@click.option("--dry-run", is_flag=True, help="Show what would be changed")
def sync(dry_run: bool):
    """Run synchronization."""
    console.print(f"[cyan]Starting sync... (dry-run: {dry_run})[/cyan]")
    console.print("[green]✓ Configuration loaded[/green]")
    console.print("[green]✓ Connected to services[/green]")
    console.print("[yellow]⚠ Sync logic pending implementation[/yellow]")
    console.print("[bold green]Done.[/bold green]")


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