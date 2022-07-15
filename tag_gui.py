import wx
import wx.grid as gridlib
import tag

DB_FILENAME = "tag.sqlite"

class TagEditor(gridlib.Grid):
    def __init__(self, parent, tagdb, filename):
        self.tagdb = tagdb
        self.filename = filename

        tags = tagdb.get_tags(filename)
        gridlib.Grid.__init__(self, parent, -1)
        self.CreateGrid(max(1, len(tags)), 2)
        
        self.height = len(tags)
        
        for (idx, tag) in enumerate(tags):
            self.SetCellValue(idx, 0, tag[0])
            self.SetCellValue(idx, 1, tag[1])
        self.SetColSize(0, 400)
        self.SetColSize(1, 400)
        self.SetColLabelValue(0, "Key")
        self.SetColLabelValue(1, "Value")
        self.Bind(gridlib.EVT_GRID_CELL_CHANGED, self.write_out);

    def add_row(self):
        """
        Add a row to the tag editor
        """
        self.AppendRows(numRows=1)
        self.height = self.height + 1
        self.ForceRefresh()

    def write_out(self, _):
        """
        write the info in the grid into the tagdb
        """
        tags = []
        for i in range(self.height):
            key = self.GetCellValue(i, 0)
            value = self.GetCellValue(i, 1)
            if len(key) > 0:
                tags.append((key, value))
            
        self.tagdb.set_tags(self.filename, tags)
        

class FileListPanel(wx.Panel):
    def __init__(self, parent, tagdb):
        super().__init__(parent)
        self.tagdb = tagdb
        self.tageditor = None

        sizer = wx.BoxSizer(wx.VERTICAL) # Arrange widgets in a column
        self.sizer = sizer

        # Initalized a list for displaying tracked files
        self.filelist = wx.ListCtrl(self, size=(100, 1000), style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.filelist.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.select_file)
        sizer.Add(self.filelist, 0, wx.ALL | wx.EXPAND, 25)

        # Sync list with database
        self.update_list()

        # Buttons
        edit_button = wx.Button(self, label='Add file')
        edit_button.Bind(wx.EVT_BUTTON, self.add_file)
        sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)    
        
        edit_button = wx.Button(self, label='Remove selected files')
        edit_button.Bind(wx.EVT_BUTTON, self.rm_file)
        sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)
        
        # Placeholder for tag editor
        self.tageditsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.tageditsizer, 0, wx.CENTER)
       
        # More buttons
        edit_button = wx.Button(self, label='Add tags to open file')
        edit_button.Bind(wx.EVT_BUTTON, self.add_row_button)
        sizer.Add(edit_button, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(sizer)

    def rm_file(self, event):
        """
        Remove the currently selected entry in the filelist.
        """
        item = self.filelist.GetFirstSelected()
        if item != -1:
            self.tagdb.rm_file(self.filelist.GetItemText(item))
            self.update_list()

    def add_row_button(self, event):
        """
        Add a row to the tag editor if it is open
        """
        if self.tageditor != None:
            self.tageditor.add_row()
            self.Layout()

    def showeditor(self, filename):
        """
        Initalize the tageditor for a filename
        """
        if self.tageditor != None:
            self.tageditor.Destroy()
        self.tageditsizer.Clear()
        self.tageditor = TagEditor(self, self.tagdb, filename)
        self.tageditsizer.Add(self.tageditor, 0, wx.ALIGN_CENTER, 0)
        self.sizer.Layout()

    def select_file(self, event):
        """
        Opens the tageditor.
        """
        filename = event.GetText()
        self.showeditor(filename)

    def update_list(self):
        """
        Sync the file list with the filenames
        """
        self.filelist.ClearAll()
        self.filelist.InsertColumn(0, 'Filename', width=1000)
        for (idx, filename) in enumerate(self.tagdb.get_filenames()):
            self.filelist.InsertItem(idx,filename)

    def add_file(self, event):
        """
        Prompts the user for a filepath and adds it to the database, updating list
        """
        title = "Choose a file to tag:"
        dlg = wx.FileDialog(self, title, style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.tagdb.set_tags(dlg.GetPath(), [["uninitalized", "yes"]])
            self.update_list()
        dlg.Destroy()

class FileListFrame(wx.Frame):
    def __init__(self, tagdb):
        super().__init__(parent=None,title='Filetag gui')
        self.panel = FileListPanel(self, tagdb)
        self.Show()

if __name__ == '__main__':
    tagdb = tag.TagDB(DB_FILENAME)
    app = wx.App()
    frame = FileListFrame(tagdb)
    app.MainLoop()
