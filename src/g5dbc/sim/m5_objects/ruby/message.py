import m5

class m5_MessageBuffer(m5.objects.MessageBuffer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MandatoryMessageBuffer(m5.objects.MessageBuffer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class TriggerMessageBuffer(m5.objects.MessageBuffer):
    randomization = 'disabled'
    allow_zero_latency = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class OrderedTriggerMessageBuffer(TriggerMessageBuffer):
    ordered = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
