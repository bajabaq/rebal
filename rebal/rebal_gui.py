#this file is the GUI interface to the Stock Portfolio Rebalancer program
# see here: https://pysimplegui.readthedocs.io/en/latest/cookbook/

import logging
import math
import os
import PySimpleGUI as sg
import subprocess

from rebal import rebal_aux
from rebal import rebal_model
from rebal import rebal_update
from rebal import rebal_view

from rebal.tadconfig import tadconfig

#------------------------------------------------------------------------------
#global variables
#------------------------------------------------------------------------------
gui_logger = logging.getLogger(__name__)
sg.change_look_and_feel('DefaultNoMoreNagging')  # I like my windows bland 'Dark Blue 3' is an option

#---------------------------------------------------------
#SUBROUTINES
#---------------------------------------------------------

#--------------------------------------------------------------------------    
# Read the files from the various subdirs in the "data" dir
#--------------------------------------------------------------------------    
def get_data_dir():
    gui_logger.info('started')
    data_dir = os.path.join(os.getcwd(),"data")
    gui_logger.info('finished')
    return data_dir
#get data runs

def get_file_list(subdir):
    gui_logger.info('started')
        
    data_dir = get_data_dir()
    sub_data_dir = os.path.join(data_dir,subdir)
    
    file_list = next(os.walk(sub_data_dir))[2]
    a_files = file_list #['1','2','3']

    gui_logger.info('finished')
    return a_files
#enddef

def get_file(k,v):
    data_dir     = get_data_dir()
    subdir       = k.strip('_')
    sub_data_dir = os.path.join(data_dir,subdir)
    xfile        = os.path.join(sub_data_dir,v[0])
    return xfile
#enddef

#update the settings file
def set_default(k,v):
    key = k.strip('_')
    print(key,v)
    tadconfig.update_setting('rebal', key, v[0])
#enddef

def get_from_values(values,key,set_default_bool):
    for k, v in values.items():
        if k == key:
            got = get_file(k, v)
            if set_default_bool:
                set_default(k, v)
            #endif
        #endif
    #endfor
    return got
#enddef


#--------------------------------------------------------------------------    
# Create,Read,Update,Delete (CRUD) buttons for Tabs
#--------------------------------------------------------------------------    
def get_buttons(ttype, pad_lr, pad_tb, w,h):
    layout = []
    
    for bt in ["Create","Read","Update","Delete"]:

        b = sg.Button(size=(w,h),
                      pad=(pad_lr,pad_tb),
                      button_text=bt,
                      button_color=("white","blue"),
                      key="_"+ttype+"_"+bt[0]+"_")
        layout.append(b)
    #endfor
    
    return layout
#enddef

#--------------------------------------------------------------------------    
# Glide Path, Assets, User Tab layouts
#--------------------------------------------------------------------------    
def get_layout(ttype, pad_lr, pad_tb, w,h):
    gui_logger.info('started')
    a_files = get_file_list(ttype)
    a_files.sort()
    dv = []
    if len(a_files) == 0:
        dv = ""
    else:
        dv = tadconfig.get_setting('rebal', ttype)
        if dv not in a_files:        
            dv = a_files[-1]
        #endif
    #endif
    gpbuttons = get_buttons(ttype,pad_lr, pad_tb, w,h)
    layout = [[sg.Listbox(a_files,
                          default_values=dv,
                          #select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                          size=(w,h*3),
                          pad=(pad_lr,pad_tb),
                          key='_'+ttype+'_')]]
        
    for b in gpbuttons:
        layout.append([b])
    #endfor
    gui_logger.info('finished')
    return layout
#enddef


#--------------------------------------------------------------------------    
# Assets, User Tab layouts
#--------------------------------------------------------------------------    
def get_layout2(ttype, pad_lr, pad_tb, w,h):
    gui_logger.info('started')
    a_files = get_file_list(ttype)
    a_files.sort()
    dv = []
    if len(a_files) == 0:
        dv = ""
    else:
        dv = tadconfig.get_setting('rebal', ttype)
        if dv not in a_files:        
            dv = a_files[-1]
        #endif
    #endif
    layout = [[sg.Listbox(a_files,
                          default_values=dv,
                          #select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                          size=(w,h*3),
                          pad=(pad_lr,pad_tb),
                          key='_'+ttype+'_')]]
        
    #gpbuttons = get_buttons(ttype,pad_lr, pad_tb, w,h)
    #for b in gpbuttons:
    #    layout.append([b])
    #endfor
    gui_logger.info('finished')
    return layout
#enddef



def get_gp_aux(ttype,pad_lr,pad_tb,w,h):
    a_files = get_file_list(ttype)
    a_files.sort()
    dv = []
    if len(a_files) == 0:
        dv = ""
    else:
        dv = tadconfig.get_setting('rebal', ttype)
        if dv not in a_files:        
            dv = a_files[-1]
        #endif
    #endif
    
    layout = [[sg.Listbox(a_files,
                          default_values=dv,
                          #select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                          size=(w,h*3),
                          pad=(pad_lr,pad_tb),
                          key='_'+ttype+'_')]]

    return layout
#enddef

#--------------------------------------------------------------------------    
# Glide Path
#--------------------------------------------------------------------------    
def get_gp_layout(ttype, pad_lr, pad_tb, w,h):
    gui_logger.info('started')
    layout = []
    gp_layout = get_gp_aux(ttype)
    layout.append([gp_layout])
    b = sg.Button(size=(w,h),
                  pad=(pad_lr,pad_tb),
                  button_text='Show Glidepath',
                  button_color=("white","blue"),
                  key="_SHOW_GP_")
    layout.append([b])    
    gui_logger.info('finished')
    return layout
#enddef

#--------------------------------------------------------------------------    
# About Tab
#--------------------------------------------------------------------------    
def get_about_layout(pad_lr, pad_tb, w,h):
    gui_logger.info('started')
    msg = ''
    msg = msg + "Portfolio Monitor v2021.0\n"
    msg = msg + "\n"
    msg = msg + "Author: Tad Whiteside\n"
    msg = msg + "Copyright 2021\n"
    msg = msg + "License: GPL v3\n"
    msg = msg + "\n"
    
    msg = msg + "This software determines\n"
    msg = msg + "how your accounts match with\n"
    msg = msg + "your glide path.\n"
    msg = msg + "\n"
    
    layout = [
        [sg.Text(msg, auto_size_text=True, pad=(pad_lr,pad_tb))],
        ]
    gui_logger.info('finished')
    return layout
#enddef

#--------------------------------------------------------------------------    
# Update Tab
#--------------------------------------------------------------------------    
def get_update_layout(pad_lr, pad_tb, w,h):
    gui_logger.info('started')

    #prices
    price_button = sg.Button(size=(w,h),
                             pad=(pad_lr,pad_tb),
                             button_text="Update Prices",
                             button_color=("white","blue"),
                             key="_UPDATE_PRICES_")
    #rois
    roi_button = sg.Button(size=(w,h),
                             pad=(pad_lr,pad_tb),
                             button_text="Update ROIs",
                             button_color=("white","blue"),
                             key="_UPDATE_ROIS_")
    #multi
    multi_button = sg.Button(size=(w,h),
                             pad=(pad_lr,pad_tb),
                             button_text="Update Multi-Asset",
                             button_color=("white","blue"),
                             key="_UPDATE_MULTI_")    
    
    layout = [
        [price_button],
        [roi_button],
        [multi_button],
        ]

    gui_logger.info('finished')
    return layout
#enddef


#--------------------------------------------------------------------------    
# Monitor Tab (This button does the action)
#--------------------------------------------------------------------------    
def get_monitor_layout(pad_lr, pad_tb, w,h):
    gui_logger.info('started')
    bt = 'Monitor Portfolio'

    layout = []
    b = sg.Button(size=(w,h),
                  pad=(pad_lr,pad_tb),
                  button_text=bt,
                  button_color=("white","blue"),
                  key="_MONITOR_")
    layout.append([b])

    b = sg.Button(size=(w,h),
                  pad=(pad_lr,pad_tb),
                  button_text='Save',
                  button_color=("white","blue"),
                  disabled=True,
                  key="_SAVE_")
    layout.append([b])     

    b = sg.Button(size=(w,h),
                  pad=(pad_lr,pad_tb),
                  button_text='Show Glidepath',
                  button_color=("white","blue"),
                  key="_SHOW_GP_")
    layout.append([b])

    b = sg.Checkbox("Also calc with User ROI",key="_CUSERROI_")
    layout.append([b])
    
    gui_logger.info('finished')
    return layout
#enddef


#--------------------------------------------------------------------------    
# Monitor Tab (This button does the action)
#--------------------------------------------------------------------------    
def get_monitor_layout2(pad_lr, pad_tb, w,h):
    gui_logger.info('started')
    bt = 'Monitor Portfolio'
    layout = []

    gp_layout    = get_gp_aux('glide_paths',pad_lr,pad_tb,w,h)
    asset_layout = get_layout2('assets',pad_lr, pad_tb, w,h)
    user_layout  = get_layout2('users',pad_lr, pad_tb, w,h)

    layout.append([sg.Frame('Glide Path',gp_layout)])
    layout.append([sg.Frame('Asset',asset_layout)])
    layout.append([sg.Frame('User',user_layout)])

#    layout.extend(asset_layout)
#    layout.extend(user_layout)
    
    b = sg.Button(size=(w,h),
                  pad=(pad_lr,pad_tb),
                  button_text=bt,
                  button_color=("white","blue"),
                  key="_MONITOR_")
    layout.append([b])

    b = sg.Button(size=(w,h),
                  pad=(pad_lr,pad_tb),
                  button_text='Save',
                  button_color=("white","blue"),
                  disabled=True,
                  key="_SAVE_")
    layout.append([b])     

    b = sg.Button(size=(w,h),
                  pad=(pad_lr,pad_tb),
                  button_text='Show Glidepath',
                  button_color=("white","blue"),
                  key="_SHOW_GP_")
    layout.append([b])

    b = sg.Checkbox("Also calc with User ROI",key="_CUSERROI_")
    layout.append([b])

    
    gui_logger.info('finished')
    return layout
#enddef

#--------------------------------------------------------------------------    
# Get the layout
#--------------------------------------------------------------------------    
def get_main_layout():
    gui_logger.info('started')
    #padding left/right and top/bottom (probably in pixels)
    pad_lr = 40
    pad_tb = 10
    
    #width/height in chars
    w = 30
    h = 1
     
#    gp_layout      = get_layout('glide_paths',pad_lr, pad_tb, w,h)
    gp_layout      = get_gp_layout('glide_paths',pad_lr, pad_tb, w, h)
    asset_layout   = get_layout('assets',pad_lr, pad_tb, w, h)
    user_layout    = get_layout('users',pad_lr, pad_tb, w, h)
    monitor_layout = get_monitor_layout(pad_lr, pad_tb, w, h)
    update_layout  = get_update_layout(pad_lr, pad_tb, w, h)
    about_layout   = get_about_layout(pad_lr, pad_tb, w, h)    
    
    tab_list = []
    tab_list.append(sg.Tab('Monitor', monitor_layout))
    tab_list.append(sg.Tab('Update', update_layout))
    tab_list.append(sg.Tab('Glide Path', gp_layout))
    tab_list.append(sg.Tab('Assets', asset_layout))
    tab_list.append(sg.Tab('Users',  user_layout))
    tab_list.append(sg.Tab('About',  about_layout))
    
    layout = [
            [sg.TabGroup([tab_list])],
        ]
        
    gui_logger.info('finished')
    return layout
#enddef


#--------------------------------------------------------------------------    
# Get the layout
#--------------------------------------------------------------------------    
def get_main_layout2():
    gui_logger.info('started')
    #padding left/right and top/bottom (probably in pixels)
    pad_lr = 40
    pad_tb = 10
    
    #width/height in chars
    w = 30
    h = 1
     
#    gp_layout      = get_layout('glide_paths',pad_lr, pad_tb, w,h)
    monitor_layout = get_monitor_layout2(pad_lr, pad_tb, w,h)
    update_layout  = get_update_layout(pad_lr, pad_tb, w,h)
    #gp_layout      = get_gp_layout('glide_paths',pad_lr, pad_tb, w,h)
    #asset_layout   = get_layout('assets',pad_lr, pad_tb, w,h)
    #user_layout    = get_layout('users',pad_lr, pad_tb, w,h)

    about_layout   = get_about_layout(pad_lr, pad_tb, w,h)    
    
    tab_list = []
    tab_list.append(sg.Tab('Monitor', monitor_layout))
    tab_list.append(sg.Tab('Update', update_layout))
    tab_list.append(sg.Tab('About',  about_layout))
    
    layout = [
            [sg.TabGroup([tab_list])],
        ]
        
    gui_logger.info('finished')
    return layout
#enddef

#--------------------------------------------------------------------------    
# Get the layout, update/set the values, and refresh the window
#--------------------------------------------------------------------------    
def update_gui(window):
    gui_logger.info('started')
    #layout = get_main_layout()
    layout = get_main_layout2()

    window.Close()
    window = get_main_window(layout)
    window.Finalize()
    gui_logger.info('finished')
    return window
#enddef

#--------------------------------------------------------------------------    
# Make the Main Window
#--------------------------------------------------------------------------    
def get_main_window(layout):
    gui_logger.info('started')
    window = sg.Window("Portfolio Monitor", layout)
    gui_logger.info('finished')
    return window
#enddef

#--------------------------------------------------------------------------    
# HERE IS THE MAIN GUI SETUP
#--------------------------------------------------------------------------    
def main_gui():
    gui_logger.info('started')
    #create an empty window object, then set it up
    window = get_main_window(None)
    window = update_gui(window)
    
    main_gui_read = True
    ret_val       = 0
    outfile       = ''
    while True:
        if main_gui_read == True:
            event, values = window.Read(timeout=1000, timeout_key="__MAIN_TIMEOUT__")
        #endif

        if event is None or event == 'Exit':
            break

        #something cool to do would be to:
        #view the glide path (graph)
        #view the assets (text)
        #view the user (text)
        elif '_UPDATE_PRICES_' in event:
            fassets     = get_from_values(values,'_assets_',False)
            rebal_update.update_prices(fassets,True)
        elif '_UPDATE_ROIS_' in event:
            #TODO, need to put a cap on this (maybe per asset class)
            #      b/c VTI has ROI of 21% (but only for 20 years vs 40 - ie back to 1970s)
            #      that should probably be closer to 10%
            #      or maybe not, this version does account for dividends/cap gains
            #      by using the adjusted close
            fassets     = get_from_values(values,'_assets_',False)            
            rebal_update.update_rois(fassets,True)
        elif '_UPDATE_MULTI_' in event:
            fglide_path = get_from_values(values,'_glide_paths_',True)
            fassets     = get_from_values(values,'_assets_',False)            
            rebal_update.update_multi(fassets, fglide_path,True)
        elif '_MONITOR_' in event:
            fglide_path = get_from_values(values,'_glide_paths_',True)
            fassets     = get_from_values(values,'_assets_',True)
            fusers      = get_from_values(values,'_users_',True)

            top_dir = get_data_dir()

            #update the asset data
            #TODO return a warning if something goes wrong
            rebal_update.update_prices(fassets,False)

            #TODO, need to put a cap on this (maybe per asset class)
            #      b/c VTI has ROI of 21% (but only for 20 years vs 40 - ie back to 1970s)
            #      that should probably be closer to 10%
            #      or maybe not, this version does account for dividends/cap gains
            #      by using the adjusted close
            rebal_update.update_rois(fassets,False)

            #update the fraction of each  asset class for each multi-asset asset
            rebal_update.update_multi(fassets,fglide_path,False)
            
            #kicking over to rebal-model (model-view-controller)
            print("Do portfolio monitoring")
            print("using the info found in these files:")
            print(fglide_path,fassets,fusers)
            outfile1 = rebal_model.monitor(top_dir,fglide_path,fassets,fusers,False)

            if values['_CUSERROI_'] == True:
                outfile2 = rebal_model.monitor(top_dir,fglide_path,fassets,fusers,True)                
            #endif
            
            window.Element("_SAVE_").Update(disabled=False)
        elif '_SHOW_GP_' in event:
            #get the files and save the defaults
            for k,v in values.items():
                if k == '_glide_paths_':
                    fglide_path = get_file(k,v)
                #endif
            #endfor
            rebal_view.graph_glidepath(fglide_path)                        
        elif '_SAVE_' in event:
            rebal_model.savefile(outfile1)
            if values['_CUSERROI_'] == True:
                rebal_model.savefile(outfile2)
            #endif
            
            window.Element("_SAVE_").Update(disabled=True)            
        elif '_MAIN_TIMEOUT' in event:
            #user hasn't clicked anything lately
            pass
        else:
            print("in the else (event action not defined)...")
            print("Event: " + event)
            print("Take event action here")
            print(event, values)
        #endif
    #endwhile
    
    window.Close()
    gui_logger.info('finished')
    return ret_val
#enddef

#------------------------------------------------------------------------
def main():
    #file_verify.file_verify()
    
    gui_log_file = os.path.join(os.path.join(os.getcwd(), "data"),"rebal_gui.log")
    gui_logger   = rebal_aux.setup_logging(gui_log_file)
    
    ret_val = main_gui()
#enddef

#------------------------------------------------------------------------
if __name__ == "__main__":
    main()
#endif
