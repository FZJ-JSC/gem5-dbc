import m5

class m5_ClockDomain(m5.objects.ClockDomain):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_VoltageDomain(m5.objects.VoltageDomain):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_SrcClockDomain(m5.objects.SrcClockDomain):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_SrcClockVoltage(m5_SrcClockDomain):
    def __init__(self, clock: str = "1GHz", voltage: str = "1.0V"):
        voltage_domain = m5_VoltageDomain(voltage=voltage)
        super().__init__(clock=clock, voltage_domain=voltage_domain)
