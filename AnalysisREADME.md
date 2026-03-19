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

1. Replace silent handling of `JSONDecodeError` in `load_tasks()` with explicit error reporting and logging.
2. Add targeted exception handling for file input/output failures such as `OSError`.
3. Introduce meaningful logging using Python’s `logging` module to record application events and failures.
4. Validate task descriptions before saving or updating tasks to prevent empty or invalid input.
5. Improve reliability of save operations by handling write failures safely and informing the user appropriately.

These fixes were selected because they directly address the major weaknesses identified in the original implementation while remaining focused and practical for the scope of the assignment.


