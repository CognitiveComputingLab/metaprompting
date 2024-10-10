"""
Copy Paste LLM
==============================
"""

# %%
# The :class:`~metaprompting.base.CopyPasteLLM` class allows you to simulate an LLM API by copy-pasting over prompts
# and responses from/to the standard output/input.
#
# The script must be called with '--interactive' command line switch to use the
# :class:`~metaprompting.base.CopyPasteLLM` class, otherwise, we define a :class:`DummyLLM` class to simulate
# interaction for generating the documentation.

import sys

from metaprompting import State, LlmAction, HistoryAction, Conversation, LLM, CopyPasteLLM


if "--interactive" in sys.argv:
    interactive = True
    llm = CopyPasteLLM(
        auto_copy_paste=True,  # automatically: copy LLM prompt to clipboard; paste response back when clipboard changes
        instructions=False,  # don't print additional instructions
    )
else:
    class DummyLLM(LLM):

        def __call__(self, prompt, *args, **kwargs):
            return f"HERE BE THE RESPONSE TO THE FOLLOWING PROMPT\n\n{prompt}"

    interactive = False
    llm = DummyLLM()

# %%
# Create conversation graph with state nodes

graph = Conversation()
input_state, history_state, inner_speech_state, output_state = graph.add_states([State(), State(), State(), State()])
graph.input_state = input_state
graph.output_state = output_state

# %%
# Create and connect action nodes

# remember history
history_action = HistoryAction()
graph.connect_action([input_state, output_state], history_action, history_state, add=True)

# generate inner speech
inner_speech_action = LlmAction(llm=llm, prompt_parts=[
    "Here is the history of a conversation between Person 1 and Person 2:\n\n",
    "What are some general thoughts about this conversation?\n\n" +
    "Keep the output short and to a single paragraph of text-only without formatting, bullet points etc",
])
graph.connect_action(history_state, inner_speech_action, inner_speech_state, add=True)

# construct prompt for response
response_action = LlmAction(llm=llm, prompt_parts=[
    "Here is the history of a conversation between Person 1 and Person 2:\n\n",
    "\n\nSome general thoughts about this conversation are:\n\n",
    "\n\nThe most recent message from Person 1 is:\n\n",
    "\n\nWhat could Person 2 reply? Only print the reply itself, nothing else!",
])
graph.connect_action([history_state, inner_speech_state, input_state], response_action, output_state, add=True)

# %%
# Initialise nodes

inner_speech_state.update("This is the beginning of the conversation...")
inner_speech_action.block(1)  # block trigger from updating history
history_state.update("BEGINNING OF HISTORY\n\n")

# %%
# Run conversation interleaved with inner speech

if interactive:
    # for running in terminal with '--interactive' switch
    def print_inner_speech():
        print(f"Inner speech: {inner_speech_state.value}")
    print("Start a conversation (use Ctrl-C to cancel)!")
    graph.run(post_response_callback=print_inner_speech)
else:
    # for generating example in documentation
    input_state.update("Some user input...")
    print("========================")
    print("User Input")
    print("========================")
    print(input_state.value)
    print("========================")
    print("LLM Response")
    print("========================")
    print(output_state.value)
    print("========================")
    print("Inner Speech")
    print("========================")
    print(inner_speech_state.value)
    print("========================")
    print("History")
    print("========================")
    print(history_state.value)
    print("========================")
