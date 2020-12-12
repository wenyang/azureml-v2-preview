from colorama import init, Fore

init()


def print_error_and_exit(text):
    print(Fore.RED + text)
    exit(1)


def print_warning(text):
    print(Fore.LIGHTYELLOW_EX + text)
