from itertools import chain, count

from metaprompting import make_iterable, read_multiline_input, State, Action


class Graph:

    def __init__(self, states=(), actions=()):
        self.states = set()
        self.actions = set()
        self.add_states(states)
        self.add_actions(actions)

    def add_states(self, states):
        states = make_iterable(states)
        for s in states:
            self.states.add(s)
        if len(states) == 1:
            return states[0]
        else:
            return states

    def add_actions(self, actions):
        actions = make_iterable(actions)
        for a in actions:
            self.actions.add(a)
        if len(actions) == 1:
            return actions[0]
        else:
            return actions

    def _assert_is_node(self, node, add=False):
        if isinstance(node, State):
            if node not in self.states:
                if add:
                    self.add_states(node)
                    return
                else:
                    raise KeyError(f"State {node} is not in this graph")
            else:
                return
        if isinstance(node, Action):
            if node not in self.actions:
                if add:
                    self.add_actions(node)
                    return
                else:
                    raise KeyError(f"Action {node} is not in this graph")
            else:
                return
        raise KeyError(f"Node {node} is neither "
                       f"State ({isinstance(node, State)}) nor "
                       f"Action node ({isinstance(node, Action)})")

    def connect_action(self, input_nodes, action, output_node, force=False, add=False):
        input_nodes = make_iterable(input_nodes)
        for n in input_nodes:
            self._assert_is_node(n)
        self._assert_is_node(output_node)
        self._assert_is_node(action, add=add)
        connect(from_nodes=input_nodes, to_nodes=action, force=force)
        connect(from_nodes=action, to_nodes=output_node, force=force)
        return action


class Conversation(Graph):

    def __init__(self, input_state=None, output_state=None, multiline=False, states=(), actions=()):
        super().__init__(states=states, actions=actions)
        self.input_state = input_state
        self.output_state = output_state
        self.multiline = multiline
        self.user_prefix = "You: "
        self.response_prefix = "LLM: "

    def run(self, n_interactions=None, pre_input_callback=None, post_input_callback=None, post_response_callback=None):
        if n_interactions is None:
            it = count()
        else:
            it = range(n_interactions)
        for i in it:
            if pre_input_callback is not None:
                pre_input_callback()
            # get user input and update input node
            if self.multiline:
                msg = read_multiline_input(self.user_prefix)
            else:
                msg = input(self.user_prefix)
            self.input_state.update(msg)
            if post_input_callback is not None:
                post_input_callback()
            # print response
            print(self.response_prefix + self.output_state.value)
            if post_response_callback is not None:
                post_response_callback()



def connect(from_nodes, to_nodes, force=False):
    # handle single node arguments
    from_nodes = make_iterable(from_nodes)
    to_nodes = make_iterable(to_nodes)
    # connect all possible 'from' --> 'to' pairs
    for fn in from_nodes:
        for tn in to_nodes:
            if isinstance(fn, State) and isinstance(tn, Action):
                # state --> action connection
                fn.add_output_actions(tn)
                tn.add_input_states(fn)
            elif isinstance(fn, Action) and isinstance(tn, State):
                # action --> state connection
                fn.set_output_state(tn, force=force)
                tn.set_input_action(fn, force=force)
            else:
                raise RuntimeError("Can only connect State to Action or Action to State node")
