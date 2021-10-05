import my_gui.paramsetter.paramviews.FloatParamView as fpv
import my_gui.paramsetter.paramviews.IntParamView as ipv
import my_gui.paramsetter.paramviews.UintParamView as uipv


def structString2paramView(parent, string: str, names):
    ret_dict = {}
    names_idx = 0
    for c in string:
        bigC = c.upper()
        if c in 'x><=@!':
            continue
        elif bigC in 'BHILQ':
            if bigC == 'B':
                bit_num = 8
            elif bigC == 'H':
                bit_num = 16
            elif bigC in 'IL':
                bit_num = 32
            elif bigC == 'Q':
                bit_num = 64
            else:
                raise Exception(f'Character idx {names_idx} in {string} is in BHILQ but neither B,H,I,L or Q')

            if c.isupper():
                new_view = ipv.IntParamView(parent, names[names_idx], bit_num)
            else:
                new_view = uipv.UintParamView(parent, names[names_idx], bit_num)

        elif c in 'fd':
            new_view = fpv.FloatParamView(parent, names[names_idx])
        else:
            raise NotImplementedError(f'Conversion for char {c} is not implemented!')

        ret_dict[names[names_idx]] = new_view
        names_idx = names_idx + 1

    return ret_dict
