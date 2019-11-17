# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
from tempfile import NamedTemporaryFile

import cobra.io as cio
from cobra.core.solution import Solution as CobraSolution
from cobra.flux_analysis import flux_variability_analysis

from .errors import CobraModelFileError, SVGMapFileError
from .utils import determine_format_and_parse_svg, draw_network, insert_interactive_script, insert_metabolite_ids


def _create_visualisation(model_filename, svg_filename, output_filename, analysis_type='FBA',
                          analysis_results=None, intermediate_filename=None):
    # Check arguments
    supported_analysis_types = {"FBA", "FVA"}
    if analysis_type not in supported_analysis_types:
        message = "Analysis type is wrong. It has to be one of the values: {}"
        raise ValueError(message.format(supported_analysis_types))
    try:
        model = cio.load_json_model(model_filename)
    except Exception as exc:
        raise CobraModelFileError("Failed to load model from given JSON : {}".format(exc.args))
    # Set default arguments if none provided
    if analysis_results is None:
        fba_results = model.optimize()
        if analysis_type == 'FBA':
            fba_results.fluxes = fba_results.fluxes.round(5)
            analysis_results = fba_results
        elif analysis_type == 'FVA':
            fva_results = flux_variability_analysis(model, fraction_of_optimum=0.5)
            fva_results = fva_results.round(3)
            analysis_results = fva_results
    vizan_kwargs = {
        'model': model,
        'file_source_path': svg_filename,
        'analysis_results': analysis_results,
        'analysis_type': analysis_type,
        'output_filename': output_filename,
    }
    if intermediate_filename is None:
        with NamedTemporaryFile(mode="w") as intermediate_file:
            vizan_kwargs['intermediate_filename'] = intermediate_file.name
            produce_output_file(**vizan_kwargs)
    else:
        vizan_kwargs['intermediate_filename'] = intermediate_filename
        produce_output_file(**vizan_kwargs)


def produce_output_file(model, file_source_path, analysis_results, analysis_type, output_filename,
                        intermediate_filename='pysvg_developed_file.svg'):
    try:
        svg_object = determine_format_and_parse_svg(file_source_path)
    except Exception as exc:
        raise SVGMapFileError("Failed to parse SVG pathway map : {}".format(exc.args))
    if type(analysis_results) == CobraSolution:
        flux_sum = calculate_common_substrate_flux(model)
    else:
        flux_sum = 0
    print('---------------------')
    draw_network(model, svg_object, analysis_results, flux_sum)
    svg_object.save(intermediate_filename)
    print('Network has been drawn')
    insert_interactive_script(intermediate_filename)
    insert_metabolite_ids(file_source_path, output_filename, intermediate_filename)
    if intermediate_filename == 'pysvg_developed_file.svg':
        os.remove(intermediate_filename)
    print('Metabolite ids have been added')


def calculate_common_substrate_flux(model):
    boundary_reactions = model.exchanges
    # generate model exchange reactions

    fva_results = flux_variability_analysis(
        model, reaction_list=boundary_reactions,
        fraction_of_optimum=1)
    # Generate FVA results

    fva_results = fva_results.sort_values(by='minimum', ascending=True)

    # sort FVA results ascending order

    substrates = fva_results['minimum'] < 0
    fva_results_substrates = fva_results[substrates].sort_values(by='minimum', ascending=True)

    # Generate dataframe where only consuming reactions are taken into account

    reaction_consist_carbon = []
    for reaction in fva_results_substrates.index:
        reaction_cobrapy = model.reactions.get_by_id(reaction)
        for metabolite in reaction_cobrapy.reactants:
            if 'C' in metabolite.elements.keys():
                reaction_consist_carbon.append(str(reaction))

    # Filter from FVA substrate list reactions which HAVE NOT included

    flux_sum = 0
    for reaction in reaction_consist_carbon:
        flux_sum = flux_sum + fva_results.loc[reaction, 'minimum']
    return flux_sum

    # Calculate flux sum how much is consumed all substrates (not taking into account carbon amount for each substrate)
    # to do is take into account substrate carbon ratio for better flux calculation
