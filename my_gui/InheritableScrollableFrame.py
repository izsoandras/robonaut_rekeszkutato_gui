import tkinter


# Source: https://blog.tecladocode.com/tkinter-scrollable-frames/
class ScrollableFrame(tkinter.Frame):
    def __init__(self, parent, *args, **kwargs):
        self.parent = tkinter.Frame(parent)
        self.canvas = tkinter.Canvas(self.parent)
        super().__init__(self.canvas, *args, **kwargs)
        self.scrollbar = tkinter.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)

        self.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"), width=self.winfo_width()
            )
        )

        self.canvas.create_window((0, 0), window=self, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)
        # self.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

    def pack_parent(self, *args, **kwargs):
        self.parent.pack(*args, **kwargs)

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)),'units')

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all('<MouseWheel>', self.on_mouse_wheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all('<MouseWheel>')
