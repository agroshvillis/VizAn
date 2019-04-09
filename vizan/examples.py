from __future__ import absolute_import
import cobra
from cobra.flux_analysis.variability import flux_variability_analysis
from .interface import Call_Vizan


def init_coli_model_FBA(prod, subst, count):
    model = cobra.io.load_json_model('iML1515.json')
    sol = model.optimize()
    sol.fluxes = sol.fluxes.round(5)

    SolutionType = "FBA"
    Call_Vizan(model, sol, SolutionType, prod, subst, count)


def init_coli_model_FVA(prod, subst, count):
    model = cobra.io.load_json_model('iML1515.json')
    fva_results = flux_variability_analysis(model, fraction_of_optimum=0.5)
    fva_results = fva_results.round(3)

    SolutionType = "FVA"
    Call_Vizan(model, fva_results, SolutionType, prod, subst, count)
