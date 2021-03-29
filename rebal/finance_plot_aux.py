#-----------------------------------------------------------------
#these are common functions in finance_plot and rebal
#-----------------------------------------------------------------

import csv
import datetime
import math
import matplotlib.dates as mdates
import scipy.optimize 
import numpy as np

def read_data(file):
    dt = [] #date
    vl = [] #value
    percent_high = []
    percent_low  = []
    
    datadic = dict()
    x = []
    y = []
    z = []
    with open(file,'r') as csvfile:
        freader = csv.reader(csvfile, delimiter='\t', quotechar='"')
#        freader.next() #skip first line
        next(freader)
        
        #    vnow = datetime.datetime.now()
        i    = 0 #date
        oval = 1        
        hval = 2 #high
        lval = 3 #low
        dval = 4 #close (this is the adjusted value)

        dflag = False
        hflag = False
        lflag = False

        for row in reversed(list(freader)):
            
            #date = 2015-08-18
            vdate = datetime.datetime.strptime(row[0], '%Y-%m-%d')
            dt.append(vdate)

            #THESE WILL BE THE SAME FOR A MUTAL FUND (NO INTRADAY CHANGES)
            #print(float(row[hval]))
            #print(float(row[lval]))
            #print(float(row[cval]))

            rdval,dflag = make_not_zero(row[dval])
            rhval,hflag = make_not_zero(row[hval])
            rlval,lflag = make_not_zero(row[lval])
            vl.append(rdval)

            #print(rdval,rhval,rlval)
            
            percent_high.append((rhval - rdval) /rdval)
            percent_low.append((rlval  - rdval) /rdval)
            
            #input("hit enter")
        #endfor
        
        if True in [dflag,hflag,lflag]:
            print("")
            print("********************************")
            print("*            Warning           *")
            print("")
            print("Substitued 0.01 for 0 in values")
            print("")
            print("*            Warning           *")
            print("********************************")
            print("")
        #endif        
    #endwith

    return (dt,vl,percent_high,percent_low)
#enddef


def make_not_zero(val):
    try:
        xval = float(val)
    except:
        print("Warning - could not make val (" + val + ") a float")
        print("   setting it to 0")
        xval = 0
    #endtry
    
    flag = False
    if xval == 0:
        xval = 0.01 #1e-99
        flag = True
    #endif
    return xval, flag
#enddef

def model2(d, m, b):
    val = m*d+b
    return val

def fit(adates,avals):
    anumdates = mdates.date2num(adates)
    print("anumdates = ")
    print(anumdates)
    
    #take natural log of avals
    avals2 = []
    for i in avals:
        avals2.append(math.log(i))
    #endfor

    param, param_cov = scipy.optimize.curve_fit(model2, anumdates, avals2, p0=[1e-4,-1e2])
    perr_model2      = np.sqrt(np.diag(param_cov))
    m = param[0]
    b = param[1]
    print("slope       = %0.2e (+/-) %0.2e" %(m, perr_model2[0]))
    print("y-intercept = %0.2e (+/-) %0.2e" %(b, perr_model2[1]))
    
    ays = m*anumdates + b
    rms = np.std(ays-avals2)
    print("rms         = %0.2e " % rms)

    """
    x     = 5
    lastx = avals2[x:]           

    pdata = pandas.DataFrame({'x':lastx,'y':ays[x:]})
    from statsmodels.formula.api import ols
    model = ols("y ~ x - 1", pdata).fit()
    print(model.summary())
    input("hit [ENTER] to continue")

    plt.plot(lastx, ays[x:],'ro')
    plt.plot(lastx, model.fittedvalues,'b')
    plt.show()
    plt.hist(model.resid_pearson)
    plt.show()
    """

    A = math.exp(b)
    B = m
    print("A = "+ str(A))
    print("B = "+ str(B))    
    large_prod = np.array(B*anumdates,dtype=np.float128)
    print(large_prod)
    o    = A*np.exp(large_prod)
    rms2 = np.sqrt(np.sum(np.square(o-avals))/(len(o)-1))
#    print("o = "+ str(o))
#    print("rms2        = %0.2e " % rms2)
#    print("")

    today     = datetime.datetime.today()
    yearend   = datetime.datetime(today.year,12,31)
    nextyear  = today + datetime.timedelta(days=365)
    xtoday    = mdates.date2num(today)
    xyearend  = mdates.date2num(yearend)
#    print("xyearend = " + str(xyearend))
    xnextyear = mdates.date2num(nextyear)
#    print("xnextyear = " + str(xnextyear))
    vyearend  = A*np.exp(B*xyearend,dtype=np.float128)
    vfuture   = A*np.exp(B*xnextyear,dtype=np.float128)
    vnow      = avals[0]
    print("now value:       ${0:0.2f}".format(vnow))
    print("year end value:  ${0:0.2f}".format(vyearend))
    print("next year value: ${0:0.2f}".format(vfuture))

    vyendreturn = ((vyearend- vnow)/vnow)*100
    vreturn     = ((vfuture - vnow)/vnow)*100
    print("year end return:  {0:0.2f}%".format(vyendreturn))
    print("next year return:  {0:0.2f}%".format(vreturn))

    vnow     = A*np.exp(B*xtoday,dtype=np.float128)  #redefine vnow based on best fit
    vtypical = ((vfuture - vnow)/vnow)*100
    vtypical = round(vtypical,4)
    print("typical return:    {0:0.2f}%".format(vtypical))
    
    return(avals2,ays,m,b,rms,A,B,o,rms2,vtypical)
#enddef

