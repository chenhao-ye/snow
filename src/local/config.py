import os
from collections import OrderedDict
from typing import Callable, Any
import json


class Config:

    class ConfigOption:

        def __init__(self, string) -> None:
            self.string = string

        def __str__(self) -> str:
            return self.string

    MISSING = ConfigOption("???")

    def __init__(self) -> None:
        self.entries = OrderedDict()
        self.values = {}
        self.parsed_values = {}

    def get_entries(self):
        return self.entries.items()

    def add(self,
            name: str,
            prompt: str,
            *,
            default: str = MISSING,
            hinter: Callable = None,
            parser: Callable = lambda x: x):
        """
        Add a configuration option.
        @param hinter accepts the current Config and return a string.
        @param parser processes input into actual value.
        """
        self.entries[name] = (prompt, hinter, parser)
        self.values[name] = default

    def set_val(self, name: str, val: str) -> None:
        # will raise exception of parser fails, need to catch
        assert name in self.entries
        _, _, parser = self.entries[name]
        parsed_val = parser(val)
        self.values[name] = val
        self.parsed_values[name] = parsed_val

    @property
    def is_all_set(self) -> bool:
        return all(self.values[name] is not self.MISSING
                   for name in self.entries.keys())

    def get_parsed_val(self, name: str) -> Any:
        if name not in self.parsed_values:
            _, _, parser = self.entries[name]
            self.parsed_values[name] = parser(self.values[name])
        return self.parsed_values[name]

    def load(self, path) -> None:
        with open(path, 'r') as f:
            self.values = json.load(f)

    def dump(self, path) -> None:
        path_tmp = f"{path}.tmp"
        with open(path_tmp, 'w') as f:
            json.dump(self.values, f, allow_nan=False, indent='\t')
            f.flush()
            os.fsync(f.fileno())
        os.rename(path_tmp, path)
        # TODO: it's a little tricky on whether to fsync after rename...

    def ask_interactive(self) -> None:
        """Ask the user interactively for configuration entries that don't already present"""
        updated_entries = set()
        for name, (prompt, hinter, parser) in self.entries.items():
            while True:
                #  if hinter is not None else ""
                hint_str = ''
                if hinter is not None:
                    hint_str = '\n\t      '.join(hinter().split('\n'))
                    hint_str = f"\n\tHint: {hint_str}\n"
                val = input(
                    f"< [{name}]: {prompt}\n\tCurrent: {self.values[name]}{hint_str}\n> "
                ).strip()
                try:
                    if val == "":
                        val = self.values[name]
                    if val is self.MISSING:
                        raise ValueError("Required value not provided")
                    parsed_val = parser(val)
                    self.values[name] = val
                    self.parsed_values[name] = parsed_val
                    updated_entries.add(name)
                    break
                except Exception as e:
                    print(f"Invalid value: {e}. Please retry.")

        print("\n------\nUpdated Configuration:")
        for name, (prompt, _, _) in self.entries.items():
            print(f"\t{name}{'*' if name in updated_entries else ' '}: "
                  f"{self.values[name]}")
