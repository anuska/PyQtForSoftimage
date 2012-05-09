from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal

from win32com.client import Dispatch as disp
from win32com.client import constants as C
si = disp('XSI.Application').Application

EVENT_MAPPING = {
    #pyqtsignal : softimage event
    "siActivate" : "QtEvents_Activate",
    "siFileExport" : "QtEvents_FileExport",
    "siFileImport" : "QtEvents_FileImport",
    "siCustomFileExport" : "QtEvents_CustomFileExport",
    "siCustomFileImport" : "QtEvents_CustomFileImport",
    
    "siRenderFrame" : "QtEvents_RenderFrame",
    "siRenderSequence" : "QtEvents_RenderSequence",
    "siRenderAbort" : "QtEvents_RenderAbort",
    "siPassChange" : "QtEvents_PassChange",
    
    "siSceneOpen" : "QtEvents_SceneOpen",
    "siSceneSaveAs" : "QtEvents_SceneSaveAs",
    "siSceneSave" : "QtEvents_SceneSave",
    "siChangeProject" : "QtEvents_ChangeProject",
    
    "siConnectShader" : "QtEvents_ConnectShader",
    "siDisconnectShader" : "QtEvents_DisconnectShader",
    "siCreateShader" : "QtEvents_CreateShader",
    
    "siDragAndDrop" : "QtEvents_DragAndDrop",
    
    "siObjectAdded" : "QtEvents_ObjectAdded",
    "siObjectRemoved" : "QtEvents_ObjectRemoved",
    
    "siSelectionChange" : "QtEvents_SelectionChange",
    
    "siSourcePathChange" : "QtEvents_SourcePathChange",
        
    "siValueChange" : "QtEvents_ValueChange",
}

class SISignals( QObject ):
    """
    Class for mapping softimage events to pyqt signals
    not all context attributes are passed as signal arguments, add more as needed
    currently all signals are expected to be 'siOnEnd' versions of softimage events.  
    It is implemented as a singleton and registers which signals are in used with which slot.    
    """
    
    # add more pyqtsignals that map to softimage events here
    siActivate = pyqtSignal(bool) # siOnActivate
    
    siFileExport = pyqtSignal(str) # siOnEndFileExport
    siFileImport = pyqtSignal(str) # siOnEndFileImport
    siCustomFileExport = pyqtSignal(str) # siOnCustomFileExport
    siCustomFileImport = pyqtSignal(str) # siOnCustomFileImport
    
    siRenderFrame = pyqtSignal(str,int) # siOnEndFrame
    siRenderSequence = pyqtSignal(str,int) # siOnEndSequence
    siRenderAbort = pyqtSignal(str,int) # siOnRenderAbort
    siPassChange = pyqtSignal(str) # siOnEndPassChange
    
    siSceneOpen = pyqtSignal(str) # siOnEndSceneOpen
    siSceneSaveAs = pyqtSignal(str) # siOnEndSceneSaveAs
    siSceneSave = pyqtSignal(str) # siOnEndSceneSave2
    siChangeProject = pyqtSignal(str) # siOnChangeProject
    
    siConnectShader = pyqtSignal(str,str) # siOnConnectShader
    siDisconnectShader = pyqtSignal(str,str) # siOnDisconnectShader
    siCreateShader = pyqtSignal(str,str) # siOnCreateShader
    
    siDragAndDrop = pyqtSignal(str) # siOnDragAndDrop
    
    siObjectAdded = pyqtSignal(list) # siOnObjectAdded
    siObjectRemoved = pyqtSignal(list) # siOnObjectRemoved
    
    siSelectionChange = pyqtSignal(int) # siOnSelectionChange
    
    siSourcePathChange = pyqtSignal(str) # siOnSourcePathChange
        
    siValueChange = pyqtSignal(str) # siOnValueChange
    
    _instance = None
    
    _connections = {}
    
    def __init__(self):
        QObject.__init__(self)
        self.setObjectName( "siSignals" )

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SISignals, cls).__new__(cls, *args, **kwargs)
        return cls._instance
                    
    def connect(self, signal, function):
        if hasattr(self, signal):
            if signal in self._connections:
                slots = self._connections[signal]
                if function not in slots:
                    getattr(self, signal).connect(function)
                    slots.append(function)
            else:
                getattr(self, signal).connect(function)
                self._connections[signal] = [function]
                muteSIEvent(signal, False)
               
    def disconnect(self, signal, function):
        if hasattr(self, signal):
            getattr(self, signal).disconnect(function)

            if signal in self._connections:
                slots = self._connections[signal]
                if function in slots:
                    slots.remove(function)
                    if not len(slots):
                        self._connections.pop(signal)
                        muteSIEvent(signal, True)
          
    def emit(self, signal, *args):
        if hasattr(self, signal):
            getattr(self,signal).emit(*args)
                                                  
    def reload(self):
        self._connections = {}
        for signal in EVENT_MAPPING:
            muteSIEvent(signal, True)
            
signals = SISignals()

def muteSIEvent(signal, state=True):
    events = si.EventInfos
    event = events(EVENT_MAPPING[signal])
    if si.ClassName(event) == "EventInfo":
        event.Mute = state
        