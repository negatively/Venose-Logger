import threading
import serial.tools.list_ports
import time

class SerialCtrl():
    def __init__(self):
        self.com_list = []
        self.sync_cnt = 200

    def getCOMList(self):
        ports = serial.tools.list_ports.comports()
        self.com_list = [com[0] for com in ports]
        self.com_list.insert(0, "-")

    def SerialOpen(self, gui):
        try:
            self.ser.is_open
        except:
            PORT = gui.clicked_com.get()
            BAUD = gui.clicked_baud.get()
            self.ser = serial.Serial()
            self.ser.baudrate = BAUD
            self.ser.port = PORT
            self.ser.timeout = 0.1
            
        
        try:
            if self.ser.is_open:
                self.ser.status = True
            else:
                PORT = gui.clicked_com.get()
                BAUD = gui.clicked_baud.get()
                self.ser = serial.Serial()
                self.ser.baudrate = BAUD
                self.ser.port = PORT
                self.ser.timeout = 0.1
                self.ser.open()
                self.ser.status = True
        except:
            self.ser.status = False

    def SerialClose(self, ComGUI):
        try:
            self.ser.is_open
            self.ser.close()
            self.ser.status = False
        
        except:
            self.ser.status = False 
    
    
    def SerialData(self, gui):
        self.threading = True
        cnt = 0
        while self.threading:
            data = self.ser.readline()
            if len(data) > 0:
                try:
                    ###############################################

                    gui.data.RowMsg = data
                    gui.data.DecodeMsg()
                    gui.data.IntMsgFunc()
                    ###############################################                                      

                    gui.data.yData.append(gui.data.IntMsg)
                    if len(gui.data.xData) == 0:
                        gui.data.xData.append(0)
                    else:
                        gui.data.xData.append(time.perf_counter() - gui.refTime)

                    self.lenYdata = len(gui.data.yData)
                    self.lenXdata = len(gui.data.xData)

                    printRange = 0
                    TimeRange = 200

                    for time_series in range(self.lenXdata-1, 0, -1):
                        printRange += 1
                        if gui.data.xData[self.lenXdata-1] - gui.data.xData[time_series-1] > TimeRange:
                            break
                    
                    if self.lenXdata == printRange:
                        gui.data.y = [k for k in gui.data.yData]
                        gui.data.x = [k for k in gui.data.xData]
                    else:
                        gui.data.y = gui.data.yData[self.lenYdata-printRange:self.lenYdata]
                        gui.data.x = gui.data.xData[self.lenXdata-printRange:self.lenXdata] 

                except Exception as e:
                    print(e)

    def SerialTemp(self, gui):
        self.threading_temp = True
        cnt = 0
        while self.threading_temp:
            data = self.ser.readline()
            if len(data) > 0:
                try:
                    ###############################################

                    gui.data.RowMsg = data
                    gui.data.DecodeMsg()
                    gui.data.FloatMsgFunc()
                    ###############################################                                        
                    
                    t2 = threading.Thread(target=gui.GraphCtrl(), args=(gui.graph,), daemon=True)
                    t2.start()


                except Exception as e:
                    print(e)
    
    def Airflow(self, gui):        
        while time.perf_counter() < gui.refTime + 2:
            self.ser.write(bytes('P', 'UTF-8'))
        while time.perf_counter() < gui.refTime + 2 + 5:
            self.ser.write(bytes('S', 'UTF-8'))
        while time.perf_counter() < gui.refTime + 2 + 5 + 7:
            self.ser.write(bytes('P', 'UTF'))
        gui.stop_stream()


if __name__ == '__main__':
    SerialCtrl()

