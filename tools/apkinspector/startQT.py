# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys
sys.path.append("./src/images")
sys.path.append("./UI")

if sys.path[0] =="":
    SYSPATH = sys.path[1]
else:
    SYSPATH = sys.path[0]
    
from Ui_MainWindow import Ui_mainWindow

import binascii
import zipfile
from GetMethods import *
from APKInfo import *
from Graph import *
from xdotParser import *
from JAD import *
from newMessageBox import *
from CodeEditor import *
from SearchFilter import *
from FindDialog import *
from CallInOut import *
from CallInOutDialog import *
from ConfigurationDialog import *
from MyThread import *
from ProgressDialog import *
from APKtool import *


class startQT(QMainWindow, Ui_mainWindow):
    """
    This is the main class, in which all UI and initializations are finished.
    """
    path2method = {}            # the dictionary from path to method object
    CL = None                   # the instance of CLASS class
    Graph = None                # the instance of GraphicsView class
    findHistroyList = None      # the histroy list for findDialog
    callInOut = None            # the instance of class CallInOut
    apktool = None              # the instance of class APKtool

    def __init__(self, parent = None):
        """
        Constructor
        """
        mainWindow=QMainWindow.__init__(self, parent)        
        self.setupUi(self)
   
        self.mdiArea.addSubWindow(self.win1)
        self.mdiArea.addSubWindow(self.win2)

        # define a size policy
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)        
        
        # initialize the Java Tab
        self.plainTextEdit_java = CodeEditor()
        sizePolicy.setHeightForWidth(self.plainTextEdit_java.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_java.setSizePolicy(sizePolicy)
        self.plainTextEdit_java.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plainTextEdit_java.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plainTextEdit_java.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plainTextEdit_java.setCenterOnScroll(False)
        self.gridLayout_15.addWidget(self.plainTextEdit_java, 0, 0, 1, 1)     
        
        # initialize the Dalvik Tab
        self.plainTextEdit_dalvik = CodeEditor()
        sizePolicy.setHeightForWidth(self.plainTextEdit_dalvik.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_dalvik.setSizePolicy(sizePolicy)
        self.plainTextEdit_dalvik.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plainTextEdit_dalvik.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plainTextEdit_dalvik.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plainTextEdit_dalvik.setCenterOnScroll(False)
        self.gridLayout_12.addWidget(self.plainTextEdit_dalvik, 0, 0, 1, 1)
        
        # initialize the Bytecode Tab
        self.plainTextEdit_bytecode = CodeEditor()
        sizePolicy.setHeightForWidth(self.plainTextEdit_dalvik.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_bytecode.setSizePolicy(sizePolicy)
        self.plainTextEdit_bytecode.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plainTextEdit_bytecode.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plainTextEdit_bytecode.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plainTextEdit_bytecode.setCenterOnScroll(False)
        self.gridLayout_13.addWidget(self.plainTextEdit_bytecode, 0, 0, 1, 1)        

        # initialize the Smali Tab
        self.plainTextEdit_smali = CodeEditor()
        sizePolicy.setHeightForWidth(self.plainTextEdit_smali.sizePolicy().hasHeightForWidth())
        self.plainTextEdit_smali.setSizePolicy(sizePolicy)
        self.plainTextEdit_smali.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plainTextEdit_smali.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plainTextEdit_smali.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plainTextEdit_smali.setCenterOnScroll(False)
        self.gridLayout_14.addWidget(self.plainTextEdit_smali, 0, 0, 1, 1)  

        # initialize the Permission Tab
        sizePolicy.setHeightForWidth(self.textEdit_permission.sizePolicy().hasHeightForWidth())
        self.textEdit_permission.setSizePolicy(sizePolicy)
        self.textEdit_permission.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.textEdit_permission.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.textEdit_permission.setLineWrapMode(QTextEdit.NoWrap)
        
        # initialize the Call in/out Tab
        sizePolicy.setHeightForWidth(self.textEdit_call.sizePolicy().hasHeightForWidth())
        self.textEdit_call.setSizePolicy(sizePolicy)
        self.textEdit_call.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.textEdit_call.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.textEdit_call.setLineWrapMode(QTextEdit.NoWrap)        
        
        # initialize the CFG Tab's Graph scene
        self.Graph = GraphicsView()
        self.Graph.initShow(self.tab_cfg, self.gridLayout_11, self.tabWidget, self.plainTextEdit_dalvik)
        
        # set the editor to "read only"
        self.plainTextEdit_dalvik.setReadOnly(1)
        self.plainTextEdit_java.setReadOnly(1)
        self.plainTextEdit_bytecode.setReadOnly(1)
        
        # connect the signal and slot
        self.connect(self.pushButton, SIGNAL("clicked()"), self.searchAndFilter)
        self.connect(self.lineEdit, SIGNAL("editingFinished()"), self.refreshTreeWidget)
        self.connect(self.lineEdit, SIGNAL("textChanged()"), self.refreshTreeWidget)
        
        # define the global variable
        import Global
        Global.GRAPH = self.Graph
        Global.MAINWINDOW = self
        Global.CONFIG = {"CFG":1, "Dalvik":1, "Java":1, "Bytecode":1, "Smali":1, "CallIn":1, "CallOut":1, "Permission":1, "Manifest":1}
        
        
        # initialize the class attribute
        self.findHistroyList = QStringList()
    
    @pyqtSignature("")
    def on_actNew_triggered(self):
        """
        Slot: When the user click the New button, this slot will receive the New signal. 
        """
        
        # initialize the class attribute
        self.path2method = {}

        # create a file dialog to open an apk file
        dlg = QFileDialog(self)
        filename = dlg.getOpenFileName(self, self.tr("Open APK File"), QString(),  self.tr("APK Files(*.apk)"))
        if not zipfile.is_zipfile(filename):
            msgbox = QMessageBox()
            msgbox.setText("Please select the APK file correctly!")
            msgbox.setWindowTitle("Warning!")
            msgbox.show()
        else:
        # create a progress dialog to show the progress
        # all pre-processing are done in a thread
            progress = ProgressDialog()
            thread = MyThread(progress, str(filename))
            thread.start()            
            progress.run()

            import Global
            # judge this APK whether it is valid or invalid
            if not Global.APK.isVaildAPK():
                msgbox = QMessageBox()
                msgbox.setText("This APK is invalid!")
                msgbox.setWindowTitle("Error!")
                msgbox.exec_()
                return
                
            # clear all the last apk's info
            self.listWidget_strings.clear()
            self.listWidget_classes.clear()
            self.Graph.scene.clear()
            self.plainTextEdit_dalvik.setPlainText("")
            self.plainTextEdit_java.setPlainText("")
            self.plainTextEdit_bytecode.setPlainText("")
            self.plainTextEdit_smali.setPlainText("")
            self.textEdit_permission.setText("")
            self.textEdit_call.setText("")
            self.textBrowser.setText("")
            self.plainTextEdit_dalvik.reset()

            # start to show some infomation of the apk
            self.Tab_APKInfo(Global.APK)
            self.Tab_Methods(Global.APK, Global.VM, Global.VMX)
            self.Tab_Strings()
            self.Tab_Classes()
            
            if Global.CONFIG["Java"] == 1:
                self.Tab_Files(str(filename))
            else:
                self.treeWidget_files.clear()
            
            if Global.CONFIG["Smali"] ==1 or Global.CONFIG["Manifest"] ==1:
                self.apktool = APKtool()
        
            if Global.CONFIG["CallIn"] == 1 or Global.CONFIG["CallOut"] == 1:
                methodInvokeList = self.CL.get_methodInvoke()
                self.callInOut = CallInOut(methodInvokeList)
            else:
                self.textEdit_call.setText("")
             
            if Global.CONFIG["Permission"] == 1:
                self.Tab_Permission()
            else:
                self.textEdit_permission.setText("")                
                        
            if Global.CONFIG["Manifest"] ==1:
                self.Tab_Manifest()
            else:
                self.textBrowser.setText("")
          
            self.tabWidget_2.setCurrentIndex(4)
            self.tabWidget.setCurrentIndex(7)



##################################################
#Tab_APKInfo:
#    build the APKInfo Tab  
##################################################
    def Tab_APKInfo(self, apk):        
        self.textEdit_receivers = QTextEdit()
        self.textEdit_receivers.setText(apk.getReceivers()[0])
        self.textEdit_services = QTextEdit()
        self.textEdit_services.setText(apk.getServices()[0])
        self.textEdit_permissions = QTextEdit()
        self.textEdit_permissions.setText(apk.getPermissions()[0])

        # get the number of lines
        num_receivers = apk.getReceivers()[1]
        num_services = apk.getServices()[1]
        num_permissions = apk.getPermissions()[1]
        
        # set the default height of textedit widget
        self.textEdit_receivers.setFixedHeight(25*num_receivers)
        self.textEdit_services.setFixedHeight(25*num_services)
        self.textEdit_permissions.setFixedHeight(25*num_permissions)
        
        # add these items to the tableWidget. the last three items is the textEdits as cell widgets 
        self.tableWidget_apkinfo.setItem(0, 0, QTableWidgetItem(apk.getFilename()))
        self.tableWidget_apkinfo.setItem(1, 0, QTableWidgetItem(apk.getVersionCode()))
        self.tableWidget_apkinfo.setItem(2, 0, QTableWidgetItem(apk.getVersionName()))
        self.tableWidget_apkinfo.setItem(3, 0, QTableWidgetItem(apk.getPackage()))
        self.tableWidget_apkinfo.setCellWidget(4, 0, self.textEdit_receivers)
        self.tableWidget_apkinfo.setCellWidget(5, 0, self.textEdit_services)
        self.tableWidget_apkinfo.setCellWidget(6, 0, self.textEdit_permissions)
        
        # resize the tableWidget for adjusting to the content
        self.tableWidget_apkinfo.resizeColumnsToContents()
        self.tableWidget_apkinfo.resizeRowsToContents()
 
 

    def Tab_Methods(self, a, vm, vmx):
        """
            Build the Method Tab
            @params: the apk, its vm and vmx from Global varibales
        """
        self.CL = CLASS(a, vm, vmx)
        classes = self.CL.get_class()
        maxdepth = self.CL.get_maxdepth()
        
        self.treeWidget_methods.clear()
        self.treeWidget_methods.setColumnCount(2)
        
        classlist = self.CL.get_classlist()
        classlist.sort()                # sort the classname list

        pathdir = {}
        pathlist = {}
        
        for i in range(0, maxdepth):
            pathdir[i] = ""
            pathlist[i] = "" 
            
        for classname in classlist:
            methodlist = self.CL.get_methods_class(classname)
            if methodlist == []:
                continue
            
            flag = 0
            slice = classname.split("/")
            
            for i in range(0, len(slice)-1):
                if slice[i] == pathlist[i]:
                    if flag == 0:
                        continue
                else:
                    flag = 1
                    
                if i == 0:
                    child = QTreeWidgetItem(self.treeWidget_methods)
                    child.setText(0, slice[i])
                    child.setIcon(0, QIcon("src/images/closed_folder_blue.png"))
                    pathdir[i] = child
                    pathlist[i] = slice[i]
                else:
                    child = QTreeWidgetItem(pathdir[i-1])
                    child.setText(0, slice[i])
                    child.setIcon(0, QIcon("src/images/closed_folder_blue.png"))
                    pathdir[i] = child
                    pathlist[i] = slice[i]
            
            if flag == 0:
                child = QTreeWidgetItem(pathdir[i])
                child.setText(0, slice[-1])
                child.setIcon(0, QIcon("src/images/closed_folder_blue.png"))
            else:
                child = QTreeWidgetItem(child)
                child.setText(0, slice[-1])
                child.setIcon(0, QIcon("src/images/closed_folder_blue.png"))
            
            # add the node child items, which are methods.
            # it must add this index for identifying the function polymorphism
            index = 0
            for m in methodlist:
                # build a gloal dir from classname+methodname path to method obj
                self.path2method[classname + m._name + str(index)] = m
                index = index + 1
                methodname = self.CL.get_methodname(m)
                childMethod = QTreeWidgetItem(child)
                childMethod.setText(0, methodname)
                childMethod.setIcon(0, QIcon("src/images/file.png"))
        
        # create a connect between signal and slot.
        self.connect(self.treeWidget_methods, SIGNAL("itemDoubleClicked(QTreeWidgetItem *, int)"), self.locateMethod)        
        
        pheader = self.treeWidget_methods.header()
        pheader.setResizeMode(3)
        pheader.setStretchLastSection(0)
        
        self.treeWidget_methods.setStyleSheet("QTreeView::item:hover{background-color:rgb(0,255,0,50)}"
                                             "QTreeView::item:selected{background-color:rgb(255,0,0,100)}")

        self.treeWidget_methods.setSelectionBehavior(QAbstractItemView.SelectItems)


    def locateMethod(self, item, index):  
      """
        Locate the method, which has been clicked.
        @param item : the QtreeWidgetItem object
        @param index : the QtreeWidgetItem object's index.
      """
      if item.childCount() != 0:
          return
      else:
          methodname = item.text(index)
          parentlist = []
          classname = ""
          parent = item.parent()
 
          while parent :
            parentlist.append(parent.text(index))
            parent = parent.parent()

          for i in reversed(parentlist):
              if i == parentlist[0]:
                  classname += i
              else:
                  classname += i + "/"
          
          path = classname + methodname
          index = item.parent().indexOfChild(item)
          method = self.path2method[str(path) + str(index)]
          
          # after locating the method, get the content for Tab_Dalvik, Tab_CFG, Tab_Bytecode,Tab_CallInOut and Tab_Smali
          import Global
          if Global.CONFIG["Dalvik"] ==1:
              self.Tab_Dalvik(method)
          else:
              self.plainTextEdit_dalvik.setPlainText("")
        
          if Global.CONFIG["CFG"] == 1:
              self.Tab_CFG(method)
              self.tabWidget.setCurrentIndex(0)
          else:
              self.Graph.scene.clear()
              
          if Global.CONFIG["Bytecode"] == 1:
              self.Tab_Bytecode(method)
          else:
              self.plainTextEdit_bytecode.setPlainText("")
              
          if Global.CONFIG["CallIn"] == 1 or Global.CONFIG["CallOut"] == 1:
              self.Tab_CallInOut(method)
          else:
              self.textEdit_call.setText("")
            
          if Global.CONFIG["Smali"] == 1:
            if self.apktool.successFlag == 1:
                self.Tab_Smali(classname)
          else:
              self.plainTextEdit_smali.setPlainText("")
              

    def Tab_Dalvik(self, method):
        """
            build the Dalvik Tab  
            @param method : the method which is onclicked
        """
        dalvikContent = ""
        code =  method.get_code()

        # judge the flag for the last method. 
        # if the flag is 1(the last method has a annotation), then save the last annotation.
        if self.plainTextEdit_dalvik.currentMethod != None:
            if self.plainTextEdit_dalvik.methodOpened2AnnotationFlag[self.plainTextEdit_dalvik.currentMethod] == 1:
                self.plainTextEdit_dalvik.saveAnnotation()

        # judge the flag for the last method. 
        # if the flag is 1(the last method has a renaming table), then save the last renaming table and new renamed codes.
        if self.plainTextEdit_dalvik.currentMethod != None:
            if self.plainTextEdit_dalvik.methodOpened2RenamingFlag[self.plainTextEdit_dalvik.currentMethod] == 1:
                self.plainTextEdit_dalvik.saveRenamingTable()
                self.plainTextEdit_dalvik.saveNewCodes()
        
        # then write the current method's dalvik codes.
        if code == None:
            self.plainTextEdit_dalvik.setPlainText("")
        # if the current method's dalvik codes don't have new renamed codes, then get the original codes.
        elif not self.plainTextEdit_dalvik.method2NewCodes.has_key(method):
            bc = code.get_bc()
            idx = 0
            for i in bc.get():
                dalvikContent += "0x%x" % idx + " "
                dalvikContent += i.show_buff(idx) + "\n"
                idx += i.get_length()   
            self.plainTextEdit_dalvik.setPlainText(dalvikContent)
        # if the current method' dalvik codes have new renamed codes, then get the new codes  
        else:
            self.plainTextEdit_dalvik.setPlainText(self.plainTextEdit_dalvik.method2NewCodes[method])

        # add the current opened method to the methodOpened2AnnotationFlag dict
        self.plainTextEdit_dalvik.addOpenedMethod(method)
        
        # if flag is 1, it means that it has created a annotation editor.
        # it will set the annotation editor to be hidden
        if self.plainTextEdit_dalvik.flag ==1:
            self.plainTextEdit_dalvik.annotationDockWidget.setVisible(0)

        # reset the firstOpenFlag when openning a new method
        self.plainTextEdit_dalvik.firstOpenFlag = 0
        
        # if flag is 1, it means that it has created a renaming table.
        # it will set the renaming table to be hidden
        if self.plainTextEdit_dalvik.flagRenaming ==1:
            self.plainTextEdit_dalvik.renamingDockWidget.setVisible(0)

        # reset the firstRenameFlag when openning a new method
        self.plainTextEdit_dalvik.firstRenameFlag = 0        
   
    def Tab_Classes(self):
        """
            build the Classes Tab
        """
        Classes = self.CL.vm.get_classes_names()
        for c in Classes:
            listItem = QListWidgetItem(c, self.listWidget_classes)
            listItem.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    def Tab_Strings(self):
        """
            build the Strings Tab
        """
        Strings = self.CL.vm.get_strings()
        for s in Strings:
            listItem = QListWidgetItem(s, self.listWidget_strings)
            listItem.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        
    def Tab_Bytecode(self, method):
        """
            build the Bytecode Tab
            @param method : the method which is onclicked
        """
        bytecode = ""
        code = method.get_code()

        # judge the flag for the last method. 
        # if the flag is 1(the last method has a annotation), then save the last annotation.
        if self.plainTextEdit_bytecode.currentMethod != None:
            if self.plainTextEdit_bytecode.methodOpened2AnnotationFlag[self.plainTextEdit_bytecode.currentMethod] == 1:
                self.plainTextEdit_bytecode.saveAnnotation()

        if code == None:
            self.plainTextEdit_bytecode.setPlainText("")
        else:
            bc = code.get_bc()
            idx = 0
            for i in bc.get():
                bytecode += "0x%x" % idx + " "
                raw = i.get_raw()
                c = binascii.hexlify(raw)
                raw = ""
                while c:
                    f = c[0:2]
                    raw += "\\x" + f
                    c = c[2:]
                bytecode += raw + "\n"
                idx += i.get_length()
            self.plainTextEdit_bytecode.setPlainText(bytecode)

        # add the current opened method to the methodOpened2AnnotationFlag dict
        self.plainTextEdit_bytecode.addOpenedMethod(method)
        
        # if flag is 1, it means that it has created a annotation editor.
        # it will set the annotation editor to be hidden
        if self.plainTextEdit_bytecode.flag ==1:
            self.plainTextEdit_bytecode.annotationDockWidget.setVisible(0)
         
        # reset the firstOpenFlag when openning a new method
        self.plainTextEdit_bytecode.firstOpenFlag = 0


    def Tab_CFG(self, method):
        """
            build the CFG Tab
            @param method: the method which is onclicked
        """
        if method.get_code() == None:
            self.Graph.scene.clear()
            return
        import Global
        xdot = XDot(method, Global.VM, Global.VMX)
        xdot.method2xdot()
        [pagesize, nodeList, linkList] = xdot.parse()
        self.Graph.setPageSize(pagesize)
        self.Graph.show(nodeList, linkList)
        
        
    def Tab_Files(self, filename):
        """
            build the Files Tab
            @param filename: the opened apk's filename
        """
        self.treeWidget_files.clear()
        self.treeWidget_files.setColumnCount(2)
        
        # create a connect between signal and slot.
        self.connect(self.treeWidget_files, SIGNAL("itemDoubleClicked(QTreeWidgetItem *, int)"), self.locateFile)

        pheader = self.treeWidget_files.header()
        pheader.setResizeMode(3)
        pheader.setStretchLastSection(0)
        
        self.treeWidget_files.setStyleSheet("QTreeView::item:hover{background-color:rgb(0,255,0,50)}"
                                             "QTreeView::item:selected{background-color:rgb(255,0,0,100)}")
        import Global
        if Global.FLAG_JAD != 1:
            return

        rootpath = SYSPATH +  "/temp/java"
        parent = self.treeWidget_files
        path2parent = {rootpath:parent}
        for root, dirs, files in os.walk(rootpath):
            for f in files:
                parent = path2parent[root]
                child = QTreeWidgetItem(parent)
                child.setText(0, f)
            for d in dirs:
                parent = path2parent[root]
                child = QTreeWidgetItem(parent)
                child.setText(0, d)
                path2parent[root + "/" +d] = child
                
##################################################
#locateFile:
#    locate the Java file, which has been clicked  
################################################## 
    def locateFile( self, item, index):  
      """
        locate the Java file, which has been clicked 
        @param item: the QTreeWidgetItem object
        @param index: the QTreeWidgetItem index
      """
      if item.childCount() != 0:
          return
      else:
          filename = item.text(index)
          parentlist = []
          path = ""
          parent = item.parent()
 
          while parent :
            parentlist.append(parent.text(index))
            parent = parent.parent()

          for i in reversed(parentlist):
              if i == parentlist[0]:
                  path += i
              else:
                  path += i + "/"
          
          inputpath = SYSPATH + "/temp/java/" + path + "/" + filename
          
          try:
            data = open(inputpath, "r").read()
          except IOError:
              print "IOError"
              data = None
          
          self.Tab_Java(data)
          self.tabWidget.setCurrentIndex(4)


    def Tab_Java(self, javacode):
        """
            Build the Java Tab
        """
        if javacode == None:
            self.plainTextEdit_java.setPlainText("")
        else:
            self.plainTextEdit_java.setPlainText(javacode)


    def Tab_Manifest(self):
        """
            Build the Manifest Tab
        """
        [flag, data] = self.apktool.getManifest()
        if flag == 1:
            # set the code for Chinese
            tc = QTextCodec.codecForName("utf8")
            QTextCodec.setCodecForCStrings(tc)
            self.textBrowser.setText(data)
        

    def Tab_Smali(self, classname): 
        """
            Build the Smali Tab
            @param classname : the class's name of the method which is onclicked 
        """
        # judge the flag for the last class. 
        # if the flag is 1(the last class has a annotation), then save the last annotation.
        if self.plainTextEdit_smali.currentClass != None:
            if self.plainTextEdit_smali.classOpened2AnnotationFlag[self.plainTextEdit_smali.currentClass] == 1:
                self.plainTextEdit_smali.saveAnnotationSmali()

        [flag, data] = self.apktool.getSmaliCode(classname)
        if flag == 0:
            pass
        elif flag == 1:
            self.plainTextEdit_smali.setPlainText(data)
            
        # add the current opened class to the classOpened2AnnotationFlag dict
        self.plainTextEdit_smali.addOpenedClass(classname)
        
        # if flag is 1, it means that it has created a annotation editor.
        # it will set the annotation editor to be hidden
        if self.plainTextEdit_smali.flag ==1:
            self.plainTextEdit_smali.annotationDockWidget.setVisible(0)
         
        # reset the firstOpenFlag when openning a new class
        self.plainTextEdit_smali.firstOpenFlag = 0
  

    def Tab_Permission(self):
        """
            Build the Permission Tab
        """
        permissionContent = ""
        permissionDict = self.CL.get_permission()
        for permission in permissionDict.keys():
            APILocationList = permissionDict[permission]
            permissionContent += "*******************************"
            permissionContent += "Permission: "
            permissionContent += permission
            permissionContent += "*******************************"
            permissionContent += "\n\n"
            for api in APILocationList:
                li = api.split("  --->  ")
                APIName = li[1]
                methodName = li[0][:li[0].index(" (@")]
                where = li[0][li[0].rindex("("):]
                permissionContent += "API: " + APIName + "\n"
                permissionContent += "Method: " + methodName + "\n"
                permissionContent += "Where: " + where + "\n\n"
        self.textEdit_permission.setText(permissionContent)
 
 
    def Tab_CallInOut(self, method):
        """
            Build the CallInOut Tab
            @param method: the method whose call in/out methods you'd like to view.
        """
        callInContent = "************************Call In*************************\n"
        callOutContent = "***********************Call Out************************\n"
        className = method.get_class_name()
        methodName = method.get_name()
        descriptor = method.get_descriptor()
        callMethod = className + " " + descriptor + "," + methodName
        
        callInList = []
        callOutList = []
        
        import Global
        if Global.CONFIG["CallIn"] == 1:
            callInList= self.callInOut.searchCallIn(callMethod)
        if Global.CONFIG["CallOut"] == 1:
            callOutList = self.callInOut.searchCallOut(callMethod)
        
        for i in callInList:
            temp = i.split("^")
            callInContent += temp[0] + "  ("+ temp[1] + ")" + "\n"
         
        for i in callOutList:
            temp = i.split("^")
            callOutContent += temp[0] + "  (" + temp[1] + ")" + "\n"
            
        self.textEdit_call.setText(callInContent + "\n\n\n" + callOutContent)

 
    def searchAndFilter(self):
        """
            search or filter the method/class/string in the line Edit.
        """
        target = self.lineEdit.text()
        option = 0
        
        if self.radioButton_filter.isChecked():
            option = 1
        elif self.radioButton_search.isChecked():
            option = 2
        
        currentIndex = self.tabWidget_2.currentIndex()
        if currentIndex not in [0, 1, 2, 3]:
            return
        
        if currentIndex == 3:
            searchFilter = SearchFilter(self.treeWidget_methods, target)
        elif currentIndex == 2:
            searchFilter = SearchFilter(self.listWidget_classes, target)
        elif currentIndex == 1:
            searchFilter = SearchFilter(self.listWidget_strings, target)
        elif currentIndex == 0:
            searchFilter = SearchFilter(self.treeWidget_files, target)
        
        if option == 1:
            if currentIndex == 3 or currentIndex == 0:
                searchFilter.filter_treewidget()
            elif currentIndex == 2 or currentIndex == 1:
                searchFilter.filter_listwidget()
        elif option ==2:
            if currentIndex == 3 or currentIndex == 0:
                searchFilter.search_treewidget()
            elif currentIndex == 2 or currentIndex == 1:
                searchFilter.search_listwidget()


    def refreshTreeWidget(self):
        """
            refresh the tabWidget_2, which is a QTreeWidget object
        """
        if self.tabWidget_2.currentIndex() == 3:
            it = QTreeWidgetItemIterator(self.treeWidget_methods)
            while it.value():
                item = it.value()
                item.setHidden(0)
                item.setSelected(0)
                it = it.__iadd__(1)
                
        elif self.tabWidget_2.currentIndex() == 0:
            it = QTreeWidgetItemIterator(self.treeWidget_files)
            while it.value():
                item = it.value()
                item.setHidden(0)
                item.setSelected(0)
                it = it.__iadd__(1)
                
        elif self.tabWidget_2.currentIndex() == 1:
            total = self.listWidget_strings.count()
            for i in range(0, total):
                item = self.listWidget_strings.item(i)
                item.setHidden(0)
                item.setSelected(0)
                
        elif self.tabWidget_2.currentIndex() == 2:
            total = self.listWidget_classes.count()
            for i in range(0, total):
                item = self.listWidget_classes.item(i)
                item.setHidden(0)
                item.setSelected(0) 


    @pyqtSignature("")
    def on_About_triggered(self):
        """
        Slot: show the infomation about this software when the user clicks the About option.
        """
        self.msgbox = newMessageBox()
        self.msgbox.setText("APKinspector\n\nAuthor:  CongZheng(CN)\nMentor: Ryan W Smith(US), Anthony Desnos(FR)\nSupported by the Honeynet Project and Gsoc2011")
        self.msgbox.setWindowTitle("About")
        pixmap = QPixmap("./src/images/logo.png")
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        self.msgbox.setIconPixmap(pixmap)
        self.msgbox.exec_()                
              

    @pyqtSignature("")
    def on_actFind_triggered(self):
        """
        Slot: Find the word or sentence in tabs: Dalvik, Bytecode, Smali, Java 
        """ 
        index2widget = {1:self.plainTextEdit_dalvik, 2:self.plainTextEdit_bytecode, 3:self.plainTextEdit_smali, 4:self.plainTextEdit_java}
        index = self.tabWidget.currentIndex()
        if index not in index2widget.keys():
            return
        widget = index2widget[index]
        cursor = widget.textCursor()
        selectedText = cursor.selectedText()
        findDialog = FindDialog(self)
        findDialog.setWidget(widget)
        findDialog.setFindHistroyList(self.findHistroyList)
        findDialog.comboBox.setEditText(selectedText)
        findDialog.exec_()
        self.findHistroyList = findDialog.findHistroyList


    @pyqtSignature("")
    def on_actCall_in_out_triggered(self):
        """
        Slot: show the call in/out methods
        """ 
        callInOutDialog = CallInOutDialog()
        callInOutDialog.exec_()
        
        callInContent = "************************Call In*************************\n"
        callOutContent = "***********************Call Out************************\n"
        callInList = []
        callOutList = []
        callMethod = callInOutDialog.callMethod

        if callInOutDialog.callInFlag == 1:
            callInList= self.callInOut.searchCallIn(callMethod)
        if callInOutDialog.callOutFlag == 1:
            callOutList = self.callInOut.searchCallOut(callMethod)
        
        for i in callInList:
            temp = i.split("^")
            callInContent += temp[0] + "  ("+ temp[1] + ")" + "\n"
        
        for i in callOutList:
            temp = i.split("^")
            callOutContent += temp[0] + "  (" + temp[1] + ")" + "\n"
        
        self.textEdit_call.setText(callInContent + "\n\n\n" + callOutContent)        


    @pyqtSignature("")
    def on_actConfiguration_triggered(self):
        """
        Slot: show the configuration dialog
        """
        configDialog = ConfigurationDialog()
        configDialog.exec_()
        
    
    @pyqtSignature("")
    def on_actQuit_triggered(self):
        """
        Slot: quit the application
        """
        sys.exit()


if __name__ == "__main__":
    app= QApplication(sys.argv)
    myapp = startQT()
    myapp.show()
    sys.exit(app.exec_())
    
