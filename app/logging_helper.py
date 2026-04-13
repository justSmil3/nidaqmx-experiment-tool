import numpy as np
import matplotlib.pyplot as plt
import datetime
import os
import random
import string
import json
from pathlib import Path

PATH = Path("log")

def init_logging_dir():
    if not os.path.exists(PATH):
        os.makedirs(PATH)

def save_wave(
    wave: np.ndarray,
    steps: list[int],
    output_name: str = "wave"
):
    appendix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    out_path = output_name + appendix + ".jpg"

    if wave.ndim != 1:
        raise ValueError("wave must be a 1D ndarray")

    plt.figure(figsize=(12,4))
    plt.plot(wave, linewidth=1)

    for step in steps: 
        if 0 <= step < len(wave):
            plt.axvline(x=step, color="red", linestyle="-", linewidth=1)

    plt.xlabel("sample")
    plt.ylabel("voltage")
    plt.title("Wave")
    plt.tight_layout()
    plt.savefig(PATH / out_path, format="jpg")
    plt.close()

def save_log(data, run_id = ""):
    if run_id == "":
        run_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    with open(PATH / f"{run_id}.txt", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
