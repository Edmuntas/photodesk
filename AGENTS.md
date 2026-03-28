# Agent Instructions

> This is a living document — update it as you add skills, learn from errors, and evolve the system.
> This same content is copied identically to three files for cross-environment compatibility.

## Project Context

**Project:** PhotoDesk
**Owner:** Дорон — Sisa Aero Photography (edmontdoron@gmail.com)
**What we do:** Два продукта: (1) PhotoDesk CRM — управление заказами, клиентами и счетами для фотографов недвижимости на иврите/RTL через Firebase Firestore + GitHub Pages. (2) Grok Batch Cleaner — desktop Python-приложение для AI-очистки и обработки фото недвижимости через xAI API.
**Target audience:** Аэрофотографы и фотографы недвижимости в Израиле и их клиенты (агенты по недвижимости, офисы)

### About the business
Дорон управляет аэрофото-студией Sisa Aero Photography. Основной продукт — PhotoDesk CRM: инструмент для управления съёмками недвижимости (нкасим), клиентами (агентами и офисами), заказами, инвойсами и доставкой. UI на иврите, RTL, тёмная тема. Второй продукт — Grok Batch Cleaner: десктопное приложение на Python/Tkinter для пакетной AI-обработки фото через xAI Grok Vision API.

### Current goals
- PhotoDesk CRM работает на GitHub Pages (photodesk.html). Активная разработка: добавление новых страниц и фич.
- Grok Batch Cleaner: стабилизация, улучшение UX, тестирование на реальных DNG/JPG файлах.

### What AI agents should handle
[Уточни: какие задачи ты хочешь автоматизировать?
Примеры: генерация инвойсов, мониторинг статусов заказов, обработка фото по расписанию, отчёты.]

### What I DON'T want
[Уточни: чего НЕ делать?
Примеры: не трогать Firebase правила без подтверждения, не тратить API-кредиты без спроса, не коммитить в main напрямую.]

### Stack
- Claude Code — оркестрация и принятие решений
- Firebase Firestore — база данных CRM
- HTML/CSS/JS — фронтенд (single-file приложения)
- GitHub Pages — хостинг (`https://edmuntas.github.io/photodesk/`)
- Python + Tkinter — Grok Batch Cleaner desktop app
- xAI Grok Vision API — AI-обработка фото в Grok Cleaner

---

## Architecture

The brain of the project is this file. It's copied identically to three locations so any AI environment sees the same instructions:

| File | Loaded by |
|------|-----------|
| `.claude/CLAUDE.md` | Claude Code CLI (auto-loaded as project instructions) |
| `AGENTS.md` | Cursor, Windsurf, other IDE agents |
| `GEMINI.md` | Google Gemini CLI / plugins |

One content, three entry points. When you update one — update all three.

Inside `.claude/` there are two folders:

**Skills** (`.claude/skills/<name>/`) — SOPs, loaded on demand.
- Each Skill = `SKILL.md` instructions + optional `scripts/` folder
- Frontmatter: `name`, `description`, `allowed-tools`
- One skill = one workflow. Short, focused, concrete.
- Claude auto-discovers and invokes based on your request

**Agents** (`.claude/agents/`) — sub-agents, spawned on demand.
- Lightweight agents with isolated context (cheaper, unbiased)
- Use for: research, code review, QA, classification
- Read-only reporters — all changes happen in the parent agent
- Created as needed, not at setup

**Shared Utilities** (`execution/`) — common infrastructure scripts used across multiple skills.

**Why this works:** 90% accuracy per step = 59% success over 5 steps. Push repetitive work into deterministic scripts. Claude focuses on decision-making.

---

## Setup Protocol

When starting a fresh project with this file, create the full structure:

```
project/
  AGENTS.md              ← this file (for Cursor/Windsurf)
  GEMINI.md              ← identical copy (for Gemini)
  .claude/
    CLAUDE.md            ← identical copy (for Claude Code)
    settings.local.json  ← permissions + MCP servers
    skills/              ← SOPs (empty at start)
    agents/              ← sub-agent definitions (empty at start)
  execution/             ← shared utility scripts
  .tmp/                  ← intermediate files (never commit)
  .env                   ← API keys (never commit)
  .gitignore             ← must include: .env, .tmp/, credentials.json, token.json
```

### Identical instruction files

All three files (`.claude/CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) contain the **exact same content**. They are not pointers — they are full copies. When you update one, update all three.

---

## How to Create New Skills

When the user asks to create a new workflow/process/skill:

### 1. Create the skill folder and SKILL.md:

```
.claude/skills/<skill-name>/SKILL.md
```

### 2. Use this SKILL.md template:

```markdown
---
name: [Skill Name]
description: [One sentence — what does this skill do]
allowed-tools: [Read, Write, WebSearch, WebFetch, Bash, etc.]
---

# [Skill Name]

## Goal
[What is the end result? Be specific.]

## Input
[What does the user provide to start this skill?]

## Steps
1. [First step — concrete action]
2. [Second step]
3. [Continue until output is produced]
4. Save result to `.tmp/[descriptive_filename].md`

## Output Format
[Describe or show the exact format of the deliverable]

## Learnings
- (This section is updated automatically after each run)
- (Record what worked, what failed, edge cases discovered)
```

### 3. If the skill needs scripts:

```
.claude/skills/<skill-name>/scripts/<script_name>.py
```

Scripts should be deterministic — no LLM calls inside scripts unless absolutely necessary. The skill calls pre-written, tested scripts. LLM decides which script to run and with what parameters.

### 4. Update this file

After creating a skill, add it to the "Available Skills" section below.

---

## How to Create Sub-Agents

When a task benefits from isolated context (research, review, classification):

### 1. Create the agent file:

```
.claude/agents/<agent-name>.md
```

### 2. Use this template:

```markdown
---
model: sonnet
allowed-tools: [Read, Glob, Grep, WebSearch, WebFetch]
---

# [Agent Name]

## Role
[One sentence — what does this agent do]

## Instructions
[What should this agent focus on? What format should it return?]

## Output Format
[Exact format of the report/response]
```

### When to use sub-agents vs skills:
- **Skill** = instructions the parent agent executes itself (like a checklist)
- **Sub-agent** = a separate agent instance with its own context (like delegating to a colleague)

### Recommended sub-agents (create as needed):

| Agent | Purpose | Tools |
|-------|---------|-------|
| `research.md` | Deep research via web/files. Returns compressed summaries (50x token savings) | Read, Glob, Grep, WebSearch, WebFetch |
| `code-reviewer.md` | Code review without context. Returns issues by severity + PASS/FAIL verdict | Read, Write |
| `qa.md` | Generate tests, run them, report pass/fail | Read, Write, Bash |
| `classifier.md` | Classify incoming data into categories (emails, leads, tickets) | Read, Write |

**Key principle:** All sub-agents are **read-only reporters**. They find issues and write reports. The parent agent applies fixes.

### Design & Build workflow (when code-reviewer and qa agents exist):
1. Write the code
2. Run `code-reviewer` sub-agent (in parallel)
3. Run `qa` sub-agent (in parallel)
4. Read both reports, apply fixes
5. Ship only when both checks pass

---

## Self-Annealing Loop

Errors are learning opportunities. When something breaks:

1. **Fix** the script or approach
2. **Test** it (if no paid API cost; otherwise ask first)
3. **Update SKILL.md** — add what you learned to the Learnings section
4. **System is now stronger** — the same error won't happen again

### Auto-update instructions
When you encounter a recurring mistake (2-3 times):
- Propose adding a rule to the instruction files so future sessions one-shot it
- Format: concise, actionable (1-2 lines max)
- Always ask the user before modifying instruction files

---

## Available Skills

> This section is auto-updated as skills are created. Keep it current.

*No skills created yet. Say "create a skill for [task]" to get started.*

<!-- Example format:
### [Category Name]
| Skill | Description |
|-------|-------------|
| `skill-name` | One-line description of what it does |
-->

### Sub-Agents

| Agent | Description |
|-------|-------------|
| `qa` | Тестировщик всего проекта (CRM + Grok Cleaner). Возвращает отчёт PASS/FAIL с найденными багами по severity. |

---

## Session Start Protocol

### First Run (project structure does not exist)

When this is a fresh project and `.claude/` folder doesn't exist yet:

1. Create the full folder structure (see Setup Protocol above)
2. Copy this file's content to `.claude/CLAUDE.md` and `GEMINI.md`
3. **Brief the user** — ask questions to fill in the Project Context section above:
   - "Tell me about yourself and your business — what do you do, who are your customers?"
   - "What are your current goals and priorities?"
   - "What tasks do you want AI agents to handle?"
   - "Are there things I should NEVER do? Any boundaries or rules?"
4. Update the Project Context section in all three instruction files with the answers
5. Confirm: "Architecture is ready. Say 'create a skill for [task]' to build your first workflow."

### Regular Session (architecture exists)

When the user sends a short greeting or "go" / "let's start" / "what do we do?":

1. Read this file to understand the project
2. List available skills
3. Ask what the user wants to work on
4. If the user names a specific skill — load its SKILL.md and execute
5. If the user wants a new workflow — create a skill using the template above

When the user sends a specific task — skip the menu, execute directly.

---

## Operating Principles

**1. Check before building.** Before writing a script, check `.claude/skills/` and `execution/`. Only create new code if nothing exists.

**2. Plan before building.** For non-trivial tasks: plan first (read-only, zero risk), then implement.

**3. One skill = one task.** Keep skills short and focused. 50-100 lines max. If a skill does two things — split it.

**4. Skills auto-activate.** Claude picks the right skill based on the user's request. Each skill's description in frontmatter tells Claude when to use it.

**5. Scripts are bundled.** Each skill runs its own scripts:
```bash
python3 .claude/skills/<name>/scripts/<script>.py
```

**6. Scrap & redo after 2-3 failed attempts.** Stop patching — revert to clean state, implement the best solution in one clean pass.

**7. Local files are for processing only.** Deliverables go to cloud services (Notion, Google Sheets, etc.). Everything in `.tmp/` can be deleted and regenerated.

---

## File Organization

| Directory | Purpose |
|-----------|---------|
| `.claude/CLAUDE.md` | Project instructions for Claude Code (identical to AGENTS.md) |
| `.claude/settings.local.json` | Permissions and MCP server configuration |
| `.claude/skills/<name>/` | SOPs — bundled skills (SKILL.md + scripts/) |
| `.claude/agents/` | Sub-agent definitions (created as needed) |
| `AGENTS.md` | Project instructions for Cursor/Windsurf (identical to CLAUDE.md) |
| `GEMINI.md` | Project instructions for Gemini (identical to CLAUDE.md) |
| `execution/` | Shared utility scripts |
| `.tmp/` | Intermediate files — never commit, always regenerated |
| `.env` | Environment variables and API keys — never commit |
