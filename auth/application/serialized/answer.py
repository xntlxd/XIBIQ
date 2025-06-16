from application.serialized.tuned import TunedModel


class Answer(TunedModel):
    data: dict | list | None = None
    message: str | None = None
