from __future__ import annotations

from datetime import datetime

from app.models import DeadlineTask, RecurringTask, StandardTask, Task
from app.repositories.tasks import TaskRepository
from app.services.recurrence import RecurrenceStrategyFactory


class TaskNotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


class InvalidRecurrencePatternError(Exception):
    pass


_ALLOWED: dict[str, set[str]] = {
    "pending": {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled", "pending"},
}


class TaskService:
    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    def create_task(self, title: str, description: str = "") -> Task:
        return self.repo.create(StandardTask(title=title, description=description))

    def create_recurring_task(self, title: str, description: str = "", recurrence_pattern: str = "", next_occurrence: datetime | None = None, end_recurrence_date: datetime | None = None) -> Task:
        try:
            RecurrenceStrategyFactory.get(recurrence_pattern)
        except KeyError:
            raise InvalidRecurrencePatternError(recurrence_pattern)
        return self.repo.create(RecurringTask(
            title=title,
            description=description,
            recurrence_pattern=recurrence_pattern,
            next_occurrence=next_occurrence,
            end_recurrence_date=end_recurrence_date,
        ))

    def create_deadline_task(self, title: str, description: str = "", due_date: datetime | None = None, reminder_time: datetime | None = None) -> Task:
        return self.repo.create(DeadlineTask(title=title, description=description, due_date=due_date, reminder_time=reminder_time))

    def get_task(self, task_id: int) -> Task:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def list_tasks(self) -> list[Task]:
        return self.repo.list_all()

    def update_task(self, task_id: int, fields: dict) -> Task:
        task = self.repo.update(task_id, fields)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def delete_task(self, task_id: int) -> None:
        deleted = self.repo.delete(task_id)
        if not deleted:
            raise TaskNotFoundError(task_id)

    def transition_task(self, task_id: int, to_status: str) -> Task:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        if to_status not in _ALLOWED.get(task.status, set()):
            raise InvalidTransitionError(task.status, to_status)
        return self.repo.update(task_id, {"status": to_status})
