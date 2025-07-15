import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import  os
from version24 import process_and_plot
from PIL import  Image , ImageTk

class TradingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Trading Chart App")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        self.minsize(800,500)
        self.maxsize(1200,900)

        # Logo icon
        logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
        logo_icon = ImageTk.PhotoImage(Image.open(logo_path))
        self.iconphoto(False, logo_icon)
        self.after(250, lambda: self.iconphoto(False, logo_icon))

        # Variables for user input
        self.csv_path = ''
        self.ma_period1 = ctk.StringVar(value="20")  # Moving Average 1
        self.ma_period2 = ctk.StringVar(value="50")  # Moving Average 2
        self.macd_short = ctk.StringVar(value="12")
        self.macd_long = ctk.StringVar(value="26")
        self.macd_signal = ctk.StringVar(value="9")
        self.stochastic_k = ctk.StringVar(value="14")
        self.stochastic_d = ctk.StringVar(value="3")
        self.stochastic_smoothing = ctk.StringVar(value="3")
        self.indicators = {
            "moving_average1": tk.BooleanVar(value=False),
            "moving_average2": tk.BooleanVar(value=False),
            "macd": tk.BooleanVar(value=False),
            "stochastic": tk.BooleanVar(value=False)   
        
        }
        
        self.balance = ctk.StringVar(value="100")
        self.leverage = ctk.StringVar(value="1")
        self.month = ctk.StringVar(value="1")
        self.rr = ctk.StringVar(value="1")
        self.stoploss = ctk.StringVar(value="5")
        self.risk = ctk.StringVar(value="1")
        
        self.resualt_respone1 = ctk.StringVar(value=3)
        self.resualt_respone2 = ctk.IntVar(value=4)
        self.resualt_respone3 = ctk.IntVar(value=5)
        self.resualt_respone4 = ctk.IntVar(value=6)
        self.resualt_respone5 = ctk.IntVar(value=7) 

        # Layout
        self.create_widgets()

    def create_widgets(self):
        #spinbox for the session
        self.session = ctk.CTkComboBox(self,values=['Tokyo','NewYork','Sydney','London'],border_color="#404040",
                        fg_color="#0093E9",dropdown_hover_color="#404040",
                        button_hover_color="#404040",command=self.browse_year).place(x= 650 ,y= 15)
        
          #RR entry
        ctk.CTkLabel(self,text='RR', font=('arial', 15, 'bold')).place(x= 650,y= 70)
        ctk.CTkEntry(self,textvariable=self.rr).place(x= 650,y= 100)
        
        #stoploss entry
        ctk.CTkLabel(self,text='Stoploss', font=('arial', 15, 'bold')).place(x= 650,y= 150)
        ctk.CTkEntry(self,textvariable=self.stoploss).place(x= 650,y= 180)
        
        #risk per trade
        ctk.CTkLabel(self,text='Risk Per Trade', font=('arial', 15, 'bold')).place(x= 650,y= 230)
        ctk.CTkEntry(self,textvariable=self.risk).place(x= 650,y= 260)
        
        #month entry
        ctk.CTkLabel(self,text='Month',font=('arial',15,'bold')).place(x=650,y=310)
        ctk.CTkEntry(self,textvariable=self.month).place(x=650,y=340)
        
        #balance entry
        ctk.CTkLabel(self,text='Balance',font=('arial',15,'bold')).place(x=650,y=390)
        ctk.CTkEntry(self,textvariable=self.balance).place(x=650,y=420)
        
        #leverage entry
        ctk.CTkLabel(self,text='Leverage',font=('arial',15,'bold')).place(x=650,y=470)
        ctk.CTkEntry(self,textvariable=self.leverage).place(x=650,y=500)
        
        # File selection
        ctk.CTkLabel(self, text="Select the year:",).place(x=10, y=15)
        self.year = ctk.CTkComboBox(self,values=['2000', '2001', '2002', '2003', '2004',
                                                        '2005', '2006', '2007', '2008', '2009',
                                                        '2010', '2011', '2012', '2013',
                                                        '2014', '2015', '2016', '2017',
                                                        '2018', '2019', '2020', '2021',
                                                        '2022', '2023', '2024 jan', '2024 feb',
                                                        '2024 mar', '2024 apr', '2024 may', '2024 jun',
                                                        '2024 jul', '2024 aug', '2024 sep'],
                        border_color="#404040",fg_color="#0093E9",dropdown_hover_color="#404040",
                        button_hover_color="#404040",command=self.browse_year).place(x= 160 ,y= 15)
        

        # Moving Average 1
        ctk.CTkCheckBox(self, text="Moving Average 1", variable=self.indicators["moving_average1"]).place(x=10, y=70)
        ctk.CTkEntry(self, textvariable=self.ma_period1, placeholder_text="Period (e.g., 20)").place(x=160, y=70)
        ctk.CTkLabel(self, text="Period 1", font=('arial', 15, 'bold')).place(x=320, y=70)

        # Moving Average 2
        ctk.CTkCheckBox(self, text="Moving Average 2", variable=self.indicators["moving_average2"]).place(x=10, y=120)
        ctk.CTkEntry(self, textvariable=self.ma_period2, placeholder_text="Period (e.g., 50)").place(x=160, y=120)
        ctk.CTkLabel(self, text="Period 2", font=('arial', 15, 'bold')).place(x=320, y=120)

        # MACD
        ctk.CTkCheckBox(self, text="MACD", variable=self.indicators["macd"]).place(x=10, y=190)
        ctk.CTkEntry(self, textvariable=self.macd_short, placeholder_text="Short Period").place(x=160, y=190)
        ctk.CTkEntry(self, textvariable=self.macd_long, placeholder_text="Long Period").place(x=310, y=190)
        ctk.CTkEntry(self, textvariable=self.macd_signal, placeholder_text="Signal Period").place(x=460, y=190)
        ctk.CTkLabel(self, text="Short Period", font=('arial', 15, 'bold')).place(x=170, y=160)
        ctk.CTkLabel(self, text="Long Period", font=('arial', 15, 'bold')).place(x=320, y=160)
        ctk.CTkLabel(self, text="Signal Period", font=('arial', 15, 'bold')).place(x=470, y=160)

        # Stochastic
        ctk.CTkCheckBox(self, text="Stochastic", variable=self.indicators["stochastic"]).place(x=10, y=270)
        ctk.CTkEntry(self, textvariable=self.stochastic_k, placeholder_text="K Period").place(x=160, y=270)
        ctk.CTkEntry(self, textvariable=self.stochastic_d, placeholder_text="D Period").place(x=310, y=270)
        ctk.CTkEntry(self, textvariable=self.stochastic_smoothing, placeholder_text="Smoothing Factor").place(x=460, y=270)
        ctk.CTkLabel(self, text="K Period", font=('arial', 15, 'bold')).place(x=180, y=240)
        ctk.CTkLabel(self, text="D Period", font=('arial', 15, 'bold')).place(x=330, y=240)
        ctk.CTkLabel(self, text="Smoothing Factor", font=('arial', 15, 'bold')).place(x=450, y=240)

        #resualt
        ctk.CTkLabel(self ,text= "Resualt" ,width= 600,height=220,font=('arial', 20, 'bold'),corner_radius=20,fg_color="#404040",justify="center",anchor="n").place(x=10 ,y= 330)
        ctk.CTkLabel(self ,text= "note1" ,font=('arial', 15, 'bold'),justify="center",anchor="n",fg_color="#404040",bg_color="#404040").place(x= 20,y= 360)
        ctk.CTkLabel(self , text= "note2" ,font=('arial', 15, 'bold'),justify="center",anchor="n",fg_color="#404040",bg_color="#404040").place(x= 20,y= 400)
        ctk.CTkLabel(self , text= "note3" ,font=('arial', 15, 'bold'),justify="center",anchor="n",fg_color="#404040",bg_color="#404040").place(x= 20,y= 440)
        ctk.CTkLabel(self , text= "note4" ,font=('arial', 15, 'bold'),justify="center",anchor="n",fg_color="#404040",bg_color="#404040").place(x= 20,y= 480)
        ctk.CTkLabel(self , text= "note5" ,font=('arial', 15, 'bold'),justify="center",anchor="n",bg_color="#404040",fg_color="#404040").place(x= 20,y= 520)
        
        #the number get from the back test
        ctk.CTkLabel(self,text=self.resualt_respone1,font=('arial',15,'bold'),justify="center",anchor="n",bg_color="#404040",fg_color="#404040").place(x= 160,y= 360)
        ctk.CTkLabel(self , text= self.resualt_respone1 ,font=('arial', 15, 'bold'),justify="center",anchor="n",fg_color="#404040",bg_color="#404040").place(x= 160,y= 400)
        ctk.CTkLabel(self , text= self.resualt_respone1 ,font=('arial', 15, 'bold'),justify="center",anchor="n",fg_color="#404040",bg_color="#404040").place(x= 160,y= 440)
        ctk.CTkLabel(self , text= self.resualt_respone1 ,font=('arial', 15, 'bold'),justify="center",anchor="n",fg_color="#404040",bg_color="#404040").place(x= 160,y= 480)
        ctk.CTkLabel(self , text= self.resualt_respone1 ,font=('arial', 15, 'bold'),justify="center",anchor="n",bg_color="#404040",fg_color="#404040").place(x= 160,y= 520)
        
        # Run button
        ctk.CTkButton(self, text="Run", command=self.run_analysis).place(x=780, y=600)

    def session_selected(self,session):
        print(session)
        #place for the setting the function to send the data to final
        
    def run_trade(self):
        #place for the setting the function to send the data to final
        print(self.rr)
        print(self.stoploss)
        print(self.risk)
        
    def browse_year(self,year):
        print(year)
        year_files = {
                    '2000' :os.path.join(os.path.dirname(__file__),"gold csv files/2000.csv"),
                    '2001' :os.path.join(os.path.dirname(__file__),"gold csv files/2001.csv"),
                    '2002' :os.path.join(os.path.dirname(__file__),"gold csv files/2002.csv"),
                    '2003' :os.path.join(os.path.dirname(__file__),"gold csv files/2003.csv"),
                    '2004' :os.path.join(os.path.dirname(__file__),"gold csv files/2004.csv"),
                    '2005' :os.path.join(os.path.dirname(__file__),"gold csv files/2005.csv"),
                    '2006' :os.path.join(os.path.dirname(__file__),"gold csv files/2006.csv"),
                    '2007' :os.path.join(os.path.dirname(__file__),"gold csv files/2007.csv"),
                    '2008' :os.path.join(os.path.dirname(__file__),"gold csv files/2008.csv"),
                    '2009' :os.path.join(os.path.dirname(__file__),"gold csv files/2009.csv"),
                    '2010' :os.path.join(os.path.dirname(__file__),"gold csv files/2010.csv"),
                    '2011' :os.path.join(os.path.dirname(__file__),"gold csv files/2011.csv"),
                    '2012' :os.path.join(os.path.dirname(__file__),"gold csv files/2012.csv"),
                    '2013' :os.path.join(os.path.dirname(__file__),"gold csv files/2013.csv"),
                    '2014' :os.path.join(os.path.dirname(__file__),"gold csv files/2014.csv"),
                    '2015' :os.path.join(os.path.dirname(__file__),"gold csv files/2015.csv"),
                    '2016' :os.path.join(os.path.dirname(__file__),"gold csv files/2016.csv"),
                    '2017' :os.path.join(os.path.dirname(__file__),"gold csv files/2017.csv"),
                    '2018' :os.path.join(os.path.dirname(__file__),"gold csv files/2018.csv"),
                    '2019' :os.path.join(os.path.dirname(__file__),"gold csv files/2019.csv"),
                    '2020' :os.path.join(os.path.dirname(__file__),"gold csv files/2020.csv"),
                    '2021' :os.path.join(os.path.dirname(__file__),"gold csv files/2021.csv"),
                    '2022' :os.path.join(os.path.dirname(__file__),"gold csv files/2022.csv"),
                    '2023' :os.path.join(os.path.dirname(__file__),"gold csv files/2023.csv"),
                    '2024 jan' :os.path.join(os.path.dirname(__file__),"gold csv files/2024 jan.csv"),
                    '2024 feb' :os.path.join(os.path.dirname(__file__),"gold csv files/2024 feb.csv"),
                    '2024 mar' :os.path.join(os.path.dirname(__file__),"gold csv files/2024 mar.csv"),
                    '2024 apr' :os.path.join(os.path.dirname(__file__),"gold csv files/2024 apr.csv"),
                    '2024 may' :os.path.join(os.path.dirname(__file__),"gold csv files/2024 may.csv"),
                    '2024 jun' :os.path.join(os.path.dirname(__file__),"gold csv files/2024 jun.csv"),
                    '2024 jul' :os.path.join(os.path.dirname(__file__),"gold csv files/2024 jul.csv"),
                    '2024 sep' :os.path.join(os.path.dirname(__file__),"gold csv files/2024 aug.csv"),
                    '2024 aug' :os.path.join(os.path.dirname(__file__),"gold csv files/2024 sep.csv"),}

                    #for choosing the file
        if year in year_files:
            self.csv_path = year_files[year]
            ctk.CTkLabel(self,text=f"Selected: {self.csv_path.split('//')[-1]}").place(x=60, y=600)
            if hasattr(self, 'file_label'):
                self.file_label.configure(text=f"Selected: {year}") 
            else:
                self.file_label = ctk.CTkLabel(self, text=f"Selected: {year}")
                self.file_label.place(x=320, y=15)

                    #for reading the file
    def run_analysis(self):
        """Run the analysis and plot the chart."""
        print("runing")
        if not self.csv_path:
            messagebox.showerror("Error", "Please select a CSV file!")
            return

        indicators_config = {}
        analysis_params = {}

        # Check which indicators are selected and pass their parameters
        # Moving Average 1
        if self.indicators["moving_average1"].get():
            analysis_params["moving_average1"] = int(self.ma_period1.get())
    
        # Moving Average 2
        if self.indicators["moving_average2"].get():
            analysis_params["moving_average2"] = int(self.ma_period2.get())

        # MACD
        if self.indicators["macd"].get():
            analysis_params["macd"] = {
                "short_period": int(self.macd_short.get()),
                "long_period": int(self.macd_long.get()),
                "signal_period": int(self.macd_signal.get())
            }

        # Stochastic
        if self.indicators["stochastic"].get():
            analysis_params["stochastic"] = {
                "k_period": int(self.stochastic_k.get()),
                "d_period": int(self.stochastic_d.get()),
                "smoothing_factor": int(self.stochastic_smoothing.get())
        }       
        print("main running")
        # Gather all other necessary values
        # Additional parameters for trading analysis
        analysis_params["balance"] = float(self.balance.get())
        analysis_params["leverage"] = float(self.leverage.get())
        analysis_params["risk"] = float(self.risk.get())
        analysis_params["rr"] = float(self.rr.get())
        analysis_params["stoploss"] = float(self.stoploss.get())
        analysis_params["month"] = int(self.month.get())

        print("end running")
        # Call the process_and_plot function from final.py
        process_and_plot(self.csv_path, analysis_params)
        print('bck')
if __name__ == "__main__":
    app = TradingApp()
    app.mainloop()