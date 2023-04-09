from re import T
import time
from PyQt6 import QtCore, QtWidgets, QtGui, uic 
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWidgets import QMessageBox 
from PyQt6.QtWidgets import QWidget
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import numpy  as np
import pandas as pd
import requests
import sys
import pyqtgraph as pg
import yfinance as yf
import talib
import random
from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium 
import io


"""
Sample StockPriceQuerySystem Demo

main code

Create by LIN, KAI-LUN at NATIONAL TAIPEI UNIVERSITY

2022/06/16
"""


 
class TableModel(QtCore.QAbstractTableModel):
 
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data # 標題
 
    def data(self, index, role):
        # print(role)
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()] # pandas's iloc method
            return str(value)
 
        if role == Qt.ItemDataRole.TextAlignmentRole:          
            return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignHCenter
            # return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignLeft
         
        if role == Qt.ItemDataRole.BackgroundRole and (index.row()%2 == 0):
            return QtGui.QColor('#fff2d5')  # 單欄顏色
 
    def rowCount(self, index):
        return self._data.shape[1]
 
    def columnCount(self, index):
        return self._data.shape[1]
 
    # Add Row and Column header
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        # ItemDataRole是通過其內部的各個Role對每一項都作出相應的Role操作從而更完美地將想要的數據以更完美的形式呈現出來。
        # model中的角色role有多個，但是常用的就幾個。
        # DisplayRole ：主要用於以文本的形式顯示數據。
        if role == Qt.ItemDataRole.DisplayRole: # more roles
            # print('role = ', role)
            # print('section = ', section) 
            # print('orientation = ', orientation) # 方向 Orientation.Horizontal
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
 
            # if orientation == Qt.Orientation.Vertical:
            #     return str(self._data.index[section])

class AnotherSubWindowWebsite(QWidget):
    # create a customized signal 
    submitted = QtCore.pyqtSignal(str) # "submitted" is like a component name 
 
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('../GUI/PyQt_Webscrapping_Stock_Website_widget.ui', self)
        # self.setGeometry(600, 200, 700, 500)
        
        
        # Signal
        self.pushButton_websiteBack.clicked.connect(self.on_submit)
        self.comboBox_news.currentIndexChanged.connect(self.show_website)
        self.pushButton_websiteReload.clicked.connect(self.show_website)
        # self.pushButton_address.clicked.connect(self.findLatLng)
        # self.comboBox_mapChoose.currentIndexChanged.connect(self.show_map)
        
    # Slot -- of Another Window (small one)
    def passInfoWebsite(self, website, company):
        print('transmit website = ', website)
        print('transmit company = ', company)
        self.company = company
        self.website = website
        self.label_websiteCompanyName.setText(str(company))
        self.show_website()
        
    def show_website(self):
        # url = 'https://new.ntpu.edu.tw/'
        # url = "https://" + self.lineEdit_url.text()
        if str(self.website) == '':
            print('No Such Stock Website')
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Stock\'s Website Information: ")
            dlg.setText("Not exist Stock\'s Website!!!")
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
            buttonY = dlg.button(QMessageBox.StandardButton.Yes)
            buttonY.setText('OK')
            dlg.setIcon(QMessageBox.Icon.Critical)
            button = dlg.exec()
            self.progressBar_scapping_stock_data.setValue(100)
            return
        else:
            pass
        
        
        if self.comboBox_news.currentText() == '中央社':
            url = 'https://www.cna.com.tw/search/hysearchws.aspx?q='
            url = url + str(self.company)
        elif self.comboBox_news.currentText() == '自由時報':
            url = 'https://search.ltn.com.tw/list?keyword=' # 自由
            url = url + str(self.company)
        elif self.comboBox_news.currentText() == '中國時報':
            url = 'https://www.chinatimes.com/search/' # 中時
            url = url + str(self.company)
        elif self.comboBox_news.currentText() == '聯合報':
            url = 'https://udn.com/search/word/2/' # udn
            url = url + str(self.company)
        elif self.comboBox_news.currentText() == '經濟日報':    
            url = 'https://money.udn.com/search/result/1001/'
            url = url + str(self.company)
        else:
            url = str(self.website)
        
        
        self.webView = QWebEngineView()
        self.webView.load(QUrl(url))
        # browser.show()
        # clear the current widget in the verticalLayout before adding one
        if self.verticalLayout.itemAt(0) : # if any existing widget
            self.verticalLayout.itemAt(0).widget().setParent(None)
        # self.webView.setBackgroudColor('blue')
        self.verticalLayout.addWidget(self.webView)
        
        
    
    def on_submit(self):
        self.close()




class AnotherSubWindowMap(QWidget):
    # create a customized signal 
    submitted = QtCore.pyqtSignal(str) # "submitted" is like a component name 
 
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('../GUI/PyQt_Webscrapping_Stock_Map_widget.ui', self)
        # self.setGeometry(600, 200, 700, 500)
        
        tiles_choose = ['Stamen Terrain',
                        'cartodb positron',
                        'openstreetmap',
                        'cartodbpositron',
                        'stamentoner',
                        'stamenwatercolor',
                        'CartoDB Positron',
                        'cartodbdark_matter']
        
        self.comboBox_mapChoose.addItems(tiles_choose)
        # self.searchStockBasicInfo()
        # Signal
        self.pushButton_goBackMap.clicked.connect(self.on_submit)
        # self.pushButton_address.clicked.connect(self.findLatLng)
        self.comboBox_mapChoose.currentIndexChanged.connect(self.show_map)
        
    # Slot -- of Another Window (small one)
    def passInfoMap(self, coordinate, company):
        print('transmit coordinate = ', coordinate)
        print('transmit company = ', company)
        self.company = company
        self.coordinate = coordinate
        self.show_map(coordinate=coordinate)
        
    def show_map(self, coordinate):
        # https://blog.yeshuanova.com/2017/10/python-visulization-folium/
        
        coordinate=self.coordinate
        company=self.company
        
        tilesName = self.comboBox_mapChoose.currentText()
        # tilesIndex = self.comboBox_mapChoose.currentIndex()
      
        
        
        m = folium.Map(
        tiles=str(tilesName),
        zoom_start=16,
        location=coordinate
        )
        # save map data to data object
        data = io.BytesIO()
        myIcon = folium.CustomIcon('C:/Documents/python_file/practice/GUI_Icon/Company/icons8-company-96.png', 
                                   icon_size=(40,40),
                                   icon_anchor = (15, 30))
        folium.Marker(location = coordinate, icon=myIcon,
                      popup='<h3 style="color:blue;">'+str(company)+'</h3>',
                      tooltip='<strong>Click here to see more information</strong>' 
                      ).add_to(m) # 插入圖標
        folium.LatLngPopup().add_to(m) # 在地圖上任意點按右鍵，就會跳出popup顯示該點的座標
        m.save(data, close_file = False)
 
        webView = QWebEngineView()  # a QWidget
        webView.setHtml(data.getvalue().decode())
 
        # clear the current widget in the verticalLayout before adding one
        if self.verticalLayout_addressMap.itemAt(0) : # if any existing widget
            self.verticalLayout_addressMap.itemAt(0).widget().setParent(None)
        # add a widget with webview inside the vertivalLayout component
        self.verticalLayout_addressMap.addWidget(webView, 0) # at position 0
        self.label_address_of_map.setText(str(company))
    
    def on_submit(self):
        self.close()


class AnotherWindow(QWidget):
    # create a customized signal 
    submitted = QtCore.pyqtSignal(str) # "submitted" is like a component name 
 
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('../GUI/PyQt_Webscrapping_Stock_Basic_Infomation_widget.ui', self)
        # self.setGeometry(600, 200, 700, 500)
  
        # self.searchStockBasicInfo()
        # Signal
        self.pushButton_goBack.clicked.connect(self.on_submit)
        self.pushButton_address.clicked.connect(self.findLatLng)
        self.pushButton_goWebsite.clicked.connect(self.findWebite)
        
        
    # Slot -- of Another Window (small one)
    def passInfo(self, stockid):
        print('transmit stock_no = ', stockid)
        
        
        self.searchStockBasicInfo(stockid=stockid)
    
    def call_subWinMap(self, coordinate, company): # 6/15 adds
        self.anotherwindowmap = AnotherSubWindowMap()
        # pass information to sub-window()
        self.anotherwindowmap.passInfoMap(coordinate = coordinate, company= company)
        # ready to accept a singal from sub-window
        self.anotherwindowmap.show()
    
    def call_subWinWebsite(self, website, company): # 6/15 adds
        self.anotherwindowwebsite = AnotherSubWindowWebsite()
        # pass information to sub-window()
        self.anotherwindowwebsite.passInfoWebsite(website=website, company= company)
        # ready to accept a singal from sub-window
        # self.anotherwindow.submitted.connect(self.update_info)
        self.anotherwindowwebsite.show()
        
        
    def searchStockBasicInfo(self, stockid):
        stock_no = stockid
        url = 'https://tw.stock.yahoo.com/quote/'+ str(stock_no)+ '.TW/profile'

        response = requests.get(url)
        soup1 = BeautifulSoup(response.text, 'html.parser')
        title_results = soup1.find_all('span', class_='')
        soup2 = BeautifulSoup(response.text, 'html.parser')
        data_results = soup2.find_all('div', class_='Py(8px) Pstart(12px) Bxz(bb)')


        data = []
        for i in range(len(data_results)):
            data.append(str(data_results[i])[42:-6])
        # print(data)

        company_name = data[0]
        company_name_EG = data[2]
        establishment_time = data[4]
        phone = data[5]
        market_time = data[6]
        industry = data[8]
        # website = str(data[9])[51:-75]
        website = str(data[9])[51:].partition('"')[0]
        chairman  = data[10]
        general_manager = data[12]
        share_capital = data[14]
        accounting_firm = data[15]
        ordinary_share_capital = data[16]
        address  = data[17]
        market = data[19]
        main_service = data[22]
        
        stock_hold_by_directors_supervusors = data[20]
        market_value = data[18]
        spokeman = data[1]
        vice_spokeman = data[3]
        fax_phone = data[7]
        email = data[11]
        stock_transfer_agent = data[13]
        group = data[21]
        
        self.company_name = company_name
            
        self.label_company_name.setText(str(company_name))
        self.label_company_name_EG.setText(str(company_name_EG))
        self.label_establishment_time.setText(str(establishment_time))
        self.label_market_time.setText(str(market_time))
        self.label_industry.setText(str(industry))
        self.label_chairman.setText(str(chairman))
        self.label_general_manager.setText(str(general_manager))
        self.label_share_capital.setText(str(share_capital))
        self.label_ordinary_share_capital.setText(str(ordinary_share_capital))
        self.label_main_service.setText(str(main_service))
        
        self.label_phone.setText(str(phone))
        self.label_website.setText(str(website))
        self.label_accounting_firm.setText(str(accounting_firm))
        self.label_address.setText(str(address))
        self.label_main_service.setText(str(main_service))
        self.label_market.setText(str(market))
        
        self.label_market_value.setText(str(market_value))
        self.label_stock_hold_by_directors_supervusors.setText(str(stock_hold_by_directors_supervusors))
        self.label_spokeman.setText(str(spokeman))
        self.label_vice_spokeman.setText(str(vice_spokeman))
        self.label_fax_phone.setText(str(fax_phone))
        self.label_stock_transfer_agent.setText(str(stock_transfer_agent))
        self.labe_group.setText(str(group))
        self.label_email.setText(str(email))
        
        self.address=address
        self.website=website
    
    def findLatLng(self):
        # My personal Google API KEY (Please use your personal Google API KEY !) 
        # 參考：https://www.youtube.com/watch?v=d1QGLwie9YU
        API_KEY = 'AIzaSyBzg-0-q4iXQKTbCaZisbMAE1gnK9Lf8JE'
        address = self.label_address.text()
        # address = 'Clifton House,75 Fort Street, PO Box 1350, Grand Cayman KY1'
        params = {
            'key': API_KEY,
            'address': address
        }

        base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

        response = requests.get(base_url, params=params).json()

        # response.keys()

        if response['status'] == 'OK':
            location = response['results'][0]['geometry']['location']
            lat =  response['results'][0]['geometry']['location']['lat']
            lng =  response['results'][0]['geometry']['location']['lng']
        else:
            # except AttributeError:
            print('No Such Stock Address')
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Stock\'s Address Information: ")
            dlg.setText("Not exist Stock\'s Address!!!")
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
            buttonY = dlg.button(QMessageBox.StandardButton.Yes)
            buttonY.setText('OK')
            dlg.setIcon(QMessageBox.Icon.Critical)
            button = dlg.exec()
            self.progressBar_scapping_stock_data.setValue(100)
            return
            # pass
        print(lat, lng)
        self.coordinate=(lat, lng)
        self.call_subWinMap(coordinate=self.coordinate, company=self.company_name)
        
    def findWebite(self):
        self.call_subWinWebsite(website=self.website, company=self.company_name)
        
    
    def on_submit(self):
        # emit a signal and pass data along
        # self.submitted.emit(self.lineEdit_sub_mu.text()) 
        self.close()
        
        

class MainWindow(QtWidgets.QMainWindow):
 
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('..\GUI\PyQt_Webscrapping_Stock_Table_graph_finalProject_test.ui', self)
        
        
        self.comboBox_timeInterval.setcurrentIndex = 0
        self.timeRenew()                  
        # self.urlSearch()
        
        # 6/5 adds timer
        # self.timer = QTimer()
        # timeInterval = 60 * 60000 /60 # 60/60 分鐘
        # self.timer.setInterval(timeInterval)
        # self.timer.start()
        
        
        
        # 6/6 adds
        # win = self.graphicsView
        # # win2 = self.graphicsView_volumn
        
        # self.t2 = win.addPlot(title = '成交量(股)')
        # self.timer=QTimer(self)
        # self.timer.timeout.connect(self.currentTime)
        # Timer(1, self.currentTime())
        self.currentTime()
        
        # Signals
        self.lineEdit_stock_no.returnPressed.connect(self.dataProcess)
        self.pBut_exit.clicked.connect(self.close)
        
           
        # 6/3 adds
        self.proxy = pg.SignalProxy(self.plt1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.proxy2 = pg.SignalProxy(self.plt2.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        
        # self.timer.timeout.connect(self.timeRenew) # emit every timeInterval millisecond
        
        # 6/7 adds
        self.comboBox_timeInterval.currentIndexChanged.connect(self.timeRenew)
        self.comboBox_index.currentIndexChanged.connect(self.replot)
        
        # 6/12 adds
        # self.graphicsView.doubleClicked.connect(self.call_subWin)
        self.pushButton_callSubwindow.clicked.connect(self.call_subWin)
        

    # Slots    
    def call_subWin(self, mi): # 6/12 adds
        self.anotherwindow = AnotherWindow()
        # pass information to sub-window
        
        self.anotherwindow.passInfo(stockid = self.lineEdit_stock_no.text())
        # print('paperid = ',  self.df.iloc[mi.row(), 0] )
        # ready to accept a singal from sub-window
        # self.anotherwindow.submitted.connect(self.update_info)
        self.anotherwindow.show()
        
             
    def stockPlot(self):
       # 畫圖*************************************
        color = []

        for i in np.array(self.y_spread):
            if i>= 0:
                color.append('red')
            else:
                color.append('green')
               
             
        # print(color)
        
        
        win1 = self.graphicsView
        win2 = self.graphicsView_volume


        # 讓self.plt1/2 不要被重複加入
        try:
            print(self.plt1)
        except:
            self.plt1 = win1.addPlot(title = '技術分析')
            win1.nextRow()
            self.plt2 = win2.addPlot(title = '成交量(股)')
        
        # self.x = np.arange(len(deal_info)
        self.x = np.arange(len(self.df))
        self.lr = pg.LinearRegionItem(values=[self.x[0], self.x[-1]])
        
        self.plt1.clear()
        self.plt2.clear()
        
        # 6/4 adds
        self.vb = self.plt1.vb
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plt1.addItem(self.vLine, ignoreBounds=True)
        self.plt1.addItem(self.hLine, ignoreBounds=True)
        
        # self.vLine2 = pg.InfiniteLine(angle=90, movable=False)
        # self.hLine2 = pg.InfiniteLine(angle=0, movable=False)
        # self.plt2.addItem(self.vLine2, ignoreBounds=True)
        # self.plt2.addItem(self.hLine2, ignoreBounds=True)


    
        # 參考顏色放置 https://stackoverflow.com/questions/70992950/set-multiple-colors-for-bargraphitem-in-pyqtgraph
        
        bg = pg.BarGraphItem(x=self.x, y=(self.y_open+self.y_close)/2, height= self.y_spread, width=0.6, brushes = color)
        
        self.plt1.addItem(bg)
        
        # self.plt1.getAxis('bottom').setTicks([[(i, date[i]) for i in x[::2]]])
        # self.graphicsView.getAxis('bottom').setTicks([[(i, date[i]) for i in x[::2]]])
        
        print(np.array(self.y_max)[0], np.array(self.y_min)[0])
        # print(x)
        mid = (np.array(self.y_max)+np.array(self.y_min))/2
        # print(mid)
        # highest_and_lowest_prices = pg.ErrorBarItem(x=self.x, y= mid, top=np.array(self.y_max)-np.array(self.y_min), bottom=np.array(self.y_max)-np.array(self.y_min), beam=0.5)
        highest_and_lowest_prices = pg.ErrorBarItem(x=self.x, y= mid, top=(np.array(self.y_max)-np.array(self.y_min))/2, bottom=(np.array(self.y_max)-np.array(self.y_min))/2, beam=0.5)
        # pg.ErrorBarItem : y:中點高度，top:最高點到終點距離，bottom:中點到最低點距離(取正)
        
        self.plt1.addItem(highest_and_lowest_prices)
        
        
        
        
        print('combobox_index = ', self.comboBox_index.currentIndex())
        # if self.comboBox_index.currentIndex() == 0:
        #     stock_volumn = pg.BarGraphItem(x = self.x, height = self.y_volumn, width=0.6, brushes = color)
        # elif self.comboBox_index.currentIndex() == 1:
        #     pen2 = pg.mkPen(color=(250,128,114), width = 2.5)
        #     self.plt2.plot(self.data2, pen=pen2)
        #     stock_volumn = pg.PlotItem(x= self.x , y = RSI(Close=self.y_close, period=12  )) 
        # else:
        #     stock_volumn = pg.BarGraphItem(x = self.x, height = self.y_volumn, width=0.6, brushes = color)
        
       
        
        # # stock_volumn = pg.BarGraphItem(x = x, height = number_of_shares, width=0.6, brushes = color)
        # try:
        #     self.plt2.addItem(stock_volumn)
        # except:
        #     print('**')
        
        # pg getAxis 客製化
        # https://zhuanlan.zhihu.com/p/385851847
        # for i in range(81, 95):
        #     time.sleep(random.uniform(0,0.3))
        #     self.progressBar_scapping_stock_data.setValue(i)
            
        if self.comboBox_timeInterval.currentIndex() == 0: #'日線'
            t = round(self.n_days / 7)
        elif self.comboBox_timeInterval.currentIndex() == 1: # '周線'
            t = round(self.n_days / 50)
        else:
            t = round(self.n_days / 250) # '月線'
            
        
        self.plt2.getAxis('bottom').setTicks([[(i, self.date.strftime('%Y-%m-%d')[i]) for i in self.x[::t]]]) # 每200筆
        # self.plt2.xticks(rotations=15)
        self.plt2.getAxis('bottom').setPen('#CDF0EA')
        # self.plt2.getAxis('bottom').rotate(45)
        self.plt2.setXRange(self.x[0], self.x[-1])
        self.plt1.setXLink(self.plt2) # plt1的x坐标轴与plt2共享
        self.plt1.getAxis('bottom').setTicks([[(i, self.date.strftime('%Y-%m-%d')[i]) for i in self.x[::t]]]) # 每200筆
        
        
    
        
        # 畫MA MACD RSI
        pen_sma5 = '#BDE6F1' # blue
        pen_sma20 = 'orange'
        pen_sma60 = '#019267' #green
        self.plt1.plot(self.x[(len(self.x)-len(self.sma5_drop_nan)):], self.sma5_drop_nan, \
            pen=pen_sma5)
        self.plt1.plot(self.x[(len(self.x)-len(self.sma20_drop_nan)):], self.sma20_drop_nan, \
            pen=pen_sma20)
        self.plt1.plot(self.x[(len(self.x)-len(self.sma60_drop_nan)):], self.sma60_drop_nan, \
            pen=pen_sma60)
        
        
        if self.comboBox_index.currentIndex() == 0: # 成交量
            stock_volumn = pg.BarGraphItem(x = self.x, height = self.y_volumn, width=0.6, brushes = color)
        elif self.comboBox_index.currentIndex() == 1: # MACD
            pen2 = pg.mkPen(color=(250,128,114), width = 2.5)
            # self.plt2.plot(self.data2, pen=pen2)
            # stock_volumn = pg.PlotItem(x= self.x , y = RSI(Close=self.y_close, period=12  )) 
            self.plt2.plot(self.x[(len(self.x)-len(self.macd_drop_nan)):], self.macd_drop_nan, \
            pen=pen_sma5)
            self.plt2.plot(self.x, np.zeros((len(self.x))), \
            pen='white')
            self.plt2.setYRange(min(self.macd_drop_nan),max(self.macd_drop_nan))
        else:  # RSI
            # stock_volumn = pg.BarGraphItem(x = self.x, height = self.y_volumn, width=0.6, brushes = color)
            self.plt2.plot(self.x[(len(self.x)-len(self.rsi5_drop_nan)):], self.rsi5_drop_nan, \
            pen=pen_sma5)
            self.plt2.plot(self.x[(len(self.x)-len(self.rsi10_drop_nan)):], self.rsi10_drop_nan, \
            pen=pen_sma20)
            self.plt2.setYRange(min(self.rsi10_drop_nan), max(self.rsi10_drop_nan))
       
        
        # stock_volumn = pg.BarGraphItem(x = x, height = number_of_shares, width=0.6, brushes = color)
        try:
            self.plt2.addItem(stock_volumn)
        except:
            print('**')
        
        
        
        
        
        # if self.comboBox_index.currentIndex() == 1: # MACD
        #     self.plt2.plot(self.x[(len(self.x)-len(self.macd_drop_nan)):], self.macd_drop_nan, \
        #     pen=pen_sma5)
        # elif self.comboBox_index.currentIndex() == 2: # RSI
        #     self.plt2.plot(self.x[(len(self.x)-len(self.rsi5_drop_nan)):], self.rsi5_drop_nan, \
        #     pen=pen_sma5)
        #     self.plt2.plot(self.x[(len(self.x)-len(self.rsi10_drop_nan)):], self.rsi10_drop_nan, \
        #     pen=pen_sma20)
        # else: # '成交量'
        #     1
    
        for i in range(81, 100):
            time.sleep(random.uniform(0,0.3))
            self.progressBar_scapping_stock_data.setValue(i)   
        
        self.progressBar_scapping_stock_data.setValue(100)
        
    
    
    
    def replot(self):
        self.plt1.clear()
        self.plt2.clear()
        
        self.stockPlot()
        self.mouseMoved() # 讓下圖標示的 量 RSI MACD 值得以更新
        
        
        
    def mouseMoved(self, point): # returns the coordinates in pixels with respect to the PlotWidget
        # print('p = ', point)
        pos = point[0]
        print('plos = ', pos)
        
        if self.plt1.sceneBoundingRect().contains(pos):
              mousePoint = self.vb.mapSceneToView(pos)
              index = int(mousePoint.x())
              print('index = ' ,index)
            #   if index > 0 and index < len(self.y_money):
            #     # self.label.setText("<span style='font-size: 14pt'>月/日/年=%s,   <span style='color: red'>開盤價=%0.2f</span>,   <span style='color: green'>收盤價=%0.2f</span>" % (self.strs[index], self.y_open[index], self.y_close[index]))
            #   self.vLine.setPos(mousePoint.x())
            #   self.hLine.setPos(mousePoint.y())
            
        # 6/11 add
        if self.plt2.sceneBoundingRect().contains(pos):
              mousePoint = self.vb.mapSceneToView(pos)
              index = int(mousePoint.x())
              print('index = ' ,index)
        #  
              
        
        # 設定對應到某日
        
        
        p = self.vb.mapSceneToView(pos) # convert to the coordinate of the plot
        self.vLine.setPos(p.x()) # set position of the verticle line
        self.hLine.setPos(p.y()) # set position of the horizontal line
        
        if p.x() > len(self.y_close)-1:
            int_px = int(len(self.y_close))-1 # index of time
        elif p.x() < 0:
            int_px = 0 # index of time
        # elif p.x() == 0:
        #     int_px = 0 # index of time
        else: 
            int_px = int(round(p.x(), 0)) # index of time
        # int_px = int(round(p.x(), 0)) # index of time
        
        
        # self.label_Close.setText(str(round(p.x(), 0))) 
        # self.label_Close.setText(str(format(self.y_close[int_px], '0.2f')))
        # print('close = ',self.y_close[int_px])
        # self.label_TradeNumber.setText(str(format(int(self.y_volumn[int_px]), ',' )))
        self.label_Date.setText(str(self.date.strftime('%Y-%m-%d')[int_px]))
        
        self.label_y_max.setText(str(format(self.y_max[int_px], '0.2f')))
        self.label_y_open.setText(str(format(self.y_open[int_px], '0.2f')))
        self.label_y_min.setText(str(format(self.y_min[int_px], '0.2f')))
        self.label_y_close.setText(str(format(self.y_close[int_px], '0.2f')))
        self.label_y_volumn.setText(str(format(int(self.y_volumn[int_px]), ',' )))
        self.label_y_spread.setText(str(format(self.y_spread[int_px], '0.2f')))
        
        try:
            self.label_MA5.setText(str(format(self.sma5_drop_nan[int_px], '0.2f')))
        except:
            self.label_MA5.setText(str('-'))
        
        # 標記 MA 值
        if int_px+1 > self.sma20.isnull().sum():
            self.label_MA20.setText(str(format(self.sma20[int_px], '0.2f')))
        else:
            self.label_MA20.setText('-')
            
        if int_px+1 > self.sma60.isnull().sum():
            self.label_MA60.setText(str(format(self.sma60[int_px], '0.2f')))
        else:
            self.label_MA60.setText('-')
            
        
        # 標記 RSI MACD 值
        if self.comboBox_index.currentIndex() == 0: # 成交量
            self.label_lower1.setText('量 '+str(int(self.y_volumn[int_px])))
            # self.label_lower2.setText('MV5 '+str(int(self.mv5[int_px])))
            print('x ',len(self.x))
            print('ma20 ',len(self.mv20))
            if int_px+1 > 5-1:
                self.label_lower2.setText('MV5 '+str(int(self.mv5[int_px])))
            else:
                 self.label_lower2.setText('MV5 '+'-')
                 
            if int_px+1 > self.sma20.isnull().sum():
                self.label_lower3.setText('MV20 '+str(int(self.mv20[int_px])))
            else:
                self.label_lower3.setText('MV20 '+'-')
            
        elif self.comboBox_index.currentIndex() == 1: # MACD
            # self.label_lower2.setText(str(format(self.macd[int_px], '0.2f')))
            
            if int_px+1 > self.macd.isnull().sum():
                self.label_lower1.setText('MACD '+str(format(self.macd[int_px], '0.2f')))
            else:
                self.label_lower1.setText('MACD  '+ '--')
                self.label_lower2.setText('')
                self.label_lower3.setText('')
            
        else:  # RSI
            # self.label_lower3.setText(str(format(self.y_volumn[int_px], '0.2f')))
            
            if int_px+1 > self.rsi5.isnull().sum():
                self.label_lower1.setText('RSI5 '+str(format(self.rsi5[int_px], '0.2f')))
            else:
                self.label_lower1.setText('RSI5  '+ '--')
                
            if int_px+1 > self.rsi10.isnull().sum():
                self.label_lower2.setText('RSI10 '+str(format(self.rsi10[int_px], '0.2f')))
            else:
                self.label_lower2.setText('RSI10  '+ '--')    
                
                
            self.label_lower3.setText('')
        
    
    def timeRenew(self):
        # https://ithelp.ithome.com.tw/articles/10235251
        different_days = []
        different_YearMonthDay = []
        # self.comboBox_index.currentIndex()
        print('comboBox_timeInterval_index = ', self.comboBox_timeInterval.currentIndex())
        if self.comboBox_timeInterval.currentIndex() == 0: # 日線
            n_days = 183
            for i in range(1, n_days+1):  # 只取年月
                different_days.append((datetime.now() - timedelta(days = i)).strftime('%Y%m%d')[:-2])
                different_YearMonthDay.append((datetime.now() - timedelta(days = i)).strftime('%Y-%m-%d'))
        elif self.comboBox_timeInterval.currentIndex() == 1: # 周線
            n_days =  27*30
            for i in range(1, n_days+1):  # 只取年月
                different_days.append((datetime.now() - timedelta(days = i)).strftime('%Y%m%d')[:-2])
                different_YearMonthDay.append((datetime.now() - timedelta(days = i)).strftime('%Y-%m-%d'))
        else:                                              # 月線
            n_days = 10*365
            for i in range(1, n_days+1):  # 只取年月
                different_days.append((datetime.now() - timedelta(days = i)).strftime('%Y%m%d')[:-2])
                different_YearMonthDay.append((datetime.now() - timedelta(days = i)).strftime('%Y-%m-%d'))
        self.n_days = n_days
        # self.label_todayTime.setText(datetime.now().strftime('%Y-%m-%d'))
        # 算一期有幾天
        
        
        #**#
        
        
        # for i in range(1, n_days+1):  # 只取年月
        #     different_days.append((datetime.now() - timedelta(days = i)).strftime('%Y%m%d')[:-2])
        # print(different_days) # '20220605' 山不轉路轉，datetime比time好用太多，以後不要使用time(很難相減時間) 
        
        # 取different_days(array)中非重複的年月(字串)
        # 算一期有幾天
        self.different_days = np.unique(different_days) # '%Y%m'
        self.different_YearMonthDay = np.unique(different_YearMonthDay) # '%Y-%m-%d'
        # self.different_days, self.counts = np.unique(different_days, return_counts=True)
        # print(self.different_days) # 寫了一天半終於搞定時間嘞 Yo~
        #***#
        
        for i in range(71, 80):
            time.sleep(random.uniform(0,0.3))
            self.progressBar_scapping_stock_data.setValue(i)
        
        # 完成後要上
        # self.dataProcess(diffDays = self.different_days)
        self.dataProcess()
        
        
       
   
        
        
    def dataProcess(self):
        # print(self.first_month)
        # print(self.last_month)
        # self.year_day
        # diffDays = self.different_days
        
        stock_no = self.lineEdit_stock_no.text()
        url = "https://www.twse.com.tw/exchangeReport/FMNPTK?response=html&stockNo="+stock_no
        # year = self.lineEdit_year.text()
        # month = self.lineEdit_month.text()
        # year = self.searchYear
        # first_month = self.searchFisrtMonth
        # last_month = self.searchLastMonth
        
        
       
        
        # url = []
        # month = [first_month, last_month]
         
        # Month1_12 = np.linspace(1,12, 12, dtype=int)
        
        # url_ = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=html&date='
        
        # '2330.TW'
        for i in range(70):
            time.sleep(random.uniform(0,0.3))
            self.progressBar_scapping_stock_data.setValue(i)
        
        if self.comboBox_timeInterval.currentIndex() == 0: # 日線
            df = yf.download(str(stock_no)+'.TW', start=str(self.different_YearMonthDay[0]), end = str(self.different_YearMonthDay[-1], threads=False))
        elif self.comboBox_timeInterval.currentIndex() == 1: # 周線
            df = yf.download(str(stock_no)+'.TW', start=str(self.different_YearMonthDay[0]), end = str(self.different_YearMonthDay[-1]), \
                 interval='1wk')
            df = df.dropna()
        else: # 月線
            df = yf.download(str(stock_no)+'.TW', start=str(self.different_YearMonthDay[0]), end = str(self.different_YearMonthDay[-1]), \
                interval='1mo')
            df = df.dropna()
        # for i in range(70):
        #     time.sleep(random.uniform(0,0.3))
        #     self.progressBar_scapping_stock_data.setValue(i)
        # time.sleep(random.uniform(5, 8))
        
        # for i in range(51, 70):
        #     time.sleep(random.uniform(0,0.3))
        #     self.progressBar_scapping_stock_data.setValue(i)
            
        print(df.head)
        print(type(df)) # pandas.core.frame.DataFrame
                
        # url = url_ + stock_no
        
        #***#
        different_time = self.different_days
        # 試過用for loop處裡時間計數，太複雜，放棄改用datetime
        
        res = requests.get(url, cert = '', timeout=5)
        soup = BeautifulSoup(res.content, 'html.parser')
        stock_name = soup.find("h2")
        

 
 
        # title = soup.find_all("thead")
        # # tmp = title[0].find_all("td")
        # headers = []
        # for i in title[0].find_all("td"):
        #     headers.append(i.text)
         
        # content = soup.find("thead")
        # tmp = content[0].find_all("th")
        # tmp = tmp.find_all('div')
        
        year = '2022'
        month = '05'
        url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=html&date='
        url = url + year + month +'01&stockNo=' + stock_no
        # 20210101&stockNo='
        # url = url + stock_no
        res = requests.get(url, cert = '', timeout=5)
        soup = BeautifulSoup(res.content, 'html.parser')
        # stock_name = soup.find("h2")
        stock_name = soup.find('th')
        
        # 可能會輸入不存在的股票代碼，如果不存在則跳出視窗提示重新輸入代號
        try: 
            stock_name = str(stock_name.contents[1].contents)
        except AttributeError:
            print('No Such Stock Symbol')
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Stock Symbol Information: ")
            dlg.setText("Please choose a correct stock symbol !!!")
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
            buttonY = dlg.button(QMessageBox.StandardButton.Yes)
            buttonY.setText('OK')
            dlg.setIcon(QMessageBox.Icon.Critical)
            button = dlg.exec()
            self.progressBar_scapping_stock_data.setValue(100)
            return
        
        
        # 字串抓取與空白部分問題待改進
        stock_name = stock_name[10:-12].lstrip().rstrip()
        # stock_name = 
        self.label_name.setText(str(stock_name))
        self.df = df
        
        
        
        #***#
        self.model = TableModel(self.df)
        
        # *** 6/16 暫時關掉
        # self.tableView.setModel(self.model)

        # self.tableView.resizeColumnsToContents()
        # ***
        
        # self.x = np.arange(len(deal_info)) # deal_info
        
        
        
        # 梳理資料
        # 
        self.date = df.index # 日期
        # self.number_of_shares = df['Volume'] # 成交股數 
        # self.y_money =  # 成交金額
        self.y_open = df['Open'] # 開盤價
        self.y_max = df['High'] # 最高價
        self.y_min = df['Low'] # 最低價
        self.y_close = df['Close'] # 收盤價
        self.y_spread = df['Close']-df['Open'] # 漲跌價差，收盤價 - 開盤價，不要減反
        self.y_volumn =df['Volume'] # 成交筆數
        
        # self.date = date  # 日期
        # self.number_of_shares = number_of_shares # 成交股數 
        # self.y_money = y_money # 成交金額
        # self.y_open =  y_open   # 開盤價
        # self.y_max = y_max  # 最高價
        # self.y_min = y_min  # 最低價
        # self.y_close = y_close  # 收盤價
        # self.y_spread = y_spread  # 漲跌價差
        # self.y_volumn = y_volumn  # 成交筆數
        
        # 算一期有幾天
        gar_diff_days, self.counts_diff_periods = np.unique(self.date, return_counts=True)
        
        # 計算指標
        print('RSI Series = ', RSI(Close=self.df['Close']))
        print(type(RSI(Close=self.df['Close']))) # <class 'pandas.core.series.Series'>

        # https://pixnashpython.pixnet.net/blog/post/28035316-%E3%80%90talib%E3%80%91python%E4%B8%80%E6%AC%A1%E5%B0%B1%E8%A3%9D%E5%A5%BDtalib%E7%9A%84%E6%96%B9%E6%B3%95%E5%8F%8A%E4%BD%BF%E7%94%A8talib
        # 一鍵安裝talib 
        # 看一下全部的函數，https://mrjbq7.github.io/ta-lib/funcs.html
        sma5 = talib.SMA(self.df['Close'], 5) # 計算5日簡單平均
        print('MA5 = ',sma5)
        sma20 = talib.SMA(self.df['Close'], 20) # 計算20日簡單平均
        sma60 = talib.SMA(self.df['Close'], 60) # 計算60日簡單平均
        rsi5 = talib.RSI(self.df['Close'], timeperiod=5)
        rsi10 = talib.RSI(self.df['Close'], timeperiod=10)
        macd, macdsignal, macdhist = talib.MACD(self.df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
        
        # 6/11
        mv5 = talib.SMA(self.df['Volume'], 5)
        mv20 = talib.SMA(self.df['Volume'], 20)
        
        # # macd = talib.MACD(df['Close'] )
        # print(type(macd))
        self.sma20 = sma20
        self.sma60 = sma60
        self.rsi5 = rsi5
        self.rsi10 = rsi10
        self.macd = macd
        self.mv5 = mv5
        self.mv20 = mv20
        
        print('macd series = \n',macd)
        self.sma5_drop_nan = sma5.dropna() # 去除 dataframe 中的NaN值
        self.sma20_drop_nan = sma20.dropna()
        self.sma60_drop_nan = sma60.dropna()
        self.rsi5_drop_nan = rsi5.dropna()
        self.rsi10_drop_nan = rsi10.dropna()
        self.macd_drop_nan = macd.dropna() # 各個len不同
        
    
        self.stockPlot()
        
        
    def currentTime(self):
        # self.timer = QTimer()
        # timeInterval = 1 * 60000 /60 # 1/60 分鐘
        # self.timer.setInterval(timeInterval)
        # self.timer.start()
        self.label_todayTime.setText(datetime.now().strftime('%Y-%m-%d'))
        self.label_todayTime_hourMinSec.setText(datetime.now().strftime('%H-%M-%S'))
        
        
        

def RSI(Close, period=12): # 收盤價 / 12 期
        Chg = Close - Close.shift(1)
        Chg_pos = pd.Series(index=Chg.index, data=Chg[Chg>0])
        Chg_pos = Chg_pos.fillna(0)
        Chg_neg = pd.Series(index=Chg.index, data=-Chg[Chg<0])
        Chg_neg = Chg_neg.fillna(0)
        up_mean = []
        down_mean = []
        for i in range(period+1, len(Chg_pos)+1):
            up_mean.append(np.mean(Chg_pos.values[i-period:i]))
            down_mean.append(np.mean(Chg_neg.values[i-period:i]))
        
        # 計算 RSI
        rsi = []
        for i in range(len(up_mean)):
            rsi.append( 100 * up_mean[i] / ( up_mean[i] + down_mean[i] ) )
        rsi_series = pd.Series(index = Close.index[period:], data = rsi)
        return rsi_series


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
 
if __name__ == '__main__':
    main()
    

# import pyqtgraph.examples
# pyqtgraph.examples.run()

# 可以參考 bar graph / ErrorBarItem


