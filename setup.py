from setuptools import setup, find_packages

setup(
    name         ='rebal',
    description  ='',
    version      ='1.0',
    author       ='Tad Whiteside',
    author_email ='tad.whiteside@gmail.com',
    #packages     =['src'],     
    packages     =find_packages(where='src'),
    package_dir  ={'': 'src'},
    package_data ={'':['*.ini','*.ASF','*.NLB']},
        
    #Rebal should be launched from the REBAL directory by calling rebal_gui.py
    #entry_points ={
    #    'console_scripts': [ 
    #       'rebal=rebal.rebal_gui:main' 
    #    ]
    #}
)

