
import configparser
import pkg_resources


def cread(fname):
    pname  = pkg_resources.resource_filename('rebal',fname)
    config = configparser.ConfigParser()
    config.read(pname)
    return config
#enddef

#------------------------------------------------------------------------------
#read the settings file
#------------------------------------------------------------------------------
def get_setting(section=None, key=None, **kwargs):
    type  = kwargs.get('type',"string")
    fname = kwargs.get('fname',"settings.ini")
    
    if section == "coin_sim":
        fname = 'settings_aux.ini'
    #endif
    config = cread(fname)
    
    val = ""
    if type == 'bool':
        val = config.getboolean(section, key)
    elif type == 'int':
        val = config.getint(section, key)
    elif type == 'float':
        val = config.getfloat(section, key)
    else:
        val = config.get(section, key)
    #endif
        
    return val
#enddef

def get_section(section, fname = 'settings.ini'):
    config = cread(fname)
    
    all_vals = list(config[section].keys())
    return all_vals
#enddef

def get_sections(fname = 'settings.ini'):
    config = cread(fname)
    
    all_sections = list(config.sections())
    return all_sections
#enddef

#------------------------------------------------------------------------------
#update the settings file
#------------------------------------------------------------------------------
def update_setting(section, key, value, fname='settings.ini'):
    pname = pkg_resources.resource_filename('rebal',fname)
    config = configparser.ConfigParser(comment_prefixes='/',allow_no_value=True)
    config.read(pname)
        
    config.set(section, key, value)
    
    with open(pname, 'w') as configfile:
        config.write(configfile)
    #endwith
#enddef
