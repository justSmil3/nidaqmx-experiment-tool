from pandas.core.generic import sample
from nidaqmx_utils import ( 
    get_device, 
    cleanup, 
    create_task, 
    construct_wave, 
    send_charge,
    get_v_at_t
)
from sthelper import render_class_inputs, show_wave, init_dataclass_state
from logging_helper import save_wave, save_log, init_logging_dir
from nidaqmx_types import SCHEMAS
import streamlit as st
import time


def log_press():
    if not st.session_state["running"] or st.session_state["started_at"] is None:
        return

    now = time.monotonic()
    elapsed = now - st.session_state["started_at"]
    v = get_v_at_t(st.session_state["wave"], elapsed, st.session_state["duration"])
    st.session_state["presses"].append({
            "second": elapsed,
            "mV": v * 1000
        })

def start_run():
    if st.session_state["running"]:
        return

    st.session_state["running"] = True
    st.session_state["stop_requested"] = False
    st.session_state["presses"] = []

    started = time.monotonic()
    st.session_state["started_at"] = started




def stop_run():
    st.session_state["stop_requested"] = True
    st.success("stopped")

# ---------- defaults ----------

PRESET_SINE = {
    "duration": 1.0,
    "sample_rate": 20000,
    "stim_amplitude": 0.05,
    "counter_ratio": 1.0,
    "freq": 4.0
}

PRESET_RECT = {
    "duration": 2.0,
    "sample_rate": 100000,
    "stim_amplitude": 0.4,
    "counter_ratio": 0.2,
    "freq": 10.0
}


# ---------- init session state ----------

initial_values = {
    "running": False,
    "started_at": None,
    "presses": [],
    "stop_requested": False
}

for k, v in PRESET_SINE.items():
    if k not in st.session_state:
        st.session_state[k] = v

for k, v in SCHEMAS.items():
    init_dataclass_state(k, v)

for k, v in initial_values.items():
    if k not in st.session_state:
        st.session_state[k] = v

init_logging_dir()


st.title("Nidaqmx Simulator UI")
st.subheader("General Settings")
col1, col2 = st.columns(2)

if col1.button("Sine Wave Preset"):
    st.session_state.update(PRESET_SINE)

if col2.button("Rect Wave Preset"):
    st.session_state.update(PRESET_RECT)

device_name = st.text_input("Device Name", value="Dev1")
channel = st.text_input("Channel", value="ao0")
duration = st.number_input("Run duration", key="duration")
sample_rate = st.number_input("Sample rate", key="sample_rate")
stim_amplitude = st.number_input("Stimulation amplitude", key="stim_amplitude")
counter_ratio = st.number_input("Counter ratio for negative amplitude", key="counter_ratio")
freq = st.number_input("Frequency", key="freq")

st.subheader("Wave Settings")
selected_name = st.selectbox("Wave type", options=list(SCHEMAS.keys()))
selected_schema = SCHEMAS[selected_name]

config = render_class_inputs(selected_name, selected_schema)

waveform = construct_wave(config, freq, sample_rate, duration, stim_amplitude, counter_ratio)

st.subheader(f"Preview")
wcol1, wcol2 = st.columns(2)

st.session_state["prev_wave"] = waveform[:int(1.0/freq*sample_rate)]

if wcol1.button("Show Full Signal"):
    st.session_state.update({"prev_wave": waveform})

if wcol2.button("Show One Cycle"):
    st.session_state.update({"prev_wave": waveform[:int(1.0/freq*sample_rate)]})

show_wave(st.session_state["prev_wave"][::int(1/(1000/sample_rate))])

bc1, bc2, bc3 = st.columns(3)

if bc1.button("Start"):
    st.session_state["wave"] = waveform
    config_dict = get_device(device_name=device_name, channel=channel)
    config_dict = create_task(config_dict, stim_amplitude, counter_ratio)
    send_charge(config_dict, waveform, duration, int(sample_rate))
    st.success("started")
    start_run()


if bc2.button("Stop"):
    stop_run()

bc3.button("track", shortcut="space", on_click=log_press)
 
if st.session_state["running"]:
    while True:
        if st.session_state["stop_requested"]:
            break

        elapsed = time.monotonic() - st.session_state["started_at"]
        if elapsed >= duration + 0.05:
            break

        time.sleep(0.001)

    st.session_state["running"] = False
    st.session_state["stop_requested"] = False
    _ = cleanup(config_dict)
    st.success("done")
    steps = []
    for press in st.session_state["presses"]:
        step = int((press["second"] / st.session_state["duration"]) * st.session_state["wave"].size)
        steps.append(step)
    save_wave(st.session_state["wave"], steps)
    save_log(st.session_state["presses"])
    print(st.session_state["presses"])
