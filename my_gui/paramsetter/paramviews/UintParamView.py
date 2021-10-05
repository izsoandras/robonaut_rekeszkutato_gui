import my_gui.paramsetter.paramviews.ParamView


class UintParamView(my_gui.paramsetter.paramviews.ParamView.ParamView):

    def __init__(self, parent, name, bit_num=32, *args, **kwargs):
        my_gui.paramsetter.paramviews.ParamView.ParamView.__init__(self, parent, name, *args, **kwargs)
        self.bit_num = bit_num

    def validate_input(self, input_value: str):
        if input_value.isdigit() and int(input_value) >= 0:
            return True
        elif input_value == '':
            return True
        else:
            return False

    def get_new_value(self):
        return int(self.tb_set_value.get())

    def get_current_value(self):
        return int(self.stvar_current.get())
