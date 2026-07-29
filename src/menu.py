from .sessions import SessionInfo
from . import instructions
from rich.console import Console
from rich.table import Table

class Menu:

    def start(self):
        SQLMenu().start()


STATUS_STYLES = {
    "pending": "yellow",
    "running": "blue",
    "failed": "bold red",
    "finished": "green",
}


class SQLMenu:

    def start(self):
        # main loop
        while True:
            sessions = [SessionInfo.from_sql(id) for id in SessionInfo.all_sessions_id()]

            select = self.select_session(sessions)
            if select:
                instruction = self.options_session(select)
            else:
                break


    @staticmethod
    def select_session(sessions:list[SessionInfo]):
        # print all sessions
        # return None for no selected or the session obj for the selected one
        console = Console()

        if not sessions:
            console.print("[yellow]No sessions found.[/yellow]")
            return None

        sessions = sorted(sessions, key=lambda s: s.id)

        table = Table(title="Generation Sessions")
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Status")
        table.add_column("Step", style="magenta")
        table.add_column("Topic")
        table.add_column("Platform")
        table.add_column("Created At", style="dim")
        table.add_column("Error", style="red")

        for session in sessions:
            gs = session.generation_session
            status_style = STATUS_STYLES.get(gs.status, "white")
            table.add_row(
                str(gs.id),
                f"[{status_style}]{gs.status}[/{status_style}]",
                gs.step,
                gs.topic,
                gs.platform,
                gs.created_at.strftime("%Y-%m-%d %H:%M"),
                gs.error_message or "",
            )

        console.print(table)

        choice = console.input("[bold]Select session ID (blank to exit): [/bold]").strip()
        if not choice:
            return None

        for session in sessions:
            if str(session.id) == choice:
                return session

        console.print(f"[red]No session with ID {choice}[/red]")
        return None

    @staticmethod
    def options_session(session):
        # delete
        # restart
        # script
        pass

class UploadMenu:

    def start(self):
        pass
