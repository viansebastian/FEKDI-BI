import pandas as pd
import pm4py as pm
import os
import io
from PIL import Image
import tempfile
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as pnml_importer

# DRAW PETRI NET
def draw_petri_csv(file_csv, sep, case_id, activity_key, timestamp_key):

    # check input format  
    df = pd.read_csv(file_csv, sep = sep)
    df = pm.format_dataframe(df, case_id = case_id, activity_key = activity_key, timestamp_key = timestamp_key)
    petri_net, initial_marking, final_marking = pm.discover_petri_net_inductive(df)
    
    # Visualize petri net
    img_petri = pn_visualizer.apply(petri_net, initial_marking, final_marking, parameters= {'format': 'png'})
    
    # PetriNet to PNML handler
    with tempfile.NamedTemporaryFile(suffix='.pnml', delete=False) as temp_file:
        pnml_exporter.apply(petri_net, initial_marking, temp_file.name, final_marking=final_marking)
        temp_file_path = temp_file.name
        
    with open(temp_file_path, 'r') as f:
        pnml_content = f.read()
    
    os.remove(temp_file_path)
    
    # PetriNet to PNG handler
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        pn_visualizer.save(img_petri, temp_file.name)
        temp_file_path = temp_file.name
        
        # Read the image from the temporary file into a BytesIO object
    with open(temp_file_path, 'rb') as f:
        img_stream = io.BytesIO(f.read())
    img_stream.seek(0)
    
    os.remove(temp_file_path)
    
    image = Image.open(img_stream)
    return pnml_content, image, petri_net, initial_marking, final_marking

# Example usage: 
# file = pd.read_csv('running-example.csv', sep=';')
# pnml, image, pn, im, fm = draw_petri_csv('running-example.csv', ';', 'case_id', 'activity', 'timestamp')
# plt.imshow(image)
# plt.axis('off')
# plt.show()
# pnml

def draw_petri_xes(file_xes):
    
    df = xes_importer.apply(file_xes)

    petri_net, initial_marking, final_marking = pm.discover_petri_net_inductive(df)
    # petri_net, initial_marking, final_marking = inductive_miner.apply(df)
    
    # Visualize petri net
    img_petri = pn_visualizer.apply(petri_net, initial_marking, final_marking, parameters= {'format': 'png'})
    
    # PetriNet to PNML handler
    with tempfile.NamedTemporaryFile(suffix='.pnml', delete=False) as temp_file:
        pnml_exporter.apply(petri_net, initial_marking, temp_file.name, final_marking=final_marking)
        temp_file_path = temp_file.name
        
    with open(temp_file_path, 'r') as f:
        pnml_content = f.read()
    
    os.remove(temp_file_path)
    
    # PetriNet to PNG handler
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        pn_visualizer.save(img_petri, temp_file.name)
        temp_file_path = temp_file.name
        
        # Read the image from the temporary file into a BytesIO object
    with open(temp_file_path, 'rb') as f:
        img_stream = io.BytesIO(f.read())
    img_stream.seek(0)
    
    os.remove(temp_file_path)
    
    image = Image.open(img_stream)
    
    return pnml_content, image, petri_net, initial_marking, final_marking

# Example Usage: 
# file_xes = 'running-example.xes'
# pnml, image, pn, im, fm = draw_petri_xes(file_xes)
# plt.imshow(image)
# plt.axis('off')
# plt.show()
# pnml

def token_based_replay_csv(file_csv, sep, case_id, activity_key, timestamp_key, petri):
    
    df = pd.read_csv(file_csv, sep = sep)   
    pn, im, fm = pnml_importer.apply(petri)
    df = pm.format_dataframe(df, case_id = case_id, activity_key = activity_key, timestamp_key = timestamp_key)
    a = pm.fitness_token_based_replay(df, pn, im, fm)
    
    return a 


# Example usage: 
# data_test = pd.read_csv('running_example_broken.csv', sep = ';')
# pnml_path = 'discovered_petri_net.pnml'
# x = token_based_replay_csv('running_example_broken.csv', ';', 'case:concept:name', 'concept:name', 'time:timestamp', pnml_path)
# x

def token_based_replay_xes(file_xes, petri):
    
    df = xes_importer.apply(file_xes)
    pn, im, fm = pnml_importer.apply(petri)
    a = pm.fitness_token_based_replay(df, pn, im, fm)
    
    return a 

# y = token_based_replay_xes(file_xes, pnml_path)
# y

def diagnostics_alignments_xes(file_xes, petri):
    df = xes_importer.apply(file_xes)
    pn, im, fm = pnml_importer.apply(petri)
    a = pm.conformance_diagnostics_alignments(df, pn, im, fm)
    
    return a 

# a2 = diagnostics_alignments_xes(file_xes, pnml_path)
# a2

def diagnostics_alignments_csv(event_log, sep, case_id, activity_key, timestamp_key, petri):

    df = pd.read_csv(event_log, sep = sep)
    pn, im, fm = pnml_importer.apply(petri)
    df = pm.format_dataframe(df, case_id = case_id, activity_key = activity_key, timestamp_key = timestamp_key)
    a = pm.conformance_diagnostics_alignments(df, pn, im, fm)
    
    return a 

# alignment = diagnostics_alignments_csv(df_problem, '', 'case:concept:name', 'concept:name', 'time:timestamp', pnml_path)
# alignment