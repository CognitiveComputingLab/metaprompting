"""
Default Action and State nodes
==============================

A simple example using the :class:`~metaprompting.base.DefaultAction` and :class:`~metaprompting.base.DefaultState`
classes."""

# %%
# Define derived classes to make the call dynamics visible

from metaprompting.base import DefaultAction, DefaultState


class VerboseAction(DefaultAction):

    def input_trigger(self, input):
        print(f"{self} was triggered by {input}")
        super().input_trigger(input)

    def execute(self, *args, **kwargs):
        print(f"executing {self}")
        super().execute(*args, **kwargs)


class VerboseState(DefaultState):

    def update(self, text):
        print(f"updating {self}")
        super().update(text)


# %%
# Create state nodes
root_1 = VerboseState()
root_2 = VerboseState()
root_3 = VerboseState()
leaf_1 = VerboseState()
leaf_2 = VerboseState()

# %%
# Create action nodes, which auto-connects states
action1 = VerboseAction(input_states=[root_1, root_2, root_3], output_state=leaf_1)
action2 = VerboseAction(input_states=[root_3, root_2, root_1], output_state=leaf_2)

# %%
# Update root state nodes, which triggers a cascade to leaf nodes
root_1.update("smoke")
root_2.update(" and ")
root_3.update("mirrors")

# %%
# Print output of leaf nodes
print(leaf_1.value)
print(leaf_2.value)
