from datetime import datetime
import csv

class DataMain():
    def __init__(self):
        self.StartStream = "#A#\n"
        self.StopStream = "#S#\n"

        self.msg = []

        self.xData = []
        self.yData = []
        self.x = []
        self.y = []
    
    def DecodeMsg(self):
        temp = self.RowMsg.decode('utf8')
        if len(temp) > 0:
            if "#" in temp:
                self.msg = temp.split("#")
                del self.msg[0]
                if self.msg[0] in "D":
                    del self.msg[0]
                    del self.msg[-1]
    
    def IntMsgFunc(self):
        self.IntMsg = [int(msg) for msg in self.msg]

    def ClearData(self):
        self.RowMsg = ""
        self.msg = []
        self.yData = []
        self.xData = []
    
    def SaveData(self):
        now = datetime.now()
        filename = "venose_data_" + now.strftime("%Y-%m-%d-%H-%M")+".csv"
        labels = ['Time','TGS-822', 'TGS-2600', 'TGS-2611', 'MQ-3', 'MQ-9', 'MQ-135']
        with open(filename, 'a', newline='') as f:
            data_writer = csv.writer(f)
            data_writer.writerow(labels)
            for i in range(len(self.yData)):
                data = [round(self.xData[i],1)] + self.yData[i]
                data_writer.writerow(data)

    # def SetRefTime(self):
    #     if len(self.xData) == 0:
    #         self.RefTime = time.perf_counter()
    #     else:
    #         self.RefTime = time.perf_counter() - self.xData[len(self.xData)-1]

    # def UpdateXData(self):
    #     if len(self.xData) == 0:
    #         self.xData.append(0)
    #     else:
    #         self.xData.append(time.perf_counter() - self.RefTime)
    
    # def UpdateYData(self):
    #     self.yData.append()
    
    

