# -*- coding: utf-8 -*-
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="sam"
__date__ ="$Sep 17, 2011 1:19:04 AM$"

import mc
import sys, os
import urllib
import random
from time import time

class Tracker:
	def __init__(self, uacode = False, debug = False):
		self.uacode = uacode
		self.version = "1.0"
		self.domain = 'code.google.com'
		self.application = mc.GetApp().GetId()

		if 'linux' in sys.platform:
			self.os = 'Linux'
		elif 'win32' in sys.platform:
			self.os = 'Windows'
		elif 'darwin' in sys.platform:
			self.os = 'Macintosh'

		try: self.platform = mc.GetPlatform()
		except: self.platform = 'Boxee'
		try: self.deviceid = mc.GetDeviceId()
		except: self.deviceid = 'None'
		try: self.boxeeid = mc.GetUniqueId()
		except: self.boxeeid = 'None'

	def trackView(self, window = False):
		#if not window:
		#	page = '/%s' % self.application
		#else:
		#	page = '/%s/%s' % (self.application, urllib.quote_plus(window) )
		page = '/p/ex-ua-boxee-tv/'

		var_utmac = self.uacode
		var_utmhn = self.domain
		var_utmn = str(random.randint(1000000000,9999999999))
		var_cookie = str(random.randint(10000000,99999999))
		var_random = str(random.randint(1000000000,2147483647))
		var_referer = '-'
		var_uservar = '-'
		var_utmp = page
		var_today = str(int(time()))
		
		imgpath = 'http://www.google-analytics.com/__utm.gif?utmwv=3&utmn='
		imgpath += var_utmn + '&utme=-utmcs=-&utmsr=-&utmsc=-&utmul=-&utmje=0&utmfl=-&utmdt=-&utmhn='
		imgpath += var_utmhn + '&utmhid=' + var_utmn + '&utmr=' + var_referer
		imgpath += '&utmp=' + var_utmp + '&utmac=' + var_utmac + '&utmcc=__utma%3D'
		imgpath += var_cookie + '.' + var_random + '.' + var_today + '.' + var_today
		imgpath += '.' + var_today + '.2%3B%2B__utmz%3D' + var_cookie + '.'
		imgpath += var_today + '.2.2.utmcsr%3D_SOURCE_%7Cutmccn%3D_CAMPAIGN_%7Cutmcmd%3D_MEDIUM_%7Cutmctr%3D_KEYWORD_%7Cutmcct%3D_CONTENT_%3B%2B__utmv%3D'
		imgpath += var_cookie + '.' + var_uservar + '%3B'
		
		print imgpath

		tracker = self.request(imgpath)
		
		if tracker:
			return True
		else:
			return False

	def request(self, path):
		myHttp = mc.Http()
		myHttp.SetUserAgent( 'Boxee App (%s; U; %s; en-us; Boxee %s %s)' % (self.os, self.platform, self.deviceid, self.boxeeid) )
		data = myHttp.Get(path)
		return data

def trackMainView(uacode):
	track = Tracker(uacode)
	track.trackView()