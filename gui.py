from tkinter.ttk import Notebook, Label, LabelFrame, Entry, Button, Combobox, Checkbutton, Treeview, Scrollbar, Sizegrip
from tkinter.scrolledtext import ScrolledText
from tkinter import Tk, PanedWindow, Frame, BOTH, NONE, LEFT, RIGHT, TOP, GROOVE, X, Y, HORIZONTAL, VERTICAL, \
    StringVar, IntVar, N, NW, S, SW, W
import gui_functions


class ShownameGui(Frame):
    def __init__(self, master=None):
        super().__init__()
        self.initVars()
        self.initUI()

    def initVars(self):
        # Sorts
        self.SORT_NAME_ASC = 'SORT_NAME_ASC'
        self.SORT_NAME_DESC = 'SORT_NAME_DESC'
        self.SORT_DATE_ASC = 'SORT_DATE_ASC'
        self.SORT_DATE_DESC = 'SORT_DATE_DESC'
        self.SORT_TYPE_ASC = 'SORT_TYPE_ASC'
        self.SORT_TYPE_DESC = 'SORT_TYPE_DESC'
        self.sort = self.SORT_NAME_DESC

        # Treeview tags
        self.TAG_ODD_ROW = 'TAG_ODD_ROW'
        self.TAG_NO_RENAME = 'TAG_NO_RENAME'
        self.TAG_BAD_RENAME = 'TAG_BAD_RENAME'
        self.TAG_FILTERED_OUT = 'TAG_FILTERED_OUT'

        # Treeview columns
        self.COL_OLD_NAME = 'COL_OLD_NAME'
        self.COL_NEW_NAME = 'COL_NEW_NAME'
        self.COL_DATE = 'COL_DATE'
        self.COL_TYPE = 'COL_TYPE'

        self.old_names = []
        self.new_names = []

        self.token = None
        self.series_data = []
        self.show_names = {}

        self.path_var = StringVar()

        self.search_show_var = StringVar()
        self.select_show_var = StringVar()

        self.filter_var = StringVar()
        self.preserve_extensions_var = IntVar()
        self.include_folders_var = IntVar()
        self.filter_regex_var = IntVar()
        self.case_sensitive_var = IntVar()

    def initUI(self):
        self.master.title = 'Shownames'
        # self.style = Style()
        # self.style.theme_use('default')
        self.pack(fill=BOTH, expand=True)

        """ Add panes """
        panes = PanedWindow(self, orient=HORIZONTAL)
        panes.pack(fill=BOTH, expand=True)
        notebook_pane = Frame()
        rename_pane = Frame()
        panes.add(notebook_pane, minsize=330, width=400)
        panes.add(rename_pane, minsize=300, width=700)

        """ Add notebook tabs """
        notebook = Notebook(notebook_pane)
        notebook.pack(fill=BOTH, expand=True)
        list_tab = Frame(notebook)
        rename_tab = Frame(notebook)
        notebook.add(list_tab, text='List')
        notebook.add(rename_tab, text='Rename')

        """ Path frame """
        path_frame_label = Label(text='Path')
        path_frame = LabelFrame(list_tab, labelwidget=path_frame_label, borderwidth=2, relief=GROOVE)
        path_frame.pack(padx=5, pady=5, ipadx=5, ipady=5, side=TOP, anchor=N, fill=X, expand=False)

        path_entry_label = Label(path_frame, text='Path:', width=7)
        path_entry_label.pack(side=LEFT, padx=5)
        self.path_entry = Entry(path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=LEFT, fill=X, expand=True, padx=3, pady=3)
        browse_button = Button(path_frame, text='Browse', command=lambda: gui_functions.choose_folder(self))
        browse_button.pack(side=LEFT, padx=3, pady=3)
        path_enter_button = Button(path_frame, text='>', width=4, command=lambda: gui_functions.update_files(self))
        path_enter_button.pack(side=LEFT, padx=3, pady=3)

        """ Shows frame """
        shows_label = Label(text='Shows')
        shows_frame = LabelFrame(list_tab, labelwidget=shows_label, borderwidth=2, relief=GROOVE)
        shows_frame.pack(padx=5, pady=5, side=TOP, anchor=N, fill=X, expand=False)

        # Search subframe
        shows_search_subframe = Frame(shows_frame)
        shows_search_subframe.pack(side=TOP, fill=X, expand=True)

        search_entry_label = Label(shows_search_subframe, text='Search:', width=7)
        search_entry_label.pack(side=LEFT, padx=5)
        search_entry = Entry(shows_search_subframe, textvariable=self.search_show_var)
        search_entry.pack(side=LEFT, padx=3, pady=3, fill=X, expand=True)
        search_entry.bind('<Return>',
                          func=lambda event: gui_functions.search_for_show(self, self.search_show_var.get()))
        self.search_button = Button(shows_search_subframe, text='Search',
                                    command=lambda: gui_functions.search_for_show(self, self.search_show_var.get()))
        self.search_button.pack(side=LEFT, padx=3, pady=3)

        # Results subframe
        shows_results_subframe = Frame(shows_frame)
        shows_results_subframe.pack(side=TOP, fill=X, expand=True)

        results_combobox_label = Label(shows_results_subframe, text='Select:', width=7)
        results_combobox_label.pack(side=LEFT, padx=5)
        self.results_combobox = Combobox(shows_results_subframe, textvariable=self.select_show_var)
        self.results_combobox.pack(side=LEFT, padx=3, pady=3, fill=X, expand=True)
        self.results_combobox.bind('<Return>',
                                   func=lambda event: gui_functions.get_episodes(self, self.select_show_var.get()))
        self.get_episodes_button = Button(shows_results_subframe, text='Get Episodes',
                                          command=lambda: gui_functions.get_episodes(self, self.select_show_var.get()))
        self.get_episodes_button.pack(side=LEFT, padx=3, pady=3)

        status_label = Label(shows_frame, text='Status')
        status_label.pack(side=TOP, anchor=W, padx=5, pady=5)

        """ Name List frame """
        list_frame_label = Label(text='Name List')
        list_frame = LabelFrame(list_tab, labelwidget=list_frame_label)
        list_frame.pack(padx=5, pady=5, side=TOP, fill=BOTH, expand=True, anchor=N)

        # TODO: implement filter
        # # Filter subframe
        # filter_subframe = Frame(list_frame)
        # filter_subframe.pack(padx=5, pady=5, fill=X, expand=False, anchor=N)
        #
        # filter_entry_label = Label(filter_subframe, text='Filter:', width=7)
        # filter_entry_label.pack(side=LEFT, padx=5)
        # filter_entry = Entry(filter_subframe, textvariable=self.filter_var)
        # filter_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        # filter_button = Button(filter_subframe, text='>', width=4)
        # filter_button.pack(side=LEFT, padx=5)

        # Name list subframe
        name_list_subframe = Frame(list_frame)
        name_list_subframe.pack(padx=5, pady=5, fill=BOTH, expand=True, anchor=N)

        list_text_label = Label(name_list_subframe, text='Name list:')
        list_text_label.pack(side=TOP, padx=5, pady=5, anchor=NW)
        self.list_scrolledtext = ScrolledText(name_list_subframe, width=1, height=1, font=("Helvetica", 10), wrap=NONE)
        self.list_scrolledtext.pack(side=TOP, padx=5, pady=5, fill=BOTH, expand=True)
        self.list_scrolledtext.bind('<KeyRelease>', func=lambda event: gui_functions.update_new_names(self))

        # Filter options and rename button subframe
        options_and_button_frame = Frame(list_frame)
        options_and_button_frame.pack(side=TOP, padx=5, pady=5, fill=X)
        filter_options_subframe_label = Label(text='Options')
        filter_options_subframe = LabelFrame(options_and_button_frame, labelwidget=filter_options_subframe_label)
        filter_options_subframe.pack(side=LEFT, padx=5, pady=5, anchor=NW)

        include_folders_checkbutton = Checkbutton(filter_options_subframe, text='Include Folders', onvalue=1,
                                                  offvalue=0, var=self.include_folders_var,
                                                  command=lambda: gui_functions.update_files(self))
        include_folders_checkbutton.pack(side=TOP, anchor=W, padx=5, pady=3)
        preserve_extensions_checkbutton = Checkbutton(filter_options_subframe, text='Preserve Extensions', onvalue=1,
                                                      offvalue=0, var=self.preserve_extensions_var,
                                                      command=lambda: gui_functions.populate_treeview(self))
        self.preserve_extensions_var.set(1)
        preserve_extensions_checkbutton.pack(side=TOP, anchor=W, padx=5, pady=3)
        filter_regex_checkbutton = Checkbutton(filter_options_subframe, text='Filter with Regex', onvalue=1, offvalue=0,
                                               var=self.filter_regex_var)
        filter_regex_checkbutton.pack(side=TOP, anchor=W, padx=5, pady=3)
        filter_case_sensitive_checkbutton = Checkbutton(filter_options_subframe, text='Filter Case Sensitive',
                                                        onvalue=1,
                                                        offvalue=0, var=self.case_sensitive_var)
        filter_case_sensitive_checkbutton.pack(side=TOP, anchor=W, padx=5, pady=3)

        rename_button = Button(options_and_button_frame, text='Rename',
                               command=lambda: gui_functions.rename_files(self))
        rename_button.pack(side=RIGHT, padx=5, pady=5, anchor=SW)

        """ List pane """
        # r'''
        treeview_vscrollbar_subframe = Frame(rename_pane)
        treeview_vscrollbar_subframe.pack(side=TOP, anchor=N, fill=BOTH, expand=True)
        hscrollbar_sizegrip_subframe = Frame(rename_pane)
        hscrollbar_sizegrip_subframe.pack(side=TOP, anchor=N, fill=X, expand=False)

        columns = (self.COL_OLD_NAME, self.COL_NEW_NAME, self.COL_DATE, self.COL_TYPE)
        self.rename_treeview = Treeview(treeview_vscrollbar_subframe, columns=columns, show='headings',
                                        height=1)
        self.rename_treeview.pack(side=LEFT, fill=BOTH, expand=True)
        rename_treeview_vscrollbar = Scrollbar(treeview_vscrollbar_subframe, orient=VERTICAL,
                                               command=self.rename_treeview.yview)
        rename_treeview_vscrollbar.pack(side=LEFT, fill=Y, expand=False, anchor=S)
        rename_treeview_hscrollbar = Scrollbar(hscrollbar_sizegrip_subframe, orient=HORIZONTAL,
                                               command=self.rename_treeview.xview)
        rename_treeview_hscrollbar.pack(side=LEFT, fill=X, expand=True, anchor=N)
        sizegrip = Sizegrip(hscrollbar_sizegrip_subframe)
        sizegrip.pack(side=LEFT)

        self.rename_treeview.configure(xscrollcommand=rename_treeview_hscrollbar.set)
        self.rename_treeview.configure(yscrollcommand=rename_treeview_vscrollbar.set)

        self.rename_treeview.heading(self.COL_OLD_NAME, text='Current name', anchor=W)
        self.rename_treeview.heading(self.COL_NEW_NAME, text='New name', anchor=W)
        self.rename_treeview.heading(self.COL_DATE, text='Date', anchor=W)
        self.rename_treeview.heading(self.COL_TYPE, text='Type', anchor=W)
        self.rename_treeview.column(self.COL_OLD_NAME, width=10, minwidth=100)
        self.rename_treeview.column(self.COL_NEW_NAME, width=10, minwidth=100)
        self.rename_treeview.column(self.COL_DATE, width=100, minwidth=100, stretch=False)
        self.rename_treeview.column(self.COL_TYPE, width=100, minwidth=50, stretch=False)

        self.rename_treeview.tag_configure(self.TAG_ODD_ROW, background='Light Gray')
        self.rename_treeview.tag_configure(self.TAG_NO_RENAME, foreground='Dim Gray')
        self.rename_treeview.tag_configure(self.TAG_FILTERED_OUT, foreground='Red')


def main():
    root = Tk()
    root.geometry('1000x620')
    root.minsize(620, 575)
    root.title("My Awesome Renaming Program GUI")
    app = ShownameGui(root)
    app.mainloop()


if __name__ == '__main__':
    main()
