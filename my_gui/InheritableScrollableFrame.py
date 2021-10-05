import tkinter


# Source: https://blog.tecladocode.com/tkinter-scrollable-frames/
class ScrollableFrame(tkinter.Frame):
    def __init__(self, parent, *args, **kwargs):
        fr_canvas = tkinter.Frame(parent)
        canvas = tkinter.Canvas(fr_canvas)
        super().__init__(canvas, *args, **kwargs)
        scrollbar = tkinter.Scrollbar(fr_canvas, orient="vertical", command=canvas.yview)

        self.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all"), width=self.winfo_width()
            )
        )

        canvas.create_window((0, 0), window=self, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        fr_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)