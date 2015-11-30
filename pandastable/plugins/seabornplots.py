#!/usr/bin/env python
"""
    DataExplore Application plugin example.
    Created Oct 2015
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from pandastable.plugin import Plugin
from pandastable import plotting
import tkinter
from tkinter import *
from tkinter.ttk import *
import pandas as pd
import pylab as plt
#import seaborn as sns

class SeabornPlugin(Plugin):
    """Template plugin for DataExmplore"""

    capabilities = ['gui','uses_sidepane']
    requires = ['']
    menuentry = 'Categorical Plots'
    gui_methods = {}
    about = 'This plugin is a template'

    def main(self, parent):
        if parent==None:
            return
        self.parent = parent
        self._doFrame()
        self.groups = grps = {'formats':['kind','wrap','despine','palette'],
                'factors':['hue','col','x']}
        styles = ['darkgrid', 'whitegrid', 'dark', 'white', 'ticks']
        kinds = ['point', 'bar', 'count', 'box', 'violin', 'strip']
        palettes = ['Spectral','cubehelix','hls','hot','coolwarm','copper',
                    'winter','spring','summer','autumn','Greys','Blues','Reds',
                    'Set1','Set2','Accent']
        datacols = []
        self.opts = {'wrap': {'type':'entry','default':2,'label':'cols'},
                    #'style': {'type':'combobox','default':'white','items':styles},
                     'despine': {'type':'checkbutton','default':0,'label':'despine'},
                     'palette': {'type':'combobox','default':'Spectral','items':palettes},
                     'kind': {'type':'combobox','default':'bar','items':kinds},
                     'col': {'type':'combobox','default':'','items':datacols},
                     'hue': {'type':'combobox','default':'','items':datacols},
                     'x': {'type':'combobox','default':'','items':datacols},
                        }
        fr = self._plotWidgets(self.mainwin)
        fr.pack(side=LEFT,fill=BOTH)
        bf = Frame(self.mainwin, padding=2)
        bf.pack(side=LEFT,fill=BOTH)
        b = Button(bf, text="Replot", command=self._plot)
        b.pack(side=TOP,fill=X,expand=1)
        b = Button(bf, text="Clear", command=self.clear)
        b.pack(side=TOP,fill=X,expand=1)
        b = Button(bf, text="Close", command=self.quit)
        b.pack(side=TOP,fill=X,expand=1)

        self.table = self.parent.getCurrentTable()
        df = self.table.model.df
        self.update(df)

        sheet = self.parent.getCurrentSheet()
        pw = self.parent.plotframes[sheet]
        self.table.pf.hide()
        self.pf = Frame(pw)
        #self.pf.pack(side=LEFT,fill=BOTH)
        pw.add(self.pf, weight=5)
        print(sheet)

        #self.pf = Toplevel(self.parent)
        #self.pf.geometry('600x600+800+400')

        self.fig, self.canvas = plotting.addFigure(self.pf)
        #use tables frame?

        return

    def setFigure(self, f=None, name=None):
        #dpi = self.fig.get_dpi()
        #w,h = self.pf.winfo_width(),self.pf.winfo_height()
        #g.fig.set_size_inches((w/float(dpi),h/float(dpi)),forward=True)
        return

    def _plot(self):
        """Do plot"""

        import seaborn as sns
        self.setDefaultStyle()
        sns.set(rc={'figure.facecolor':'white'})

        self.applyOptions()
        kwds = self.kwds
        df = self.table.getPlotData()
        dtypes = list(df.dtypes)
        col = kwds['col']
        hue = kwds['hue']
        wrap=int(kwds['wrap'])
        kind = kwds['kind']
        x = kwds['x']
        if x == '':
            x = 'var'
        aspect = 1.0
        palette=kwds['palette']

        labels = list(df.select_dtypes(include=['object','category']).columns)

        t = pd.melt(df,id_vars=labels,
                     var_name='var',value_name='value')
        print (t[10:20])
        if hue == '':
            hue=None
        if col == '':
            col=None
        print(labels,hue,col)
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        try:
            g = sns.factorplot(x=x,y='value',data=t, hue=hue, col=col,
                            col_wrap=wrap, kind=kind,size=3, aspect=float(aspect),
                            legend_out=True, sharey=False, palette=palette)
        except Exception as e:
            self.showWarning(e)
            return

        #need to always make a new canvas to get size right
        for child in self.pf.winfo_children():
            child.destroy()
        self.fig, self.canvas = plotting.addFigure(self.pf, g.fig)
        self.fig.suptitle('test')
        if kwds['despine']==True:
            sns.despine()
        plt.tight_layout()
        self.canvas.draw()
        return

    def clear(self):
        return

    def applyOptions(self):
        """Set the options"""

        kwds = {}
        for i in self.opts:
            if self.opts[i]['type'] == 'listbox':
                items = self.widgets[i].curselection()
                kwds[i] = [self.widgets[i].get(j) for j in items]
                print (items, kwds[i])
            else:
                kwds[i] = self.tkvars[i].get()
        self.kwds = kwds
        #size = kwds['fontsize']
        #plt.rc("font", family=kwds['font'], size=size)
        #plt.rc('legend', fontsize=size-1)
        return

    def setDefaultStyle(self):
        import seaborn as sns
        sns.set_style("ticks", {'figure.facecolor':'white',
                                'axes.facecolor': '#F7F7F7','legend.frameon': True})
        sns.set_context("paper", rc={'legend.fontsize':16,'xtick.labelsize':12,
                        'ytick.labelsize':12,'axes.labelsize':14,'axes.titlesize':16})
        return

    def _plotWidgets(self, parent, callback=None):
        """Auto create tk vars, widgets for corresponding options and
           and return the frame"""

        dialog, self.tkvars, self.widgets = plotting.dialogFromOptions(parent, self.opts, self.groups)
        #self.applyOptions()
        return dialog

    def update(self, df):
        """Update data widget(s)"""

        cols = list(df.columns)
        cols += ''
        self.widgets['hue']['values'] = cols
        self.widgets['col']['values'] = cols
        self.widgets['x']['values'] = cols
        return

    def showWarning(self, s='plot error'):

        ax=self.fig.add_subplot(111)
        ax.text(.5, .5, s,transform=ax.transAxes,
                       horizontalalignment='center', color='blue', fontsize=16)
        self.canvas.draw()
        return

    def quit(self, evt=None):
        """Override this to handle pane closing"""

        self.fig.clear()
        plt.close('all')
        self.pf.destroy()
        self.mainwin.destroy()
        return

    def _importSeaborn(self):
        """Try to import seaborn. If not installed return false"""
        try:
            import seaborn as sns
            return 1
        except:
            print('seaborn not installed')
            return 0

    def _doFrame(self):

        if 'uses_sidepane' in self.capabilities:
            self.mainwin = self.parent.addPluginFrame(self)
        else:
            self.mainwin=Toplevel()
            self.mainwin.title('Seaborn plotting plugin')
            self.mainwin.geometry('600x600+200+100')

        self.ID=self.menuentry
        self.mainwin.bind("<Destroy>", self.quit)
        return

    def _createButtons(self, methods):
        """Dynamically create buttons for supplied methods"""

        for m in methods:
            b=Button(self.mainwin,text=m[0],command=m[1])
            b.pack( side=TOP,fill=BOTH)
        return
