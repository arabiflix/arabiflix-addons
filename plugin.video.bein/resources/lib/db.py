#-*- coding: utf-8 -*-
#Venom.
from resources.lib.config import cConfig
from resources.lib.handler.inputParameterHandler import cInputParameterHandler
from resources.lib.handler.outputParameterHandler import cOutputParameterHandler
import os, sys
import urllib
import xbmc


SITE_IDENTIFIER = 'cDb'
SITE_NAME = 'DB'


try:
    from sqlite3 import dbapi2 as sqlite
    cConfig().log('SQLITE 3 as DB engine') 
except:
    from pysqlite2 import dbapi2 as sqlite
    cConfig().log('SQLITE 2 as DB engine') 


class cDb:

    def __init__(self):

        DB = cConfig().getFileDB()

        try:
            self.db = sqlite.connect(DB)
            self.dbcur = self.db.cursor()

            #self._create_tables()
        except:
            return False
        
      

    def __del__(self):
        ''' Cleanup db when object destroyed '''
        try:
            self.dbcur.close()
            self.dbcon.close()
        except: pass

    def _create_tables(self):

        sql_create2 = "DROP TABLE history"
        
        ''' Create table '''
        sql_create = "CREATE TABLE IF NOT EXISTS history ("" addon_id integer PRIMARY KEY AUTOINCREMENT, ""title TEXT, ""disp TEXT, ""icone TEXT, ""isfolder TEXT, ""level TEXT, ""lastwatched TIMESTAMP "");"
        self.dbcur.execute(sql_create)
        
        sql_create = "CREATE TABLE IF NOT EXISTS resume ("" addon_id integer PRIMARY KEY AUTOINCREMENT, ""title TEXT, ""hoster TEXT, ""point TEXT, ""UNIQUE(title, hoster)"");"
        self.dbcur.execute(sql_create)

        sql_create = "CREATE TABLE IF NOT EXISTS watched ("" addon_id integer PRIMARY KEY AUTOINCREMENT, ""title TEXT, ""site TEXT, ""UNIQUE(title, site)"");"
        self.dbcur.execute(sql_create)

        sql_create = "CREATE TABLE IF NOT EXISTS favorite ("" addon_id integer PRIMARY KEY AUTOINCREMENT, ""title TEXT, ""siteurl TEXT, ""site TEXT, ""fav TEXT, ""cat TEXT, ""icon TEXT, ""fanart TEXT, ""UNIQUE(title, site)"");"
        self.dbcur.execute(sql_create)         

        #sql_create = "DROP TABLE download"
        #self.dbcur.execute(sql_create)
        
        sql_create = "CREATE TABLE IF NOT EXISTS download ("" addon_id integer PRIMARY KEY AUTOINCREMENT, ""title TEXT, ""url TEXT, ""path TEXT, ""cat TEXT, ""icon TEXT, ""size TEXT,""totalsize TEXT, ""status TEXT, ""UNIQUE(title, path)"");"
        self.dbcur.execute(sql_create) 

        cConfig().log('Table initialized') 
    
    #Ne pas utiliser cette fonction pour les chemins
    def str_conv(self, data):
        if isinstance(data, str):
            # Must be encoded in UTF-8
            data = data.decode('utf8')
            
        import unicodedata
        data = unicodedata.normalize('NFKD', data).encode('ascii','ignore')
        data = data.decode('string-escape') #ATTENTION : provoque des bugs pour les chemins a cause du caractere '/'
        
        return data
    
    def insert_history(self, meta):

        #title = urllib.unquote(meta['title']).decode('ascii', 'ignore')
        title = self.str_conv(urllib.unquote(meta['title']))
        disp = meta['disp']
        icon = 'icon.png'
        ex = "INSERT INTO history (title, disp, icone) VALUES (?, ?, ?)"
        self.dbcur.execute(ex, (title,disp,icon))

        try:
            self.db.commit() 
            cConfig().log('SQL INSERT history Successfully') 
        except Exception, e:
            #print ('************* Error attempting to insert into %s cache table: %s ' % (table, e))
            cConfig().log('SQL ERROR INSERT') 
            pass
        self.db.close()

    def insert_resume(self, meta):
        title = self.str_conv(meta['title'])
        site = urllib.quote_plus(meta['site'])
        #hoster = meta['hoster']
        point = meta['point']
        ex = "DELETE FROM resume WHERE hoster = '%s'" % (site)
        self.dbcur.execute(ex)
        ex = "INSERT INTO resume (title, hoster, point) VALUES (?, ?, ?)"
        self.dbcur.execute(ex, (title,site,point))

        try:
            self.db.commit() 
            cConfig().log('SQL INSERT resume Successfully') 
        except Exception, e:
            #print ('************* Error attempting to insert into %s cache table: %s ' % (table, e))
            cConfig().log('SQL ERROR INSERT') 
            pass
        self.db.close()  

    def insert_watched(self, meta):

        title = self.str_conv(meta['title'])
        print meta['title']
        site = urllib.quote_plus(meta['site'])
        ex = "INSERT INTO watched (title, site) VALUES (?, ?)"
        self.dbcur.execute(ex, (title,site))
        try:
            self.db.commit() 
            cConfig().log('SQL INSERT watched Successfully') 
        except Exception, e:
            #print ('************* Error attempting to insert into %s cache table: %s ' % (table, e))
            cConfig().log('SQL ERROR INSERT') 
            pass
        self.db.close()

    def get_history(self):
    
        sql_select = "SELECT * FROM history"

        try:    
            self.dbcur.execute(sql_select)
            #matchedrow = self.dbcur.fetchone()
            matchedrow = self.dbcur.fetchall()
            return matchedrow        
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return None
        self.dbcur.close()

    def get_resume(self, meta):
        title = self.str_conv(meta['title'])
        site = urllib.quote_plus(meta['site'])

        sql_select = "SELECT * FROM resume WHERE hoster = '%s'" % (site)

        try:    
            self.dbcur.execute(sql_select)
            #matchedrow = self.dbcur.fetchone()
            matchedrow = self.dbcur.fetchall()
            #cConfig().log(matchedrow)
            return matchedrow        
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return None
        self.dbcur.close()

    def get_watched(self, meta):        
        count = 0
        site = urllib.quote_plus(meta['site'])
        sql_select = "SELECT * FROM watched WHERE site = '%s'" % (site)

        try:    
            self.dbcur.execute(sql_select)
            #matchedrow = self.dbcur.fetchone()
            matchedrow = self.dbcur.fetchall()

            if matchedrow:
                count = 1
            else:
                count = 0    
            return count        
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return None
        self.dbcur.close()          

    def del_history(self):

        sql_delete = "DELETE FROM history;"

        try:    
            self.dbcur.execute(sql_delete)
            self.db.commit()
            cConfig().showInfo('bein', 'History deleted')
            cConfig().update()
            return False, False       
        except Exception, e:
            cConfig().log('SQL ERROR DELETE') 
            return False, False
        self.dbcur.close()  
       
    def del_watched(self, meta):
        site = urllib.quote_plus(meta['site'])
        sql_select = "DELETE FROM watched WHERE site = '%s'" % (site)

        try:    
            self.dbcur.execute(sql_select)
            self.db.commit()
            return False, False
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return False, False
        self.dbcur.close() 
        
    def del_resume(self, meta):
        site = urllib.quote_plus(meta['site'])

        sql_select = "DELETE FROM resume WHERE hoster = '%s'" % (site)

        try:    
            self.dbcur.execute(sql_select)
            self.db.commit()
            #cConfig().showInfo('bein', 'Resume supprimer')
            return False, False
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return False, False
        self.dbcur.close()

        
        
    #***********************************
    #   Favoris fonctions
    #***********************************
    
    def insert_favorite(self, meta):

        title = self.str_conv(meta['title'])
        siteurl = urllib.quote_plus(meta['siteurl'])      
        sIcon = meta['icon']
        
        try:
            ex = "INSERT INTO favorite (title, siteurl, site, fav, cat, icon, fanart) VALUES (?, ?, ?, ?, ?, ?, ?)"
            self.dbcur.execute(ex, (title,siteurl, meta['site'],meta['fav'],meta['cat'],sIcon,meta['fanart']))
            
            self.db.commit() 
            cConfig().log('SQL INSERT favorite Successfully') 
            cConfig().showInfo(meta['title'], 'Saved')
        except Exception, e:
            if 'UNIQUE constraint failed' in e.message:
                cConfig().showInfo(meta['title'], 'Already saved')
            cConfig().log('SQL ERROR INSERT') 
            pass
        self.db.close()
        
    def get_favorite(self):
    
        sql_select = "SELECT * FROM favorite"

        try:    
            self.dbcur.execute(sql_select)
            #matchedrow = self.dbcur.fetchone()
            matchedrow = self.dbcur.fetchall()
            return matchedrow        
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return None
        self.dbcur.close()

    def del_favorite(self, meta):
        siteUrl = urllib.quote_plus(meta['siteurl'])
        title = self.str_conv(meta['title'])
        title = title.replace("'", r"''")       

        sql_select = "DELETE FROM favorite WHERE siteurl = '%s' AND title = '%s'" % (siteUrl,title)

        try:    
            self.dbcur.execute(sql_select)
            self.db.commit()
            cConfig().showInfo('bein', 'Favoris supprimé')
            cConfig().update()
            return False, False
        except Exception, e:
            cConfig().log('SQL ERROR EXECUTE') 
            return False, False
        self.dbcur.close() 
        
    def getFav(self):
        oGui = cGui()
        fav_db = self.__sFile

        oInputParameterHandler = cInputParameterHandler()
        if (oInputParameterHandler.exist('sCat')):
            sCat = oInputParameterHandler.getValue('sCat')
        else:
            sCat = '5'

        if os.path.exists(fav_db): 
            watched = eval( open(fav_db).read() )

            items = []
            item = []
            for result in watched:

                sUrl = result

                items.append([sId, sFunction, sUrl])
                item.append(result)
                oOutputParameterHandler = cOutputParameterHandler()
                oOutputParameterHandler.addParameter('siteUrl', sUrl)
                oOutputParameterHandler.addParameter('sMovieTitle', sTitle)
                oOutputParameterHandler.addParameter('sThumbnail', 'False')
                
                if (sFunction == 'play'):
                    oHoster = cHosterGui().checkHoster(sUrl)
                    oOutputParameterHandler.addParameter('sHosterIdentifier', oHoster.getPluginIdentifier())
                    oOutputParameterHandler.addParameter('sFileName', oHoster.getFileName())
                    oOutputParameterHandler.addParameter('sMediaUrl', sUrl)

                if (sCategorie == sCat):
                    oGui.addFav(sId, sFunction, sTitle, 'mark.png', sUrl, oOutputParameterHandler)
               
            
            oGui.setEndOfDirectory()
        else: return
        return items


    def writeFavourites(self):

        oInputParameterHandler = cInputParameterHandler()
        sTitle = oInputParameterHandler.getValue('sTitle')
        sId = oInputParameterHandler.getValue('sId')
        sUrl = oInputParameterHandler.getValue('siteUrl')
        sFav = oInputParameterHandler.getValue('sFav')

        if (oInputParameterHandler.exist('sCat')):
            sCat = oInputParameterHandler.getValue('sCat')
        else:
            sCat = '5'

        sUrl = urllib.quote_plus(sUrl)
        fav_db = self.__sFile

        if not os.path.exists(fav_db):
            file(fav_db, "w").write("%r" % watched) 
            
        if os.path.exists(fav_db):
            watched = eval(open(fav_db).read() )
            watched[sUrl] = watched.get(sUrl) or []
            

        file(fav_db, "w").write("%r" % watched)
        cConfig().showInfo('Bookmark', sTitle)
        #fav_db.close()
    
    
