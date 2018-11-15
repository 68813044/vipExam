import requests
import re
import threading
import os

def getIdValue(id,html):
    return re.findall(r'id="'+id+'" value="(.*?)"',html)[0]

def getExamName(html):
    return re.findall(r'<span id="WebSplitter2_tmpl1_lblExamName">(.*?)</span>',html)[0]


#传入试卷id 将试卷下载在根目录下
def downLoad(id):
    url = 'http://lib.vipexam.org/test/spliter.aspx?uid=test&loadState=false&id='+id
    print('Open page:'+url)
    res = requests.get(url)
    res.raise_for_status()

    html = res.text
    postData = {
        "__MSPVSTATE":getIdValue("__MSPVSTATE",html),
        "__VIEWSTATE":"",
        "__EVENTVALIDATION":getIdValue("__EVENTVALIDATION",html),
        "wordid":getIdValue("wordid",html),
        "worduser":"test",
        "WebSplitter2$tmpl0$btnSabeExam":"下载试卷"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        "Content-Length": "7538",
        #"Cache-Control":" max-age=0",
        "Origin": "http://lib.vipexam.org",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    ExamName = getExamName(html)
    print('Download :'+ ExamName,end="    ")
    res = requests.post(url,headers=headers,data = postData)
    res.raise_for_status()
    print(res.status_code)
    playFile = open(ExamName+'.mht','wb')
    for chunk in res.iter_content(100000):
        playFile.write(chunk)
    playFile.close()

def getCourseAllId(pageRange,examCode,examType = 0):
    idList = []
    #examType 1即真题、2即模拟题、默认为获取全部题目id
    for id in range(1,pageRange+1):
        url = 'http://lib.vipexam.org/ImitateSelfTest.aspx'

        c = ",,,,"
        if examType == 1:   #获得真题：请求主体p=load&i=1&ps=10&c=,,,,,csrmsd,
            c = c + ","
        elif examType == 2: #获得模拟题请求主体p=load&i=1&ps=10&c=,,,,1,csrmsd,
            c = c + "1,"
        else:               #获得全部的请求主体p=load&i=1&ps=10&c=,,,,2,csrmsd,
            c = c + "2,"
        c = c + examCode
        postData = {
            "p":"load",
            "i":str(id),
            "ps":"10",
            "c":c
        }
        print(postData)
        res = requests.post(url,data = postData)
        html = res.text
        examId = re.findall(r"id='gf' value='(.*?)'",html)
        #print (examId)
        idList = idList + examId
        print(examId)
    return idList


#请求地址：http://lib.vipexam.org/ImitateSelfTest.aspx  请求主体：p=load&i=1&ps=10&c=,,,,,csrmsd,（获得全）

examCode = "csrmsd"    #获得某个考试科目的文件夹代码,
examType = 1           #默认为获取所有试卷id,1为真题，2为模拟题
pageRange = 21         #为对应真题(模拟题)下有多少页面

list = getCourseAllId(1,examCode)
for id in list:
    downLoad(id)