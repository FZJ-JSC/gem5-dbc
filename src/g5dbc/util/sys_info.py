import platform


def get_local_architecture():
    uname = platform.uname()

    local_arch = ""
    match uname.machine:
        case "aarch64":
            local_arch = "arm64"
        case _:
            raise ValueError("Not supported")

    return local_arch
