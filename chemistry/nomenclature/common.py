from utilities.io import prompt_regex

acid_ext = [('hypo', 'ous'), ('', 'ous'), ('', 'ic'), ('per', 'ic')]
anion_ext = [('hypo', 'ite'), ('', 'ite'), ('', 'ate'), ('per', 'ate')]


def name_anion():
    anion = prompt_regex("name of the anion element", r"[a-zA-Z]+").lower()
    if anion == 'oxygen':
        anion = 'ox'
    elif anion == 'nitrogen':
        anion = 'nitr'
    elif anion == 'sulfur':
        anion = 'sulf'
    elif anion == 'fluorine':
        anion = 'fluor'
    elif anion == 'chlorine':
        anion = 'chlor'
    elif anion == 'bromine':
        anion = 'brom'
    elif anion == 'iodine':
        anion = 'iod'
    elif anion == 'phosphorus':
        anion = 'phosph'
    else:
        print("i dont know about this anion, result could be wrong")

    ic = int(prompt_regex("-ic prefix amount", r"[0-9]+", "3"))
    nox = int(prompt_regex("number of oxygen", r"[0-9]+", '0'))

    if nox == 0:
        bprefix, bsuffix = '', 'ide'
    else:
        bprefix, bsuffix = anion_ext[nox - ic + 2]

    name = f'{bprefix}{anion}{bsuffix}'
    print(f'your anion is called {name}')

# Make this if you wish
# def name_acid():
#
#     acid = prompt_regex("name of the acid element", r"[a-zA-Z]+").lower()
#
#     ic = int(prompt_regex("-ic prefix amount", r"[0-9]+", "3"))
#     nox = int(prompt_regex("number of oxygen", r"[0-9]+", '0'))
#
#     if nox == 0:
#         aprefix, asuffix = 'hydro', 'ic'
#     else:
#         aprefix, asuffix = acid_ext[nox - ic + 2]
#
#     name = f'{aprefix}{acid}{asuffix}'
#     print(f'your acid is called {name}')


if __name__ == '__main__':
    name_anion()
