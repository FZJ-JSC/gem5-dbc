import m5


class m5_SimpleBTB(m5.objects.SimpleBTB):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_LocalBP(m5.objects.LocalBP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_TournamentBP(m5.objects.TournamentBP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_BiModeBP(m5.objects.BiModeBP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_TAGEBase(m5.objects.TAGEBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_LoopPredictor(m5.objects.LoopPredictor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_TAGE(m5.objects.TAGE):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class m5_LTAGE(m5.objects.LTAGE):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
