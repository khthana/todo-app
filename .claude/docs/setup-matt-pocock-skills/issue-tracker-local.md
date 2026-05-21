# Issue Tracker: Local Markdown

Issues and PRDs for this repo live as markdown files under `.scratch/`.

## File Organization

- Features get their own directories: `.scratch/<feature-slug>/`
- Each feature has a PRD at `.scratch/<feature-slug>/PRD.md`
- Implementation issues live in `.scratch/<feature-slug>/issues/<NN>-<slug>.md` (numbered sequentially)

## Key Practices

**Status Tracking:** Each issue includes a "Status:" field near the top that documents triage state using role-based labels (defined in `triage-labels.md`).

**Discussion History:** Conversations accumulate at the bottom of files under a `## Comments` section.

**Publishing Workflow:** When publishing to the tracker, create a new file in `.scratch/<feature-slug>/`, making the directory if necessary.

**Retrieval Process:** To access a specific ticket, read the file at its path — users typically provide either the file path or issue number.

This approach keeps all project management artifacts version-controlled alongside the codebase itself.
