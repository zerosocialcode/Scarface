from termcolor import colored

def prompt(text):
    return input(colored(text, "cyan", attrs=["bold"]))

def print_success(msg):
    print(colored(msg, "green"))

def print_error(msg):
    print(colored(msg, "red"))

def print_info(msg):
    print(colored(msg, "white"))
