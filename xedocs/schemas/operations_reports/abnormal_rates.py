from .base_report import BaseOperationsReport


class AbnormalDAQRate(BaseOperationsReport):
    """Abnormal DAQ rate report"""

    _ALIAS = "abnormal_daq_rates"

    anode_voltage_kv: float
    action_taken: str
    plot: str

    reader0_rate: float
    reader1_rate: float
    reader2_rate: float
    muon_veto_rate: float
    nveto_rate: float
