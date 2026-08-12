from .sessions import SessionInfo
from . import pipeline
from . import instructions
from rich.console import Console
from rich.table import Table
import dataclasses

@dataclasses.dataclass
class Options:

    title:str
    options:dict = dataclasses.field(default_factory=dict)
    cur_num = 1

    def show(self):
        console = Console()

        while True:
            console.print(f"[bold]{self.title}[/bold]")
            for key, (label, _) in self.options.items():
                console.print(f"{key}. {label}")

            choice = console.input("[bold]Select an option (blank to exit): [/bold]").strip()
            if not choice:
                break

            action = self.options.get(choice)
            if action is None:
                console.print(f"[red]Invalid option {choice}[/red]")
                continue

            if action[1]():
                break


    def add_option(self, **kwargs):
        for key, value in kwargs.items():
            self.options[str(self.cur_num)] = (
                str(key),
                value
            )
            self.cur_num += 1
    def add_title(self):
        return self



class Menu:

    def start(self):
        menu = Options(title="Main Menu")
        menu.add_option(**{
            "Sessions": lambda: SQLMenu().start(),
            "New session": lambda: instructions.Instruction.new()(),
            "Login (not implemented)": self._not_implemented("Login"),
            "Update (not implemented)": self._not_implemented("Update"),
        })
        menu.show()

    @staticmethod
    def _not_implemented(name: str):
        def _run():
            Console().print(f"[yellow]{name} is not implemented yet.[/yellow]")
        return _run


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
            #sessions = [s for s in sessions if not s.is_finished]

            select = self.select_session(sessions)
            if select:
                self.options_session(select)
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
    def options_session(session: SessionInfo):
        # delete
        # restart
        # script
        menu = Options(title=f"Session {session.id} - {session.generation_session.topic} (step: {session.step})")
        menu.add_option(**{
            "Restart (rerun the full pipeline from the prompt step)": lambda: instructions.Instruction.restart(session)(),
            "Restart from a specific step":lambda: SQLMenu.options_steps(session),
            f"Continue (rerun from the current step: {session.step})": lambda: instructions.Instruction.restart_from_step(session)(),
            "View script": lambda: instructions.Instruction.show_script(session)(),
            "Edit script": lambda: instructions.Instruction.edit_script(session)(),
            "Upload": lambda: instructions.Instruction.upload(session)(),
            "Delete": lambda: SQLMenu._delete_session(session),
        })
        menu.show()

    @staticmethod
    def _delete_session(session: SessionInfo):
        console = Console()
        confirm = console.input(
            f"[bold red]Type 'yes' to confirm deleting session {session.id}: [/bold red]"
        ).strip().lower()
        if confirm != "yes":
            console.print("[yellow]Cancelled.[/yellow]")
            return False

        instructions.Instruction.delete(session)()
        return True

    @staticmethod
    def options_steps(session:SessionInfo):
        menu = Options(title=f"Session {session.id} - {session.generation_session.topic} (step: {session.step})")
        steps_to_iterate = list()
        for step in pipeline.PipelineBuilder.steps:
            steps_to_iterate.append(step)
            if step == session.step:
                break

        for step in steps_to_iterate:
            menu.add_option(
                **{
                    str(step):lambda: instructions.Instruction.restart_from_step(session, str(step))()
                }
            )

        menu.show()

class UploadMenu:

    def start(self):
        pass
