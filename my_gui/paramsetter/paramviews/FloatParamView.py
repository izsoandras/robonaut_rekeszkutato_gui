import my_gui.paramsetter.paramviews.ParamView


class FloatParamView(my_gui.paramsetter.paramviews.ParamView.ParamView):

    def __init__(self, parent, name, *args, **kwargs):
        my_gui.paramsetter.paramviews.ParamView.ParamView.__init__(self, parent, name, *args, **kwargs)

    def validate_input(self, input_value: str):
        if input_value == '':
            return True

        try:
            float(input_value)
            return True
        except ValueError:
            return False

    def get_new_value(self):
        return float(self.tb_set_value.get())

    def get_current_value(self):
        return float(self.stvar_current.get())
