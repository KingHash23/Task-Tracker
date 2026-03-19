#!/usr/bin/env python3
import logging
import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
import argparse
from rich.prompt import Prompt

console = Console()

TASKS_FILE = "tasks.json"
LOG_FILE = "task_tracker.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


TASK_TRACKER_ASCII = """
╔╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╤╗
╟┼┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┼╢
╟┤                                                                                                ├╢
╟┤ ████████╗ █████╗ ███████╗██╗  ██╗    ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗  ├╢
╟┤ ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗ ├╢
╟┤    ██║   ███████║███████╗█████╔╝        ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝ ├╢
╟┤    ██║   ██╔══██║╚════██║██╔═██╗        ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗ ├╢
╟┤    ██║   ██║  ██║███████║██║  ██╗       ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║ ├╢
╟┤    ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ├╢
╟┤                                                                                                ├╢
╟┼┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┬┼╢
╚╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╧╝
"""

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

def get_next_id(tasks):
    return max([task['id'] for task in tasks], default=0) + 1

def validate_description(description):
    if not description or not description.strip():
        logging.warning("Invalid task description provided.")
        console.print("[red]Error: Task description cannot be empty.[/red]")
        return False
    return True


def add_task(description):
    if not validate_description(description):
        return

    tasks = load_tasks()
    task_id = get_next_id(tasks)
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    new_task = {
        "id": task_id,
        "description": description.strip(),
        "status": "Pending",
        "createdAt": formatted_time,
        "updatedAt": formatted_time,
    }

    tasks.append(new_task)

    if save_tasks(tasks):
        logging.info("Added task ID %d", task_id)
        console.print(f"[green]Task added successfully (ID: {task_id})[/green]")


def list_tasks(status=None):
    tasks = load_tasks()

    if status:
        tasks = [task for task in tasks if task["status"] == status.lower().capitalize()]

    if not tasks:
        logging.info("No tasks found for status filter: %s", status)
        console.print("[red]No tasks found.[/red]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#")
    table.add_column("Description")
    table.add_column("Status")
    table.add_column("Created At")
    table.add_column("Updated At")

    for task in tasks:
        if task["status"] == "Pending":
            status_color = "green"
        elif task["status"] == "In-progress":
            status_color = "purple"
        elif task["status"] == "Completed":
            status_color = "red"
        else:
            status_color = "white"

        table.add_row(
            str(task["id"]),
            task["description"],
            f"[{status_color}]{task['status']}[/{status_color}]",
            task["createdAt"],
            task["updatedAt"],
        )

    logging.info("Displayed %d task(s)", len(tasks))
    console.print(table)


def update_task_status(task_id, new_status):
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            old_status = task["status"]
            task["status"] = new_status
            task["updatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if save_tasks(tasks):
                logging.info(
                    "Updated task ID %d status from %s to %s",
                    task_id,
                    old_status,
                    new_status
                )
                console.print(f"[green]Task ID {task_id} marked as {new_status}.[/green]")
            return

    logging.warning("Attempted to update status of non-existent task ID %d", task_id)
    console.print(f"[red]Task ID {task_id} not found.[/red]")


def mark_in_progress(task_id):
    update_task_status(task_id, "In-progress")


def mark_done(task_id):
    update_task_status(task_id, "Completed")


def delete_task(task_id):
    tasks = load_tasks()
    task_exists = False

    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            task_exists = True
            break

    if task_exists:
        if save_tasks(tasks):
            logging.info("Deleted task ID %d", task_id)
            console.print(f"[yellow]Task ID {task_id} deleted successfully.[/yellow]")
    else:
        logging.warning("Attempted to delete non-existent task ID %d", task_id)
        console.print(f"[red]Task ID {task_id} does not exist.[/red]")


def update_task(task_id, new_description):
    if not validate_description(new_description):
        return

    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            old_description = task["description"]
            task["description"] = new_description.strip()
            task["updatedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if save_tasks(tasks):
                logging.info(
                    "Updated task ID %d description from '%s' to '%s'",
                    task_id,
                    old_description,
                    new_description.strip()
                )
                console.print(f"[green]Task ID {task_id} updated successfully.[/green]")
            return

    logging.warning("Attempted to update non-existent task ID %d", task_id)
    console.print(f"[red]Task ID {task_id} not found.[/red]")


def main():
    parser = argparse.ArgumentParser(description="Task Tracker CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    parser_add = subparsers.add_parser("add", help="Add a new task")
    parser_add.add_argument("description", type=str, help="Description of the task")

    parser_list = subparsers.add_parser("list", help="List all tasks")
    parser_list.add_argument(
        "status",
        type=str,
        nargs="?",
        default=None,
        help="Status of the tasks to list (optional)"
    )

    parser_update = subparsers.add_parser("update", help="Update an existing task")
    parser_update.add_argument("id", type=int, help="ID of the task to update")
    parser_update.add_argument("description", type=str, help="New description of the task")

    parser_mark = subparsers.add_parser("mark", help="Mark a task as completed or pending")
    parser_mark.add_argument("id", type=int, help="ID of the task to mark")
    parser_mark.add_argument(
        "status",
        type=str,
        choices=["completed", "pending"],
        help="New status of the task"
    )

    parser_delete = subparsers.add_parser("delete", help="Delete a task")
    parser_delete.add_argument("id", type=int, help="ID of the task to delete")

    args = parser.parse_args()

    logging.info("Application started with command: %s", args.command)

    console.print(TASK_TRACKER_ASCII, style="bold violet")
    console.print("Welcome to the Task Tracker v1.0", style="green")
    console.print(
        """
        - A CLI-based Task tracker tool that can easily track your small todo tasks.
        - Store them in JSON format.
        - Keep a log of them.
        - Categorize them by using specific labels.

        [bold]Connect with the author:[/bold]
        - 📂 [link=https://github.com/yashksaini-coder]GitHub[/link]
        - 🌐 [link=https://twitter.com/yash_k_saini]Twitter[/link]
        """,
        style="green"
    )

    if args.command == "add":
        add_task(args.description)
    elif args.command == "list":
        list_tasks(args.status)
    elif args.command == "update":
        update_task(args.id, args.description)
    elif args.command == "mark":
        update_task_status(args.id, args.status.capitalize())
    elif args.command == "delete":
        if Prompt.ask(f"Are you sure you want to delete task {args.id}?", choices=["y", "n"]) == "y":
            delete_task(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()