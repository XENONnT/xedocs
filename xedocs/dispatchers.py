import rframe
import pandas as pd


from typing import Any
from plum import dispatch


@dispatch
def json_serializable(value: Any):
    return value


@dispatch
def json_serializable(value: list):
    return [json_serializable(v) for v in value]


@dispatch
def json_serializable(value: tuple):
    return tuple(json_serializable(v) for v in value)


@dispatch
def json_serializable(value: dict):
    return {json_serializable(k): json_serializable(v) for k, v in value.items()}


@dispatch
def json_serializable(value: pd.Interval):
    return json_serializable((value.left, value.right))


@dispatch
def json_serializable(value: rframe.IntegerInterval):
    return value.left, value.right


@dispatch
def json_serializable(value: rframe.TimeInterval):
    return f"{str(value.left)} to {str(value.right)}"
