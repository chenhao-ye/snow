class Column:
    def __init__(self, data) -> None:
        self.name = data['name']
        self.type = data['type']
        self.options = None
        if self.type == 'select' or self.type == 'multi_select':
            self.options = list(o['name'] for o in data[self.type]['options'])

    def __str__(self) -> str:
        options_str = "" if self.options is None else f":{','.join(self.options)}"
        return f"{self.name} ({self.type}{options_str})"
