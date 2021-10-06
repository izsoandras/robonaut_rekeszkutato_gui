import tkinter


# Source: https://blog.tecladocode.com/tkinter-scrollable-frames/
class ScrollableFrame(tkinter.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = tkinter.Frame(parent)
        canvas = tkinter.Canvas(self.parent)
        super().__init__(canvas, *args, **kwargs)
        scrollbar = tkinter.Scrollbar(self.parent, orient="vertical", command=canvas.yview)

        self.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all"), width=self.winfo_width()
            )
        )

        canvas.create_window((0, 0), window=self, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        # self.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

    def pack_parent(self, *args, **kwargs):
        self.parent.pack(*args, **kwargs)
