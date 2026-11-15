# Commit Message Guidelines

Rules for commit messages in CourseLab (learning platform: FastAPI
backend in `api/`, Vue frontend in `web/`),
used by humans and by GitHub Copilot when generating commit messages.

The project is built in small steps (34 steps in 8 phases); every step
ends with exactly one commit. Commit history should show work spread over
several days, with messages that describe the change.

## Format

```
<type>(<scope>): <subject>

<body>
```

## Type

Use exactly one of the six types used by the project specification and
the course reference project:

| Type       | When to use                                                   |
|------------|---------------------------------------------------------------|
| `feat`     | New behavior: endpoint, model + migration, business rule      |
| `fix`      | Bug fix in existing behavior                                  |
| `refactor` | Code change that neither fixes a bug nor adds a feature       |
| `test`     | Adding or fixing tests only                                   |
| `docs`     | README or other documentation only                            |
| `chore`    | Setup and configuration: repository, Docker, Alembic, tooling |

If a commit mixes types, pick the most significant one
(`feat` > `fix` > `refactor` > others). A new dependency in
`requirements.txt` belongs to the commit that first uses it, not to a
separate commit.

## Scope

| Scope   | When to use                                                   |
|---------|---------------------------------------------------------------|
| `api`   | Anything under `api/`: app code, migrations, tests, tooling   |
| `web`   | Anything under `web/` (frontend, part 2 of the project)       |
| (none)  | Repository-wide changes: root `README.md`, `.gitignore`, first commit |

Examples: `feat(api): ...`, `test(api): ...`, `chore: initialize repository`,
`docs: complete setup instructions`.

## Subject

- Imperative mood: "add", "fix", "cover", "enforce" (not "added", "fixes").
- Lowercase first letter, no trailing period.
- Max 72 characters including type and scope.
- Say WHAT changed in domain terms (courses, enrollments, capacity,
  grading), not which files were touched.
  - Good: `feat(api): enforce course capacity on acceptance`
  - Bad: `feat(api): update services`, `chore: changes`, `fix stuff`
- When following the tutorial, use the subject given for that step.

## Body

Optional for setup steps and one-line changes, recommended otherwise.
Separate it from the subject with one blank line.

1. **File list:** one bullet per changed file:
   ```
   - api/app/services/enrollment_service.py: lock course row before counting
   ```
   - Paths relative to the repository root (`api/app/...`, `api/tests/...`).
   - Describe the change concretely (function, model, constraint,
     endpoint), not just "updated".
   - Group trivial changes into one bullet, e.g.
     `- api/app/**/__init__.py: add empty package markers`.
   - For a migration, name the schema change:
     `- api/alembic/versions/006_create_enrollments.py: enrollments table,
     enrollment_status enum, unique (student_id, course_id)`.

2. **Reason (optional):** a short paragraph after the list when the WHY
   is not obvious from the diff, e.g. a race condition, a PostgreSQL
   limitation or a rule from the specification.

- Wrap lines at 72 characters.
- Write in English (code identifiers are English; comments and API
  error messages in the code are Croatian).

## Before committing

Run from `api/` with the virtual environment active:

```bash
ruff format .
ruff check .
pytest -q          # from step 1.5 on, when tests exist
```

For a commit that adds a migration, also check:

```bash
alembic upgrade head && alembic downgrade -1 && alembic upgrade head
```

## Project rules

- One tutorial step = one commit. Don't combine steps, don't split one
  step's code across unrelated commits.
- Never commit `.env` (only `.env.example`).
- Never change a migration that is already committed; fix it with a new
  migration (`--rev-id 013`, ...) and a `fix(api): ...` commit.
- Don't invent issue numbers, ticket IDs or authors. The project has
  no issue tracker, so no footer is needed.

## Examples

### Setup (no scope, no body)

```
chore: initialize repository
```

### Model and migration

```
feat(api): add enrollments table

- api/app/models/enrollment.py: Enrollment model, status enum,
  unique (student_id, course_id), FKs with ON DELETE RESTRICT
- api/app/models/user.py, api/app/models/course.py: add enrollments
  relationship with back_populates
- api/app/models/__init__.py: register Enrollment for autogenerate
- api/alembic/versions/006_create_enrollments.py: create table and
  enum, drop enum type in downgrade
```

### Business rule

```
feat(api): enforce course capacity on acceptance

- api/app/repositories/course_repo.py: add lock_by_id (SELECT ... FOR
  UPDATE)
- api/app/services/enrollment_service.py: add accept/reject, count
  accepted enrollments after locking the course
- api/app/services/course_service.py: reject capacity below accepted
- api/app/routers/enrollments.py: add accept and reject endpoints
- api/alembic/versions/007_add_enrollments_course_status_index.py:
  index on (course_id, status)

Locking the course row prevents two simultaneous acceptances from
exceeding capacity.
```

### Tests

```
test(api): cover enrollment rules

- api/tests/conftest.py: add make_enrollment helper
- api/tests/test_enrollments.py: deadline boundaries, duplicates,
  capacity, concurrent acceptance, status transitions
```

### Bug fix

```
fix(api): reject enrollment exactly at the deadline

- api/app/services/enrollment_service.py: compare clock.now() with
  enrollment_deadline using < instead of <=
- api/tests/test_enrollments.py: cover enrolling one second after deadline
```

### Documentation

```
docs: complete setup instructions
```

## Don'ts

- Don't write vague messages: "update", "changes", "wip", "fix bug".
- Don't describe the diff line by line; summarize the intent per file.
- Don't use types outside the six above (`style`, `build`, `ci`, `perf`,
  `revert`); the project specification allows only these six.
