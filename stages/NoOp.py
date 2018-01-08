from .BaseStage import BaseStage


class NoOp(BaseStage):
    def execute(self):
        pass
