from venose_main import RootGUI, ComGUI
from serial_com_ctrl import SerialCtrl
from data_com_ctrl import DataMain


MySerial = SerialCtrl()
MyData = DataMain()
RootMain = RootGUI()

ComMain = ComGUI(RootMain.root, MySerial, MyData)

RootMain.root.mainloop()