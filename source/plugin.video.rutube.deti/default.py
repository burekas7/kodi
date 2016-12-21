#!/usr/bin/python
# -*- coding: utf-8 -*-
# Writer (c) 2016, Silhouette, E-mail: 
# Rev. 0.1.0


import xbmcplugin,xbmcgui,xbmcaddon
import urllib, urllib2, os, re, sys, json

_ADDOD_ID_= 'plugin.video.rutube.deti'
_FEEDS_URL_= 'https://rutube.ru/feeds/kids/'

def QT(url): return urllib.quote_plus(url)
def UQT(url): return urllib.unquote_plus(url)

class RTFeeds():
    def __init__(self):
        self.id = _ADDOD_ID_
        self.addon = xbmcaddon.Addon(self.id)
        self.aicon = self.addon.getAddonInfo('icon')
        self.fanart = self.addon.getAddonInfo('fanart')
        self.profile = self.addon.getAddonInfo('profile')
        self.version = self.addon.getAddonInfo('version')
        self.handle = int(sys.argv[1])
        self.params = sys.argv[2]
        self.murl = _FEEDS_URL_
        self.mode = ''
        self.icon = ''
        self.url = ''  
        self.name = ''
        
        self.debug = 1
        self.dbg_level = 2
        
    # start_pg = fixurl(u"http://спутник.дети")
    def fixurl(self, url):
        # turn string into unicode
        if not isinstance(url,unicode):
            url = url.decode('utf8')
    
        # parse it
        parsed = urlparse.urlsplit(url)
    
        # divide the netloc further
        userpass,at,hostport = parsed.netloc.rpartition('@')
        user,colon1,pass_ = userpass.partition(':')
        host,colon2,port = hostport.partition(':')
    
        # encode each component
        scheme = parsed.scheme.encode('utf8')
        user = urllib.quote(user.encode('utf8'))
        colon1 = colon1.encode('utf8')
        pass_ = urllib.quote(pass_.encode('utf8'))
        at = at.encode('utf8')
        host = host.encode('idna')
        colon2 = colon2.encode('utf8')
        port = port.encode('utf8')
        path = '/'.join(  # could be encoded slashes!
            urllib.quote(urllib.unquote(pce).encode('utf8'),'')
            for pce in parsed.path.split('/')
        )
        query = urllib.quote(urllib.unquote(parsed.query).encode('utf8'),'=&?/')
        fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf8'))
    
        # put it back together
        netloc = ''.join((user,colon1,pass_,at,host,colon2,port))
        return urlparse.urlunsplit((scheme,netloc,path,query,fragment))
    
    def get_rutube(self, url):
        self.dbg_log('-get_rutube:' + '\n')
        self.dbg_log('- url-in:'+  url + '\n')
        if 'rutube.ru' in url:
            try: videoId = re.findall('rutube.ru/play/embed/(.*?)"', url)[0]
            except:
                try: videoId = re.findall('rutube.ru/video/(.*?)/', url)[0]
                except: return None
            url = 'http://rutube.ru/api/play/options/'+videoId+'?format=json'
            request = urllib2.Request(url)
            request.add_header('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36')
            response = urllib2.urlopen(request)
            resp = response.read()
            jsonDict = json.loads(resp)
            link = urllib.quote_plus(jsonDict['video_balancer']['m3u8'])
            return link
        else: 
            return None
    
    def dbg_log(self, line):
        if self.debug: xbmc.log(line)
        
       
    
    def get_url(self, url, data = None, cookie = None, save_cookie = False, referrer = None):
        self.dbg_log('-get_url:' + '\n')
        self.dbg_log('- url:'+  url + '\n')
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.7.62 Version/11.00')
        req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
        req.add_header('Accept-Language', 'ru,en;q=0.9')
        if cookie: req.add_header('Cookie', cookie)
        if referrer: req.add_header('Referer', referrer)
        if data: 
            response = urllib2.urlopen(req, data,timeout=30)
        else:
            response = urllib2.urlopen(req,timeout=30)
        link=response.read()
        if save_cookie:
            setcookie = response.info().get('Set-Cookie', None)
            if setcookie:
                setcookie = re.search('([^=]+=[^=;]+)', setcookie).group(1)
                link = link + '<cookie>' + setcookie + '</cookie>'
        
        response.close()
        return link



      # Converts the request url passed on by xbmc to the plugin into a dict of key-value pairs
    def getParameters(self, parameterString):
        self.log("", 5)
        commands = {}
        #parameterString = urllib.unquote_plus(parameterString)
        splitCommands = parameterString[parameterString.find('?') + 1:].split('&')

        for command in splitCommands:
            if (len(command) > 0):
                splitCommand = command.split('=')
                key = splitCommand[0]
                try: value = splitCommand[1]
                except: value = ''
                commands[key] = value

        self.log(repr(commands), 5)
        return commands
      # *** Add-on helpers
    def log(self, message, level = 1):
        if (level < self.dbg_level) or (self.debug and self.dbg_level >= level):
            xbmc.log("[%s LOG]: %s" % (self.id, message.encode('utf8')))

    def error(self, message):
        xbmc.log("[%s ERROR]: %s" % (self.id, message))

    def showErrorMessage(self, msg):
        xbmc.log(msg.encode('utf-8'))
        xbmc.executebuiltin("XBMC.Notification(%s %s, %s)" % ("ERROR:", msg.encode('utf-8'), str(10 * 1000)))

    def encode(self, string):
        return string.decode('cp1251').encode('utf-8')
    
    def list_items(self, ictlg, films=False):
        self.log("-list_items:")
#        print ictlg

        if films == False:
            xbmcplugin.setContent(self.handle, 'Episodes')
            self.log('Episodes')
        else:
            xbmcplugin.setContent(self.handle, 'Movies')
            self.log('Movies')
        
        for ctUrl, ctIcon, ctFolder, ctLabels in ictlg:
            ctTitle = ctLabels['title']
            item = xbmcgui.ListItem(ctTitle, iconImage=ctIcon, thumbnailImage=ctIcon)

            item.setInfo( type='Video', infoLabels=ctLabels)
            if ctFolder == False: item.setProperty('IsPlayable', 'true')
            item.setProperty('fanart_image', self.fanart)
            xbmcplugin.addDirectoryItem(self.handle, sys.argv[0] + ctUrl, item, ctFolder)
            self.log("ctTitle: %s"  % ctTitle, 2) 
#             self.log("ctUrl: %s"  % ctUrl, 2) 
            self.log("ctIcon: %s"  % ctIcon, 2) 

        xbmcplugin.endOfDirectory(self.handle)
            
    def init_self(self, params):
    
        self.mode = params['mode'] if 'mode' in params else None
        self.icon = UQT(params['icon']) if 'icon' in params else ''
        self.url = UQT(params['url']) if 'url' in params else ''  
        self.name = params['name'] if 'name' in params else ''
            
    def main(self):
        self.log("Addon: %s"  % self.id)
        self.log("Params: %s" % self.params)

        params = self.getParameters(self.params)
           
        self.init_self(params)
       
        if self.mode == 'tabs':
            self.m_tabs()
        elif self.mode == 'list':
            self.m_list()
        elif self.mode == 'show':
            self.m_show()
        elif self.mode == 'play':
            self.m_play()
        else:
            self.m_tabs()
            
    def m_tabs(self):
        self.log("-m_tabs:")
        ct_cat = []
        
        http = self.get_url(self.murl)
        jdata = re.compile("initialData.showcase = '{(.*?)}';").findall(http)[0].decode('unicode-escape')
        js = json.loads('{'+jdata+'}')
        for tab in js['tabs']:
            name = tab['name']
            url = tab['url']
            params = '?mode=list&url=' + QT(url)
            ct_cat.append((params, self.aicon, True, {'title': name}))
        self.list_items(ct_cat, True)
        
    def m_list(self):
        self.log("-m_list:")
        self.log("--url: %s"%self.url)
        ct_list = []
        
        if not self.url == 'https://rutube.ru/feeds/kids/popular/':
    #     if 1:
            http = self.get_url(self.url)
            jtdata = re.compile("initialData.resultsOfActiveTabResources\[(.*?)\] = '{(.*?)}';").findall(http)[0][1].decode('unicode-escape')
            jts = json.loads('{'+jtdata+'}')
            for res in jts['results']:
#                 self.log(str(res).decode('unicode-escape'))
                name = ''
                url = ''
                pic = ''
                plot = ''
                try:
                    name = res['object']['name']
                    pic = res['object']['picture']
                    url = res['object']['absolute_url']
                    plot = res['object']['description']
                except:
                    try:
                        name = res['title']
                        pic = res['picture_url']
                        url = res['video_url']
                        plot = res['description']
                    except: pass
    
                if pic == '':
                    try: pic = res['thumbnail_url']
                    except: pass
                if plot == '':
                    try: plot = res['short_description']
                    except: pass
                
                self.log("-m_list-name: %s"%name)
                self.log("-m_list-pic: %s"%pic)
                self.log("-m_list-url: %s"%url)
                
                if url and name:
                    if url.find('video') > -1 or url.find('play/embed') > -1:
                        mode = 'play'
                        folder = False
                    else:
                        mode = 'show'
                        folder = True
                    params = '?mode=%s&url=%s'%(mode, QT(url))
                    ct_list.append((params, pic, folder, {'title': name, 'plot':plot}))
        
        self.list_items(ct_list, True)
        
    def m_show(self):
        self.log("-m_show:")
        self.log("--url: %s"%self.url)
        ct_show = []
        
        http = self.get_url(self.url)

        try:
            brdata = re.compile("initialData.branding = '{(.*?)}';").findall(http)[0].decode('unicode-escape')
            brs = json.loads('{'+brdata+'}')
#             self.log(str(brs).decode('unicode-escape'))
            try: self.fanart = brs['banner'][1]['picture']
            except: self.fanart = brs['banner'][0]['picture']
            self.log(self.fanart)
        except: pass
        
        
        try: jtdata = re.compile("initialData.resultsOfActiveTabResources\[(.*?)\] = '{(.*?)}';").findall(http)[0][1].decode('unicode-escape')
        except:
            try: jtdata = re.compile("initialData.personVideoTab = JSON.parse\('{(.*?)}'\);").findall(http)[0].decode('unicode-escape')
            except: jtdata = re.compile('data-value="{(.*?)}"></div>').findall(http)[0]
            
#         self.log(str(jtdata).decode('unicode-escape'))
        try:jts = json.loads('{'+jtdata+'}')
        except:jts = json.loads(jtdata)
#         self.log(str(jts).decode('unicode-escape'))
        for res in jts['results']:
#             self.log(str(res).decode('unicode-escape'))
            name = ''
            url = ''
            pic = ''
            plot = ''
            try:
                name = res['object']['name']
                pic = res['object']['picture']
                url = res['object']['absolute_url']
                plot = res['object']['description']
            except:
                try:
                    name = res['title']
                    pic = res['picture_url']
                    url = res['video_url']
                    plot = res['description']
                except: pass

            if pic == '':
                try: pic = res['thumbnail_url']
                except: pass
            if plot == '':
                try: plot = res['short_description']
                except: pass
            
            self.log("-m_show-name: %s"%name)
            self.log("-m_show-pic: %s"%pic)
            self.log("-m_show-url: %s"%url)
            
            if url and name:
                params = '?mode=play&url=%s&icon=%s&name=%s'%(QT(url), QT(pic), name)
                ct_show.append((params, pic, True, {'title': name, 'plot':plot}))

        self.list_items(ct_show, True)

    def m_play(self):
        self.log("-m_play:")

        
        uri = None
        try:uri = self.get_rutube(self.url)
        except:pass
            
        if uri != None and uri != False:
            if not uri.startswith('http'): uri = 'http:' + uri
            uri = UQT(uri)
            self.dbg_log('- uri: '+  uri + '\n')
            if 0:
                item = xbmcgui.ListItem(self.name, path = uri, iconImage=self.icon, thumbnailImage=self.icon)
                xbmcplugin.setResolvedUrl(pluginhandle, True, item)
            else:
                item = xbmcgui.ListItem(self.name, iconImage=self.icon, thumbnailImage=self.icon)
                sPlayer = xbmc.Player()
                item.setInfo( type='Video', infoLabels={'title':self.name})
                item.setProperty('IsPlayable', 'true')
                sPlayer.play(uri, item)
        else:
            self.showErrorMessage("Sorry.\nYour region is not supported")


rodina = RTFeeds()
rodina.main()  

