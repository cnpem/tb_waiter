import os
import time

from .models import TensorboardInstance


def create_mobius(time_branch: int):
    variants: dict[str, TensorboardInstance] = {}
    access_times: dict[str, float] = {}

    def get(loki: str):
        if loki in variants:
            current_time = time.time()

            if current_time - access_times[loki] > time_branch:
                os.kill(variants[loki].pid, 9)
                del variants[loki]
                del access_times[loki]
                raise KeyError(f"Instance {loki} has expired")

            access_times[loki] = current_time
            return variants[loki]
        else:
            raise KeyError(f"Instance {loki} not found")

    def get_all():
        prune()
        current_time = time.time()
        for loki in variants:
            access_times[loki] = current_time
        return variants

    def set(loki: str, instance: TensorboardInstance):
        current_time = time.time()
        variants[loki] = instance
        access_times[loki] = current_time
        prune()

    def remove(loki: str):
        if contains(loki):
            os.kill(variants[loki].pid, 9)
            del variants[loki]
            del access_times[loki]

    def prune():
        current_time = time.time()
        expired = [
            loki
            for loki, access_time in access_times.items()
            if current_time - access_time > time_branch
        ]

        for loki in expired:
            os.kill(variants[loki].pid, 9)
            del variants[loki]
            del access_times[loki]

    def contains(loki: str):
        try:
            get(loki)
            return True
        except KeyError:
            return False

    return get, get_all, set, remove, contains, prune
