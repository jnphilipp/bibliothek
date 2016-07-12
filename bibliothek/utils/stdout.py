# -*- coding: utf-8 -*-


def p(fields, line_length=100, after='_', positions=[.33, .55, .67, 1.]):
    if positions[-1] <= 1:
        positions = [int(line_length * p) for p in positions]

    def print_row(fields, positions):
        line = ''
        rfields = []
        for i in range(len(fields)):
            line += str(fields[i])

            if len(line) > positions[i]:
                rf = line.rfind(' ', positions[i - 1] if i > 0 else 0, positions[i])
                if rf > 0:
                    rfields.append(line[rf + 1:])
                    line = line[:rf]
                else:
                    line = line[:positions[i]]
                    rfields.append(line[positions[i]:])
            else:
                rfields.append('')
            line += ' ' * (positions[i] - len(line))
        print(line)
        if max([f != '' for f in rfields]):
            print_row(rfields, positions)

    print_row(fields, positions)
    if after:
        print(after * line_length)
