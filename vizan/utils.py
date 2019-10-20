# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
from shutil import move
from tempfile import mkstemp
from xml.dom import Node, minidom
from xml.etree import ElementTree

import pandas as pd
import pysvg
from cobra.core.solution import Solution as CobraSolution

for subpackage in ['core', 'filter', 'gradient', 'linking', 'script', 'shape', 'structure', 'style', 'text']:
    try:
        exec('from pysvg.' + subpackage + ' import *')
    except ImportError:
        pass


def draw_network(model, svg_object, analysis_results, flux_sum):
    reaction_ids = [s.id for s in model.reactions]
    for s in svg_object._subElements:
        # str(s.__class__) <> 'core.TextContent': # str(s.__class__) == 'structure.g':
        if isinstance(s, pysvg.structure.G) and not isinstance(s, pysvg.core.TextContent):
            for s1 in s._subElements:
                # if str(s1.__class__) != 'core.TextContent':
                if not isinstance(s1, pysvg.core.TextContent):
                    set_reaction_id_from_sympheny(s1, ' ', d=0)  # to put ID on reaction class group elements
                    set_metabolite_id_from_sympheny(s1, ' ', d=0)  # to put ID on metabolite class group elements
                    traverse_svg(s1, model, analysis_results, '', flux_sum,
                                 reaction_ids)  # for calculating colors and etc


def calculate_method_name(attr):
    name = attr
    name = name.replace(':', '_')
    name = name.replace('-', '_')
    name = 'set_' + name
    return name


def set_attributes(attrs, obj):
    for attr in attrs.keys():
        if hasattr(obj, calculate_method_name(attr)):
            eval('obj.' + calculate_method_name(attr))(attrs[attr].value)


def build2(node_, obj):
    attrs = node_.attributes

    if attrs is not None:
        set_attributes(attrs, obj)

    for child_ in node_.childNodes:
        node_name_ = child_.nodeName.split(':')[-1]
        if child_.nodeType == Node.ELEMENT_NODE:
            try:
                object_instance = eval(node_name_.title())()
            except BaseException:
                continue
            if object_instance is not None:
                obj.addElement(build2(child_, object_instance))
        elif child_.nodeType == Node.TEXT_NODE:
            if child_.nodeValue is not None:
                obj.appendTextContent(child_.nodeValue)
        elif child_.nodeType == Node.CDATA_SECTION_NODE:
            obj.appendTextContent('<![CDATA[' + child_.nodeValue + ']]>')
        elif child_.nodeType == Node.COMMENT_NODE:
            obj.appendTextContent('<!-- ' + child_.nodeValue + ' -->')
        else:
            continue
    return obj


def parse2(input_filename):
    doc = minidom.parse(input_filename)
    root_node = doc.documentElement
    root_obj = pysvg.structure.Svg()
    build2(root_node, root_obj)
    return root_obj


class Style2(dict):
    def __init__(self, instr=""):
        for kv in instr.split(";"):
            if kv != '':
                k, v = kv.split(":")
                self[k.strip()] = v.strip()

    def change_color_text(self, color, attr):  # not only color but also attribute property
        for k in self:
            if k == attr:
                self[k.strip()] = color

    def __str__(self):
        rv = ""
        for k in self:
            rv += k + ":" + self[k] + ";"
        return str(rv)


def traverse_svg(svg_obj, model, analysis_results, reaction, flux_sum, reaction_id, d=0):
    for s in svg_obj._subElements:
        if not isinstance(s, pysvg.core.TextContent):
            if str(s.getAttribute('class')) == 'reaction' and str(s.getAttribute('id')) in reaction_id:
                reaction = str(s.getAttribute('id'))
                info_reaction = model.reactions.get_by_id(reaction)
                attributes = [
                    ('Name', info_reaction.name),
                    ('Stoichiometry', info_reaction.reaction),
                    ('GPR', str(info_reaction.gene_reaction_rule)),
                    ('Lower_bound', str(info_reaction.lower_bound)),
                    ('Upper_bound', str(info_reaction.upper_bound)),
                ]
                for name, value in attributes:
                    s.setAttribute(attribute_name=name, attribute_value=value)
                traverse_svg(s, model, analysis_results, reaction, flux_sum, reaction_id, d + 1)
            if str(s.getAttribute('class')) == 'segment-group' or s.getAttribute('class') == 'arrowheads' or str(
                    s.getAttribute('class')) == 'reaction-label-group':
                traverse_svg(s, model, analysis_results, reaction, flux_sum, reaction_id, d + 1)
            if str(s.getAttribute('class')) == 'segment' and reaction in reaction_id:
                set_color_in_svg(s, reaction, analysis_results, 'stroke', flux_sum)
            if str(s.getAttribute('class')) == 'arrowhead' and reaction in reaction_id:
                set_color_in_svg(s, reaction, analysis_results, 'fill', flux_sum)
            if str(s.getAttribute('class')) == 'reaction-label label' and reaction in reaction_id:
                for l in s._subElements:
                    if isinstance(l, pysvg.core.TextContent):
                        if type(analysis_results) == CobraSolution:
                            l.setContent(reaction + ' ' + str(analysis_results[reaction]))
                        if type(analysis_results) == pd.core.frame.DataFrame:
                            l.setContent(reaction + ' ' + str(analysis_results.loc[reaction, 'minimum']) + ' ' + str(
                                analysis_results.loc[reaction, 'maximum']))
            if str(s.getAttribute('class')) == 'node':
                metabolite = s.getAttribute('id_metabolite')
                if metabolite is not None:
                    info_metabolite = model.metabolites.get_by_id(metabolite)
                    attributes = [
                        ('Charge', info_metabolite.charge),
                        ('Compartment', info_metabolite.compartment),
                        ('Elements', info_metabolite.elements),
                        ('Formula', info_metabolite.formula),
                        ('Name', info_metabolite.name),
                        ('Shadow_price', info_metabolite.shadow_price),
                    ]
                    for name, value in attributes:
                        s.setAttribute(attribute_name=name, attribute_value=value)
                    traverse_svg(s, model, analysis_results, reaction, flux_sum, reaction_id, d + 1)
            if str(s.getAttribute('class')) == 'node-circle metabolite-circle':
                print("")


def set_color_in_svg(svg_obj, reaction, analysis_results, color_type, flux_sum):
    def reaction_max(this_reaction):
        return analysis_results.loc[this_reaction, 'maximum']

    def reaction_min(this_reaction):
        return analysis_results.loc[this_reaction, 'minimum']

    style_text = Style2(str(svg_obj.getAttribute('style')))
    if type(analysis_results) == CobraSolution:
        if analysis_results[reaction] > 0:
            style_text.change_color_text('#008000', color_type)
        elif analysis_results[reaction] < 0:
            style_text.change_color_text('#d40000', color_type)
        else:
            style_text.change_color_text('#808000', color_type)
        if color_type == 'stroke':
            style_text.change_color_text(color=set_stroke_line_width_fba(analysis_results, reaction, flux_sum),
                                         attr='stroke-width')
    if type(analysis_results) == pd.core.frame.DataFrame:
        style_text.change_color_text(color=set_stroke_line_width_fva(analysis_results, reaction), attr='stroke-width')
        if reaction_max(reaction) > 0:
            if reaction_min(reaction) >= 0:  # Positive !!
                style_text.change_color_text('#008000', color_type)
            else:  # Both Directions !!
                style_text.change_color_text('#0024ff', color_type)
        if reaction_max(reaction) < 0 and reaction_min(reaction) < 0:  # Negative !!
            style_text.change_color_text('#d40000', color_type)
        if reaction_max(reaction) == 0 and reaction_min(reaction) == 0:  # Zero
            style_text.change_color_text('#000000', color_type)
        if color_type == 'stroke':
            style_text.change_color_text(color=set_stroke_line_width_fva(analysis_results, reaction),
                                         attr='stroke-width')
    svg_obj.setAttribute('style', str(style_text.__str__()))


def set_stroke_line_width_fba(analysis_results, reaction, flux_sum):
    solution = abs(analysis_results[reaction])
    flux_sum = abs(flux_sum)
    width = None
    if solution >= flux_sum * 0.7:
        width = 21
    if flux_sum * 0.5 <= solution < flux_sum * 0.7:
        width = 20
    if flux_sum * 0.3 <= solution < flux_sum * 0.5:
        width = 18
    if flux_sum * 0.2 <= solution < flux_sum * 0.3:
        width = 16
    if flux_sum * 0.1 <= solution < flux_sum * 0.2:
        width = 13
    if 0 <= solution < flux_sum * 0.1:
        width = 4
    return str(width)


def set_stroke_line_width_fva(analysis_results, reaction):
    def reaction_max(this_reaction):
        return analysis_results.loc[this_reaction, 'maximum']

    def reaction_min(this_reaction):
        return analysis_results.loc[this_reaction, 'minimum']

    # max_diapason = abs(analysis_results.max().loc['maximum']) + \
    #                abs(analysis_results.max().loc['minimum'])  # Need something more intelligent
    max_diapason = 100
    flux_diapason = 0
    if reaction_max(reaction) > 0 or reaction_max(reaction) == \
            reaction_min(reaction):
        flux_diapason = reaction_max(reaction) - reaction_min(reaction)
    if reaction_max(reaction) < 0:
        flux_diapason = abs(reaction_max(reaction) + reaction_min(reaction))
    width = None
    if max_diapason * 0.5 <= flux_diapason < max_diapason or flux_diapason > max_diapason:
        width = 24
    if max_diapason * 0.25 <= flux_diapason < max_diapason * 0.5:
        width = 20
    if max_diapason * 0.13 <= flux_diapason < max_diapason * 0.25:
        width = 16
    if max_diapason * 0.05 <= flux_diapason < max_diapason * 0.13:
        width = 12
    if max_diapason * 0.0 <= flux_diapason < max_diapason * 0.05:
        width = 8
    return str(width)


def set_reaction_id_from_sympheny(svg_obj, reaction=' ', d=0):
    for s in svg_obj._subElements:
        if not isinstance(s, pysvg.core.TextContent):
            if str(s.getAttribute('class')) == 'reaction':
                reaction = set_reaction_id_from_sympheny(s, reaction, d + 1)
                if reaction != ' ' and d == 0:
                    name, reaction_value = reaction.split(' ')
                    s.setAttribute(attribute_name='id', attribute_value=name)
            if str(s.getAttribute('class')) == 'reaction-label-group':
                reaction = set_reaction_id_from_sympheny(s, reaction, d + 1)
            if str(s.getAttribute('class')) == 'reaction-label label':
                for l in s._subElements:
                    if isinstance(l, pysvg.core.TextContent):
                        reaction = str(l.content)
    return reaction


def set_metabolite_id_from_sympheny(svg_obj, metabolite=' ', d=0):
    for s in svg_obj._subElements:
        if not isinstance(s, pysvg.core.TextContent):
            if str(s.getAttribute('class')) == 'node':
                metabolite = set_metabolite_id_from_sympheny(s, metabolite, d + 1)
                if metabolite != ' ' and d == 0:
                    s.setAttribute(attribute_name='id_metabolite', attribute_value=metabolite)
            if str(s.getAttribute('class')) == 'node-label label':
                for l in s._subElements:
                    if isinstance(l, pysvg.core.TextContent):  # str(l.__class__) == 'core.TextContent':
                        metabolite = str(l.content)
                        metabolite = metabolite[0:]
    return metabolite


def insert_scrip_call(source_file_path, pattern, substring):
    fh, target_file_path = mkstemp()
    with open(target_file_path, 'w') as target_file:
        with open(source_file_path, 'r') as source_file:
            for line in source_file:
                target_file.write(line.replace(pattern, substring))
    os.remove(source_file_path)
    move(target_file_path, source_file_path)


def is_script_html_insert_needed(intermediate_filename):
    is_insert_needed = True
    with open(intermediate_filename, 'r') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if 'overlayImageToCancelPopup' in line:
                is_insert_needed = False
                break
        if is_insert_needed:
            print('Update is completed')
        else:
            print('Update is not needed')
        return is_insert_needed


def add_popup_for_element_reaction(line_to_change, intermediate_filename):  # save string
    line_new = "onclick='ShowTooltip(this, evt)' \n " + line_to_change
    insert_scrip_call(intermediate_filename, line_to_change, line_new)


def add_script_and_popup(place_to_end, insert_lines, intermediate_filename):
    with open(intermediate_filename, 'r+') as f:
        lines = f.readlines()
        if place_to_end:
            lines[-2:-2] = insert_lines
        else:
            lines[1:1] = insert_lines
        f.seek(0)
        f.write(''.join(lines))
    f.close()


def insert_interactive_script(intermediate_filename):
    css_to_insert = """<defs>
        <style type="text/css"> #chart-1 { width: 100px; height: 220px; } .metric-chart { position: relative; margin: auto; } .y-axis-line-list, .x-axis-line-list, .y-axis-label-list, .x-axis-label-list, .y-axis-bar-list, .x-axis-bar-list { margin: 0; padding: 0; list-style: none; } .y-axis { position: absolute; left: 50px; top: 0px; bottom: 80px; right: auto; width: 1px; background-color: #434a54; } .y-axis-line-list { position: absolute; top: 10px; right: 0; bottom: 50px; left: 51px; } .y-axis-line-item { position: absolute; top: auto; right: 0; bottom: 0; left: 0; } .count-1 .y-axis-line-item:nth-of-type(1) { bottom: 100%; } .count-2 .y-axis-line-item:nth-of-type(1) { bottom: 50%; } .count-2 .y-axis-line-item:nth-of-type(2) { bottom: 100%; } .count-3 .y-axis-line-item:nth-of-type(1) { bottom: 33.333333333333336%; } .count-3 .y-axis-line-item:nth-of-type(2) { bottom: 66.66666666666667%; } .count-3 .y-axis-line-item:nth-of-type(3) { bottom: 100%; } .count-4 .y-axis-line-item:nth-of-type(1) { bottom: 25%; } .count-4 .y-axis-line-item:nth-of-type(2) { bottom: 50%; } .count-4 .y-axis-line-item:nth-of-type(3) { bottom: 75%; } .count-4 .y-axis-line-item:nth-of-type(4) { bottom: 100%; } .count-5 .y-axis-line-item:nth-of-type(1) { bottom: 20%; } .count-5 .y-axis-line-item:nth-of-type(2) { bottom: 40%; } .count-5 .y-axis-line-item:nth-of-type(3) { bottom: 60%; } .count-5 .y-axis-line-item:nth-of-type(4) { bottom: 80%; } .count-5 .y-axis-line-item:nth-of-type(5) { bottom: 100%; } .y-axis-line { display: block; height: 1px; background-color: #ccd1d9; } .y-axis-label-list { position: absolute; top: 10px; right: auto; bottom: 50px; left: 0; width: 40px; } .y-axis-label-item { position: absolute; top: auto; right: 0; bottom: 0; left: 0; } .count-1 .y-axis-label-item:nth-of-type(1) { bottom: 100%; } .count-2 .y-axis-label-item:nth-of-type(1) { bottom: 50%; } .count-2 .y-axis-label-item:nth-of-type(2) { bottom: 100%; } .count-3 .y-axis-label-item:nth-of-type(1) { bottom: 33.333333333333336%; } .count-3 .y-axis-label-item:nth-of-type(2) { bottom: 66.66666666666667%; } .count-3 .y-axis-label-item:nth-of-type(3) { bottom: 100%; } .count-4 .y-axis-label-item:nth-of-type(1) { bottom: 25%; } .count-4 .y-axis-label-item:nth-of-type(2) { bottom: 50%; } .count-4 .y-axis-label-item:nth-of-type(3) { bottom: 75%; } .count-4 .y-axis-label-item:nth-of-type(4) { bottom: 100%; } .count-5 .y-axis-label-item:nth-of-type(1) { bottom: 20%; } .count-5 .y-axis-label-item:nth-of-type(2) { bottom: 40%; } .count-5 .y-axis-label-item:nth-of-type(3) { bottom: 60%; } .count-5 .y-axis-label-item:nth-of-type(4) { bottom: 80%; } .count-5 .y-axis-label-item:nth-of-type(5) { bottom: 100%; } .y-axis-label { position: relative; display: block; color: #656d78; text-align: right; font-size: 12px; line-height: 1; } .h-bar-chart .y-axis-label { bottom: -6px; } .x-axis-bar-list { position: absolute; top: 0; right: 5px; bottom: 0px; left: 56px; } .x-axis-bar-item { position: absolute; top: 0px; /*high position */ right: auto; bottom: 32px; /*lowerposition */ left: 0; } .count-1 .x-axis-bar-item:nth-of-type(1) { right: 0%; left: 0%; } .x-axis-bar { position: absolute; top: auto; right: 5px; bottom: 0; left: 5px; display: block; border: 1px solid transparent; border-radius: 3px 3px 3px 3px; background-color: #4fc1e9; box-shadow: inset 0px 1px 0px rgba(255, 255, 255, 0.4); transition: all 0.15s linear; } .x-axis-bar.primary { border-color: #1f2225; background-image: -webkit-gradient(linear, 0% top, 100% top, from(#7e8692), to(#656d78)); background-image: -webkit-linear-gradient(left, color-stop(#7e8692 0%), color-stop(#656d78 100%)); background-image: -moz-linear-gradient(left, #7e8692 0%, #656d78 100%); background-image: linear-gradient(to right, #7e8692 0%, #656d78 100%); background-repeat: repeat-x; filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#ff7e8692', endColorstr='#ff656d78', GradientType=1); }</style>
   </defs>\n"""

    html_overlay_to_insert = """ <foreignObject x="0px" y="0px" width="100%" height="100%" id="overlayImageToCancelPopup" style="position: absolute;">
        <body class="overlay" xmlns="http://www.w3.org/1999/xhtml" onclick="HideTooltip()" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index:-1000;">
        </body>
    </foreignObject>\n"""

    html_popup_to_insert = """<foreignObject x="0" y="0" width="420px" height="270px" id="thepopup">
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

    script_to_insert = """<script type="text/javascript">
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

    if is_script_html_insert_needed(intermediate_filename):
        add_script_and_popup(False, [css_to_insert, script_to_insert, html_overlay_to_insert], intermediate_filename)
        add_script_and_popup(True, [html_popup_to_insert], intermediate_filename)
        add_popup_for_element_reaction('class="node"', intermediate_filename)
        add_popup_for_element_reaction('class="reaction"', intermediate_filename)


def insert_metabolite_ids(file_source_path, output_filename, intermediate_filename):
    ElementTree.register_namespace('svg', "http://www.w3.org/2000/svg")

    path_original_file = file_source_path
    tree_original_file = ElementTree.parse(path_original_file)
    root_original_file = tree_original_file.getroot()

    path_py_svg_file = intermediate_filename
    tree_py_svg_file = ElementTree.parse(path_py_svg_file)
    root_py_svg_file = tree_py_svg_file.getroot()

    for node_py_svg_file in root_py_svg_file.findall('text'):
        id_el_py_svg_file = node_py_svg_file.get('id')
        met_id_py_svg_file = node_py_svg_file.get('id_metabolite')
        if id_el_py_svg_file is not None:
            for node_original_file in root_original_file.findall('{http://www.w3.org/2000/svg}text'):
                id_el_original_file = node_original_file.get('id')
                if id_el_original_file == id_el_py_svg_file:
                    met_id_original_file = node_original_file.get('id_metabolite')
                    if met_id_original_file is not None and met_id_py_svg_file is not None:
                        node_py_svg_file.set('id_metabolite', str(met_id_original_file))
    for node_py_svg_file in root_py_svg_file.findall('g'):
        id_el_py_svg_file = node_py_svg_file.get('id')
        met_id_py_svg_file = node_py_svg_file.get('id_metabolite')
        if id_el_py_svg_file is not None:
            for node_original_file in root_original_file.findall('{http://www.w3.org/2000/svg}g'):
                id_el_original_file = node_original_file.get('id')
                if id_el_original_file == id_el_py_svg_file:
                    met_id_original_file = node_original_file.get('id_metabolite')
                    if met_id_original_file is not None and met_id_py_svg_file is not None:
                        node_py_svg_file.set('id_metabolite', str(met_id_original_file))

    tree_py_svg_file.write(output_filename)
