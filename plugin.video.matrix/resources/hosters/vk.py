#-*- coding: utf-8 -*-
# https://github.com/Kodi-vStream/venom-xbmc-addons
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.hosters.hoster import iHoster
from resources.lib.comaddon import dialog, xbmcgui
from resources.lib.comaddon import VSlog


class cHoster(iHoster):

    def __init__(self):
        self.__sDisplayName = 'Vk'
        self.__sFileName = self.__sDisplayName
        self.__sHD = ''

    def getDisplayName(self):
        return  self.__sDisplayName

    def setDisplayName(self, sDisplayName):
        self.__sDisplayName = sDisplayName + ' [COLOR skyblue]' + self.__sDisplayName + '[/COLOR] [COLOR khaki]' + self.__sHD + '[/COLOR]'

    def setFileName(self, sFileName):
        self.__sFileName = sFileName

    def getFileName(self):
        return self.__sFileName

    def setHD(self, sHD):
        if 'hd' in sHD:
            self.__sHD = 'HD'
        else:
            self.__sHD = ''

    def getHD(self):
        return self.__sHD

    def getPluginIdentifier(self):
        return 'vk'

    def isDownloadable(self):
        return True

    def isJDownloaderable(self):
        return True

    def getPattern(self):
        return ''

    def __getIdFromUrl(self):
        sPattern = "?([^<]+)"
        oParser = cParser()
        aResult = oParser.parse(self.__sUrl, sPattern)
        if (aResult[0] == True):
            return aResult[1][0]

        return ''

    def __modifyUrl(self, sUrl):
        if (sUrl.startswith('http://')):
            oRequestHandler = cRequestHandler(sUrl)
            oRequestHandler.request()
            sRealUrl = oRequestHandler.getRealUrl()
            self.__sUrl = sRealUrl
            return self.__getIdFromUrl()

        return sUrl

    def __getKey(self):
        oRequestHandler = cRequestHandler(self.__sUrl)
        sHtmlContent = oRequestHandler.request()
        sPattern = 'fkzd="(.+?)";'
        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            aResult = aResult[1][0].replace('.', '%2E')
            return aResult

        return ''

    def setUrl(self, sUrl):
        self.__sUrl = sUrl

    def checkUrl(self, sUrl):
        return True

    def getUrl(self):
        return self.__sUrl

    def getMediaLink(self):
        return self.__getMediaLinkForGuest()

    def __getMediaLinkForGuest(self):
        VSlog(self.__sUrl)
        url=[]
        qua=[]
        oRequest = cRequestHandler(self.__sUrl)
        sHtmlContent = oRequest.request()
     # (.+?) ([^<]+) .+?
        sPattern =  '"hls":"(.+?)",'

        oParser = cParser()
        aResult = oParser.parse(sHtmlContent, sPattern)
        if (aResult[0] == True):
            api_call = aResult[1][0] + '&Referer=' + self.__sUrl

            if (api_call):
                return True, api_call

        return False, False
