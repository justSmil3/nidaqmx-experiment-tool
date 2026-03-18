from __future__ import annotations
import numpy as np
import streamlit as st
import pandas as pd
from typing import Any

from dataclasses import fields
def init_dataclass_state(prefix: str, cls: type[Any]) -> None:
    for f in fields(cls):
        key = f"{prefix}_{f.name}"
        if key not in st.session_state:
            st.session_state[key] = getattr(cls, f.name)

def render_class_inputs(prefix: str, cls: type[Any]) -> Any:
    init_dataclass_state(prefix, cls)

    values = {}
    for f in fields(cls):
        key = f"{prefix}_{f.name}"

        if f.type is int:
            values[f.name] = st.number_input(f.name, key=key, step=1)
        elif f.type is float:
            values[f.name] = st.number_input(f.name, key=key, format="%.6f", value=st.session_state[key])
        elif f.type is str:
            values[f.name] = st.text_input(f.name, key=key)
        elif f.type is bool:
            values[f.name] = st.checkbox(f.name, key=key)
        else:
            values[f.name] = st.text_input(f"{f.name} ({f.type})", key=key)


    return cls(**values)

def show_wave(y: np.ndarray) -> None:
    df = pd.DataFrame({
        "sample": np.arange(len(y)),
        "amplitude": y,
    })
    st.line_chart(df, x="sample", y="amplitude")
