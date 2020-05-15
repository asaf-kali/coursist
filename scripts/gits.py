import os
import sys

branches = ["asaf", "kirsh", " evyatar", "avihai", "shani"]


def execute(cmd: str):
    print(cmd)
    os.system(cmd)


def clear_cache():
    execute(f"rm -f .git/FETCH_HEAD")


def for_branch(*commands: str):
    for branch in branches:
        clear_cache()
        execute(f"git checkout {branch}")
        clear_cache()
        for cmd in commands:
            cmd = cmd.replace("<branch>", branch)
            execute(cmd)


def pull():
    for_branch("git pull")


def push():
    for_branch("git push")


def rebase(to: str):
    execute(f"git checkout {to}")
    execute(f"git push")
    pull()
    for_branch(f"git rebase {to}", "git push")


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "pull":
        pull()
    elif command == "push":
        push()
    elif command == "rebase":
        rebase("master")
    execute("git checkout master")
