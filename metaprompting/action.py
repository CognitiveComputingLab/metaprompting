from abc import ABC

from metaprompting import make_iterable, LLM


class Action(ABC):

    def __init__(self):
        """
        An executable node that takes zero or more input_states, executes an action, and returns its output to the
        output_state.

        :param input_states: Iterable over input :class:`~State`\s
        :param output_state: Output :class:`~State`
        """
        self._input_states = []
        self._inputs_updated = {}
        self._output_state = None
        self._block = 0

    def block(self, state=True):
        self._block = state

    def add_input_states(self, states):
        states = make_iterable(states)
        for s in states:
            self._input_states.append(s)
            self._inputs_updated[s] = False

    def set_output_state(self, state, force=False):
        if self._output_state is not None and not force:
            raise RuntimeError("Output state is already set (use force=True to override)")
        self._output_state = state

    def input_trigger(self, input):
        """
        Trigger the :class:`~Action` from a specific input, typically when the input has been updated.

        :param input: input :class:`~State`
        """
        # remember updated inputs
        try:
            self._inputs_updated[input] = True
        except KeyError:
            raise KeyError("Given input is not an input of this node")
        # return False if any inputs are not updated
        for is_updated in self._inputs_updated.values():
            if not is_updated:
                return False
        # reset update flags
        for key in self._inputs_updated.keys():
            self._inputs_updated[key] = False
        # ignore if blocking active
        if self._block is True:
            return False
        if self._block > 0:
            self._block -= 1
            return False
        # execute otherwise
        self._execute()
        # return True to signal execution
        return True

    def _execute(self):
        """
        Excecute the :class:`~Action` with given arguments and pass on the output to the output :class:`~State`.
        """
        out = self.execute()
        # update output
        self._output_state.update(out)
        return out

    def execute(self):
        # simple action: concatenate inputs with " + " in between
        out = None
        for i in self._input_states:
            if out is None:
                out = i.value
            else:
                out = out + i.value
        return out


class LlmAction(Action):

    def __init__(self, llm: LLM, prompt_parts):
        super().__init__()
        self.llm = llm
        self.prompt_parts = list(prompt_parts)

    def execute(self):
        if len(self.prompt_parts) != len(self._input_states) + 1:
            raise RuntimeError(f"Number of prompt parts ({len(self.prompt_parts)}) must be one less than "
                               f"number of input states ({len(self._input_states)})")
        prompt = self.prompt_parts[0]
        for i, p in zip(self._input_states, self.prompt_parts[1:]):
            prompt += i.value + p
        return self.llm(prompt)


class HistoryAction(Action):

    def __init__(self):
        super().__init__()
        self.history = []

    def execute(self):
        self.history.append(tuple(i.value for i in self._input_states))
        out = ""
        for msgs in self.history:
            for i, msg in enumerate(msgs):
                out += f"Person {i + 1}: {msg}\n\n"
        return out
