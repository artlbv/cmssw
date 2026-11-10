import jinja2
import L1Trigger.Phase2L1GT.VHDLWriter.Conditions
import os

def conditionwriter(name,attributes):
    templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(__file__))    # this has to be changed there seems to be a version of this thats called packageloader instead of filesystemloader
    templateEnv = jinja2.Environment(loader=templateLoader,trim_blocks=True,lstrip_blocks=True)
    template = templateEnv.get_template(attributes.Template,)
 
    '''
    This for loop facilitates 2 functionalities. 
    1 -> Add num_eta_regions variable in regionsAbsEtaLowerBounds cuts, this var counts 
         the length of each sublist BEFORE padding. NUM_ETA_REGIONS is also added in jinja
    2 -> In case of sublists of different lengths, add zeros to match their length (padding),
         with the max value of num_eta_regions. Otherwise one gets vhdl compiler error
    '''
    maxlength = 0   
    for cut_name, cut_obj in attributes.Cuts.items():
        if cut_name == "regionsAbsEtaLowerBounds":
            num_eta_regions = []  
            for sublist in cut_obj.hwcut:
                if isinstance(sublist, list):
                    num_eta_regions.append(len(sublist))
                elif sublist == '(others => 0)':
                    num_eta_regions.append(0)  
            cut_obj.num_eta_regions = num_eta_regions
            maxlength = max(num_eta_regions)
        cut_obj.hwcut = pad_lists(cut_obj.hwcut, maxlength)  
        cut_obj.physcut = pad_lists(cut_obj.physcut, maxlength)  

    if(attributes.Label == 'L1GTDoubleObjectCond'):
        outputText = template.render(condition_name = name, cuts = attributes.Cuts, objects_first = attributes.InputObjects.get(1),objects_second = attributes.InputObjects.get(2), algo_bit_name = name) 
    elif(attributes.Label == 'L1GTSingleObjectCond' ):
        outputText = template.render(condition_name = name, cuts = attributes.Cuts, object = attributes.InputObjects.get(1), algo_bit_name = name) 
    elif(attributes.Label == 'L1GTTripleObjectCond' ):
        outputText = template.render(condition_name = name, cuts = attributes.Cuts, objects_first = attributes.InputObjects.get(1),objects_second = attributes.InputObjects.get(2),objects_third = attributes.InputObjects.get(3), algo_bit_name = name) 
    elif(attributes.Label == 'L1GTQuadObjectCond' ):
        outputText = template.render(condition_name = name, cuts = attributes.Cuts, objects_first = attributes.InputObjects.get(1),objects_second = attributes.InputObjects.get(2),objects_third = attributes.InputObjects.get(3),objects_fourth = attributes.InputObjects.get(4), algo_bit_name = name) 
    else:
        print("Warning Condition not know to algounit writer, condition is of type{}".format(attributes.Label))
    return outputText

def algounitWriter(algobits,conditions,filts,logicalcomb,slrnumber):
    templateLoader = jinja2.FileSystemLoader(searchpath=os.path.dirname(__file__))    # this has to be changed there seems to be a version of this thats called packageloader instead of filesystemloader
    templateEnv = jinja2.Environment(loader=templateLoader,trim_blocks=True,lstrip_blocks=True)
    template = templateEnv.get_template("algounit.template",)
    outputText = template.render(algobits = algobits, Conditions = conditions, filtermodules = filts ,logicalcomb = logicalcomb, slrnumber = slrnumber)
    return outputText

def writeAlgounitToFile(filename,contents):
    f = open(filename,"w")
    f.write(contents)
    f.close()

def pad_lists(input_list, max_length):
    """ Ensures all sublists in input_list have the same length by padding with zeros, but skips 'others => 0'. """
    if not isinstance(input_list, list) or not any(isinstance(i, list) for i in input_list):
        return input_list  
    # Filter out non-list elements like 'others => 0' when determining max length
    valid_sublists = [sublist for sublist in input_list if isinstance(sublist, list)]
    if not valid_sublists:  
        return input_list 
    padded_list = [
        sublist + [0] * (max_length - len(sublist)) if isinstance(sublist, list) else sublist
        for sublist in input_list
    ]
    return padded_list

    