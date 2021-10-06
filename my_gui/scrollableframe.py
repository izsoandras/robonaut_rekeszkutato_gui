import tkinter


# Source: https://blog.tecladocode.com/tkinter-scrollable-frames/
class ScrollableFrame(tkinter.Frame):
    def __init__(self, parent, child: tkinter.Frame, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        canvas = tkinter.Canvas(self)
        scrollbar = tkinter.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.child = child

        self.child.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all"), width=self.child.winfo_width()
            )
        )

        canvas.create_window((0, 0), window=self.child, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        # canvas.configure(highlightbackground='pink', highlightthickness=1)