#this code is written in python3

#------------------------------------------------------------------------------
#this module updates the assests file
#
#
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#python imports
#------------------------------------------------------------------------------
import csv
import datetime
import dateutil
import decimal
import logging
import numpy as np
import os
import pandas as pd
import PySimpleGUI as sg

import time
import webbrowser
import yfinance as yf

from rebal import finance_plot_aux

#GOT TO FIGURE THIS OUT
#from .tadconfig import tadconfig
from rebal.tadconfig import tadconfig
#from tadconfig import tadconfig

#------------------------------------------------------------------------------
#global variables
#------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
sg.change_look_and_feel('DefaultNoMoreNagging')  # I like my windows bland 'Dark Blue 3' is an option

#------------------------------------------------------------------------------
# see how long ago something was
#------------------------------------------------------------------------------
def data_is_old(asset_key, old_time):
    today      = datetime.datetime.today()
    #get this value from settings.ini
    key  = "update_freq_" + asset_key
    past = tadconfig.get_setting('rebal',key,type='float')
    yestertime = today - datetime.timedelta(hours=past)

    get_new_data = False

    try:
        data_age = datetime.datetime.strptime(old_time,'%Y-%m-%d %H:%M:%S.%f')
    except: #time format is wierd, get data again (1 hour in the past from yestertime)
        data_age = yestertime - datetime.timedelta(hours=1)
    
    #if age of data is more than 1 hour old, get new data
    if data_age < yestertime:
        print(old_time, "<", yestertime, " getting new data")
        get_new_data = True
    #endif

    return get_new_data
#endif


def get_years(final,init):
    diff_years  = (final - init)/np.timedelta64(1,'Y')
    print(diff_years,"years")
    return diff_years
#enddef

#------------------------------------------------------------------------------
# get the price of the asset
# utime (last) not used yet TODO
#------------------------------------------------------------------------------
def get_price(symbol, old_price, utime):
    new_price = decimal.Decimal(old_price)
    print("getting new data for " + symbol + ":")           
    tsymbol   = yf.Ticker(symbol)
    print(tsymbol)
    thist     = tsymbol.history(period='5d')  #was 1d but fails on mutual funds
    new_price = decimal.Decimal(thist.iloc[-1]['Close']) #get closing price from last row
    new_price = new_price.quantize(decimal.Decimal('0.0001'),rounding=decimal.ROUND_HALF_UP)
        
    #tinfo     = tsymbol.info
    #new_price = decimal.Decimal(tinfo['previousClose'])
    print("price",new_price)
    
    return new_price    
#enddef

def get_val_manual(desc, title, old_val):
    width  = len(desc) + 5
    layout = [[sg.Text(desc,size=(width,None)),sg.InputText(size=(10,None),key='_val_')]]
    layout.append([sg.Submit(),sg.Cancel()])

    #TODO include a while that checks that price is a number
    window = sg.Window(title, layout)
    event, values = window.read()
    window.close()
    
    if event == 'Cancel':
        val = old_val
        #break
    else:
        val = decimal.Decimal(values['_val_'])
    #endwhile
    
    return val
#enddef


#------------------------------------------------------------------------------
# get roi (sdate='inception' or specific date)
# typically since inception (to figure what might happen in future)
# if a specific date, then maybe use for future tax determination  TODO
#------------------------------------------------------------------------------
def get_roi(symbol, old_roi, sdate, fassets):
    roi = old_roi

    print("getting new data for " + symbol + ":")           
    tsymbol = yf.Ticker(symbol)
    if sdate == 'inception':
        thist = tsymbol.history(period='max')
    else:
        thist = tsymbol.history(period='max') #don't have anything else defined yet
    #endif

    assets_dir = os.path.dirname(fassets)
    data_dir   = os.path.dirname(assets_dir)
    hist_file  = os.path.join(os.path.join(data_dir,"ticker"),symbol+"-data.csv")
    
    thist.to_csv(hist_file,sep='\t',encoding='utf-8')

    (adates,aval,_ph,_pl) = finance_plot_aux.read_data(hist_file)    

    (_aval2,_ays,_m,_b,_rms,_A,_B,_o,_rms2,roi_percent) = finance_plot_aux.fit(adates,aval)

    """
    final_price = thist.iloc[-1]['Close'] #get closing price from last row
    init_price  = thist.iloc[0]['Close']  #get closing price from first row

    final_date  = thist.index[-1]  #get final date
    init_date   = thist.index[0]   #get init date

    years = get_years(final_date, init_date)

    print(final_price,init_price,years)
    
    roi = ((final_price - init_price)/init_price) / years
    """
    roi = round(roi_percent/100,6)
    
    print("roi",roi)
    
    #what about dividends/cap gains? (this for specific holdings to be implemented later)
    #roi = (((final-init)*shares + dividends - commissions) / (init*shares))*100
    
    return roi    
#enddef

#------------------------------------------------------------------------------
# get multi asset fractions
#------------------------------------------------------------------------------
def read_gp_acs(fgp):
    gpacs = []
    #from gp file
    with open(fgp,mode='r') as fh:
        csv_reader = csv.DictReader(fh)
        csv_reader.fieldnames = [name.lower().strip() for name in csv_reader.fieldnames]
        gpacs = csv_reader.fieldnames
        gpacs.remove('age')
    #endwith
    return gpacs
#enddef

def get_multi_aux(gpacs, symbol, desc):
    maxstr = max(gpacs, key = len)
    maxlen = len(maxstr)
    width  = maxlen + 5
        
    minok = 0.9999
    maxok = 1.0001
    
    s = 0.0
    while s < minok or s > maxok:
        layout = [[sg.Text(desc)]]
        for ac in gpacs:
            line = [sg.Text(ac,size=(width,None)),sg.InputText(size=(10,None),key=ac)]
            layout.append(line)
        #endfor
        layout.append([sg.Submit(),sg.Cancel()])
        window = sg.Window("MultiAsset Update "+ symbol, layout)
        event, values = window.read()
        window.close()
        
        multi = {}
        if event == 'Cancel':
            multi = 'no_update'
            break
        else:
            for k,v in values.items():
                print(k, v)
                if v == '' or v == None:
                    v = 0.0
                else:
                    v = float(v)
                #endif
                multi[k] = v
                s = s + v
            #endfor

            if s < minok or s > maxok:
                msg ="Total fraction (" + str(s) + ") did not sum to 1.0, try again (4 decimal places)"
                sg.popup(msg)
                s = 0
            #endif
        #endif
    #endwhile
        
    return multi    
#enddef

def yn_popup(question):
    yn = 'yes'
    layout = [[sg.Text(question)],
              [sg.Button('Yes'),sg.Button('No')]]
    window = sg.Window('Yes or No', layout,enable_close_attempted_event=True)
    while True:
        event, values = window.read()
        #print(event,values)
        if event == 'Yes':
            yn = 'yes'
            break
        elif event == 'No':
            yn = 'no'
            break
        elif event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            yn = 'cancel'
            break
        #endif
    #endwhile
    window.close()
    return yn
#endif

def input_popup(title,question):
    info = ''
    layout = [[sg.Text(question),sg.Input(key='_INPUT_')],
              [sg.Button('Submit')]]
    window = sg.Window(title, layout)
    while True:
        event, values = window.read()
        print(event, values)
        if event == 'Submit':
            info = values['_INPUT_']
            break
#        elif event == sg.WIN_CLOSED:
#            break
        #endif
    #endwhile
    window.close()
    return info
#enddef

def dict_popup(title, num_rows):
    minok = 0.9999
    maxok = 1.0001
    adict = {}
    layout = [[sg.Text("Name"),sg.Text("Fraction")]]
    for i in range(1,num_rows+1):
        row = [sg.Input(key='_name'+str(i)+'_'),sg.Input(key='_frac'+str(i)+'_')]
        layout.append(row)
    #endfor
    layout.append([sg.Button('Submit')])
    window = sg.Window(title, layout)
    while True:
        event, values = window.read()
#        print(event, values)
        if event == 'Submit':
            s = 0
            for i in range(1,num_rows+1):
                adict[values['_name'+str(i)+'_']] = float(values['_frac'+str(i)+'_'])
                s = s + float(values['_frac'+str(i)+'_'])
            #endfor
            if s > minok or s < maxok:
                break
            else:
                print('not 1, loop again')
            #endif
        elif event == sg.WIN_CLOSED:
            break
        #endif
    #endwhile
    window.close()
    return adict
#enddef

def get_gp_frac(gpacs,name,num_ac):
    minok = 0.9999
    maxok = 1.0001
    adict = {}
    layout = [[sg.Text("Asset Class"),sg.Text("Fraction")]]
    for i in range(1,num_ac+1):
        row = [sg.Combo(gpacs,readonly=True,key='_name'+str(i)+'_'),sg.Input(key='_frac'+str(i)+'_')]
        layout.append(row)
    #endfor
    layout.append([sg.Button('Submit')])
    window = sg.Window(name, layout)
    while True:
        event, values = window.read()
        print(event, values)
        if event == 'Submit':
            s = 0
            for i in range(1,num_ac+1):
                adict[values['_name'+str(i)+'_']] = float(values['_frac'+str(i)+'_'])
                s = s + float(values['_frac'+str(i)+'_'])
            #endfor
            if s > minok or s < maxok:
                break
            else:
                print('not 1, loop again')
            #endif
        elif event == sg.WIN_CLOSED:
            break
        #endif
    #endwhile
    window.close()
    return adict
#enddef

def gp_frac(gpacs,symbol,desc):
    fund_of_funds = yn_popup("Is " + desc  + " a Fund of Funds?")

    if fund_of_funds == 'yes':
        num_funds = 'a'
        while not num_funds.isnumeric():
            num_funds = input_popup("Funds","How many Funds?")
        #endwhile
        num_funds = int(num_funds)
        #get dict of funds;fraction
        afunds = dict_popup("Funds",num_funds)

        adict = {}
        for ac in gpacs:
            adict[ac] = 0
        #endfor

        for name,frac in afunds.items():
            gpdict = gp_frac(gpacs,'',name)
            print(name, frac, gpdict)
            for ac,frac2 in gpdict.items():
                adict[ac] = adict[ac] + frac2 * frac 
            #endfor
        #endfor

        return adict
    elif fund_of_funds == 'no':
        num_ac = 'a'
        while not num_ac.isnumeric():
            num_ac = input_popup("Asset Classes","How many Asset Classes are in this Fund?")
        #endwhile
        num_ac = int(num_ac)
        adict = get_gp_frac(gpacs,desc,num_ac)
        print(adict)
        return adict
    else:
        return 'no_update'
    #endif    
#enddef

def get_multi(symbol, desc, old_multi, fglidepath):
    if symbol == 'unlisted':
        pass
    else:
        #if asset class is multi, popup vanguard or yahoo webpage showing portfolio?
        url1 = "https://finance.yahoo.com/quote/"+symbol+"/holdings"
        url2 = "https://investor.vanguard.com/mutual-funds/profile/portfolio/"+symbol
        try:
            webbrowser.open_new(url1)
            time.sleep(2)
            webbrowser.open_new_tab(url2)
        except Exception as e:
            print(e)
        #endtry
    #endif

    #get the glide path asset classes
    gpacs = read_gp_acs(fglidepath)

    multi = gp_frac(gpacs,symbol,desc)
    print(multi)

    #get the data via a popup
#    multi = get_multi_aux(gpacs, symbol, desc)

    return multi
#enddef



#------------------------------------------------------------------------------
#update the assets file
#------------------------------------------------------------------------------
def update_assets_aux(fassets,asset_key,asset_dt_key,variable,override):
    logger.info('started')

    #make the tmp file
    tempfile = os.path.splitext(fassets)[0] + '.tmp'   
    try:
        os.remove(tempfile)  # delete any existing temp file
    except OSError:
        pass

    #read the original file, write to the tempfile
    with open(fassets,mode='r') as fh, open(tempfile,mode='w') as outfile:
        csv_reader = csv.DictReader(fh)
        csv_reader.fieldnames = [name.lower() for name in csv_reader.fieldnames]
        writer = csv.DictWriter(outfile,fieldnames=csv_reader.fieldnames)
        writer.writeheader()
        for row in csv_reader:
            asset_class = row['asset_class'].lower()
            symbol      = row['symbol']
            asset_val   = row[asset_key]
            asset_dt    = row[asset_dt_key]
            desc        = row['description']

            if ("DUMMY" in symbol) or ('cash' in asset_class):
                pass
            else:
                if (data_is_old(asset_key, asset_dt) or override):
                    new_time = datetime.datetime.now()
                    if asset_key == 'price':
                        if "unlisted" == symbol:
                            new_val = get_val_manual(desc,"Price Update",asset_val)
                        else:
                            new_val = get_price(symbol, asset_val, variable)
                        #endif
                    elif asset_key == 'roi':
                        if "unlisted" == symbol:
                            new_val = get_val_manual(desc,"ROI Update", asset_val)
                        else:
                            new_val = get_roi(symbol, asset_val, variable,fassets)
                        #endif
                    elif asset_key == 'multi':
                        if asset_class == 'multi':
                            new_val = get_multi(symbol, desc, asset_val, variable)
                            if new_val == 'no_update':
                                new_val = asset_val
                                new_time= asset_dt
                            #endif
                        else: #don't update multi fields in non-multi assets
                            new_val  = asset_val
                            new_time = asset_dt
                        #endif
                    #endif
                    row[asset_key]    = new_val
                    row[asset_dt_key] = new_time
                 #endif
            #endif
            writer.writerow(row)
        #endfor
    #endwith

    #assuming it didn't crap out, rename tempfile, fassets file
    os.rename(tempfile, fassets)

    logger.info('finished')    
#enddef    

#------------------------------------------------------------------------------
# TODO: return exception (or something) if there is an error so can warn user
#------------------------------------------------------------------------------
def update_prices(fassets,override):
    print("updating prices")
    update_assets_aux(fassets,'price','price_update_date','last',override)
    print("done")

def update_rois(fassets,override):
    print("updating rois")
    update_assets_aux(fassets,'roi','roi_update_date','inception',override)
    print("done")

def update_multi(fassets, fglide_path,override):
    print("updating multi asset class assets")
    update_assets_aux(fassets,'multi','multi_update_date',fglide_path,override)
    print("done")
   
    
#------------------------------------------------------------------------------
if __name__ == "__main__":
    print("in the main")

    top  ='/home/tad/Documents/projects/rebal/data'
#    fglide_path = os.path.join(os.path.join(top,'glide_paths'),'5050gp0.csv')
    fglide_path = os.path.join(os.path.join(top,'glide_paths'),'vanguardtr.csv')
    fassets     = os.path.join(os.path.join(top,'assets'),'tad.csv')
    fusers      = os.path.join(os.path.join(top,'users'),'5050u.csv')

    #update_prices(fassets)
    update_rois(fassets,True)
    
#endif
