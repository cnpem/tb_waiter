import subprocess
import socket

def get_available_port():
    initial_port = 6006
    hostname = "localhost"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = initial_port
    while port < 65535:
        try:
            s.bind((hostname, port))
            s.close()
            return port
        except OSError:
            port += 1
    return None


def start_tensorboard(logdir: str, name: str):
    port = get_available_port()
    if port is None:
        raise Exception("No available port found")
    p = subprocess.Popen(
        [
            "tensorboard",
            "--logdir",
            logdir,
            "--port",
            str(port),
            "--bind_all",
            "--path_prefix",
            f"/{name}/{port}",
            "--load_fast",
            "false"
        ]
    )

    return p, port