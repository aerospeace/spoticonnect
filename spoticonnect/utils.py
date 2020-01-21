import colored


status_style = colored.fg(119) + colored.attr("bold")
message_style = colored.fg("cyan") + colored.attr("bold")
warning_style = colored.fg("yellow") + colored.attr("bold")
error_style = colored.fg("red") + colored.attr("bold")


def print_status(msg):
    print(colored.stylize(msg, status_style))


def print_message(msg):
    print(colored.stylize(msg, message_style))


def print_warning(msg):
    print(colored.stylize(msg, warning_style))


def print_error(msg):
    print(colored.stylize(msg, error_style))
