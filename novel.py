from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from ui_novel import Ui_MainWindow
from configparser import ConfigParser
from threading import Thread
import numpy as np
import sys
import cv2
import os
import shutil
import time

is_working = False #is_working flag

def bsrc() -> None:
    '''
    获取源目录地址
    '''
    path = QFileDialog.getExistingDirectory()
    if path == '': #判断路径是否为空
        return
    MainWindowUi.lineEdit_src.setText(path) #设置路径
    pass

def bepub() -> None:
    '''
    浏览EPUB保存位置
    '''
    path = QFileDialog.getSaveFileName(filter='.epub')
    path = path[0]+path[1] #合并路径
    if path == '': #判断路径是否为空
        return
    MainWindowUi.lineEdit_epubadd.setText(path) #设置路径

def epubload() -> None:
    '''
    加载EPUB预设文件
    '''
    path = './template/epub.ini'
    cf = ConfigParser() #创建ConfigParser对象
    cf.read(path,'utf-8') #读取EPUB预设文件
    name = cf.get('epub', 'name') #获取书名
    writer = cf.get('epub', 'writer') #获取作者
    right = cf.get('epub', 'right') #获取版权信息
    publisher = cf.get('epub', 'publisher') #获取出版社
    MainWindowUi.lineEdit_epubname.setText(name)
    MainWindowUi.lineEdit_epubwriter.setText(writer)
    MainWindowUi.lineEdit_epubright.setText(right)
    MainWindowUi.lineEdit_epubpub.setText(publisher)

def loadimg() -> None:
    '''
    加载预设封面
    '''
    path = './template/cover.png'
    pixmap = QPixmap(path) #读取预设封面
    MainWindowUi.label_img.setPixmap(pixmap) #设置封面

def bimg() -> None:
    '''
    浏览封面图片
    '''
    path = QFileDialog.getOpenFileName(filter='*.png, *.jpg')
    path = path[0]
    if path == '': #判断路径是否为空
        return
    pixmap = QPixmap(path) #读取图片
    MainWindowUi.label_img.setPixmap(pixmap) #设置封面

def btxt() -> None:
    '''
    浏览TXT目标文件
    '''
    path = QFileDialog.getSaveFileName(filter='.txt')
    path = path[0]+path[1]
    if path == '':
        return
    MainWindowUi.lineEdit_txtadd.setText(path)

def txtload() -> None:
    '''
    加载TXT书名和作者预设文件
    '''
    path = './template/txt.ini'
    cf = ConfigParser() #创建ConfigParser对象
    cf.read(path, 'utf-8') #读取预设文件
    name = cf.get('txt', 'name') #获取书名
    writer = cf.get('txt', 'writer') #获取作者
    MainWindowUi.lineEdit_txtname.setText(name)
    MainWindowUi.lineEdit_txtwriter.setText(writer)

def txtThread(src:str, dst:str, name:str, writer:str) -> None:
    '''
    :param src: 源文件夹地址
    :param dst: 目标文件地址
    :param name: 书名
    :param writer: 作者
    '''
    global is_working
    print('正在以以下参数运行')
    print('源目录：'+src)
    print('目标文件：'+dst)
    print('书名：'+name)
    print('作者：'+writer)
    is_working = True
    MainWindowUi.statusbar.showMessage('正在读取文件列表',999000)
    _ = [] #文件列表
    txts = [] #TXT文件列表
    res = []
    for path in os.listdir(src): #检索源文件列表
        if os.path.isfile(os.path.join(src, path)):
            _.append(src+'/'+path)
    for i in _: #筛选TXT文件
        if i.endswith('.txt'):
            txts.append(i)
        else:
            pass
    length = len(txts) #章节数
    count = 0 #章节处理计数器
    cns = [] #章节标题名
    for i in txts: #从每个TXT中读取章节标题与内容
        count +=1
        MainWindowUi.statusbar.showMessage('正在处理第'+str(count)+'章，共'+str(length)+'章')
        chapname = os.path.basename(i).replace('.txt', '')
        cns.append(chapname) #将章节标题添加至列表
        with open(i, 'r', encoding='utf-8') as f:
            chapcont = f.read().replace('　　', '\n　　')
        res.append(chapcont) #将章节内容添加至列表
    content = '' #最终结果
    content += '0000 书籍信息\n\n' #书籍信息标题
    content += '　　'+name + '\n' #添加书名
    content += '　　作者：'+writer + '\n\n' #添加作者信息
    MainWindowUi.statusbar.showMessage('正在整合', 999000)
    c=0 #章节标题计数器
    for i in res: #添加每一章的标题与内容
        content += cns[c] + '    ' + i + '\n\n' 
        c += 1
    MainWindowUi.statusbar.showMessage('正在写入', 999000)
    with open(dst, 'w' ,encoding='utf-8') as f: #写入文件
        f.write(content)
    MainWindowUi.statusbar.showMessage('完成！', 999000000)
    is_working = False


def txtrun() -> None:
    '''
    开始生成TXT
    '''
    if is_working == True: #检查is_working flag
        _ = QMessageBox.warning(title='警告', text='有一个任务正在运行，请等待任务完成。')
    src = MainWindowUi.lineEdit_src.text() #读取源目录地址
    dst = MainWindowUi.lineEdit_txtadd.text() #读取目标文件地址
    name = MainWindowUi.lineEdit_txtname.text() #读取书名
    writer = MainWindowUi.lineEdit_txtwriter.text() #读取作者
    if src == '': #检查源目录地址是否为空
        _ = QMessageBox.warning(Main, '警告', '请浏览源文件夹')
        return
    if dst == '': #检查目标文件地址是否为空
        _ = QMessageBox.warning(Main, '警告', '请浏览目标文件')
        return
    if name == '': #检查书名是否为空
        _ = QMessageBox.warning(Main, '警告', '请填写书名或加载预设')
        return
    if writer == '': #检查作者是否为空
        _ = QMessageBox.warning(Main, '警告', '请填写作者或加载预设')
        return
    if not os.path.isdir(src): #检查源目录是否存在
        _ = QMessageBox.warning(Main, '警告', '源目录不存在')
        return
    t = Thread(target=txtThread, args=(src, dst, name, writer)) #创建子线程
    t.start()

def qtpixmap_to_cvimg(qtpixmap):

    qimg = qtpixmap.toImage()
    temp_shape = (qimg.height(), qimg.bytesPerLine() * 8 // qimg.depth())
    temp_shape += (4,)
    ptr = qimg.bits()
    ptr.setsize(qimg.byteCount())
    result = np.array(ptr, dtype=np.uint8).reshape(temp_shape)
    result = result[..., :3]

    return result

def epubThread(src:str, dst:str, name:str, writer:str, right:str, publisher:str, cover) -> None:
    cv2.imwrite('temp/OPS/images/cover.jpg', cover, [cv2.IMWRITE_PNG_COMPRESSION, 0])

def epubrun() -> None:
    src = MainWindowUi.lineEdit_src.text() #获取源目录地址
    dst = MainWindowUi.lineEdit_epubadd.text() #获取目标文件地址
    name = MainWindowUi.lineEdit_epubname.text() #获取书名
    writer = MainWindowUi.lineEdit_epubwriter.text() #获取作者
    right = MainWindowUi.lineEdit_epubright.text() #获取版权
    publisher = MainWindowUi.lineEdit_epubpub.text() #获取出版社
    pixmap = MainWindowUi.label_img.pixmap() #获取封面
    shutil.rmtree('temp')
    os.mkdir('temp')
    try: #检查封面是否为空
        cover = qtpixmap_to_cvimg(pixmap) #将QPixmap对象转为OpenCV对象
    except AttributeError:
        _ = QMessageBox.warning(Main, '警告', '封面为空，请选择封面或加载预设。')
        return
    if src == '': #检查源文件夹地址是否为空
        _ = QMessageBox.warning(Main, '警告', '请浏览源文件夹')
        return
    if dst == '': #检查目标文件地址是否为空
        _ = QMessageBox.warning(Main, '警告', '请浏览目标文件')
        return
    if name == '': #检查书名是否为空
        _ = QMessageBox.warning(Main, '警告', '请填写书名或加载预设')
        return
    if writer == '': #检查作者是否为空
        _ = QMessageBox.warning(Main, '警告', '请填写作者或加载预设')
        return
    if right == '': #检查版权信息是否为空
        _ = QMessageBox.warning(Main, '警告', '请填写版权信息或加载预设')
        return
    if publisher == '': #检查出版社是否为空
        _ = QMessageBox.warning(Main, '警告', '请填写出版社或加载预设')
        return
    if not os.path.isdir(src): #检查源目录是否存在
        _ = QMessageBox.warning(Main, '警告', '源目录不存在')
        return
    

def slotConn() -> None:
    '''
    链接信号与槽
    '''
    MainWindowUi.pushButton_bsrc.clicked.connect(bsrc)
    MainWindowUi.pushButton_epubb.clicked.connect(bepub)
    MainWindowUi.pushButton_epubload.clicked.connect(epubload)
    MainWindowUi.pushButton_loadimg.clicked.connect(loadimg)
    MainWindowUi.pushButton_bimg.clicked.connect(bimg)
    MainWindowUi.pushButton_txtb.clicked.connect(btxt)
    MainWindowUi.pushButton_txtload.clicked.connect(txtload)
    MainWindowUi.pushButton_txtrun.clicked.connect(txtrun)
    MainWindowUi.pushButton_epubrun.clicked.connect(epubrun)
    MainWindowUi.action_exit.triggered.connect(exit)

if __name__ == '__main__':  # 程序主方法
    app = QtWidgets.QApplication(sys.argv)
    Main = QtWidgets.QMainWindow()
    MainWindowUi = Ui_MainWindow()
    MainWindowUi.setupUi(Main)
    Main.show() #显示窗体
    slotConn() #连接信号槽
    sys.exit(app.exec_())