import platform
import sys

def is_windows_ansi_supported():
    """
    In case user running the user uses
    Windows10 OS with a build number below 10586 this function return False
    Use for checking if user OS have the capability to render ANSI Color Escape sequence
    """
    if sys.platform != "win32":
        return True 

    version_info = platform.version()  # Example: '10.0.10240'
    build_number = int(version_info.split('.')[-1])

    return build_number >= 10586 

if is_windows_ansi_supported() :
    RESET   = "\033[0m"

    # Regular colors
    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    # Bright colors
    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"

    # Background colors
    BG_BLACK   = "\033[40m"
    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_WHITE   = "\033[47m"

    # Bright background colors
    BG_BRIGHT_BLACK   = "\033[100m"
    BG_BRIGHT_RED     = "\033[101m"
    BG_BRIGHT_GREEN   = "\033[102m"
    BG_BRIGHT_YELLOW  = "\033[103m"
    BG_BRIGHT_BLUE    = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN    = "\033[106m"
    BG_BRIGHT_WHITE   = "\033[107m"

    # Style
    BOLD       = "\033[1m"
    DIM        = "\033[2m"
    ITALIC     = "\033[3m"
    UNDERLINE  = "\033[4m"

    # Info logo style
    CRITICAL = f"[{BOLD}{RED}!{RESET}]"
    INFO = f"[i]"
    UNREC = f"[{BOLD}{YELLOW}i{RESET}]"
    SUCCES = f"[{BOLD}{GREEN}*{RESET}]"

else :
    RESET   = ""

    # Regular colors
    BLACK   = ""
    RED     = ""
    GREEN   = ""
    YELLOW  = ""
    BLUE    = ""
    MAGENTA = ""
    CYAN    = ""
    WHITE   = ""

    # Bright colors
    BRIGHT_BLACK   = ""
    BRIGHT_RED     = ""
    BRIGHT_GREEN   = ""
    BRIGHT_YELLOW  = ""
    BRIGHT_BLUE    = ""
    BRIGHT_MAGENTA = ""
    BRIGHT_CYAN    = ""
    BRIGHT_WHITE   = ""

    # Background colors
    BG_BLACK   = ""
    BG_RED     = ""
    BG_GREEN   = ""
    BG_YELLOW  = ""
    BG_BLUE    = ""
    BG_MAGENTA = ""
    BG_CYAN    = ""
    BG_WHITE   = ""

    # Bright background colors
    BG_BRIGHT_BLACK   = ""
    BG_BRIGHT_RED     = ""
    BG_BRIGHT_GREEN   = ""
    BG_BRIGHT_YELLOW  = ""
    BG_BRIGHT_BLUE    = ""
    BG_BRIGHT_MAGENTA = ""
    BG_BRIGHT_CYAN    = ""
    BG_BRIGHT_WHITE   = ""

    # Style
    BOLD       = ""
    DIM        = ""
    ITALIC     = ""
    UNDERLINE  = ""

    # Info logo style
    CRITICAL = f"[!]"
    INFO = f"[i]"
    UNREC = f"[i]"
    SUCCES = f"[*]"