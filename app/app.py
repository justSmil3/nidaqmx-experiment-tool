from pandas.core.generic import sample
from nidaqmx_utils import ( 
    get_device, 
    close_task, 
    cleanup, 
    create_task, 
    construct_wave, 
    send_charge
)
from sthelper import render_class_inputs, show_wave, init_dataclass_state
from nidaqmx_types import SCHEMAS
import streamlit as st
import time

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
for k, v in PRESET_SINE.items():
    if k not in st.session_state:
        st.session_state[k] = v

for k, v in SCHEMAS.items():
    init_dataclass_state(k, v)


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

show_wave(st.session_state["prev_wave"])

if st.button("Start"):
    config_dict = get_device(device_name=device_name, channel=channel)
    config_dict = create_task(config_dict, stim_amplitude, counter_ratio)
    st.success("started")
    send_charge(config_dict, waveform, duration, int(sample_rate))
    time.sleep(duration + 0.05)
    st.success("done")


