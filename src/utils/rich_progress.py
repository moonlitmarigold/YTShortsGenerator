import contextvars
from typing import Optional

import proglog
from rich.progress import Progress, TaskID

_current_progress: contextvars.ContextVar[Optional[Progress]] = contextvars.ContextVar(
    '_current_progress', default=None
)


def get_progress() -> Optional[Progress]:
    return _current_progress.get()


def set_progress(progress: Optional[Progress]) -> None:
    _current_progress.set(progress)


class RichProglogLogger(proglog.ProgressBarLogger):
    """Bridges moviepy/proglog progress bars into the shared rich Progress instance.

    moviepy's default logger draws its own tqdm-style bar straight to stdout,
    which fights with rich's Live-managed display for the terminal. This
    forwards each proglog bar to a nested task on whatever Progress is
    currently active (set via set_progress), so everything renders inside one
    Live region. No-ops if no Progress is active.
    """

    def __init__(self):
        super().__init__()
        self._task_ids: dict[str, TaskID] = {}

    def bars_callback(self, bar, attr, value, old_value=None):
        progress = get_progress()
        if progress is None:
            return

        infos = self.bars[bar]
        task_id = self._task_ids.get(bar)
        if task_id is None:
            task_id = progress.add_task(infos['title'], total=infos['total'])
            self._task_ids[bar] = task_id

        if attr != 'index':
            return

        total = infos['total']
        if total and value >= total:
            progress.remove_task(task_id)
            del self._task_ids[bar]
        else:
            progress.update(task_id, completed=value)

    def callback(self, **kw):
        progress = get_progress()
        message = kw.get('message')
        if progress is not None and message:
            progress.console.print(message.strip())
