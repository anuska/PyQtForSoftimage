import os
import sip

from PyQt4 import uic

from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import pyqtSlot

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QCursor


class ExampleDialog( QDialog ):
    def __init__( self, parent ):
        QDialog.__init__( self, parent )
        
        self.setGeometry( 100, 100, 200, 100 )
        self.setWindowTitle( "Hello World" )
        self.setToolTip( "This is a <b>QWidget</b> widget" )
        
        self.btn = QPushButton( "Log Text", self )
        self.btn.setToolTip( "This is a <b>QPushButton</b> widget" )
        self.btn.resize( self.btn.sizeHint() )
        self.btn.clicked.connect( self.logText )

        self.lineedit = QLineEdit( "Hello World", self )
        self.lineedit.setToolTip( "Type Something" )
        
        layout = QVBoxLayout( self )
        layout.addWidget( self.lineedit )
        layout.addWidget( self.btn )
        
    def logText( self ):
        Application.LogMessage( self.lineedit.text() )

class ExampleSignalSlot( ExampleDialog ):
    def __init__( self, parent ):
        ExampleDialog.__init__( self,parent )
        self.setWindowTitle( "Signal/Slot Example" )
        self.lineedit.setText( "" )

        # module containing sievents mapped to pyqtsignals
        from sisignals import signals
        
        # connect the siActivate signal to the activate slot and unmute the event if necessary.
        signals.connect('siActivate', self.activate )
        
        # connect the siPassChange signal to the passChanged slot and unmute the event if necessary.
        signals.connect('siPassChange', self.passChanged )

    def activate( self, state = None ):
        if state is not None:
            if state:
                self.lineedit.setText( "Welcome Back!" )
            else:
                self.lineedit.setText( "Good Bye!")
           
    def passChanged( self, targetPass = "" ):
        self.lineedit.setText( targetPass )
    
    def closeEvent( self, event ):
        # Disconnect signals from slots when you close the widget.
        # Softimage signals are muted if no other widgets are using them.
        from sisignals import signals
        signals.disconnect('siActivate', self.activate )
        signals.disconnect('siPassChange', self.passChanged )  

class ExampleMenu( QMenu ):
    def __init__( self, parent ):
        QMenu.__init__( self, parent )
        
        # add actions and a separator
        hello = self.addAction("Print 'Hello!'")
        self.addSeparator()    
        world = self.addAction("Print 'World!'")
        
        # connect to the individual action's signal
        hello.triggered.connect( self.hello )
        world.triggered.connect( self.world )
        
        # connect to the menu level signal
        self.triggered.connect( self.menuTrigger )
        
    def hello( self ):
        print( "Hello!" )
    
    def world( self ):
        print( "World!" )
    
    def menuTrigger( self, action ):
        if action.text() == "Print 'Hello!'":
            print( "You clicked, Print 'Hello!'" )
        elif action.text() == "Print 'World!'":
            print( "You clicked, Print 'World!'" )

class ExampleUIFile( QDialog ):
    def __init__( self, parent, uifilepath ):
        QDialog.__init__( self, parent )
        
        # load ui file
        self.ui = uic.loadUi( uifilepath, self )
        
        # connect to the createCube function
        self.ui.uiCreateCube.clicked.connect( self.createCube )
        
    def createCube( self ):
        cube = Application.CreatePrim("Cube", "MeshSurface", str(self.uiCubeName.text()), "")
        cube.Length.Value = self.uiCubeLength.value()
 
def XSILoadPlugin( in_reg ):
    in_reg.Name = "PyQt_Example"
    in_reg.Author = "Steven Caron"
    in_reg.RegisterCommand( "ExampleDialog" )
    in_reg.RegisterCommand( "ExampleSignalSlot" )
    in_reg.RegisterCommand( "ExampleMenu" )
    in_reg.RegisterCommand( "ExampleUIFile" )

def ExampleDialog_Execute():
    """a simple example dialog showing basic functionality of the pyqt for softimage plugin"""
    sianchor = Application.getQtSoftimageAnchor()
    sianchor = sip.wrapinstance( long(sianchor), QWidget )
    dialog = ExampleDialog( sianchor )
    dialog.show()
    
def ExampleSignalSlot_Execute():
    """a simple example showing softimage events triggering pyqt signals"""
    sianchor = Application.getQtSoftimageAnchor()
    sianchor = sip.wrapinstance( long(sianchor), QWidget )
    dialog = ExampleSignalSlot( sianchor )
    dialog.show()

def ExampleMenu_Execute():
    """a simple example showing the use of a qmenu""" 
    sianchor = Application.getQtSoftimageAnchor()
    sianchor = sip.wrapinstance( long(sianchor), QWidget )
    menu = ExampleMenu( sianchor )
    
    # notice the use of QCursor and exec_ call
    menu.exec_(QCursor.pos())

def ExampleUIFile_Execute():
    """a simple example showing the use of a .ui file created using QtDesigner"""
    
    # find plugin to get the path to the example ui file
    plugin = Application.Plugins("PyQt_Example")
    if plugin is None:
        return False
        
    sianchor = Application.getQtSoftimageAnchor()
    sianchor = sip.wrapinstance( long(sianchor), QWidget )
    uifilepath = os.path.join(plugin.OriginPath, "exampleui.ui")
    dialog = QDialog(sianchor)
    dialog = ExampleUIFile( dialog, uifilepath )
    dialog.show()