import os
import sys

branches = ["master", "asaf", "kirsh", " evyatar", "avihai", "shani"]


def for_branch(*commands: str):
    for branch in branches:
        os.system(f"git checkout {branch}")
        for command in commands:
            os.system(command.replace("<branch>", branch))


def pull():
    for_branch("git pull")


def push():
    for_branch("git push")


def rebase(to: str):
    for_branch(f"git rebase {to}")
    push()


if __name__ == '__main__':
    command = sys.argv[1]
    if command == "pull":
        pull()
    elif command == "push":
        push()
    elif command == "rebase":
        rebase("asaf")
