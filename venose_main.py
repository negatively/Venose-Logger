
from tkinter import *
from tkinter import messagebox, ttk
import threading
import time

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)


class RootGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Serial Communication")
        # self.root.state('zoomed')
        self.root.config(bg='#fff')

class Graphics():
    pass

class ComGUI():
    def __init__(self, root, serial, data):
        # Frame 
        self.root = root
        self.serial = serial
        self.data = data
        self.frame = LabelFrame(root, text="COM Manager", padx = 5, pady = 5, bg = '#fff')
        self.label_com = Label(
            self.frame, text="Available Port : ", bg='#fff', width=15, anchor='w')
        self.label_bd = Label(
            self.frame, text='Baud Rate : ', bg='#fff', width=15, anchor='w')
        self.com_option_menu()
        self.baud_option_menu()
        self.btn_refresh = Button(self.frame, text="Refresh", width=10,
                            command=self.com_refresh)
        self.btn_connect = Button(self.frame, text="Connect",
                                  width=10, state="disabled",  command=self.serial_connect)

        self.padx = 20
        self.pady = 12
        self.publish()
        

    def com_option_menu(self):
        self.serial.getCOMList()
        self.clicked_com = StringVar()
        self.clicked_com.set(self.serial.com_list[0])
        self.drop_com = OptionMenu(
            self.frame, self.clicked_com, *self.serial.com_list, command=self.connect_ctrl)
        self.drop_com.config(width=10)

    def baud_option_menu(self):
        bauds = ["-", '9600', '115200', '256000']
        self.clicked_baud = StringVar()
        self.clicked_baud.set(bauds[0])
        self.drop_baud = OptionMenu(
            self.frame, self.clicked_baud, *bauds, command=self.connect_ctrl)
        self.drop_baud.config(width=10)

    def publish(self):
        self.frame.grid(row = 0, column = 0, rowspan=3, columnspan=3, padx = 5, pady=5)
        self.label_com.grid(column=1, row=2)
        self.drop_com.grid(column=2, row=2, padx = self.padx, pady=self.pady)
        self.label_bd.grid(column=1, row=3)
        self.drop_baud.grid(column=2, row=3, padx = self.padx, pady=self.pady)

        self.btn_refresh.grid(column=3, row=2)
        self.btn_connect.grid(column=3, row=3)

    def connect_ctrl(self, widget):
        print('Connecting...')        
        if "-" in self.clicked_baud.get() or "-" in self.clicked_com.get():
            self.btn_connect["state"] = "disabled"
        else:
            self.btn_connect["state"] = "active"

    def com_refresh(self):
        self.drop_com.destroy()
        self.com_option_menu()
        self.drop_com.grid(column=2, row=2, padx = self.padx, pady=self.pady)
        logic = []
        self.connect_ctrl(logic)

    def serial_connect(self):
       

        if self.btn_connect['text'] in "Connect":
            # Start the connection
            self.serial.SerialOpen(self)

            if self.serial.ser.status:
                self.btn_connect["text"] = "Disconnect"
                self.btn_refresh["state"] = "disable"
                self.drop_baud["state"] = "disable"
                self.drop_com["state"] = "disable"
                InfoMsg = "Connection successfully"
                messagebox.showinfo("showinfo", InfoMsg)

                self.conn = ConnGUI(self.root, self.serial, self.data)


            else:
                ErrorMsg = f"Error"
                messagebox.showerror("showerror", ErrorMsg)
            
        else:
            self.serial.threading = False
            self.serial.threading_temp = False
            self.serial.SerialClose(self)

            self.conn.ConnGUIClose()
            self.data.ClearData()
            # Start closing the connection
            
            InfoMsg = "Connection Closed"
            messagebox.showinfo("showinfo", InfoMsg)
            self.btn_connect["text"] = "Connect"
            self.btn_refresh["state"] = "active"
            self.drop_baud["state"] = "active"
            self.drop_com["state"] = "active"

class ConnGUI():
    def __init__(self, root, serial, data):
        self.root = root
        self.serial = serial
        self.data = data

        self.frame = LabelFrame(root, text="Serial Read Manager", padx = 5, pady=5, bg='#fff',
                                width=60)

        ########## Label ##########        
        self.flush_label = Label(
            self.frame, text="Flush Time : ", bg='#fff', width=15, anchor='w')
        self.sample_label = Label(
            self.frame, text="Sample Time : ", bg='#fff', width=15, anchor='w')
        self.purge_label = Label(
            self.frame, text="Purge Time : ", bg='#fff', width=15, anchor='w')

        ########## Button ##########        
        self.btn_start_stream = Button(
            self.frame, text="Start", state='disabled', width=15, command=self.start_stream)
        self.btn_stop_stream = Button(
            self.frame, text="Stop", state='disabled', width=15, command=self.stop_stream)
        self.btn_save_stream = Button(
            self.frame, text="Save To CSV", state='disabled', width=15, command=self.save_stream)

        ########## Call Option Menu ########## 
        self.flush_option_menu()
        self.sample_option_menu()
        self.purge_option_menu() 

        ########## Display For Temperature ########## 
        self.graph = Graphics()
        # Static Part #        
        self.graph.canvas = Canvas(self.frame, width = 100, height=100, bg='#fff', highlightthickness=0)  
        self.graph.canvas.create_rectangle(75,75,25,25,outline = '#f11', fill='#fff', width=2)
        self.graph.canvas.create_text(65, 10, anchor=E, text='Temp')
        # Dynamic Part #
        self.graph.text = self.graph.canvas.create_text(64, 60, anchor=E, text='---', font=('Arial 10 bold'))
        # Static Part #
        self.graph.canvas.create_text(55, 65, anchor=E, text='C', font=('Arial 10 bold'))

        self.serial.t4 = threading.Thread(
            target=self.serial.SerialTemp, args=(self,), daemon = True
        )
        self.serial.t4.start()      
        

        ##########################################
        
        self.separator = ttk.Separator(self.frame, orient='vertical')
        self.separator2 = ttk.Separator(self.frame, orient='vertical')
        self.padx = 20
        self.pady = 3
        self.chartMain = PlotData(self.root, self.serial, self.data)
        self.ConnGUIOpen()

    def GraphCtrl(self):
        self.graph.canvas.itemconfig(self.graph.text, text=f"{self.data.StrMsg}")
    
    def ConnGUIOpen(self):
        
        self.frame.grid(row=0, column=4, rowspan=3, columnspan=5, padx=5, pady=5)

        self.flush_label.grid(column=1, row=1)
        self.drop_flush.grid(column=2, row=1, padx=self.padx, pady=self.pady)

        self.sample_label.grid(column=1, row=2)
        self.drop_sample.grid(column=2, row=2, padx=self.padx, pady=self.pady)

        self.purge_label.grid(column=1, row=3)
        self.drop_purge.grid(column=2, row=3, padx=self.padx, pady=self.pady)

        self.separator.place(relx=0.5, rely=0, relwidth=0.001, relheight=1)
        self.separator2.place(relx=0.81, rely=0, relwidth=0.001, relheight=1)

        self.btn_start_stream.grid(column=3, row=1, padx=self.padx)
        self.btn_stop_stream.grid(column=3, row=2, padx=self.padx)
        self.btn_save_stream.grid(column=3, row=3, padx=self.padx)        

        self.graph.canvas.grid(column = 4, row=1, rowspan = 3)
        self.chartMain.OpenPlot()


    def ConnGUIClose(self):
        self.chartMain.ClosePlot()
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()


    def flush_option_menu(self):
        t_flush = ["-", '10', '20', '30', '40', '50', '60']
        self.clicked_flush = StringVar()
        self.clicked_flush.set(t_flush[0])
        self.drop_flush = OptionMenu(
            self.frame, self.clicked_flush, *t_flush, command=self.start_ctrl)
        self.drop_flush.config(width=10)
    
    def sample_option_menu(self):
        t_sample = ["-", '15','30', '45', '60', '75', '90', '105', '120']
        self.clicked_sample = StringVar()
        self.clicked_sample.set(t_sample[0])
        self.drop_sample = OptionMenu(
            self.frame, self.clicked_sample, *t_sample, command=self.start_ctrl)
        self.drop_sample.config(width=10)

    def purge_option_menu(self):
        t_purge = ["-", '15', '30', '45', '60', '75', '90', '105', '120']
        self.clicked_purge = StringVar()
        self.clicked_purge.set(t_purge[0])
        self.drop_purge = OptionMenu(
            self.frame, self.clicked_purge, *t_purge, command=self.start_ctrl)
        self.drop_purge.config(width=10)
    
    def start_ctrl(self, widget):       
        
        if "-" in self.clicked_flush.get() or "-" in self.clicked_sample.get() or "-" in self.clicked_purge.get():
            self.btn_start_stream["state"] = "disabled"
        else:
            self.btn_start_stream["state"] = "active" 
    
    def start_stream(self):
        self.serial.threading_temp = False
        self.data.ClearData()
        # Menambahkan figure plot
        self.serial.ser.write(bytes('H', 'UTF-8'))

        # Mengatur keadaan state button stop dan start
        self.btn_stop_stream["state"] = "active"
        self.btn_start_stream["state"] = "disabled"
        self.btn_save_stream["state"] = "disabled"

        self.chartMain.chart.get_tk_widget().grid()

        self.root.geometry("1200x800")
        if len(self.data.xData) == 0:
            self.refTime = time.perf_counter()
        else:
            self.refTime = time.perf_counter() - self.data.xData[len(self.data.xData) - 1]

        self.serial.t1 = threading.Thread(
            target=self.serial.SerialData, args=(self,), daemon = True
        )
        self.serial.t1.start()

        self.UpdateChart()
        self.UpdateTime()

    def stop_stream(self):
        self.serial.ser.write(bytes('O', 'UTF-8'))

        # Mengatur keadaan state button stop dan start
        self.btn_start_stream["state"] = "disabled"
        self.btn_stop_stream["state"] = "disabled"
        self.btn_save_stream["state"] = "active"

        # self.chartMain.chart.get_tk_widget().grid_remove()

        self.serial.threading = False
    
    def save_stream(self):
        self.data.SaveData()
        self.btn_save_stream["state"] = "disabled"

    def UpdateChart(self):        
        self.chartMain.ax.clear()
        self.chartMain.ax.plot(self.data.x, self.data.y, '-', dash_capstyle='projecting')
        self.chartMain.ax.grid(color='b', linestyle='-', linewidth=0.2)
        labels = ['TGS-2600', 'TGS-2611', 'MQ-3', 'TGS-822', 'MQ-9', 'MQ-135']
        self.chartMain.ax.legend(labels, prop={'size':6})
        self.chartMain.ax.set_ylabel('Data Sensor (mV)')
        self.chartMain.ax.set_xlabel('Time (s)')
        self.chartMain.fig.canvas.draw()
        if self.serial.threading:
            self.root.after(250, self.UpdateChart)

    def UpdateTime(self):
        t_flush = int(self.clicked_flush.get())
        t_sample = int(self.clicked_sample.get())
        t_purge = int(self.clicked_purge.get())
        if time.perf_counter() < (self.refTime + t_flush):
            self.serial.ser.write(bytes('P', 'UTF-8'))

        elif time.perf_counter() < (self.refTime + t_flush + t_sample):
            self.serial.ser.write(bytes('S', 'UTF-8'))

        elif time.perf_counter() < (self.refTime + t_flush + t_sample + t_purge):
            self.serial.ser.write(bytes('P', 'UTF-8'))

        elif time.perf_counter() > (self.refTime + t_flush + t_sample + t_purge):
            self.stop_stream() 
    
        if self.serial.threading:
            self.root.after(250, self.UpdateTime)  
        


class PlotData():
    def __init__(self, root, serial, data):
        self.root = root
        self.serial = serial
        self.data = data
        self.frame = LabelFrame(self.root, text="Plotting Data", padx = 5, pady = 5, bg='#fff')
        self.CreatFig()
    
    def OpenPlot(self):        
        self.frame.grid(padx=5, columnspan = 9,sticky = NW)
        self.chart.get_tk_widget().grid(column=0, row=10, columnspan=20, rowspan=20)
        self.chart.get_tk_widget().grid_remove()

    def ClosePlot(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.destroy()
    
    def CreatFig(self):
        ########## Plot Set Up ##########         
        self.fig = plt.Figure(figsize=(7,5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.chart = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.chart.get_tk_widget().grid(column=0, row=10, columnspan=20, rowspan=20)
    



if __name__ == "__main__":
    RootGUI()
    ComGUI()
    ConnGUI()
    PlotData()