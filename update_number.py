#!/usr/bin/env python3
import os
import random
import subprocess
from datetime import datetime
import shutil
import win32com.client

from commit_schedule import is_date_in_commit_schedule

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def read_number():
    with open("number.txt", "r") as f:
        return int(f.read().strip())


def write_number(num):
    with open("number.txt", "w") as f:
        f.write(str(num))


def generate_random_commit_message():
    from transformers import pipeline

    generator = pipeline(
        "text-generation",
        model="openai-community/gpt2",
    )
    prompt = """
        Generate a Git commit message following the Conventional Commits standard. The message should include a type, an optional scope, and a subject.Please keep it short. Here are some examples:

        - feat(auth): add user authentication module
        - fix(api): resolve null pointer exception in user endpoint
        - docs(readme): update installation instructions
        - chore(deps): upgrade lodash to version 4.17.21
        - refactor(utils): simplify date formatting logic

        Now, generate a new commit message:
    """
    generated = generator(
        prompt,
        max_new_tokens=50,
        num_return_sequences=1,
        temperature=0.9,
        top_k=50,
        top_p=0.9,
        truncation=True,
    )
    text = generated[0]["generated_text"]

    if "- " in text:
        return text.rsplit("- ", 1)[-1].strip()
    else:
        raise ValueError(f"Unexpected generated text {text}")


def git_commit():
    # Stage the changes
    subprocess.run(["git", "add", "number.txt"])
    # Create commit with current date
    # if "FANCY_JOB_USE_LLM" in os.environ:
    #     commit_message = generate_random_commit_message()
    # else:
    #     date = datetime.now().strftime("%Y-%m-%d")
    #     commit_message = f"Update number: {date}"
    commit_message = generate_random_commit_message()
    subprocess.run(["git", "commit", "-m", commit_message])


def git_push():
    # Push the committed changes to GitHub
    result = subprocess.run(["git", "push"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)


def update_task_scheduler():
    # # Generate random hour (0-23) and minute (0-59)
    # random_hour = random.randint(0, 23)
    # random_minute = random.randint(0, 59)
    random_hour = 17
    random_minute = 25

    # Define task name
    task_name = "UpdateNumberTask"

    # Path to Python executable
    python_path = shutil.which("python")

    # Path to the script
    script_path = os.path.join(script_dir, "update_number.py")

    # Create a Task Scheduler object
    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect()
    root_folder = scheduler.GetFolder("\\")

    # Delete existing task if it exists
    try:
        root_folder.DeleteTask(task_name, 0)
    except Exception:
        pass

    # Create a new task
    task_def = scheduler.NewTask(0)
    trigger = task_def.Triggers.Create(1)  # Daily trigger
    trigger.StartBoundary = datetime.now().strftime(f"%Y-%m-%dT{random_hour:02}:{random_minute:02}:00")
    action = task_def.Actions.Create(0)  # Execute action
    action.Path = python_path
    action.Arguments = f'"{script_path}"'
    task_def.RegistrationInfo.Description = "Update number script"
    task_def.Settings.Enabled = True
    task_def.Settings.StartWhenAvailable = True

    # Register the task
    root_folder.RegisterTaskDefinition(
        task_name,
        task_def,
        6,  # Create or update the task
        None,  # No user
        None,  # No password
        0,
    )

    print(f"Task Scheduler updated to run at {random_hour:02}:{random_minute:02}.")


def main():
    try:
        today_date = datetime.today().strftime("%Y-%m-%d")
        output = is_date_in_commit_schedule("ARIF 25 !", today_date, "2025-01-19")
        
        iterations = 1
        if output:
            iterations = 7
        for i in range(iterations):
            current_number = read_number()
            new_number = current_number + 1
            write_number(new_number)
            git_commit()
            git_push()
        update_task_scheduler()
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
