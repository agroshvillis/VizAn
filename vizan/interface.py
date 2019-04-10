from __future__ import absolute_import
from .utils import final_output_svg_file_name
from .visualisation import _call_vizan_cli, _create_visualisation


#####
#########################  Main function to call VizAn
########## Call_Vizan(model,file_source_path,sol,SolutionType,prod,subst,count)
#################### model - metabolic model of organism
#################### file_source_path - using tkinker open window choose metabolic network layout file in SVG format developed according to the manual
#################### SolutionAnalysis - Flux Balance Analysis (FBA) or Flux Variability Analysis (FVA) optimisation results
#################### SolutionType - optional input where "FBA": FBA type visualization "FVA" : FVA type visualization
#################### prod - the analysis product name(s)
#################### subst - the analysis substrate name(s)
#################### count - arbitrary parameter for condition specific classification (any symbol or string)
#####


def Call_Vizan(model, SolutionAnalysis, SolutionType, prod, subst, count):
    try:
        # for Python2
        import Tkinter as tk
        from tkinter import tkFileDialog

        root = tk.Tk()
        root.withdraw()
        file_source_path = tkFileDialog.askopenfilename()

    except ImportError:

        # for Python3
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        file_source_path = tk.filedialog.askopenfilename()
    output_filename = final_output_svg_file_name(prod, subst, count)
    call_vizan_cli(model, file_source_path, SolutionAnalysis, SolutionType, output_filename)


def call_vizan_cli(model, file_source_path, SolutionAnalysis, SolutionType, output_filename,
                   intermediate_filename='pysvg_developed_file.svg'):
    return _call_vizan_cli(model, file_source_path, SolutionAnalysis, SolutionType, output_filename,
                           intermediate_filename)


def visualise(model_filename, svg_filename, output_filename, analysis_type='FBA',
              analysis_results=None):
    return _create_visualisation(model_filename, svg_filename, output_filename, analysis_type,
                                 analysis_results)
