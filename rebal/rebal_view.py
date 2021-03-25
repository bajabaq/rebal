#this code is written in python3


#------------------------------------------------------------------------------
#this code displays the results of the MODEL (it is the VIEW)

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#python imports
#------------------------------------------------------------------------------
import csv
import locale
import logging
import matplotlib.pyplot as plt
import os
import pandas as pd
import webbrowser

#------------------------------------------------------------------------------
#global variables
#------------------------------------------------------------------------------
logger = logging.getLogger(__name__)

#==============================================================================
#Subroutines
#==============================================================================
def format_money(xin):
    locale.setlocale(locale.LC_ALL,'')
    xout = locale.currency(xin,grouping=True)
    return xout

def create_output(outfile, all_assets, asset_class_objs, assets, user, gp_info):
    logger.info('started')
    
    info   = ['Asset Class','Asset','Qty.','Unit Val.','Total Val.','Target %','Actual %','Diff %','Action','Rebal']
    numcol = len(info)

    html = "<!DOCTYPE html>\n"    
    html = html + "<head>\n"
    html = html + "<title>Portfolio Monitor</title>\n"
    html = html + "<style>\n"
    #html = html + "dl { white-space: nowrap;}\n"
    html = html + "dt { float: left; clear: left; width:17em; text-align: left; }\n"
#    html = html + "dd { margin: 0 0 0 0; padding: 0 0 0 0;}\n"
    
    html = html + "</style>\n"    
    html = html + "</head>\n"
    html = html + "<body>\n"

    #ASSET INFO --------------------------------------------------    
    html = html + "<h2>Assets</h2>\n"    
    html = html + "<table>\n"

    #header
    row    = "<tr>"
    for i in info:
        if i in ["Asset Class","Asset","Action","Rebal"]:
            row = row + "<th style=text-align:left;>" + i + "</th>"
        else:
            row = row + "<th style=text-align:right;>" + i + "</th>"
        #endif
    #endfor
    row  = row + "</tr>\n"
    html = html + row
    
    #data
    
    for ac in sorted(asset_class_objs,key=lambda asset_class:asset_class.name):
        if ac.name == 'zzzother' and ac.total == 0:
            pass
        else:
            
            #each asset class
            row     = "<tr>"
            data    = ['']*numcol
            data[0] = ac.name
            for i in data:
#                if 'us' in i[:2]:
#                    i = i.replace('us','US')
                if 'zzzother' in i:
                    i = 'Other'
                #endif
                row = row + "<td>" + i + "</td>"
            #endfor
            row  = row + "</tr>\n"
            html = html + row

            #each asset in that class
            for a in assets:
                if a.gp_assetclass == ac.name:
                    if a.quantity == 0:
                        pass
                    else:
                        row     = "<tr>"
                        data    = ['']*numcol

                        if a.symbol == "UNLISTED":
                            data[1] = a.desc    
                        else:
                            data[1] = a.desc + "<br/>" + a.symbol
                        #endif
                        
                        data[2] = str('{0:.4f}'.format(a.quantity))
                        data[3] = format_money(a.price)
                        data[4] = format_money(a.total)
                        #print(a.desc, a.quantity, a.price, a.total)
                        j = 0
                        for i in data:
                            if j in [2,3,4]:
                                row = row + '<td style="text-align:right; font-variant-numeric: tabular-nums;">' + i + "</td>"
                            else:
                                row = row + "<td>" + i + "</td>"
                            #endif
                            j = j + 1
                        #endfor
                
                        row  = row + "</tr>\n"
                        html = html + row
                    #endif
                #endif
            #endfor

            #bottom line for that asset class
            row = "<tr>"
            data    = ['']*numcol
            data[4] = format_money(ac.total)        
            #data[6] = "{:.2%}".format(gp_info[ac.name])
            #data[7] = "{:.2%}".format(ac.total/all_assets.total)
            #data[8] = str('a%-t%')
            #data[9] = str('action')
            data[5] = "{:.2%}".format(ac.tp)      #target %
            data[6] = "{:.2%}".format(ac.ap)      #actual %
            data[7] = "{:.2%}".format(ac.diffp)   #diff %
            data[8] = ac.action                   #action to take
            bs = "sell "
            if ac.diffv > 0:
                bs = "buy "
            #data[9] =  bs + format_money(ac.diffv)
            data[9] =  format_money(ac.diffv)
            
            j = 0
            for i in data:
                if j in [4,5,6,7]:
                    cello = '<td style="padding-top: 1ex; text-align:right; font-variant-numeric: tabular-nums;">'
                    if j == 4:
                        i     = '<div style="border-top:1px solid red">' + str(i) + '</div>'
                    #endif
                    cellc = "</td>"
                else:
                    cello = '<td style="padding-top: 1ex">'
                    cellc = "</td>"
                #endif
                row = row + cello + i + cellc
                j = j+1
            #endfor
            row  = row + "</tr>\n"
            html = html + row
        #endif
    #endfor

    row     = '<tr>'
    data    = ['']*numcol
    data[0] = "All Assets"
    data[4] = format_money(all_assets.total)
    data[5] = "{:.2%}".format(all_assets.tp)
    data[6] = "{:.2%}".format(all_assets.ap)
    data[7] = "{:.2%}".format(all_assets.quadrature)  #show the Quadrature difference
    data[8] = "Quadrature"

    j = 0
    for i in data:
        if j in [4,5,6,7]:
            cello = '<td style="padding-top: 1em;text-align:right; font-variant-numeric: tabular-nums;">'
            if j == 4:
                i = '<div style="border-top: double red">' + str(i) + '</div>'
            else:
                i =  str(i)
            #endif
            cellc = "</td>"
        else:
            cello = '<td style="padding-top: 1em">'
            cellc = "</td>"
        #endif
        row = row + cello + i + cellc
        j = j+1
    #endfor
    row  = row + "</tr>\n"
    html = html + row

    row     = "<tr>"
    data    = ['']*numcol
    data[7] = "{:.2%}".format(all_assets.rms)        #show the RMS difference
    data[8] = "RMS"

    j = 0
    for i in data:
        if j in [7]:            
            cello = '<td style="text-align:right; font-variant-numeric: tabular-nums;">'
        else:
            cello = "<td>"
        #endif
        cellc = "</td>"
        row = row + cello + i + cellc
        j = j+1
    #endfor
    row  = row + "</tr>\n"
    html = html + row
        
    html = html + "</table>\n"

    #USER INFO--------------------------------------------------
    html = html + "<h2>Goals</h2>\n"
    html = html + "<dl>\n"
    html = html + "<dt>End Goal</dt>\n"
    html = html + "<dd>"+format_money(user.end_goal)+"</dd>\n"
    html = html + "</dl>\n"
    html = html + "<dl>\n"
    html = html + "<dt>Estimated Annual ROI</dt>\n"
    html = html + "<dd>"+"{:.2%}".format(user.roi)+"</dd>\n"
    html = html + "</dl>\n"
    html = html + "<dl>\n"
    html = html + "<dt>Additional payments per year</dt>\n"
    html = html + "<dd>"+str(user.months_add_money)+"</dd>\n"
    html = html + "</dl>\n"
    html = html + "<dl>\n"
    html = html + "<dt>Amount per addition</dt>\n"
    html = html + "<dd>"+format_money(user.monthly_savings_amt)+"</dd>\n"
    html = html + "</dl>\n"
    html = html + "<dl>\n"
    html = html + "<dt>Current Assets</dt>\n"
    html = html + "<dd>"+format_money(all_assets.total)+"</dd>\n"
    html = html + "</dl>\n"
    html = html + "<dl>\n"
    html = html + "<dt>Years to Goal</dt>\n"
    html = html + "<dd>"+"{:.2f}".format(user.ytg)+"</dd>\n"
    html = html + "</dl>\n"
    html = html + "<dl>\n"
    html = html + "<dt>Retirement Age</dt>\n"
    html = html + "<dd>"+str(user.retire_age)+"</dd>\n"
    html = html + "</dl>\n"
    html = html + "<dl>\n"
    html = html + "<dt>Real Age</dt>\n"
    html = html + "<dd>"+str(user.real_age)+"</dd>\n"
    html = html + "</dl>\n"
    html = html + "<dl>\n"
    html = html + "<dt>Savings Age</dt>\n"
    html = html + "<dd>"+str(user.savings_age)+"</dd>\n"
    html = html + "</dl>\n"

    #WARNINGS ------------------------------------
    if len(user.warnings) > 0:
        html = html + '<div style="border: 5px outset red;">\n<ul>\n'
        for warn in user.warnings:
            html = html + "<li>" + str(warn) + "</li>\n"
        #endfor
        html = html + "</ul>\n</div>\n"
    #endif        
    
    html = html + "</body>\n"    
    html = html + "</html>\n"

    #write the HTML
    with open(outfile,'w') as fh:
        fh.write(html)
    #endwith
    logger.info('finished')

    return outfile
#enddef

def show_output(ofile):
    try:
        webbrowser.open_new(ofile)
    except Exception as e:
        print(e)
    #endtry
#enddef


def graph_glidepath(gpfile):
    gp  = pd.read_csv(gpfile)
    gp2 = gp.set_index('Age')

    #maybe make this a setting
#    gp2.plot.bar(stacked=True)
    gp2.plot.area()
    plt.show()
    
#enddef

if __name__ == '__main__':

    top  ='/home/tad/Desktop/rebal/data'
    fglide_path = os.path.join(os.path.join(top,'glide_paths'),'5050gp0x.csv')
    
    graph_glidepath(fglide_path)
#endif

