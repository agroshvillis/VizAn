from __future__ import absolute_import

from .visualisation import _create_visualisation


def visualise(model_filename, svg_filename, output_filename, analysis_type='FBA',
              analysis_results=None):
    """

    :param model_filename: a filename string, which gives JSON metabolic model of an organism
    :param svg_filename: a filename string, which gives SVG map of pathways, that is made based on Manual.rst
    :param output_filename: a filename string, which specifies where to save the resulting SVG map
    :param analysis_type: "FBA" or "FVA" string, to specify type of visualisation
    :param analysis_results: optional FBA or FVA results to be given (otherwise they are calculated using defaults(
    :return: None
    """
    return _create_visualisation(model_filename, svg_filename, output_filename, analysis_type,
                                 analysis_results)
