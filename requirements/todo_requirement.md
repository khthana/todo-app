# Requirements Specification: Advanced Todo List Backend API

## 1. Objective & Scope
**Objective:** 
Develop a robust, scalable, and fully functional Backend API for a complex Task Management (Todo List) system using Python. The system must heavily utilize Object-Oriented Programming (OOP) principles to handle varying complexities of tasks.

**Scope:**
The API must support the CRUD operations and business logic for the following task types:
*   **Standard Todo:** Basic task with title, description, and status.
*   **Deadline Todo:** Tasks that must be completed before a specific datetime.
*   **Recurring Todo:** Tasks that automatically regenerate based on a defined schedule (e.g., daily, weekly, custom intervals).
*   **Complex Features:** 
    *   **Task Dependencies:** A task can be blocked by one or multiple other tasks (Sub-tasks / Prerequisite tasks).
    *   **Tagging/Categorization:** Grouping tasks.
    *   **State Management:** Transitioning states (e.g., Pending -> In Progress -> Completed -> Archived).

## 2. Architectural Constraints
*   **Language & Framework:** Python 3.10+ (Use FastAPI for the API layer due to its asynchronous support and typing system).
*   **Programming Paradigm:** Strict Object-Oriented Programming (OOP).
    *   Apply **SOLID principles**.
    *   Use **Design Patterns** where applicable (e.g., *Factory Pattern* for instantiating different types of Todos, *Strategy Pattern* for recurrence logic).
*   **Naming Conventions:** 
    *   **Classes:** `PascalCase` (e.g., `DeadlineTodo`).
    *   **Variables and Methods:** Strictly **`snake_case`** (e.g., `generate_next_occurrence()`, `due_date`, `is_overdue`).
*   **Database & ORM:** SQLite (for local development/testing). Use SQLAlchemy 2.0 as the ORM, utilizing its OOP mapping features.
*   **Separation of Concerns:** Maintain a clean architecture (e.g., Routers/Controllers -> Services/Use Cases -> Repositories -> Models).

## 3. Core Entities & Business Rules
Implement a class hierarchy for the tasks to demonstrate Inheritance and Polymorphism.

### 3.1 Base Entity: `Task` (Abstract Base Class)
*   **Attributes:** `id`, `title`, `description`, `created_at`, `updated_at`, `status` (Enum: PENDING, IN_PROGRESS, COMPLETED, CANCELLED), `tags` (List), `dependencies` (List of Task IDs).
*   **Behaviors (Methods):** 
    *   `mark_as_completed()`: Changes status. Must check if `dependencies` are all completed before allowing state change.
    *   `add_dependency(task_id)`: Adds a prerequisite task.

### 3.2 Subclass: `StandardTask`
*   Inherits from `Task` without additional complex timing logic.

### 3.3 Subclass: `DeadlineTask`
*   **Attributes:** `due_date` (datetime), `reminder_time` (datetime).
*   **Behaviors (Methods):**
    *   `is_overdue()`: Returns Boolean comparing `due_date` to current time.
    *   `extend_deadline(new_date)`: Updates the deadline.

### 3.4 Subclass: `RecurringTask`
*   **Attributes:** `recurrence_pattern` (Enum/String: DAILY, WEEKLY, MONTHLY, or Cron expression), `next_occurrence` (datetime), `end_recurrence_date` (datetime, optional).
*   **Behaviors (Methods):**
    *   `mark_as_completed()`: *Overrides* the base method. When marked as completed, it should spawn a new instance of the task for the `next_occurrence` and set the current one to COMPLETED.
    *   `calculate_next_occurrence()`: Logic to parse the `recurrence_pattern` and update the date.

### 3.5 Business Rules
*   **Dependency Checking:** A task cannot transition to `COMPLETED` if any task in its `dependencies` list is not `COMPLETED`.
*   **Cycle Detection:** When adding a dependency, the system must ensure no circular dependencies are formed (e.g., Task A depends on Task B, which depends on Task A).

## 4. Exception & Error Handling
Do not use generic exceptions for business logic. Create a hierarchy of custom domain exceptions (Inheriting from Python's `Exception` class).

### 4.1 Custom Exception Classes
*   `DomainException` (Base Exception)
*   `TaskNotFoundError`: Raised when querying an ID that doesn't exist.
*   `DependencyCycleError`: Raised when a circular dependency is detected during `add_dependency()`.
*   `TaskBlockedError`: Raised when attempting to `mark_as_completed()` on a task with pending dependencies.
*   `InvalidRecurrencePatternError`: Raised when creating a `RecurringTask` with an unparseable pattern.

### 4.2 API Error Mapping (Exception Handler)
The API layer must catch these domain exceptions and map them to appropriate HTTP Status Codes:
*   `TaskNotFoundError` -> `404 Not Found`
*   `DependencyCycleError` -> `400 Bad Request`
*   `TaskBlockedError` -> `422 Unprocessable Entity`
*   `InvalidRecurrencePatternError` -> `400 Bad Request`
*   Unhandled Exceptions -> `500 Internal Server Error` (with safe logging, hiding internal stack traces from the client).