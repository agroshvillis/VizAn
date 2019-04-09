from __future__ import absolute_import


def final_output_svg_file_name(prod, subst, count):
    return str(prod) + "_" + str(subst) + "_" + str(count) + '.svg'
