# Software Construction Assignment

**Topic:** Project Code Review

**Name:** OBBA MARK CALVIN     S23B23\047    B24277


**Course:** BSCS 3:2


**Course Unit:** Software Construction

## Analyze Poorly Written Error Handling Code

In the selected open-source project, **Task Tracker CLI**, the original implementation contains several weak error-handling practices that reduce reliability, maintainability, and debuggability.

### 1. Silent handling of corrupted JSON data

The most serious issue appears in the `load_tasks()` function:

```python
with open('tasks.json', 'r') as file:
    try:
        return json.load(file)
    except json.JSONDecodeError:
        return []
```
This is poor because when tasks.json contains invalid or corrupted JSON, the program simply returns an empty list instead of reporting the problem. This hides the actual failure and may mislead the user into thinking there are no saved tasks. In reality the data may still exist but be unreadable due to corruption. 

The risks may include:
- Hides real data problems

- Makes debugging difficult

- Can create false assumptions about lost tasks

- Provides no diagnostic trace



### 2. File operations are not protected against system level failures

The application directly opens and writes to `tasks.json` in both `load_tasks()` and `save_tasks()`:

```python
with open('tasks.json', 'w') as file:
    json.dump(tasks, file, indent=4)
```

#### Why this is poor

This assumes file access will always succeed. However, file operations can fail due to permission errors, missing paths, disk issues, or other operating system problems. Since these cases are not handled, the program may crash unexpectedly.

#### Risk

- Sudden program termination  
- Unclear error messages  
- Possible corruption of stored task data  


---

### 3. No meaningful logging

The project uses `console.print()` for user feedback, for example:

```python
console.print(f"[green]Task added successfully (ID: {task_id})[/green]")
```

#### Why this is poor

Printing to the terminal is not the same as logging. Terminal messages disappear after execution and do not provide a persistent record of what happened. If an error occurs in production or during later testing, there is no log file to trace the cause.

#### Risk

- No audit trail of operations  
- No stored error history  
- Difficult debugging and maintenance  


---

### 4. Weak defensive programming

Task descriptions are accepted without validation:

```python
parser_add.add_argument("description", type=str, help="Description of the task")
```

#### Why this is poor

The program does not check whether the description is empty or invalid before saving it. This is a defensive programming weakness because user input should be validated before being processed or stored.

#### Risk

- Poor data quality  
- Invalid or empty tasks being stored  
- Reduced usability of the application  


---
## Improve exception strategies with targeted fixes


Based on the analysis of the original code, the following targeted fixes will be implemented:

1. Replaced silent handling of `JSONDecodeError` in `load_tasks()` with explicit error reporting.
where the former one was:
``` python
def load_tasks(): 
    if not os.path.exists('tasks.json'):
         with open('tasks.json', 'w') as file: 
            json.dump([], file) return [] with open('tasks.json', 'r') as file: 
            try: return json.load(file) except json.JSONDecodeError:
             return []
```
to
```python
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "w", encoding="utf-8") as file:
                json.dump([], file)
            logging.info("Created new task storage file: %s", TASKS_FILE)
            return []
        except OSError as e:
            logging.error("Failed to create %s: %s", TASKS_FILE, e, exc_info=True)
            console.print("[red]Error: Could not create task storage file.[/red]")
            return []

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            tasks = json.load(file)
            logging.info("Loaded %d task(s) from %s", len(tasks), TASKS_FILE)
            return tasks
    except json.JSONDecodeError as e:
        logging.error("Corrupted JSON in %s: %s", TASKS_FILE, e, exc_info=True)
        console.print("[red]Error: Task file is corrupted and could not be read.[/red]")
        return []
    except OSError as e:
        logging.error("Failed to read %s: %s", TASKS_FILE, e, exc_info=True)
        console.print("[red]Error: Could not read tasks file.[/red]")
        return []
```
2. Add targeted exception handling for file input/output failures such as `OSError`:
Original code:
```python
def save_tasks(tasks):
    with open('tasks.json', 'w') as file:
        json.dump(tasks, file, indent=4)
```
New Code:
```python
def save_tasks(tasks):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4)
        logging.info("Saved %d task(s) to %s", len(tasks), TASKS_FILE)
        return True
    except OSError as e:
        logging.error("Failed to save tasks to %s: %s", TASKS_FILE, e, exc_info=True)
        console.print("[red]Error: Could not save tasks.[/red]")
        return False
```
3. Introduce meaningful logging using Python’s `logging` module to record application events and failures.
``` python
def validate_description(description):
    if not description or not description.strip():
        logging.warning("Invalid task description provided.")
        console.print("[red]Error: Task description cannot be empty.[/red]")
        return False
    return True
```
The original code accepted task descriptions without checking whether they were empty or invalid. This weakens defensive programming and reduces data quality.

5. Added Logging to Task Creation
```python
if save_tasks(tasks):
    logging.info("Added task ID %d", task_id)
    console.print(f"[green]Task added successfully (ID: {task_id})[/green]")
```
This ensures that task creation is recorded in the log file with useful context.

6. Added Logging to Task Listing
```python
if not tasks:
    logging.info("No tasks found for status filter: %s", status)
    console.print("[red]No tasks found.[/red]")
    return


logging.info("Displayed %d task(s)", len(tasks))
console.print(table)
```
These logs help trace user actions and application behavior during execution.

# AI-Generated Logging vs. Human Reasoning 
## General Comparison

| Aspect              | AI-Generated Logging                              | Human Reasoning & Best Practices                          |
|---------------------|---------------------------------------------------|-----------------------------------------------------------|
| **Focus**           | Adds logging quickly across the codebase          | Adds logging strategically where it provides real value   |
| **Detail**          | Often generic / one-size-fits-all messages        | Context-rich, meaningful, structured messages             |
| **System Awareness**| Limited understanding of application context      | Deep understanding of behavior, failure modes & domain    |
| **Goal**            | Ensure logging *exists*                           | Ensure logging is useful, safe, actionable & debuggable   |
| **Exception Info**  | Rarely includes stack trace or full context       | Usually includes `exc_info=True` + relevant identifiers   |
| **Safety**          | Frequently logs sensitive data unintentionally    | Actively avoids PII, credentials, tokens, full payloads   |


