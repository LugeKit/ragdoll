from typing import LiteralString, AnyStr, Callable

Str = LiteralString | AnyStr
Callback = Callable[[Str], None]


class Error(RuntimeError):
    pass


class StateNotFound(Error):
    pass


class StateTransIllegal(Error):
    pass


class State:
    def __init__(
            self,
            name: Str,
            next_states: set[Str] = None,
            on_enter: Callback | None = None,
            on_exit: Callback | None = None
    ):
        if next_states is None:
            next_states = set[Str]()
        self.name = name
        self.next_states = next_states
        self.on_enter = on_enter
        self.on_exit = on_exit


class Machine:
    def __init__(self, states: set[State], initial_state: Str):
        self._states = {}
        for state in states:
            self._states[state.name] = state

        for state in states:
            for next_state in state.next_states:
                if next_state not in self._states:
                    raise StateNotFound(f"{state.name}'s next state: {next_state} is not in states")

        if initial_state not in self._states:
            raise StateNotFound(f"initial state: {initial_state} is not in states")

        self._state = self._states[initial_state]

    def trans_to(self, next_state_name: Str):
        if next_state_name not in self._states:
            raise StateNotFound(f"{next_state_name} is not in current state machine")

        if next_state_name not in self._state.next_states:
            raise StateTransIllegal(f"{next_state_name} can not be trans from {self._state}")

        next_state = self._states[next_state_name]
        curr_state_name = self._state.name

        if self._state.on_exit:
            self._state.on_exit(next_state_name)

        self._state = next_state

        if self._state.on_enter:
            self._state.on_enter(curr_state_name)

    def state(self):
        return self._state.name
