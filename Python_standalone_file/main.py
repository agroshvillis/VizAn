#!/usr/bin/env python3

from cobra.flux_analysis import flux_variability_analysis
import cobra.io as cio
import VizAn_1_0_0 as VizAn


def main(model_filename='iML1515.json', analysis=None, analysis_type='FBA'):
    model = cio.load_json_model(model_filename)
    if analysis is None:
        sol = model.optimize()
        sol.fluxes = sol.fluxes.round(5)
    else:
        sol = analysis
    prod = 'prod'
    subst = 'subst'
    count = '0'
    VizAn.Call_Vizan(model, sol, analysis_type, prod, subst, count)


def perform_visualisation(model_file_path='iML1515.json', svg_file_path='E_coli_source.svg', analysis_type='FBA',
                          analysis_results=None):
    model = cio.load_json_model(model_file_path)
    if analysis_results is None:
        fba_results = model.optimize()
        if analysis_type == 'FBA':
            fba_results.fluxes = fba_results.fluxes.round(5)
            analysis_results = fba_results
        elif analysis_type == 'FVA':
            fva_results = flux_variability_analysis(model, fraction_of_optimum=0.5)
            fva_results.round(3)
            analysis_results = fva_results

    prod = 'prod'
    subst = 'subst'
    count = '0'
    VizAn.call_vizan_cli(model, svg_file_path, analysis_results, analysis_type, prod, subst, count)


if __name__ == "__main__":
    # execute only if run as a script
    perform_visualisation()
