from __future__ import annotations

from datetime import datetime

from app.models import DeadlineTask, RecurringTask, StandardTask, Task
from app.repositories.tags import TagRepository
from app.repositories.tasks import TaskRepository
from app.services.recurrence import RecurrenceStrategyFactory


class TaskNotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


class InvalidRecurrencePatternError(Exception):
    pass


class DependencyCycleError(Exception):
    pass


class TaskBlockedError(Exception):
    pass


_ALLOWED: dict[str, set[str]] = {
    "pending": {"in_progress", "cancelled"},
    "in_progress": {"completed", "cancelled", "pending"},
}


class TaskService:
    def __init__(self, repo: TaskRepository, tag_repo: TagRepository | None = None) -> None:
        self.repo = repo
        self.tag_repo = tag_repo

    def _resolve_tags(self, names: list[str]):
        if not names or self.tag_repo is None:
            return []
        return [self.tag_repo.upsert(n) for n in names]

    def create_task(self, title: str, description: str = "", tags: list[str] | None = None) -> Task:
        task = self.repo.create(StandardTask(title=title, description=description))
        if tags:
            task.tags = self._resolve_tags(tags)
            self.repo.save(task)
        return task

    def create_recurring_task(self, title: str, description: str = "", recurrence_pattern: str = "", next_occurrence: datetime | None = None, end_recurrence_date: datetime | None = None, tags: list[str] | None = None) -> Task:
        try:
            RecurrenceStrategyFactory.get(recurrence_pattern)
        except KeyError:
            raise InvalidRecurrencePatternError(recurrence_pattern)
        task = self.repo.create(RecurringTask(
            title=title,
            description=description,
            recurrence_pattern=recurrence_pattern,
            next_occurrence=next_occurrence,
            end_recurrence_date=end_recurrence_date,
        ))
        if tags:
            task.tags = self._resolve_tags(tags)
            self.repo.save(task)
        return task

    def create_deadline_task(self, title: str, description: str = "", due_date: datetime | None = None, reminder_time: datetime | None = None, tags: list[str] | None = None) -> Task:
        task = self.repo.create(DeadlineTask(title=title, description=description, due_date=due_date, reminder_time=reminder_time))
        if tags:
            task.tags = self._resolve_tags(tags)
            self.repo.save(task)
        return task

    def get_task(self, task_id: int) -> Task:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def list_tasks(self, status: str | None = None, tag: str | None = None) -> list[Task]:
        return self.repo.list_all(status=status, tag=tag)

    def list_tags(self):
        if self.tag_repo is None:
            return []
        return self.tag_repo.list_all()

    def update_task(self, task_id: int, fields: dict) -> Task:
        tags = fields.pop("tags", None)
        task = self.repo.update(task_id, fields)
        if task is None:
            raise TaskNotFoundError(task_id)
        if tags is not None:
            task.tags = self._resolve_tags(tags)
            self.repo.save(task)
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
        if to_status == "completed":
            for blocker in task.blockers:
                if blocker.status != "completed":
                    raise TaskBlockedError(task_id, blocker.id)
        updated = self.repo.update(task_id, {"status": to_status})
        if to_status == "completed" and isinstance(task, RecurringTask):
            self._spawn_next_occurrence(task)
        return updated

    def add_dependency(self, task_id: int, blocker_id: int) -> Task:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        blocker = self.repo.get(blocker_id)
        if blocker is None:
            raise TaskNotFoundError(blocker_id)
        if self._reaches(blocker_id, task_id):
            raise DependencyCycleError(task_id, blocker_id)
        task.blockers.append(blocker)
        return self.repo.save(task)

    def remove_dependency(self, task_id: int, blocker_id: int) -> Task:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        blocker = self.repo.get(blocker_id)
        if blocker is None:
            raise TaskNotFoundError(blocker_id)
        task.blockers = [b for b in task.blockers if b.id != blocker_id]
        return self.repo.save(task)

    def _reaches(self, start_id: int, target_id: int) -> bool:
        visited: set[int] = set()
        stack = [start_id]
        while stack:
            node_id = stack.pop()
            if node_id == target_id:
                return True
            if node_id in visited:
                continue
            visited.add(node_id)
            node = self.repo.get(node_id)
            if node:
                for b in node.blockers:
                    stack.append(b.id)
        return False

    def _spawn_next_occurrence(self, completed: RecurringTask) -> None:
        strategy = RecurrenceStrategyFactory.get(completed.recurrence_pattern)
        next_occ = strategy.calculate_next(completed.next_occurrence)
        if completed.end_recurrence_date and next_occ > completed.end_recurrence_date:
            return
        self.repo.create(RecurringTask(
            title=completed.title,
            description=completed.description,
            recurrence_pattern=completed.recurrence_pattern,
            next_occurrence=next_occ,
            end_recurrence_date=completed.end_recurrence_date,
        ))
