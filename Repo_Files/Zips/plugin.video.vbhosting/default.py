 #############Imports#############
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,base64,os,re,unicodedata,requests,time,string,sys,urllib,urllib2,json,urlparse,datetime,zipfile,shutil
from resources.modules import client,control,tools,shortlinks,userinfo
from datetime import date
from metahandler import metahandlers
#################################

#############Defined Strings#############
username     = control.setting('Username')
password     = control.setting('Password')

icon         = xbmc.translatePath(os.path.join('special://home/addons/' + userinfo.addon_id, 'icon.png'))
fanart       = xbmc.translatePath(os.path.join('special://home/addons/' + userinfo.addon_id , 'fanart.jpg'))

vod_url      = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(userinfo.host,userinfo.port,username,password)
tv_url       = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_scategories&scat_id=21'%(userinfo.host,userinfo.port,username,password)
panel_api    = '%s:%s/panel_api.php?username=%s&password=%s'%(userinfo.host,userinfo.port,username,password)
play_url     = '%s:%s/live/%s/%s/'%(userinfo.host,userinfo.port,username,password)

advanced_settings           =  xbmc.translatePath('special://home/addons/'+userinfo.addon_id+'/resources/advanced_settings')
advanced_settings_target    =  xbmc.translatePath(os.path.join('special://home/userdata','advancedsettings.xml'))
#########################################


def start():
	if username=="":
		user = userpopup()
		passw= passpopup()
		control.setSetting('Username',user)
		control.setSetting('Password',passw)
		xbmc.executebuiltin('Container.Refresh')
		auth = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(userinfo.host,userinfo.port,user,passw)
		auth = tools.OPEN_URL(auth)
		if auth == "":
			line1 = "Incorrect Login Details"
			line2 = "Please Re-enter" 
			line3 = "" 
			xbmcgui.Dialog().ok('Attention', line1, line2, line3)
			start()
		else:
			line1 = "Login Sucsessfull"
			line2 = "Welcome to "+userinfo.addon_name
			line3 = ('[COLOR white]%s[/COLOR]'%user)
			xbmcgui.Dialog().ok(userinfo.addon_name, line1, line2, line3)
			addonsettings('ADS2','')
			xbmc.executebuiltin('Container.Refresh')
			home()
	else:
		auth = '%s:%s/enigma2.php?username=%s&password=%s&type=get_vod_categories'%(userinfo.host,userinfo.port,username,password)
		auth = tools.OPEN_URL(auth)
		if not auth=="":
			tools.addDir('Account Information','url',6,icon,fanart,'')
			tools.addDir('Movies','vod',1,icon,fanart,'')
			tools.addDir('TV Shows','tv',2,icon,fanart,'')
			tools.addDir('Search','url',5,icon,fanart,'')
			tools.addDir('Settings','url',8,icon,fanart,'')
def home():
	tools.addDir('Account Information','url',6,icon,fanart,'')
	tools.addDir('Movies','vod',1,icon,fanart,'')
	tools.addDir('TV Shows','tv',2,icon,fanart,'')
	tools.addDir('Search','',5,icon,fanart,'')
	tools.addDir('Settings','url',8,icon,fanart,'')
	
	
def movies(url):
	if url =="vod":
		open = tools.OPEN_URL(vod_url)
	else:
		open = tools.OPEN_URL(url)
	all_cats = tools.regex_get_all(open,'<channel>','</channel>')
	for a in all_cats:
		if '<playlist_url>' in open:
			name = tools.regex_from_to(a,'<title>','</title>')
			name = base64.b64decode(name)
			url1  = tools.regex_from_to(a,'<playlist_url>','</playlist_url>').replace('<![CDATA[','').replace(']]>','')
			if not 'TV shows' in name:
				tools.addDir(str(name).replace('?',''),url1,1,icon,fanart,'')
		else:
				try:
					name = tools.regex_from_to(a,'<title>','</title>')
					name = base64.b64decode(name)
					thumb= tools.regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
					url  = tools.regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
					desc = tools.regex_from_to(a,'<description>','</description>')
					desc = base64.b64decode(desc)
					plot = tools.regex_from_to(desc,'PLOT:','\n')
					cast = tools.regex_from_to(desc,'CAST:','\n')
					ratin= tools.regex_from_to(desc,'RATING:','\n')
					year = tools.regex_from_to(desc,'RELEASEDATE:','\n').replace(' ','-')
					year = re.compile('-.*?-.*?-(.*?)-',re.DOTALL).findall(year)
					runt = tools.regex_from_to(desc,'DURATION_SECS:','\n')
					genre= tools.regex_from_to(desc,'GENRE:','\n')
					tools.addDirMeta(str(name).replace('[/COLOR].','.[/COLOR]'),url,4,thumb,fanart,plot,str(year).replace("['","").replace("']",""),str(cast).split(),ratin,runt,genre)
				except:pass
				xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	
def tvshows(url):
	if url =="tv":
		open = tools.OPEN_URL(tv_url)
	else:
		open = tools.OPEN_URL(url)
	all_cats = tools.regex_get_all(open,'<channel>','</channel>')
	for a in sorted(all_cats):
		if '<playlist_url>' in open:
			name = tools.regex_from_to(a,'<title>','</title>')
			name = base64.b64decode(name)
			url1  = tools.regex_from_to(a,'<playlist_url>','</playlist_url>').replace('<![CDATA[','').replace(']]>','')
			
			from metahandler import metahandlers
			md   = metahandlers.MetaData()
			meta = md.get_meta('tvshow', name, '')
			
			i = meta['cover_url']
			if i == "":i = icon
			
			f = meta['backdrop_url']
			if f == "":f = fanart

			tools.addDir(str(name).replace('?',''),url1,2,i,f,'')
		else:
		
		
			name = tools.regex_from_to(a,'<title>','</title>')
			name = base64.b64decode(name)
			thumb= tools.regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
			url  = tools.regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>','')
			tools.addDir(name,url,4,icon,fanart,'')
				
				
def stream_video(url):
	url = str(url).replace('USERNAME',username).replace('PASSWORD',password)
	liz = xbmcgui.ListItem('', iconImage='DefaultVideo.png', thumbnailImage=icon)
	liz.setInfo(type='Video', infoLabels={'Title': '', 'Plot': ''})
	liz.setProperty('IsPlayable','true')
	liz.setPath(str(url))
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
	
	


	
def search():
	if mode==3:
		return False
	text = searchdialog()
	if not text:
		xbmc.executebuiltin("XBMC.Notification([COLOR red][B]Search is Empty[/B][/COLOR],Aborting search,4000,"+icon+")")
		return
	xbmc.log(str(text))
	open = tools.OPEN_URL(panel_api)
	all_chans = tools.regex_get_all(open,'{"num":','epg')
	for a in all_chans:
		name = tools.regex_from_to(a,'name":"','"').replace('\/','/')
		url  = tools.regex_from_to(a,'"stream_id":"','"')
		thumb= tools.regex_from_to(a,'stream_icon":"','"').replace('\/','/')
		if text in name.lower():
			tools.addDir(name,play_url+url+'.ts',4,thumb,fanart,'')
		elif text not in name.lower() and text in name:
			tools.addDir(name,play_url+url+'.ts',4,thumb,fanart,'')
			
def searchdialog():
	search = control.inputDialog(heading='Search '+userinfo.addon_name+':')
	if search=="":
		return
	else:
		return search

	
def settingsmenu():
	tools.addDir('Edit Advanced Settings','ADS',10,icon,fanart,'')
	tools.addDir('Log Out','LO',10,icon,fanart,'')
	

def addonsettings(url,description):
	if   url =="CC":
		tools.clear_cache()
	elif url =="AS":
		xbmc.executebuiltin('Addon.OpenSettings(%s)'%userinfo.addon_id)
	elif url =="ADS":
		dialog = xbmcgui.Dialog().select('Edit Advanced Settings', ['Enable Fire TV Stick AS','Enable Fire TV AS','Enable 1GB Ram or Lower AS','Enable 2GB Ram or Higher AS','Enable Nvidia Shield AS','Disable AS'])
		if dialog==0:
			advancedsettings('stick')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
		elif dialog==1:
			advancedsettings('firetv')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
		elif dialog==2:
			advancedsettings('lessthan')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
		elif dialog==3:
			advancedsettings('morethan')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
		elif dialog==4:
			advancedsettings('shield')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
		elif dialog==5:
			advancedsettings('remove')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Advanced Settings Removed')
	elif url =="ADS2":
		dialog = xbmcgui.Dialog().select('Select Your Device Or Closest To', ['Fire TV Stick ','Fire TV','1GB Ram or Lower','2GB Ram or Higher','Nvidia Shield'])
		if dialog==0:
			advancedsettings('stick')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
		elif dialog==1:
			advancedsettings('firetv')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
		elif dialog==2:
			advancedsettings('lessthan')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
		elif dialog==3:
			advancedsettings('morethan')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
		elif dialog==4:
			advancedsettings('shield')
			xbmcgui.Dialog().ok(userinfo.addon_name, 'Set Advanced Settings')
	elif url =="tv":
		dialog = xbmcgui.Dialog().select('Select a TV Guide to Setup', ['iVue TV Guide','PVR TV Guide','Both'])
		if dialog==0:
			ivueint()
			xbmcgui.Dialog().ok(userinfo.addon_name, 'iVue Integration Complete')
		elif dialog==1:
			pvrsetup()
			xbmcgui.Dialog().ok(userinfo.addon_name, 'PVR Integration Complete')
		elif dialog==2:
			pvrsetup()
			ivueint()
			xbmcgui.Dialog().ok(userinfo.addon_name, 'PVR & iVue Integration Complete')
	elif url =="ST":
		xbmc.executebuiltin('Runscript("special://home/addons/'+userinfo.addon_id+'/resources/modules/speedtest.py")')
	elif url =="META":
		if 'ON' in description:
			xbmcaddon.Addon().setSetting('meta','false')
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmcaddon.Addon().setSetting('meta','true')
			xbmc.executebuiltin('Container.Refresh')
	elif url =="LO":
		xbmcaddon.Addon().setSetting('Username','')
		xbmcaddon.Addon().setSetting('Password','')
		xbmc.executebuiltin('XBMC.ActivateWindow(Videos,addons://sources/video/)')
		xbmc.executebuiltin('Container.Refresh')
	elif url =="UPDATE":
		if 'ON' in description:
			xbmcaddon.Addon().setSetting('update','false')
			xbmc.executebuiltin('Container.Refresh')
		else:
			xbmcaddon.Addon().setSetting('update','true')
			xbmc.executebuiltin('Container.Refresh')
	
		
def advancedsettings(device):
	if device == 'stick':
		file = open(os.path.join(advanced_settings, 'stick.xml'))
	elif device == 'firetv':
		file = open(os.path.join(advanced_settings, 'firetv.xml'))
	elif device == 'lessthan':
		file = open(os.path.join(advanced_settings, 'lessthan1GB.xml'))
	elif device == 'morethan':
		file = open(os.path.join(advanced_settings, 'morethan1GB.xml'))
	elif device == 'shield':
		file = open(os.path.join(advanced_settings, 'shield.xml'))
	elif device == 'remove':
		os.remove(advanced_settings_target)
	
	try:
		read = file.read()
		f = open(advanced_settings_target, mode='w+')
		f.write(read)
		f.close()
	except:
		pass
		
		
def asettings():
	choice = xbmcgui.Dialog().yesno(userinfo.addon_name, 'Please Select The RAM Size of Your Device', yeslabel='Less than 1GB RAM', nolabel='More than 1GB RAM')
	if choice:
		lessthan()
	else:
		morethan()
		
def userpopup():
	kb =xbmc.Keyboard ('', 'heading', True)
	kb.setHeading('Enter Username')
	kb.setHiddenInput(False)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
		return text
	else:
		return False

		
def passpopup():
	kb =xbmc.Keyboard ('', 'heading', True)
	kb.setHeading('Enter Password')
	kb.setHiddenInput(False)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
		return text
	else:
		return False
		
		
def accountinfo():
	open = tools.OPEN_URL(panel_api)
	try:
		username   = tools.regex_from_to(open,'"username":"','"')
		status     = tools.regex_from_to(open,'"status":"','"')
		connects   = tools.regex_from_to(open,'"max_connections":"','"')
		active     = tools.regex_from_to(open,'"active_cons":"','"')
		expiry     = tools.regex_from_to(open,'"exp_date":"','"')
		expiry     = datetime.datetime.fromtimestamp(int(expiry)).strftime('%d/%m/%Y - %H:%M')
		expreg     = re.compile('^(.*?)/(.*?)/(.*?)$',re.DOTALL).findall(expiry)
		for day,month,year in expreg:
			month     = tools.MonthNumToName(month)
			year      = re.sub(' -.*?$','',year)
			expiry    = month+' '+day+' - '+year
			ip        = tools.getlocalip()
			extip     = tools.getexternalip()
			tools.addDir('[COLOR white]Username :[/COLOR] '+username,'','',icon,fanart,'')
			tools.addDir('[COLOR white]Expiry Date:[/COLOR] '+expiry,'','',icon,fanart,'')
			tools.addDir('[COLOR white]Account Status :[/COLOR] %s'%status,'','',icon,fanart,'')
			tools.addDir('[COLOR white]Current Connections:[/COLOR] '+ active,'','',icon,fanart,'')
			tools.addDir('[COLOR white]Allowed Connections:[/COLOR] '+connects,'','',icon,fanart,'')
			tools.addDir('[COLOR white]Local IP Address:[/COLOR] '+ip,'','',icon,fanart,'')
			tools.addDir('[COLOR white]External IP Address:[/COLOR] '+extip,'','',icon,fanart,'')
	except:pass

	
	
	
	
	
	
	
	
	
	
	
	
def num2day(num):
	if num =="0":
		day = 'monday'
	elif num=="1":
		day = 'tuesday'
	elif num=="2":
		day = 'wednesday'
	elif num=="3":
		day = 'thursday'
	elif num=="4":
		day = 'friday'
	elif num=="5":
		day = 'saturday'
	elif num=="6":
		day = 'sunday'
	return day

params=tools.get_params()
url=None
name=None
mode=None
iconimage=None
description=None
query=None
type=None

try:
	url=urllib.unquote_plus(params["url"])
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	iconimage=urllib.unquote_plus(params["iconimage"])
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass
try:
	description=urllib.unquote_plus(params["description"])
except:
	pass
try:
	query=urllib.unquote_plus(params["query"])
except:
	pass
try:
	type=urllib.unquote_plus(params["type"])
except:
	pass

if mode==None or url==None or len(url)<1:
	start()

elif mode==1:
	movies(url)
	
elif mode==2:
	tvshows(url)
	
elif mode==3:
	vod(url)
	
elif mode==4:
	stream_video(url)
	
elif mode==5:
	search()
	
elif mode==6:
	accountinfo()
	
elif mode==8:
	settingsmenu()
	
elif mode==9:
	xbmc.executebuiltin('ActivateWindow(busydialog)')
	tools.Trailer().play(url) 
	xbmc.executebuiltin('Dialog.Close(busydialog)')
	
elif mode==10:
	addonsettings(url,description)
	
elif mode==16:
	extras()
	
elif mode==17:
	shortlinks.Get()

xbmcplugin.endOfDirectory(int(sys.argv[1]))