#this code is written in python3


#------------------------------------------------------------------------------
#METHOD



#exit
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#python imports
#------------------------------------------------------------------------------
import csv
import datetime
import decimal
import json
import logging
import math
import numpy
import os
import shutil
import sys
import time

#------------------------------------------------------------------------------
#user imports
#------------------------------------------------------------------------------
#FIX THIS WHEN MAKING USE GUI
from rebal import rebal_view #this is when called from rebal_gui
#import rebal_view           #this is when call directly from __MAIN__

#from rebal.tadconfig import tadconfig


#------------------------------------------------------------------------------
#global variables
#------------------------------------------------------------------------------
logger = logging.getLogger(__name__)

#==============================================================================
#Classes/Objects
#==============================================================================
class Asset:
    def __init__(self,asset_class,row,frac):
        self.asset_class = asset_class
        for k, v in row.items():
            if k == 'symbol':
                self.symbol = v.upper()
            elif k == 'quantity':
                self.quantity = decimal.Decimal(float(v)*frac)
            elif k == 'price':
                self.price = decimal.Decimal(v)
            elif k == 'price_update_date':
                self.pudate = v
            elif k == 'user_roi':
                self.user_roi = decimal.Decimal(v)
            elif k == 'roi':
                self.roi = decimal.Decimal(v)
            elif k == 'roi_update_date':
                self.rudate = v
            elif k == 'description':
                self.desc = v
            #endif
        #endfor
        self.total         = self.total_value()
        self.gp_assetclass = None
    #enddef
        
    def total_value(self):
        tv = self.quantity * self.price
        tv = tv.quantize(decimal.Decimal('0.01'))
        return tv
    #enddef
#endclass
      

class AssetClass:
    def __init__(self,name):
        self.name  = name
        
#endef

class AllAssets:
    def __init__(self,total):
        self.total = total
    #endef
#endclass

#add dict of each {ac1name:ac1%,ac2name:ac2%,....acNname:acN%}
#when reading file
class GlidePath:
    def __init__(self,age):
        self.age = age
    #enddef
#endclass

class User:
    def __init__(self):
        self.expected_annual_expenses = None
        self.months_add_money         = None
        self.monthly_savings_amt      = None
        self.retire_age               = None
        self.target_tolerance         = None
        self.birthday                 = None
        self.warnings                 = []
    #enddef


#==============================================================================
#SUBROUTINES
#==============================================================================

#this seems really convoluted
def read_glide_path(fgp):
    gp = {}
    #from gp file
    #
    with open(fgp,mode='r') as fh:
        csv_reader = csv.reader(fh)
        i = 0
        for row in csv_reader:
            if i == 0: #age row
                col = 0
                for age in row:
                    if col == 0:
                        pass #age
                    else:
                        gp[int(age)] = {}
                    #endif
                    col = col+1
                #endfor
            else:  #asset class row
                col = 0
                for c in row:
                    if col == 0:
                        ac = c  #asset class name
                        print(ac)
                    else:
                        gp[col].update({ac:float(c)})
                    #endif
                    col = col + 1
                #endfor
            #endif
            i = i + 1
        #endfor
    #endwith

#    for k,v in gp.items():
#        print(k,v)
    
    return gp
#enddef

def read_glide_path2(fgp):
    gpos = []
    #from gp file
    with open(fgp,mode='r') as fh:
        csv_reader = csv.DictReader(fh)
        csv_reader.fieldnames = [name for name in csv_reader.fieldnames]
        for row in csv_reader:
            row.update({'zzzother':'0'})  #add the catchall asset-class
            gpos.append(row)
        #endfor
    #endwith

#    print("\n\n\n\n")
#    for gp in gpos:
#        if gp['age'] == str(100):
#            print(gp)
#    print("\n\n\n\n")
    
    return gpos
#enddef

#------------------------------------------------------------------------------
#read the users file
#------------------------------------------------------------------------------
def read_users(fuser):
    user = User()
    with open(fuser,mode='r') as fh:
        csv_reader = csv.reader(fh)
        for row in csv_reader:
            val = None
            key = row[0].strip().lower()
            if key == 'retire_age':
                val = int(row[1])
            elif key == 'birthday':
                val = row[1]   #TODO check that format is MM/DD/YYYY
            else:
                val = decimal.Decimal(row[1])
            #endif
            setattr(user,key,val)
        #endfor
    #endwith
    return user
#enddef

#------------------------------------------------------------------------------
#read the assets file and add assets to list
#------------------------------------------------------------------------------
def add_asset(asset_class, row, frac):
    asset = Asset(asset_class, row, frac)
    return asset
#enddef


def read_assets(fassets):
    logger.info('started')

    print("open assets file")

    assets  = []
        
    with open(fassets,mode='r') as fh:
        csv_reader = csv.DictReader(fh)
        csv_reader.fieldnames = [name for name in csv_reader.fieldnames]        
        line_count = 0
        for row in csv_reader:
            ac = row['asset_class'].strip()
            if ac == 'multi':
                multi = row['multi']
                multi = multi.strip('"')
                multi = multi.replace("'",'"')

                multi = json.loads(multi)
                print(multi)

                #multi = {"US fixed income":0.50,"US large cap equities":0.50}
                
                s = 0
                for ac,frac in multi.items():
                    asset = add_asset(ac,row,frac)
                    assets.append(asset)
                    s = s + frac
                #endfor
                print("Frac: ",s)
                
                if not math.isclose(s,1.0,rel_tol=1e-4):
                    print("Error, sum of fractions don't equal 1",s)
                    sys.exit()
                #endif
            else:
                asset = add_asset(ac,row,1)
                assets.append(asset)
            #endif
        #endfor
    #endwith

    logger.info('finished')    
    return assets
#enddef


#------------------------------------------------------------------------------
#get the asset classes from the glide path
#------------------------------------------------------------------------------
def get_asset_classes(gpos):
    #get first gp (should have all asset classes in it)
    gp = gpos[0]
    keys = gp.keys()
    asset_classes = []
    for k in keys:
        k = k.strip()
        if k != 'Age':
            asset_classes.append(k)
        #endif
    #endfor
    return asset_classes
#enddef

#------------------------------------------------------------------------------
#calc the overall ROI, from the average annual return (not after-tax)
#------------------------------------------------------------------------------
def calc_roi(assets,key):
    roi = 0
    t   = 0
    p   = 0
    for a in assets:
        proi = getattr(a,key)
        print(proi,a.total)
        
        p = p + proi * a.total
        t = t + a.total
    #endfor
    roi = p/t
    roi = roi.quantize(decimal.Decimal('0.0001'))  #return ROI to 4 decimal places
    return roi
#enddef

#------------------------------------------------------------------------------
#calc the years to go before retirement
#------------------------------------------------------------------------------
def calc_goals(user, roi, total):

    roi   = float(roi)
    total = float(total)
    
    annual_expenses = float(user.expected_annual_expenses)
    add_money       = float(user.months_add_money)
    money           = float(user.monthly_savings_amt)

    egoal = annual_expenses / roi
        
    print("end goal:"+str(egoal))              #calculated
    print("estimated annual roi: " + str(roi)) #from assets
    print("additional payments per year: " + str(add_money))
    print("amount added: " + str(money))
    print("curr total: " + str(total))

    #good example here https://xplaind.com/696036/excel-nper-function    
    ytg = numpy.nper(roi/12, money, total, -egoal)/12
    
    print("years to goal: {:.2f}".format(ytg))
    return egoal, ytg
#enddef

def get_userage(user):
    bday = user.birthday
    try:
        born = datetime.datetime.strptime(bday,'%m/%d/%y')
    except Exception as e:
        print(e)
        try:
            born = datetime.datetime.strptime(bday,'%m/%d/%Y')
        except Exception as e:
            print(e)
        #endtry
    #endtry

    today = datetime.date.today()
    age   = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    return age
#enddef

#--------------------------------------------------------------------------------
    #I made the savings age assuming that you're ahead (ie real age=40, savings age=50)
    #so, you typically want to take less risk as you get older
    #with the idea that you hit your number with these assets and then
    #anything you make on top of this is just gravy:
    #track those assets in another set of parameters

    #I haven't really considered what happens if you're behind
    #(ie real age=40, savings age = 30)
    #hmmm more to think about
#--------------------------------------------------------------------------------
def calc_savings_age(user, ytg):
    retire_age  = user.retire_age
    savings_age = int(round(retire_age - ytg, 0))
    return savings_age
#enddef

#--------------------------------------------------------------------------------
# get the maximum value on this glide path
#--------------------------------------------------------------------------------
def get_maxval(name,user,gpos,end_goal):
    savings_age = calc_savings_age(user, 0)  #years to go = 0
    gp_info     = get_gpinfo(gpos,savings_age)    
    maxper      = float(gp_info[name])
    maxval      = end_goal * maxper
    return maxval
#enddef

#--------------------------------------------------------------------------------
#tell the user what to do based on this asset class
#--------------------------------------------------------------------------------
def get_action(all_assets, aco, tolerance):
    action = "no action"
    adiff  = abs(aco.diffp)

    if aco.total > aco.maxval:
        action = "above max: sell"
    else:
        if adiff < tolerance:
            action = "no action"
        else:
            target_val = all_assets.total * decimal.Decimal(aco.tp)
            if aco.diffp > 0:
                buy_amount = target_val - aco.total
                action = "rebalance: buy"# + "${:.2f}".format(buy_amount)
            else:
                sell_amount = aco.total - target_val
                action = "rebalance: sell"# + "${:.2f}".format(sell_amount)
            #endif
        #endif
    #endif
    
    return action
#enddef

#--------------------------------------------------------------------------------
#pull out the information based on the age
#TODO if age doesn't exist, then use the one just before it (ie 100 or 25)
#--------------------------------------------------------------------------------
def get_gpinfo(gpos,age):    
    gp_info = {}
    for gp in gpos:
        if gp['Age'] == str(age):
            gp_info = gp
        #endif
    #endfor
    return gp_info
#enddef


#--------------------------------------------------------------------------------
#monitor the portfolio - this is the MAIN program here
#--------------------------------------------------------------------------------
def monitor(topdir,fglide_path,fassets,fusers,use_user_roi):
    print(fglide_path)
    print(fassets)
    print(fusers)
    
    user             = read_users(fusers)
    assets           = read_assets(fassets)
    gpos             = read_glide_path2(fglide_path) #glidepath objects dicts
    gp_asset_classes = get_asset_classes(gpos)
    
    gp_asset_class_objs = []
    for ac in gp_asset_classes:
        gp_asset_class_objs.append(AssetClass(ac))
    #endfor
    
    for a in assets:
        if a.asset_class in gp_asset_classes:
            a.gp_assetclass = a.asset_class
        else:
            a.gp_assetclass = 'zzzother'
        #endif
    #endfor

    grand_total = decimal.Decimal(0.0)

    for ac in gp_asset_class_objs:
        #each asset in that class
        actotal = decimal.Decimal(0.0)
        for a in assets:
            if a.gp_assetclass == ac.name:
                actotal = actotal + a.total
            #endif
        #endfor
        grand_total = grand_total + actotal
        ac.total    = actotal
#        print(ac.name,ac.total)

        if ac.name == 'zzzother' and ac.total > 0:
            msg = "You have UNASSIGNED assets (those in the Other asset class).\n"
            msg = msg + "Either change your glide path or reassign those assets.\n"
            user.warnings.append(msg)
        #endif
        
    #endfor

    all_assets = AllAssets(grand_total)

    if use_user_roi:
        roi = calc_roi(assets,'user_roi')
    else:
        roi = calc_roi(assets,'roi')
    #endif
    user.roi = roi
    
    end_goal, ytg = calc_goals(user, roi, grand_total)
    user.end_goal = end_goal
    user.ytg      = ytg

    user.savings_age = calc_savings_age(user, ytg)
    user.real_age    = get_userage(user)
   
    if user.real_age > user.savings_age:
        msg = "You need to save more (or increase your retirement age)!\n"
        msg = msg + "Your real age is more than your savings age.\n"
        msg = msg + "You will hit your retirement age before you've saved enough.\n"
        print("!!Warning!!")
        print(msg)

        user.warnings.append(msg)
        
        print("retire age",user.retire_age)
        print("savings age ",user.savings_age)
        print("real age",user.real_age)
    #endif
    
    gp_info = get_gpinfo(gpos,user.savings_age)

    #update the asset_classes
    aatp  = 0
    aaap  = 0
    acodiffsq = []
    for aco in gp_asset_class_objs:
        aco.tp     = float(gp_info[aco.name])                   #target percent
        aco.ap     = float(aco.total/grand_total)               #actual percent
        aco.diffp  = aco.tp - aco.ap                            #difference
        aco.maxval = get_maxval(aco.name,user,gpos,end_goal)    #maxval for this asset class

        aco.tv     = all_assets.total * decimal.Decimal(aco.tp) #target value
        aco.diffv  = aco.tv - aco.total                         #difference value (>0 = buy, <0 = sell)
        #print(aco.tv, aco.adiffv)
        
        action     = get_action(all_assets,aco,user.target_tolerance)
        aco.action = action
        aatp = aatp + aco.tp
        aaap = aaap + aco.ap
        acodiffsq.append(aco.diffp**2)
    #endfor
    all_assets.tp  = aatp
    all_assets.ap  = aaap
    all_assets.rms = numpy.sqrt(sum(acodiffsq)/len(acodiffsq))
    all_assets.quadrature = numpy.sqrt(sum(acodiffsq))

    #print(aatp,aaap,all_assets.rms)
    if use_user_roi:
        outfile = getoutfile(topdir,"2")
    else:
        outfile = getoutfile(topdir,"1")        
    #endif
    
    #make the output
    rebal_view.create_output(outfile, all_assets, gp_asset_class_objs, assets, user, gp_info)

    #show the output
    rebal_view.show_output(outfile)
    return(outfile)    
#enddef

def getprefix(suffix):
    return "temp"+str(suffix)

def getoutfile(topdir,suffix):
    sub     ='output'
    subdir  = os.path.join(topdir,sub)
    now     = getprefix(suffix)
    outfile = os.path.join(subdir,now+".html")
    return outfile
#enddef

def savefile(outfile):
    #ofile is dir\temp.html
    tnow   = datetime.datetime.today().strftime('%Y%m%d-%H%M%S')
    ofile2 = outfile.replace(getprefix(),tnow)
    print("saving file: ",ofile2)
    shutil.copy(outfile,ofile2)   
#enddef


#------------------------------------------------------------------------------
#MAIN
#------------------------------------------------------------------------------
if __name__ == '__main__':

    top  ='/home/tad/Desktop/rebal/data'
    #fglide_path = os.path.join(os.path.join(top,'glide_paths'),'5050gp0.csv')
    #fassets     = os.path.join(os.path.join(top,'assets'),'5050a.csv')
    #fusers      = os.path.join(os.path.join(top,'users'),'5050u.csv')
    fglide_path = os.path.join(os.path.join(top,'glide_paths'),'vanguardtr.csv')
    fassets     = os.path.join(os.path.join(top,'assets'),'1fundmulti40a.csv')
    fusers      = os.path.join(os.path.join(top,'users'),'mid40u.csv')    

    monitor(top,fglide_path,fassets,fusers)
#endif __main__
