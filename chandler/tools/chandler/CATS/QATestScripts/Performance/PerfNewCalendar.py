import util.QAUITestAppLib as QAUITestAppLib
import os

filePath = os.getenv('CATSREPORTDIR')
if not filePath:
    filePath = os.getcwd()
    
#initialization
fileName = "PerfNewCalendar.log"
logger = QAUITestAppLib.QALogger(os.path.join(filePath, fileName),"Test New Calendar for performance")

#action
col = QAUITestAppLib.UITestItem("Collection", logger)

#action
col.Check_Sidebar({"displayName":"Untitled"})


#cleaning
logger.Close()

# quit chandler
App_ns = QAUITestAppLib.App_ns
App_ns.root.Quit()