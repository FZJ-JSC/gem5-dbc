import m5


class Versions:
    _seqs = 0

    @classmethod
    def getSeqId(cls):
        val = cls._seqs
        cls._seqs += 1
        return val


class m5_RubySequencer(m5.objects.RubySequencer):
    def __init__(self, **kwargs):
        super().__init__(version=Versions.getSeqId(), **kwargs)
