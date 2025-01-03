from abc import ABC

from metaprompting import make_iterable

class State(ABC):

    def __init__(self):
        """
        A static node holding information generated by an input_action. It may pass on the information to zero or
        more output_actions.

        :param input_action: Input :class:`~Action`
        :param output_actions: Iterable over output :class:`~Action`\s
        """
        self._input_action = None
        self._output_actions = []
        self.value = None

    def set_input_action(self, action, force=False):
        if self._input_action is not None and not force:
            raise RuntimeError("Input action is already set (use force=True to override)")
        self._input_action = action

    def add_output_actions(self, actions):
        actions = make_iterable(actions)
        for a in actions:
            self._output_actions.append(a)

    def trigger_outputs(self):
        """
        Trigger all outputs of this :class:`~State`. Should typically be called at the end of :meth:`~update`.
        """
        for output in self._output_actions:
            output.input_trigger(self)

    def update(self, value, *args, **kwargs):
        self.value = value
        self.trigger_outputs()
