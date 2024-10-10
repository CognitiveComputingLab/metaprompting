"""
Default Action and State nodes
==============================

A simple example using the :class:`~metaprompting.DefaultAction` and :class:`~metaprompting.DefaultState`
classes."""

# %%
# Verbose Nodes
# -------------

# %%
# First, we define derived classes that print nicely and make the dynamic calls visible

from metaprompting import State, Action, Graph, connect

class VerboseAction(Action):

    def __repr__(self):
        return f"Action({id(self)})"

    def input_trigger(self, input):
        print(f"{self} was triggered by {input}")
        if super().input_trigger(input):
            print(f"{self} was executed")
        else:
            print(f"{self} was NOT executed")

    def execute(self):
        print(f"executing {self}")
        return super().execute()

class VerboseState(State):

    def __repr__(self):
        return f"State({id(self)})"

    def update(self, text, *args, **kwargs):
        print(f"updating {self}")
        super().update(text)

# %%
# Basic Manual Setup
# ------------------

# %%
# We can manually create a graph of connected state and action nodes using basic operations.
#
# For this, we create the state nodes, create the action nodes, and connect them (note that the order matters)
root_1 = VerboseState()
root_2 = VerboseState()
root_3 = VerboseState()
leaf_1 = VerboseState()
leaf_2 = VerboseState()

action_1 = VerboseAction()
action_2 = VerboseAction()

connect([root_1, root_2, root_3], action_1)
connect([root_3, root_2, root_1], action_2)
connect(action_1, leaf_1)
connect(action_2, leaf_2)

# %%
# Updating all root state nodes triggers a cascade of executions and updates (execution of an action only happens
# after all inputs were updated)
root_1.update("smoke")
root_2.update(" and ")
root_3.update("mirrors")

# %%
# Note how the different input order leads to different values in the two leaf nodes
print(leaf_1.value)
print(leaf_2.value)

# %%
# Graph Objects
# -------------
#
# The :class:`~metaprompting.Graph` class holds all nodes and provides some convenience functions for working
# with graphs.

graph = Graph()

(root_1_, root_2_, root_3_,
 leaf_1_, leaf_2_) = graph.add_states([VerboseState(), VerboseState(), VerboseState(),
                                       VerboseState(), VerboseState()])

graph.connect_action([root_1_, root_2_, root_3_], VerboseAction(), leaf_1_, add=True)
graph.connect_action([root_3_, root_2_, root_1_], VerboseAction(), leaf_2_, add=True)

print(list(graph.states))
print(list(graph.actions))

root_1.update("smoke")
root_2.update(" and ")
root_3.update("mirrors")

print(leaf_1.value)
print(leaf_2.value)
