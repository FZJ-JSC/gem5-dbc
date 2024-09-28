import m5

class m5_TournamentBP(m5.objects.TournamentBP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_BiModeBP(m5.objects.BiModeBP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_LocalBP(m5.objects.LocalBP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_TAGEBP(m5.objects.TAGE):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class m5_MultiperspectivePerceptron64KB(m5.objects.MultiperspectivePerceptron64KB):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
