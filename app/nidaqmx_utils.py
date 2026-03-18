from functools import singledispatch
from typing import Any
import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.system import System
from nidaqmx.system.device import Device
from utils.logging import logged, info, warn, error
import json
import asyncio
import numpy as np
from nidaqmx_types import Sinewave, Rectwave

CLEANUP_VALUES = {
    "min_val": 0,
    "max_val": 0.05
}

@logged
def get_device(device_name: str | None = None, channel: str = 'ao0'):
    try:
        system = System.local()
        avaliable_devices = [device.name for device in system.devices]

        if len(avaliable_devices) == 0:
            raise ValueError("No decices connected!")

        if not device_name:
            device_name = avaliable_devices[0]

        if device_name not in avaliable_devices:
            raise ValueError(f"Device {device_name} not found. Available devices: {avaliable_devices}")
        config = {
            "device_name": device_name,
            "channel": f"{device_name}/{channel}",
            "device": Device(device_name),
        }
        info(json.dumps(config))
        return config
    except Exception as e:
        error(f"Error setting up device configuration: {e}")
        raise

@logged
def close_task(task: nidaqmx.Task | None):
    if not task:
        warn(f"trying to close {device_config}, but no actice task.")
    else:
        try:
            task.stop()
            task.close()
            info(f"Task {task.name} closed.")
        except:
            error(f"Failed closing task {task.name}")

@logged
async def cleanup(device_config: dict[str, Any]):
    task = device_config.get("task")
    close_task(task)

    try:
        channel = device_config.get("channel")
        if not channel:
            raise ValueError("No channel defined for cleanup")
        reset = nidaqmx.Task()
        reset.ao_channels.add_ao_voltage_chan(channel, **CLEANUP_VALUES)
        reset.write(0.0, auto_start=True)
        await asyncio.sleep(0.1)
        close_task(reset)
        info("io_channel reset to 0V")
    except nidaqmx.errors.nidaqmx.DaqError as e:
        error(f"NI-DAQmxerror during cleanup: {e}")
        raise
    except Exception as e:
        error(f"General error during cleanup: {e}")
        raise

    return device_config.copy().pop("task", None)

@logged 
def create_task(
    config: dict,
    stim_amplitude: float = 0.4,
    counter_ratio: float = 1.0,
    **kwargs
):
    task = nidaqmx.Task() 
    channel = config.get("channel")
    task.ao_channels.add_ao_current_chan(
        channel,
        min_val = -stim_amplitude * counter_ratio,
        max_val = stim_amplitude 
    )
    config["task"] = task
    return config

@singledispatch
def construct_wave(
    mode,
    freq: float = 4.0,
    sample_rate: float = 20000,
    duration: float = 1.0,
    stim_amplitude: float = 0.05,
    counter_ratio: float = 1.0,
    **kwargs
):
    return np.array([])

@construct_wave.register
def _(
    mode: Sinewave,
    freq: float = 4.0,
    sample_rate: float = 20000,
    duration: float = 1.0,
    stim_amplitude: float = 0.05,
    counter_ratio: float = 1.0,
    **kwargs
):
    total_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    t[t<0] *= counter_ratio
    return stim_amplitude * np.sin(2* np.pi * freq * t)

@construct_wave.register
def _(
    mode: Rectwave,
    freq: float = 4.0,
    sample_rate: float = 100000,
    duration: float = 2.0,
    stim_amplitude: float = 0.4,
    counter_ratio: float = 0.2,
    **kwargs
):
    period = 1.0 / freq
    working_time = mode.main_width + mode.break_time + mode.counter_width
    if working_time > period:
        raise ValueError("Duration of one rectwave to long!")
    baseline_time = period - working_time
    main_samples = int(round(mode.main_width * sample_rate))
    break_samples = int(round(mode.break_time * sample_rate))
    counter_samples = int(round(mode.counter_width * sample_rate))
    baseline_samples = int(round(baseline_time * sample_rate))
    A = stim_amplitude
    C = stim_amplitude * counter_ratio * (-1.0)
    cycle = np.concatenate([
        A * np.ones(main_samples),
        np.zeros(break_samples),
        C * np.ones(counter_samples),
        np.zeros(baseline_samples)
    ])
    total_samples = int(duration * sample_rate)
    repeats = int(np.ceil(duration * freq))
    return np.tile(cycle, repeats)[:total_samples]

@logged 
def send_charge(
    device_config: dict[str, Any],
    waveform: np.ndarray,
    duration: float = 1.0,
    sample_rate: int = 100_000,
    **kwargs
):
    task = device_config["task"]
    task.timing.cfg_samp_clk_timing(
        rate=sample_rate,
        sample_mode=AcquisitionType.FINITE,
        samps_per_chan=int(duration * sample_rate)
    )
    task.write(waveform, auto_start=True)
