from typing import Literal


SOURCE = Literal[
    "ambe",
    "ar-37",
    "kr-83m",
    "rn-220",
    "led",
    "pulser",
    "noise",
    "none",
    "th-228",
    "th-232",
    "Y88",
    "YBe",
]

DIFFUSED_SOURCE = Literal["rn-220", "kr-83m", "ar-37"]

DETECTOR = Literal["tpc", "neutron_veto", "muon_veto", "tpc_he"]

PARTITION = Literal["all_tpc", "ab", "cd"]