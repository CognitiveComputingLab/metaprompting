from abc import ABC, abstractmethod
from time import sleep

import pyperclip

from metaprompting import read_multiline_input


class LLM(ABC):

    @abstractmethod
    def __call__(self, prompt, *args, **kwargs):
        """
        Call the LLM with given arguments and return its output.
        """
        raise NotImplemented


class CopyPasteLLM(LLM):

    def __init__(self, multiline=True, auto_copy_paste=False, instructions=True):
        self.multiline = multiline
        self.auto_copy_paste = auto_copy_paste
        self.instructions = instructions

    def __call__(self, prompt, *args, **kwargs):
        if self.auto_copy_paste:
            pyperclip.copy(prompt)
            if self.instructions:
                print("COPY-PASTE LLM: The LLM prompt has been copied to your clipboard. "
                      "Please paste it into your LLM and copy the response. "
                      "The clipboard will be automatically monitored and the "
                      "response is read out as soon as it is copied in.")
            while True:
                sleep(0.01)
                response = pyperclip.paste()
                if response != prompt:
                    return response
        else:
            if self.instructions:
                print("COPY-PASTE LLM: Copy-paste the text in between the >>>/<<< lines to your LMM")
            print(">>>")
            print(prompt)
            print("<<<")
            if self.instructions:
                print("COPY-PASTE LLM: Copy-paste your LLM response here!")
            if self.multiline:
                if self.instructions:
                    print("COPY-PASTE LLM: (use enter for new lines and Ctrl-D to send)")
                return read_multiline_input()
            else:
                return input()
