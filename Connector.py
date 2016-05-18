import httplib
import urllib
import os
import logging as log
import datetime
from ImgResolver import ImgResolver
from HtmlResolver import HtmlResolver

class Connector(object):
    def __init__(self):
        self.headers = {
        'Accept' : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
	'Accept-Encoding' : "gzip, deflate",
	'Accept-Language' : "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
	'Cache-Control' : "max-age=0",
	'Connection' : "keep-alive",
	'Content-Type' : "application/x-www-form-urlencoded",
	'Host' : "www.einvoice.nat.gov.tw",
	'Origin' : "https://www.einvoice.nat.gov.tw",
	'Referer' : "https://www.einvoice.nat.gov.tw/APMEMBERVAN/PublicAudit/PublicAudit!queryInvoiceByCon",
	'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
	}
        self.postData = {
        'publicAuditVO.customerIdentifier' : "",
        'publicAuditVO.randomNumber' : "",
        'CSRT' : "4415786180457926558"
        }
        self.imgresolver = ImgResolver()
        self.htmlresolver = HtmlResolver()
        self.conn = httplib.HTTPSConnection(self.headers['Host'])
        if self.conn == None:
            raise Exception

    def Get(self):
        self.conn.request("GET","/APMEMBERVAN/PublicAudit/PublicAudit!generateImageCode",headers = self.headers)
        while True:
            try:
                res = self.conn.getresponse()
            except httplib.ResponseNotReady:
                print "FUCK"
                continue
            else:
                break
        for header in res.getheaders():
            if header[0] == "set-cookie":
                self.headers['Cookie'] = header[1]
		break
        self.postData['txtQryImageCode'] = self.imgresolver.solve(res.read())
        log.debug("Cookie : {}".format(self.headers['Cookie']))
	log.debug("Captcha : {}".format(self.postData['txtQryImageCode']))

    def Post(self):
        params = urllib.urlencode(self.postData)
        self.conn.request("POST","/APMEMBERVAN/PublicAudit/PublicAudit!queryInvoiceByCon",params,self.headers)
        while True:
            try:
                res = self.conn.getresponse()
            except httplib.ResponseNotReady:
                print "FUCK"
                continue
            else:
                break
        return res.read()

    def Hack(self,number,date):
        self.postData['publicAuditVO.invoiceNumber'] = number
        self.postData['publicAuditVO.invoiceDate'] = date
        success,money = self.htmlresolver.solve(self.Post())
        while not success:
            self.Get()
            success,money = self.htmlresolver.solve(self.Post())
        return money

    def Task(self,number,date,direction,):
        _ABC = number[:2]
        _123 = int(number[2:])
        print _ABC,str(_123)
        for i in range(10):
            money = self.Hack(_ABC+str(_123+i),date)
            if money == 0:
                someday = datetime.datetime.strptime(str(int(date[0:3])+1991)+date[3:],"%Y/%m/%d")
                someday = someday + datetime.timedelta(days = direction)
                date = str(int(someday.strftime("%Y/%m/%d")[0:4])-1991)+someday.strftime("%Y/%m/%d")[4:]
                log.debug("date modify")
                money = self.Hack(_ABC+str(_123+i),date)
            print money

if __name__ == '__main__':
    log.basicConfig(level = log.INFO)
    C = Connector()
    print "Welcome to Receipt Crawlers World!!"
    number = raw_input("Number:").strip()
    date = raw_input("Date:").strip()
    C.Task(number,date,1)