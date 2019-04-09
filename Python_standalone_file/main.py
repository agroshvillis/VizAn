#!/usr/bin/env python3

import cobra
import VizAn_1_0_0 as VizAn


def main(model_filename='iML1515.json', analysis=None, analysis_type='FBA'):
    model = cobra.io.load_json_model(model_filename)
    if analysis is None:
        sol = model.optimize()
        sol.fluxes = sol.fluxes.round(5)
    else:
        sol = analysis
    prod = 'prod'
    subst = 'subst'
    count = '0'
    VizAn.Call_Vizan(model, sol, analysis_type, prod, subst, count)


if __name__ == "__main__":
    # execute only if run as a script
    main()
