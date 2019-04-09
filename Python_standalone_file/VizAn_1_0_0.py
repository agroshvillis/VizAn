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





import os
import sys
import json
import numpy as np
import pandas as pd
import cobra
from cobra.flux_analysis import flux_variability_analysis
import pysvg
from tempfile import mkstemp
from shutil import move
from os import remove


import xml.etree.ElementTree as ET

from xml.dom import minidom
from xml.dom import Node

from pysvg.structure import Svg
for subpackage in ['core', 'filter', 'gradient', 'linking', 'script', 'shape', 'structure', 'style', 'text']:
    try:
        exec('from pysvg.' + subpackage + ' import *')
    except ImportError:
        pass
    
    
def init_coli_model_FBA(prod,subst,count):
    model=cobra.io.load_json_model('iML1515.json')
    sol=model.optimize()
    sol.fluxes=sol.fluxes.round(5)
        
    SolutionType="FBA"    
    Call_Vizan(model,sol,SolutionType,prod,subst,count)
    
def init_coli_model_FVA(prod,subst,count):
    model=cobra.io.load_json_model('iML1515.json')
    fva_results=flux_variability_analysis(model, fraction_of_optimum=0.5)
    fva_results=fva_results.round(3)  
        
        
    SolutionType="FVA"    
    Call_VizAn(model,fva_results,SolutionType,prod,subst,count)

    
    
##_______________________________________________________________________________________________________________________



def calculateMethodName(attr):
    name=attr
    name=name.replace(':','_')
    name=name.replace('-','_')
    name='set_'+name
    return name

def setAttributes(attrs,obj):
    for attr in attrs.keys():
        if hasattr(obj, calculateMethodName(attr)):
            eval ('obj.'+calculateMethodName(attr))(attrs[attr].value)

def build2(node_, object):
    attrs = node_.attributes

    if attrs != None:
        setAttributes(attrs, object)

    for child_ in node_.childNodes:
        nodeName_ = child_.nodeName.split(':')[-1]
        if child_.nodeType == Node.ELEMENT_NODE:
            objectinstance = None
            try:
                objectinstance = eval(nodeName_.title())()
            except:
                continue
            if objectinstance is not None:
                object.addElement(build2(child_,objectinstance))
        elif child_.nodeType == Node.TEXT_NODE:
            if child_.nodeValue != None:
                object.appendTextContent(child_.nodeValue)
        elif child_.nodeType == Node.CDATA_SECTION_NODE:  
            object.appendTextContent('<![CDATA['+child_.nodeValue+']]>')          
        elif child_.nodeType == Node.COMMENT_NODE:  
            object.appendTextContent('<!-- '+child_.nodeValue+' -->')          
        else:
            continue
    return object

def parse2(inFileName):
    doc = minidom.parse(inFileName)
    rootNode = doc.documentElement
    rootObj = Svg()
    build2(rootNode,rootObj)
    doc = None
    return rootObj



##___________________________________________________________________________________________________________________
    
   
    
    
def Call_Vizan(model,SolutionAnalysis,SolutionType,prod,subst,count):
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
        file_source_path=tk.filedialog.askopenfilename()

    call_vizan_cli(model, file_source_path, SolutionAnalysis, SolutionType, prod, subst, count)


def call_vizan_cli(model, file_source_path, SolutionAnalysis, SolutionType, prod, subst, count):
    SVGObject = parse2(file_source_path)
    if type(SolutionAnalysis) == cobra.core.solution.Solution:
        flux_sum = calculate_common_substrate_flux(model)
    else:
        flux_sum = 0
    reac_id = []
    for s in model.reactions:
        reac_id.append(s.id)
    print('---------------------')
    for s in SVGObject._subElements:
        # str(s.__class__) <> 'core.TextContent':
        if not isinstance(s, pysvg.core.TextContent):
            if isinstance(s, pysvg.structure.G):  # str(s.__class__) == 'structure.g':
                for s1 in s._subElements:
                    # if str(s1.__class__) != 'core.TextContent':
                    if not isinstance(s1, pysvg.core.TextContent):
                        set_reaction_id_from_sympheny(s1, ' ', d=0)  ## to put ID on reaction class group elements
                        set_metabolite_id_from_sympheny(s1, ' ', d=0)  ## to put ID on metabolite class group elements
                        TravSVGFBA(s1, model, SolutionAnalysis, '', flux_sum,
                                   reac_id)  ## for calculating colors and etc
    SVGObject.save('pysvg_developed_file.svg')
    print('Network has been drawn')
    insert_interactive_script(file_source_path)
    insert_metab_id(file_source_path, prod, subst, count)
    print('metab id has been drawn added')


        
        
class Style2(dict):
    def __init__(self, instr=""):
        for kv in instr.split(";"):
            if kv != '':
                k,v = kv.split(":")
                self[k.strip()]  = v.strip()
         
    def changeColorText(self,color,attr):		## not only color but also attribute property
        for k in self:
            if k==attr:
                self[k.strip()]=color

    def __str__ (self):
        rv = ""
        for k in self:
            rv += k +":" + self[k] + ";"
        return str(rv)

    
def TravSVGFBA (svgobj,model,SolutionAnalysis,Reac,flux_sum,reac_id,d=0):		
        for s in svgobj._subElements:				            
            if not isinstance(s, pysvg.core.TextContent):
                if str(s.getAttribute('class')) == 'reaction' and str(s.getAttribute('id')) in reac_id:						   
                    Reac=str(s.getAttribute('id'))
                    info_reac=model.reactions.get_by_id(Reac)  
                    s.setAttribute(attribute_name='Name',attribute_value=info_reac.name)    
                    s.setAttribute(attribute_name='Stoichiometry',attribute_value=info_reac.reaction)    
                    s.setAttribute(attribute_name='GPR',attribute_value=str(info_reac.gene_reaction_rule))    
                    s.setAttribute(attribute_name='Lower_bound',attribute_value=str(info_reac.lower_bound))
                    s.setAttribute(attribute_name='Upper_bound',attribute_value=str(info_reac.upper_bound))
                    TravSVGFBA(s,model,SolutionAnalysis,Reac,flux_sum,reac_id,d+1)
                if str(s.getAttribute('class')) == 'segment-group' or s.getAttribute('class') == 'arrowheads' or str(s.getAttribute('class')) == 'reaction-label-group':
                    TravSVGFBA(s,model,SolutionAnalysis,Reac,flux_sum,reac_id,d+1)       
                if str(s.getAttribute('class')) == 'segment' and Reac in reac_id:
                    setColorSVGFBA(s,Reac,SolutionAnalysis,'stroke',flux_sum) 
                if str(s.getAttribute('class')) == 'arrowhead' and Reac in reac_id:
                    setColorSVGFBA(s,Reac,SolutionAnalysis,'fill',flux_sum) 
                if str(s.getAttribute('class')) == 'reaction-label label' and Reac in reac_id:
                    for l in s._subElements:
                        if isinstance(l, pysvg.core.TextContent): 
                            if type(SolutionAnalysis) == cobra.core.solution.Solution:
                                l.setContent(Reac + ' ' + str(SolutionAnalysis[Reac])) 
                            if type(SolutionAnalysis) == pd.core.frame.DataFrame:
                                l.setContent(Reac + ' ' + str(SolutionAnalysis.loc[Reac,'minimum']) + ' ' + str(SolutionAnalysis.loc[Reac,'maximum']))
                if str(s.getAttribute('class')) == 'node':
                    Metab=s.getAttribute('id_metabolite')
                    if Metab is not None:
                        info_metab=model.metabolites.get_by_id(Metab)
                        s.setAttribute(attribute_name='Charge',attribute_value=info_metab.charge)
                        s.setAttribute(attribute_name='Compartment',attribute_value=info_metab.compartment)
                        s.setAttribute(attribute_name='Elements',attribute_value=info_metab.elements)
                        s.setAttribute(attribute_name='Formula',attribute_value=info_metab.formula)
                        s.setAttribute(attribute_name='Name',attribute_value=info_metab.name)
                        s.setAttribute(attribute_name='Shadow_price',attribute_value=info_metab.shadow_price)
                        TravSVGFBA(s,model,SolutionAnalysis,Reac,flux_sum,reac_id,d+1)
                if str(s.getAttribute('class')) == 'node-circle metabolite-circle':
                    print ("")
    


def setColorSVGFBA(svgobj,Reac,SolutionAnalysis,color_type,flux_sum):	
    styleText = Style2(str(svgobj.getAttribute('style')))
    if type(SolutionAnalysis)==cobra.core.solution.Solution:
        if SolutionAnalysis[Reac] > 0:
            styleText.changeColorText('#008000',color_type)
        elif SolutionAnalysis[Reac] < 0:
            styleText.changeColorText('#d40000',color_type)
        else:
            styleText.changeColorText('#808000',color_type)
        if color_type == 'stroke':
            styleText.changeColorText(color=set_stroke_line_width_FBA(SolutionAnalysis,Reac,flux_sum),attr='stroke-width')
    if type(SolutionAnalysis) == pd.core.frame.DataFrame:
        styleText.changeColorText(color=set_stroke_line_width_FVA(SolutionAnalysis,Reac),attr='stroke-width')
        if SolutionAnalysis.loc[Reac,'maximum']>0 and SolutionAnalysis.loc[Reac,'minimum'] >= 0: ## pozitivs !!
            styleText.changeColorText('#008000',color_type)
        if SolutionAnalysis.loc[Reac,'maximum']>0 and SolutionAnalysis.loc[Reac,'minimum'] < 0: ## abpusejs
            styleText.changeColorText('#0024ff',color_type)
        if SolutionAnalysis.loc[Reac,'maximum']< 0 and SolutionAnalysis.loc[Reac,'minimum'] < 0: ## negativs !!
            styleText.changeColorText('#d40000',color_type)
        if SolutionAnalysis.loc[Reac,'maximum']==0 and SolutionAnalysis.loc[Reac,'minimum'] == 0: ## nulee    
            styleText.changeColorText('#000000',color_type)
        if color_type == 'stroke':
            styleText.changeColorText(color=set_stroke_line_width_FVA(SolutionAnalysis,Reac),attr='stroke-width')
    svgobj.setAttribute('style',str(styleText.__str__()))
    
    
    
##________________________________________________________________________

def calculate_common_substrate_flux(model):
    from cobra.flux_analysis.variability import flux_variability_analysis
    boundary_reactions = model.exchanges
    ##### generate model exchange reactions#####################

    fva_results = flux_variability_analysis(
                    model, reaction_list=boundary_reactions,
                    fraction_of_optimum=1)
    #### Generate FVA results   ###############################################


    fva_results=fva_results.sort_values(by='minimum', ascending=True)


    ### sort FVA results ascending order###


    substrates = fva_results['minimum'] < 0
    fva_results_substrates=fva_results[substrates].sort_values(by='minimum', ascending=True)

    #####   Generate dataframe where only consuming reactions are taken into account   #####


    reac_consist_carbon=[]
    for reaction in fva_results_substrates.index:
        reac_cobrapy=model.reactions.get_by_id(reaction)
        for metabolite in reac_cobrapy.reactants:
            if 'C' in metabolite.elements.keys():
                reac_consist_carbon.append(str(reaction))


    ###### Filter from FVA substrate list reactions which HAVE NOT included 


    ##print reac_consist_carbon
    flux_sum=0
    for reaction in reac_consist_carbon:
        flux_sum=flux_sum + fva_results.loc[reaction,'minimum']
    return flux_sum


    ##### calculate flux sum how much is consumed all substrates (not taking into account carbon amount for each substrate)
    ## to do is take into account substrate carbon ratio for better flux calculation
    
    
    
def set_stroke_line_width_FBA(SolutionAnalysis,Reac,flux_sum):
    Solution=abs(SolutionAnalysis[Reac])
    flux_sum=abs(flux_sum)
    if Solution>= flux_sum * 0.7 :
        width = 21
    if Solution >= flux_sum * 0.5 and Solution < flux_sum * 0.7:
        width = 20
    if Solution >= flux_sum * 0.3 and Solution < flux_sum * 0.5:
        width = 18
    if Solution >= flux_sum * 0.2 and Solution < flux_sum * 0.3:
        width = 16
    if Solution >= flux_sum * 0.1 and Solution < flux_sum * 0.2:
        width = 13
    if Solution >= 0 and Solution < flux_sum * 0.1:
        width = 4
    return str(width)

def set_stroke_line_width_FVA(SolutionAnalysis,Reac):
##    max_diapazon=abs(SolutionAnalysis.max().loc['maximum']) + abs(SolutionAnalysis.max().loc['minimum']) ## kaut ko gudraaku vajag
    max_diapazon=100
    flux_diapasone=0
    if SolutionAnalysis.loc[Reac,'maximum'] > 0 or SolutionAnalysis.loc[Reac,'maximum']== SolutionAnalysis.loc[Reac,'minimum']:   
        flux_diapasone=SolutionAnalysis.loc[Reac,'maximum']-SolutionAnalysis.loc[Reac,'minimum']
    if SolutionAnalysis.loc[Reac,'maximum'] < 0:
        flux_diapasone=abs(SolutionAnalysis.loc[Reac,'maximum']+SolutionAnalysis.loc[Reac,'minimum'])
    if flux_diapasone>= max_diapazon * 0.5 and flux_diapasone < max_diapazon or flux_diapasone > max_diapazon:
        width = 24
    if flux_diapasone >= max_diapazon * 0.25 and flux_diapasone < max_diapazon * 0.5:
        width = 20
    if flux_diapasone >= max_diapazon * 0.13 and flux_diapasone < max_diapazon * 0.25:
        width = 16
    if flux_diapasone >= max_diapazon * 0.05  and flux_diapasone < max_diapazon * 0.13:
        width = 12
    if flux_diapasone >= max_diapazon * 0.0 and flux_diapasone < max_diapazon * 0.05:
        width = 8
    return str(width)


##________________________________________________________________________
    
    
    
    
    
    
def set_reaction_id_from_sympheny(svgobj, Reac=' ',d=0):
        for s in svgobj._subElements:				  
            if not isinstance(s, pysvg.core.TextContent):
                if str(s.getAttribute('class')) == 'reaction':
                    Reac=set_reaction_id_from_sympheny(s, Reac,d+1)
                    if Reac != ' ' and d==0:
                        name,reac_value = Reac.split(' ')
                        s.setAttribute(attribute_name='id',attribute_value=name)  
                if str(s.getAttribute('class')) == 'reaction-label-group':
                    Reac=set_reaction_id_from_sympheny(s, Reac,d+1)
                if str(s.getAttribute('class')) == 'reaction-label label':
                    for l in s._subElements:
                        if isinstance(l, pysvg.core.TextContent):
                            Reac=str(l.content)
        return Reac
    
    
def set_metabolite_id_from_sympheny(svgobj, Metab=' ',d=0):
        for s in svgobj._subElements:				  
            if not isinstance(s, pysvg.core.TextContent):
                if str(s.getAttribute('class')) == 'node':
                    Metab=set_metabolite_id_from_sympheny(s, Metab,d+1)
                    if Metab != ' ' and d==0:
                        s.setAttribute(attribute_name='id_metabolite',attribute_value=Metab)  
                if str(s.getAttribute('class')) == 'node-label label':
                    for l in s._subElements:
                        if isinstance(l, pysvg.core.TextContent): #str(l.__class__) == 'core.TextContent': 
                            Metab=str(l.content)
                            Metab=Metab[0:]
        return Metab
    
    
    
    
    
    
 ##____________________________________________________________________________________________________________________
    

def InsertScripCall(source_file_path, pattern, substring):
    from tempfile import mkstemp
    fh, target_file_path = mkstemp()
    with open(target_file_path, 'w') as target_file:
        with open(source_file_path, 'r') as source_file:
            for line in source_file:
                target_file.write(line.replace(pattern, substring))
    remove(source_file_path)
    move(target_file_path, source_file_path)





def IsScripHtmlInsertNeeded() :
    isInsertNeeded = True
    with open('pysvg_developed_file.svg', 'r') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if 'overlayImageToCancelPopup' in line:
                isInsertNeeded = False
                break;
        if isInsertNeeded :
            print ('Update is completed');
        else : 
            print ('Update is not needed');
        return isInsertNeeded


def AddPopupForElementReaction(lineToChange) :                  ####### savestring
    lineNew = "onclick='ShowTooltip(this, evt)' \n " + lineToChange
    InsertScripCall('pysvg_developed_file.svg', lineToChange, lineNew)


def AddScriptAndPopup(placeToEnd, insert_lines) :
    with open('pysvg_developed_file.svg', 'r+') as myfile:
        lines = myfile.readlines()
        if placeToEnd :
            lines[-2:-2] = insert_lines
        else : 
            lines[1:1] = insert_lines
        myfile.seek(0)
        myfile.write(''.join(lines))
    myfile.close()
    
    
def insert_interactive_script(file_source_path):    
    from tempfile import mkstemp
    from shutil import move
    from os import remove


    path =  'pysvg_developed_file.svg'

    
    cssToInsert = cssToInsert = """<defs>
        <style type="text/css"> #chart-1 { width: 100px; height: 220px; } .metric-chart { position: relative; margin: auto; } .y-axis-line-list, .x-axis-line-list, .y-axis-label-list, .x-axis-label-list, .y-axis-bar-list, .x-axis-bar-list { margin: 0; padding: 0; list-style: none; } .y-axis { position: absolute; left: 50px; top: 0px; bottom: 80px; right: auto; width: 1px; background-color: #434a54; } .y-axis-line-list { position: absolute; top: 10px; right: 0; bottom: 50px; left: 51px; } .y-axis-line-item { position: absolute; top: auto; right: 0; bottom: 0; left: 0; } .count-1 .y-axis-line-item:nth-of-type(1) { bottom: 100%; } .count-2 .y-axis-line-item:nth-of-type(1) { bottom: 50%; } .count-2 .y-axis-line-item:nth-of-type(2) { bottom: 100%; } .count-3 .y-axis-line-item:nth-of-type(1) { bottom: 33.333333333333336%; } .count-3 .y-axis-line-item:nth-of-type(2) { bottom: 66.66666666666667%; } .count-3 .y-axis-line-item:nth-of-type(3) { bottom: 100%; } .count-4 .y-axis-line-item:nth-of-type(1) { bottom: 25%; } .count-4 .y-axis-line-item:nth-of-type(2) { bottom: 50%; } .count-4 .y-axis-line-item:nth-of-type(3) { bottom: 75%; } .count-4 .y-axis-line-item:nth-of-type(4) { bottom: 100%; } .count-5 .y-axis-line-item:nth-of-type(1) { bottom: 20%; } .count-5 .y-axis-line-item:nth-of-type(2) { bottom: 40%; } .count-5 .y-axis-line-item:nth-of-type(3) { bottom: 60%; } .count-5 .y-axis-line-item:nth-of-type(4) { bottom: 80%; } .count-5 .y-axis-line-item:nth-of-type(5) { bottom: 100%; } .y-axis-line { display: block; height: 1px; background-color: #ccd1d9; } .y-axis-label-list { position: absolute; top: 10px; right: auto; bottom: 50px; left: 0; width: 40px; } .y-axis-label-item { position: absolute; top: auto; right: 0; bottom: 0; left: 0; } .count-1 .y-axis-label-item:nth-of-type(1) { bottom: 100%; } .count-2 .y-axis-label-item:nth-of-type(1) { bottom: 50%; } .count-2 .y-axis-label-item:nth-of-type(2) { bottom: 100%; } .count-3 .y-axis-label-item:nth-of-type(1) { bottom: 33.333333333333336%; } .count-3 .y-axis-label-item:nth-of-type(2) { bottom: 66.66666666666667%; } .count-3 .y-axis-label-item:nth-of-type(3) { bottom: 100%; } .count-4 .y-axis-label-item:nth-of-type(1) { bottom: 25%; } .count-4 .y-axis-label-item:nth-of-type(2) { bottom: 50%; } .count-4 .y-axis-label-item:nth-of-type(3) { bottom: 75%; } .count-4 .y-axis-label-item:nth-of-type(4) { bottom: 100%; } .count-5 .y-axis-label-item:nth-of-type(1) { bottom: 20%; } .count-5 .y-axis-label-item:nth-of-type(2) { bottom: 40%; } .count-5 .y-axis-label-item:nth-of-type(3) { bottom: 60%; } .count-5 .y-axis-label-item:nth-of-type(4) { bottom: 80%; } .count-5 .y-axis-label-item:nth-of-type(5) { bottom: 100%; } .y-axis-label { position: relative; display: block; color: #656d78; text-align: right; font-size: 12px; line-height: 1; } .h-bar-chart .y-axis-label { bottom: -6px; } .x-axis-bar-list { position: absolute; top: 0; right: 5px; bottom: 0px; left: 56px; } .x-axis-bar-item { position: absolute; top: 0px; /*high position */ right: auto; bottom: 32px; /*lowerposition */ left: 0; } .count-1 .x-axis-bar-item:nth-of-type(1) { right: 0%; left: 0%; } .x-axis-bar { position: absolute; top: auto; right: 5px; bottom: 0; left: 5px; display: block; border: 1px solid transparent; border-radius: 3px 3px 3px 3px; background-color: #4fc1e9; box-shadow: inset 0px 1px 0px rgba(255, 255, 255, 0.4); transition: all 0.15s linear; } .x-axis-bar.primary { border-color: #1f2225; background-image: -webkit-gradient(linear, 0% top, 100% top, from(#7e8692), to(#656d78)); background-image: -webkit-linear-gradient(left, color-stop(#7e8692 0%), color-stop(#656d78 100%)); background-image: -moz-linear-gradient(left, #7e8692 0%, #656d78 100%); background-image: linear-gradient(to right, #7e8692 0%, #656d78 100%); background-repeat: repeat-x; filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#ff7e8692', endColorstr='#ff656d78', GradientType=1); }</style>
   </defs>\n"""

    htmlOverlayToInsert = """ <foreignObject x="0px" y="0px" width="100%" height="100%" id="overlayImageToCancelPopup" style="position: absolute;">
        <body class="overlay" xmlns="http://www.w3.org/1999/xhtml" onclick="HideTooltip()" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index:-1000;">
        </body>
    </foreignObject>\n"""

    htmlPopupToInsert = """<foreignObject x="0" y="0" width="420px" height="270px" id="thepopup">
        <body xmlns="http://www.w3.org/1999/xhtml" onload="HideTooltip()">
            <div style="min-width: 380px; min-height: 220px; border: 1px solid rgb(181, 135, 135); padding: 7px; background-color: rgb(255, 255, 255); box-shadow: rgba(0, 0, 0, 0.4) 4px 6px 6px 0px; text-align: left; font-size: 16px; font-family: sans-serif; color: rgb(17, 17, 17); position: relative;">
                <span id="tooltip-abbr" style="position: absolute; top: 20px; left: 20px; font-size: 16px; width: 290px;font-weight: bold;"></span>
                <span id="tooltip-name" style="position: absolute; top: 55px; left: 20px; width: 290px; font-size: 16px; word-wrap: break-word;"></span>
                <span id="tooltip-data" style="position: absolute; top: 125px; left: 20px; width: 290px; font-size: 16px; word-wrap: break-word;"></span>
                <span id="tooltip-type" style="position: absolute; top: 15px; right: 20px; font-size: 14px;  color: rgb(210, 112, 102);"></span>
                <div class="metric-chart h-bar-chart" id="chart-1" style="position: absolute; top: 40px; right: 20px; display: block; ">
                    <div class="y-axis"></div>
                    <ul class="y-axis-line-list count-5">
                        <li class="y-axis-line-item">
                        </li>
                        <li class="y-axis-line-item">
                            <span class="y-axis-line"></span>
                        </li>
                        <li class="y-axis-line-item">
                            <span class="y-axis-line"></span>
                        </li>
                        <li class="y-axis-line-item">
                            <span class="y-axis-line"></span>
                        </li>
                        <li class="y-axis-line-item">
                            <span class="y-axis-line"></span>
                        </li>
                    </ul>
                    <ul class="y-axis-label-list count-5">
                        <li class="y-axis-label-item">
                            <span class="y-axis-label">-1000</span>
                        </li>
                        <li class="y-axis-label-item">
                            <span class="y-axis-label">-500</span>
                        </li>
                        <li class="y-axis-label-item">
                            <span class="y-axis-label">0</span>
                        </li>
                        <li class="y-axis-label-item">
                            <span class="y-axis-label">500</span>
                        </li>
                        <li class="y-axis-label-item">
                            <span class="y-axis-label">1000</span>
                        </li>
                    </ul>
                    <ul class="x-axis-bar-list count-1">
                        <li class="x-axis-bar-item nested-bars">
                            <span class="x-axis-bar primary" style="top: 10px; bottom:48px;"> </span>
                        </li>
                    </ul>
                </div>
                <form id="tooltip-link" target="_blank">
                    <button style="position: absolute; bottom: 10px; left: 20px; font-size: 16px; font-weight: bold;">Open in browser</button>
                </form>
            </div>
        </body>
    </foreignObject>\n"""




    scriptToInsert = """<script type="text/javascript">
        <![CDATA[
        
        function IsMetabolite(parent) {
             return parent.getElementsByClassName('node-label label').length>0;
        }

        function ShowTooltip(parent, evt) {
            HideTooltip();

            var zoom = window.outerWidth / window.innerWidth
            var isChrome = /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
            if (isChrome) {
                zoom = 1;
            }

            var tooltip = document.getElementById('thepopup');

            tooltip.setAttribute("x", (evt.clientX + window.scrollX) * zoom);
            tooltip.setAttribute("y", (evt.clientY + window.scrollY) * zoom);

            var tooltipabbr = document.getElementById('tooltip-abbr');
            var tooltipname = document.getElementById('tooltip-name');
            var tooltipdata = document.getElementById('tooltip-data');
            var tooltiptype = document.getElementById('tooltip-type');
            var tooltiplink = document.getElementById('tooltip-link');

            var barParent = document.getElementById('chart-1');

            if (IsMetabolite(parent)){
                barParent.style.display = 'none';
                tooltipabbr.innerHTML = GetTextValueForPopup(parent.getElementsByClassName('node-label label')[0].textContent);
                tooltiptype.innerHTML = 'Metabolite';
                tooltipname.innerHTML =  'Name: ' + GetTextValueForPopup(parent.getAttribute("Name"));
                tooltipdata.innerHTML =  'Formula: ' + GetTextValueForPopup(parent.getAttribute("Formula"));

                if (IsScrumpyFile()){
                    var metId = ClearElementData(parent.getAttribute("id_metabolite"));
                    tooltiplink.action = 'http://bigg.ucsd.edu/universal/metabolites/' + metId;

                }else{
                    var ell = ClearElementData(parent.getAttribute("id_metabolite"));
                    tooltiplink.action = 'http://identifiers.org/biocyc/META:' + ell;
                }
            } else {
                if (IsFVAFile(parent)) {
                    InitBar(parent, barParent);
                    barParent.style.display = 'block';
                } else {
                    barParent.style.display = 'none';
                }
                tooltipabbr.innerHTML = GetTextValueForPopup(parent.getAttribute("id"));
                tooltiptype.innerHTML = 'Reaction';
                tooltipname.innerHTML = 'Name: ' + GetTextValueForPopup(parent.getAttribute("Name"));

                tooltipdata.innerText = 'Stoichiometry: ' + GetTextValueForPopup(parent.getAttribute("Stoichiometry"));

                if (IsScrumpyFile()){
                    var ell = ClearElementData(parent.getAttribute("id"));
                    tooltiplink.action = 'http://bigg.ucsd.edu/universal/reactions/' + ell;
                } else {
                    var ell = ClearElementData(parent.getAttribute("id"));
                    tooltiplink.action = 'http://identifiers.org/biocyc/META:' + ell;
                }
            }
            tooltip.style.display = 'inline';
        }

        function IsScrumpyFile(){
            return !document.getElementById("svg2");
        }

        function GetTextValueForPopup(inputText) {
            return (inputText == '') ? 'Not specified' : ClearElementData(inputText);
        }
        
        function ClearElementData(inputElement) {
            return inputElement.replace(/_Plas/g, '').replace(/_Cyto/g, '').replace(/_Mitop/g, '').replace(/_Vaco/g, '').replace(/_tx/g, '').replace(/_c/g, '').replace(/_p/g, '').replace(/_e/g, '');
        }  
    
        function HideTooltip() {
            var tooltip = document.getElementById('thepopup');
            tooltip.style.display = 'none';
            console.log('close pressed ');
        }

        function IsFVAFile(parent) {
            if (parent.getElementsByClassName('reaction-label label').length > 0){
                innerHTML = parent.getElementsByClassName('reaction-label label')[0].textContent.trim().split(' ');
                return innerHTML.length > 2;
            }
            else {
                return false;
            }
            return false;
        }


        function InitBar(parent, barParent) {
            innerHTML = parent.getElementsByClassName('reaction-label label')[0].textContent.trim().split(' ');
            lowValue =  Math.round(innerHTML[1] / 10) * 10;
            highValue = Math.round(innerHTML[2] / 10) * 10;

            var maxFlux = parseFloat(innerHTML[2]);
            var minFlux = parseFloat(innerHTML[1]);

            var barMaxPx = 128;

            var maxValue = Math.max(Math.abs(lowValue), Math.abs(highValue));

            if (maxValue == 0) {
                maxValue = 10
            }

            var barMiddlePoint = barMaxPx / 2;
            var bottomPositionDefault = 50;
            var topPositionDefault = 10;
            var barStepsPx =  barMaxPx / 2 / maxValue;

            var top =  topPositionDefault + (maxValue - Math.abs(maxFlux)) * barStepsPx
            var bottom = bottomPositionDefault + (maxValue - Math.abs(minFlux)) * barStepsPx;
            var bar = document.getElementsByClassName('x-axis-bar primary')[0];
            bar.style.top = top + 'px';
            bar.style.bottom = bottom + 'px';
            valueStep = (maxValue * 2) / 4;

            barLinesArray = barParent.getElementsByClassName('y-axis-label');
            barLinesArray[0].innerText = Math.round(maxValue - valueStep * 4);
            barLinesArray[1].innerText = Math.round(maxValue - valueStep * 3);
            barLinesArray[2].innerText = Math.round(maxValue - valueStep * 2);
            barLinesArray[3].innerText = Math.round(maxValue - valueStep * 1);
            barLinesArray[4].innerText = Math.round(maxValue - valueStep * 0);
        }
     
        ]]>
    </script>\n"""
    
    

    if IsScripHtmlInsertNeeded():        
        AddScriptAndPopup(False, [cssToInsert, scriptToInsert, htmlOverlayToInsert])
        AddScriptAndPopup(True, [htmlPopupToInsert])
        AddPopupForElementReaction('class="node"')
        AddPopupForElementReaction('class="reaction"')

def insert_metab_id(file_source_path,prod,subst,count):
    ET.register_namespace('svg', "http://www.w3.org/2000/svg")

    pathOriginalFile = file_source_path
    treeOriginalFile = ET.parse(pathOriginalFile)
    rootOriginalFile = treeOriginalFile.getroot()

    pathPySVGFile ='pysvg_developed_file.svg'
    treePySVGFile = ET.parse(pathPySVGFile)
    rootPySVGFile = treePySVGFile.getroot()

    for nodePySVGFile in rootPySVGFile.findall('text'):
        idElPySVGFile = nodePySVGFile.get('id')
        metIdPySVGFile = nodePySVGFile.get('id_metabolite')
        if (idElPySVGFile is not None):
            for nodeOriginalFile in rootOriginalFile.findall('{http://www.w3.org/2000/svg}text'):
                idElOriginalFile = nodeOriginalFile.get('id')
                if(idElOriginalFile == idElPySVGFile):
                    metIdOriginalFile = nodeOriginalFile.get('id_metabolite')
                    if (metIdOriginalFile is not None):
                        if (metIdPySVGFile is not None):
                            nodePySVGFile.set('id_metabolite', str(metIdOriginalFile))
    for nodePySVGFile in rootPySVGFile.findall('g'):
        idElPySVGFile = nodePySVGFile.get('id')
        metIdPySVGFile = nodePySVGFile.get('id_metabolite')
        if (idElPySVGFile is not None):
            for nodeOriginalFile in rootOriginalFile.findall('{http://www.w3.org/2000/svg}g'):
                idElOriginalFile = nodeOriginalFile.get('id')
                if(idElOriginalFile == idElPySVGFile):
                    metIdOriginalFile = nodeOriginalFile.get('id_metabolite')
                    if (metIdOriginalFile is not None):
                        if (metIdPySVGFile is not None):
                            nodePySVGFile.set('id_metabolite', str(metIdOriginalFile))

    treePySVGFile.write(str(prod) + "_" + str(subst) + "_" + str(count) + '.svg') 
    os.remove('pysvg_developed_file.svg')






        
    
