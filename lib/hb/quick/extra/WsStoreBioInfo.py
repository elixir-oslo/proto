# -*- coding: utf-8 -*-
import ftplib
from suds import WebFault
from suds.client import Client
from suds.wsse import *
from suds.sax.element import Element
from suds.sax.parser import Parser
from suds import WebFault
from xml.dom import minidom
import ast
import time
import urllib2
from urlparse import urlparse
import pickle
import copy_reg
from  quick.util.FtpUtils import upload_all
from storebioinfo import token_service, storage_service, public_storage_service, user_management_service
from storebioinfo.config import config
from glob import glob
#import logging
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)

messageSep = '##'
#http://www.bccs.uni.no/~hakont/files/UserMgntSchema.xsd
#targetNamespace="http://esysbio.org/common/schema"

#wssAssertionTokenMal = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xenc="http://www.w3.org/2001/04/xmlenc#"><soapenv:Header xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><wsse:Security soapenv:mustUnderstand="1"> %s %s </wsse:Security></soapenv:Header><soapenv:Body>
#<ns0:ListUsers xmlns:ns0="http://storebioinfo.norstore.no/service/UserManagement"/>   </soapenv:Body></soapenv:Envelope>'

#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)

class DomUtility:
    
    #@staticmethod
    #def getNodeValue( domTree, element, typeOfElement):
    #    for _, element in etree.iterparse(xml_file, tag='a'):
    #        print('%s -- %s' % (element.findtext('b'), element[1].text))
    #        element.clear()
    #        break
    
    @staticmethod
    def getNodeValues( domTree, element, typeOfElement):
        parentElem = domTree.getElementsByTagName(element)[0]
        childVal = len(parentElem.childNodes)>0
        valueList = []
        for node in domTree.getElementsByTagName(element):
            print node
            if typeOfElement == 'str':
                value = ''
                if childVal:
                    value = node.childNodes[0].nodeValue.encode('latin-1')# if childVal else ''
            elif typeOfElement == 'int':
                value = None
                if childVal:
                    value = int(node.childNodes[0].nodeValue)# if childVal else None
            elif typeOfElement == 'date':
                value = ''
                if childVal:
                    value = node.childNodes[0].nodeValue[:-10]# if childVal else ''
            elif typeOfElement == 'boolean':
                value = None
                if childVal:
                    value = bool(node.childNodes[0].nodeValue)# if childVal else None
            else:
                pass
            valueList.append(value)
        return valueList
    
    @staticmethod
    def getNodeValue( domTree, element, typeOfElement):
        parentElem = domTree.getElementsByTagName(element)[0]
        childVal = len(parentElem.childNodes)>0
        value = ''
        if typeOfElement == 'str':
            if childVal:
                value = parentElem.childNodes[0].nodeValue.encode('latin-1')# if childVal else ''
        elif typeOfElement == 'int':
            value = None
            if childVal:
                value = int(parentElem.childNodes[0].nodeValue)# if childVal else None
        elif typeOfElement == 'date':
            if childVal:
                value = parentElem.childNodes[0].nodeValue[:-10]# if childVal else ''
        elif typeOfElement == 'boolean':
            value = None
            if childVal:
                value = bool(parentElem.childNodes[0].nodeValue)# if childVal else None
        else:
            pass        
        return value
    @staticmethod
    def nodeExists(domTree, element):
        return len(domTree.getElementsByTagName(element))>0

class ParseXml(object):
    
    def getNodeValue(self, domTree, element, typeOfElement):
        parentElem = domTree.getElementsByTagName(element)[0]
        childVal = len(parentElem.childNodes)>0
        value = ''
        if typeOfElement == 'str':
            if childVal:
                value = parentElem.childNodes[0].nodeValue.encode('latin-1')# if childVal else ''
        elif typeOfElement == 'int':
            value = None
            if childVal:
                value = int(parentElem.childNodes[0].nodeValue)# if childVal else None
        elif typeOfElement == 'date':
            if childVal:
                value = parentElem.childNodes[0].nodeValue[:-10]# if childVal else ''
        elif typeOfElement == 'boolean':
            value = None
            if childVal:
                value = bool(parentElem.childNodes[0].nodeValue)# if childVal else None
        else:
            pass        
        return value
    
    def nodeExists(self, domTree, element):
        return len(domTree.getElementsByTagName(element))>0
    
    
    def ParseXmlResponse(self, wsName, domTree ):
        if wsName == 'ListProjects':
            ProjectsList = []
            for project in domTree.getElementsByTagName('Project'):
                ProjectsList.append(self.ParseProjectXml(project))
            return {'projects':ProjectsList}
            
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        elif wsName == '':
            pass
        else:
            pass
        
        
    def ParseQuotaXml(self, domTree):
        QuotaDict = dict()
        QuotaDict['Id'] = self.getNodeValue(domTree, 'Id', 'str')
        QuotaDict['Quota'] = self.getNodeValue(domTree, 'Quota', 'int')
        if DomUtility.nodeExists(domTree, 'Name'):
            QuotaDict['Name'] = DomUtility.getNodeValue(domTree, 'Name', 'str')
            
        if DomUtility.nodeExists(domTree, 'Created'):
            QuotaDict['Created'] = DomUtility.getNodeValue(domTree, 'Created', 'date')
            
        if DomUtility.nodeExists(domTree, 'Description'):
            QuotaDict['Description'] = DomUtility.getNodeValue(domTree, 'Description', 'str')
        
        if DomUtility.nodeExists(domTree, 'Creater'):
            QuotaDict['Creater'] = DomUtility.getNodeValue(domTree, 'Creater', 'str')
        
        if DomUtility.nodeExists(domTree, 'Projects'):
            projectList = []
            for project in  domTree.getElementsByTagName('Project'):
                tempDict = dict()
                tempDict['ProjectId'] = DomUtility.getNodeValue(project, 'ProjectId', 'str')
                tempDict['ProjectName'] = DomUtility.getNodeValue(project, 'ProjectName', 'str')
                tempDict['UsedQuota'] = DomUtility.getNodeValue(project, 'UsedQuota', 'int')
                projectList.append(tempDict)
            if len(projectList)>0:
                QuotaDict['Projects'] = projectList
        return QuotaDict
    
    def ParseProjectXml(self, domTree):
        ProjectDict = dict()

        if self.nodeExists(domTree, 'Id'):
            ProjectDict['Id'] = self.getNodeValue(domTree, 'Id', 'str')
        
        if self.nodeExists(domTree, 'Name'):
            ProjectDict['Name'] = self.getNodeValue(domTree, 'Name', 'str')
        
        if self.nodeExists(domTree, 'Created'):
            ProjectDict['Created'] = self.getNodeValue(domTree, 'Created', 'date')
        
        if self.nodeExists(domTree, 'Description'):
            ProjectDict['Description'] = self.getNodeValue(domTree, 'Description', 'str')
        
        if self.nodeExists(domTree, 'Creater'):
            ProjectDict['Creater'] = self.getNodeValue(domTree, 'Creater', 'str')
        
        if self.nodeExists(domTree, 'Quota'):
            ProjectDict['Quota'] = self.ParseQuotaXml(domTree.getElementsByTagName('Quota')[0])
        
        if self.nodeExists(domTree, 'DiskUsage'):
            ProjectDict['DiskUsage'] = self.getNodeValue(domTree, 'DiskUsage', 'int')
        
        if self.nodeExists(domTree, 'Restricted'):
            ProjectDict['Restricted'] = self.getNodeValue(domTree, 'Name', 'boolean')
        
        if self.nodeExists(domTree, 'ProjectMembers'):
            ProjectMemberList = []
            for ProjectMember in domTree.getElementsByTagName('ProjectMember'):            
                ProjectMemberList.append(self.ParseProjectMemberXml(ProjectMember))
            ProjectDict['ProjectMembers'] = ProjectMemberList
        
        if self.nodeExists(domTree, 'MessageBoard'):
            ProjectDict['MessageBoard'] = self.ParseMessageBoardXml(domTree.getElementsByTagName('MessageBoard')[0])
            
        if self.nodeExists(domTree, 'PublicationList'):
            PublicationListDomTree = domTree.getElementsByTagName('PublicationList')[0]
            publicationList = []
            for publication in PublicationListDomTree.getElementsByTagName('Publication'):            
                publicationList.append(self.ParsePublicationXml(publication))
            
            ProjectDict['PublicationList'] = publicationList
            
        return ProjectDict
    
    def ParseMessageBoardXml(self, domTree):
        MessageBoardDict = dict()
            
        MessageBoardDict['Id'] = self.getNodeValue(domTree, 'Id', 'str')

        if self.nodeExists(domTree, 'Owner'):
            MessageBoardDict['Owner'] = self.getNodeValue(domTree, 'Owner', 'str')
        
        if self.nodeExists(domTree, 'Messages'):
            MessageList = []
            for message in domTree.getElementsByTagName('Message'):
                MessageList.append(self.ParseMessageXml(message))
            MessageBoardDict['Messages'] = MessageList
        
        return MessageBoardDict
    
    def ParseMessageXml(self, domTree):
        messageDict = dict()

        if self.nodeExists(domTree, 'Id'):
            messageDict['Id'] = self.getNodeValue(domTree, 'Id', 'str')
        
        if self.nodeExists(domTree, 'CreatedBy'):
            messageDict['CreatedBy'] = self.getNodeValue(domTree, 'CreatedBy', 'str')
        
        if self.nodeExists(domTree, 'Created'):
            messageDict['Created'] = self.getNodeValue(domTree, 'Created', 'date')
        
        if self.nodeExists(domTree, 'Read'):
            messageDict['Read'] = self.getNodeValue(domTree, 'Read', 'boolean')
        
        if self.nodeExists(domTree, 'MessageEnum'):
            messageDict['MessageEnum'] = self.getNodeValue(domTree, 'MessageEnum', 'str')
        
        if self.nodeExists(domTree, 'Recipient'):
            messageDict['Recipient'] = self.getNodeValue(domTree, 'Recipient', 'str')
        
        if self.nodeExists(domTree, 'Subject'):
            messageDict['Subject'] = self.getNodeValue(domTree, 'Subject', 'str')
        
        if self.nodeExists(domTree, 'Issuer'):
            messageDict['Issuer'] = self.getNodeValue(domTree, 'Issuer', 'str')
        
        if self.nodeExists(domTree, 'IssuerId'):
            messageDict['IssuerId'] = self.getNodeValue(domTree, 'IssuerId', 'str')
        
        if self.nodeExists(domTree, 'ConfimatioId'):
            messageDict['ConfimatioId'] = self.getNodeValue(domTree, 'ConfimatioId', 'str')
        else:
            messageDict['FreeText'] = self.getNodeValue(domTree, 'FreeText', 'str')
        
    def ParseMemberXml(self, domTree):
        memberDict = dict()
        
        if self.nodeExists(domTree, 'Id'):
            memberDict['Id'] = self.getNodeValue(domTree, 'Id', 'str')
        
        if self.nodeExists(domTree, 'Username'):
            memberDict['Username'] = self.getNodeValue(domTree, 'Username', 'str')
        
        if self.nodeExists(domTree, 'Email'):
            memberDict['Email'] = self.getNodeValue(domTree, 'Email', 'str')

        return memberDict

    def ParseProjectMemberXml(self, domTree):
        projectMemberDict = self.ParseMemberXml(domTree)
        #roleList = []
        #for role in domTree.getElementsByTagName('Role'):
        #    roleList.append(self.getNodeValue(role, 'Role', 'str'))
        projectMemberDict['Roles'] = self.getNodeValue(domTree, 'Roles', 'str')
        return projectMemberDict
    
    def ParsePublicationXml(self, domTree):
        publicationDict = dict()
        
        publicationDict['Title'] = self.getNodeValue(domTree, 'Title', 'str')
        publicationDict['MainAuthor'] = self.getNodeValue(domTree, 'MainAuthor', 'str')
        publicationDict['Journal'] = self.getNodeValue(domTree, 'Journal', 'str')
        publicationDict['Year'] = self.getNodeValue(domTree, 'Year', 'int')
        
        if self.nodeExists(domTree, 'URL'):
            publicationDict['URL'] = self.getNodeValue(domTree, 'URL', 'str')
        
        if self.nodeExists(domTree, 'Abstract'):
            publicationDict['Abstract'] = self.getNodeValue(domTree, 'Abstract', 'str')
        
        return publicationDict
    
    def ParseUserXml(self, domTree):
        userDict = dict()
        if self.nodeExists(domTree, 'Id'):
            userDict['Id'] = self.getNodeValue(domTree, 'Id', 'str')
        if self.nodeExists(domTree, 'Firstname'):
            userDict['Firstname'] = self.getNodeValue(domTree, 'Firstname', 'str')
        if self.nodeExists(domTree, 'Surname'):
            userDict['Surname'] = self.getNodeValue(domTree, 'Surname', 'str')
        if self.nodeExists(domTree, 'Email'):
            userDict['Email'] = self.getNodeValue(domTree, 'Email', 'str')
        if self.nodeExists(domTree, 'Username'):
            userDict['Username'] = self.getNodeValue(domTree, 'Username', 'str')
        if self.nodeExists(domTree, 'RestrictedProfile'):
            userDict['RestrictedProfile'] = self.getNodeValue(domTree, 'RestrictedProfile', 'boolean')
        if self.nodeExists(domTree, 'MessageBoard'):
            
            userDict['MessageBoard'] = self.ParseMessageBoardXml(domTree.getElementsByTagName('MessageBoard')[0])
        if self.nodeExists(domTree, 'SystemRoles'):
            roleList = []
            for sysRole in domTree.getElementsByTagName('SystemRoles'):
                for role in sysRole.getElementsByTagName('Role'):
                    roleList.append(self.getNodeValue(role, 'Role', 'str'))
            userDict['SystemRoles'] = roleList
            
        if self.nodeExists(domTree, 'RoleInProjectList'):
            roleInProjectList = []
            for RoleInProject in domTree.getElementsByTagName('RoleInProject'):
                roleInProjectList.append(self.ParseRoleInProjectXml(RoleInProject))
            userDict['RoleInProjectList'] = roleInProjectList
            
    def ParseRoleInProjectXml(self, domTree):
        roleInProjectDict = dict()
        
        roleInProjectDict['ProjectId'] = self.getNodeValue(domTree, 'ProjectId', 'str')
        if self.nodeExists(domTree, 'Projectname'):
            roleInProjectDict['Projectname'] = self.getNodeValue(domTree, 'Projectname', 'str')
        if self.nodeExists(domTree, 'Created'):
            roleInProjectDict['Created'] = self.getNodeValue(domTree, 'Created', 'date')
        roleList = []
        for role in domTree.getElementsByTagName('Role'):
            roleList.append(self.getNodeValue(role, 'Role', 'str'))
        roleInProjectDict['Roles'] = roleList
        
        return roleInProjectDict
    
    
    def ParseDataSetType(self, domTree):
        dataSetTypeList = []
        
        for dataSetTypeEL in domTree.getElementsByTagName('DataSetTypeEL'):
            tmpDict = dict()
            tmpDict['Name'] = self.getNodeValue(dataSetTypeEL, 'Name', 'str')
            for subtype in dataSetTypeEL.getElementsByTagName('SubTypes'):
                tmpDict['subNames'] = DomUtility.getNodeValues(subtype, 'Name', 'str')
            dataSetTypeList.append(tmpDict)
        
        return dataSetTypeList    
        
    
class WsPublicDatastorageService(object):
    WSDL_PUBLIC_DATA_STORAGE_SERVICE = 'https://storebioinfo.norstore.no/wsdl/wsdl-ds/DataStorageService_test.xml'
    WS_NON_SEC_XML_TEMPLATE = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xenc="http://www.w3.org/2001/04/xmlenc#"><soapenv:Body xmlns:user="http://storebioinfo.norstore.no/service/UserManagement" xmlns:user1="http://storebioinfo.norstore.no/schema/usermanagement" xmlns:user2="http://esysbio.org/common/schema" xmlns:dat="http://storebioinfo.norstore.no/service/datastorage" xmlns:dat1="http://storebioinfo.norstore.no/schema/datastorage"> %s </soapenv:Body></soapenv:Envelope>'
     
    def __init__(self):
        self.dataStorageClient = Client(WsPublicDatastorageService.WSDL_PUBLIC_DATA_STORAGE_SERVICE, cache=None)

    def _fetchWsResponse(self, bodyXml, webService, operation):
        xmlMessage = WsPublicDatastorageService.WS_NON_SEC_XML_TEMPLATE % (bodyXml)
        print xmlMessage, '\n\n'
        #print repr(self.dataStorageClient.service)
       
        wsResponse =  getattr(self.dataStorageClient.service[webService], operation)(__inject={'msg':xmlMessage})
       
        #xmlString = self.ExtractXml(wsResponse)
        #print xmlString
        #xmlDocument = minidom.parseString(xmlString)
       
        #print xmlDocument.toxml().encode('latin-1')+'\n\n\n\n\n\n\n\###############################################n\n\n\n\n\n\n\n\n'
        #open('manualXml.xml','w').write(xmlMessage+'\n\n\n\n\n\n\n'+xmlString)
        return wsResponse

    def ExtractXml(self, wsResponseString):
        if wsResponseString[:5]=='<?xml':
            return wsResponseString
        return wsResponseString[wsResponseString.find('<?xml'):wsResponseString.rfind('--MIMEBoundary')]

   
    def ListPublicDataSets(self):
        return public_storage_service.get_public_dataset_list(include_meta_data='true', include_sub_type='true')
        
    def GetPublicDataSet(self, dataSetId):
        GET_PUBLIC_DATASET_MAL='<dat:GetPublicDataSet><DataSetId>%s</DataSetId></dat:GetPublicDataSet>'
        bodyXml = GET_PUBLIC_DATASET_MAL  % (dataSetId)
        dataSet = self._fetchWsResponse(bodyXml, 'PublicDataStorageService', 'GetPublicDataSet')
        return dataSet
    
    def GetPublicResource(self, dataSetId, SubEntryLevel, SubEntryParent, resourceId=None, resourceName=None):
        GET_RESOURCE_BY_ID_OR_NAME_MAL = '<dat:GetPublicResource><DataSetId>%s</DataSetId>%s<dat1:ReturnFilter><dat1:SubEntryLevel>%i</dat1:SubEntryLevel><dat1:SubEntryParent>%s</dat1:SubEntryParent></dat1:ReturnFilter></dat:GetPublicResource>'
        
        contentStr = ''
        if resourceId:
            contentStr += '<ResourceId>%s</ResourceId>' % resourceId
        else:
            contentStr += '<ResourceName>%s</ResourceName>' % resourceName
            
        bodyXml = GET_RESOURCE_BY_ID_OR_NAME_MAL % (dataSetId, contentStr, SubEntryLevel, SubEntryParent)
        return self._fetchWsResponse(bodyXml, 'PublicDataStorageService', 'GetPublicResource')
    
    
    def GetFilePreviewFromPublicDataset(self, datasetId, SubTypeFilePair):
        GET_FILE_PREVIEW_MAL = """<dat:GetFilePreviewFromPublicDataset><DatasetId>%s</DatasetId><dat:SubTypeFilePair><Subtype>%s</Subtype><FileToExtract>%s</FileToExtract></dat:SubTypeFilePair></dat:GetFilePreviewFromPublicDataset>"""
        
        if SubTypeFilePair[0].find('(')>0:
            SubTypeFilePair[0] = SubTypeFilePair[0].split('(')[0].strip()# if SubTypeFilePair[0].find('(')>0
        
        bodyXml = GET_FILE_PREVIEW_MAL % (tuple([datasetId] + SubTypeFilePair))
        tmpResult =  self._fetchWsResponse(bodyXml, 'PublicDataStorageService', 'GetFilePreviewFromPublicDataSet')
        
        count = 0
        while hasattr(tmpResult, 'PreviewStaus') and count<20:
            time.sleep(5)
            tmpResult =  self._fetchWsResponse(bodyXml, 'PublicDataStorageService', 'GetFilePreviewFromPublicDataSet')
            count+=1
        
        if count == 20:
            return'Not able to fetch FilePreview'
        
        return tmpResult
            
    
    def GetFileUrlsFromDataSet2(self, datasetId, subTypeFilePairs, fileEncoding={'TransferMode':'FTP_URL', 'ArchiveMethod':'PLAIN_TEXT'}):
        
        transferHandler = public_storage_service.start_public_file_transfer(datasetId, subTypeFilePairs[0]['Subtype'], subTypeFilePairs[0]['FileToExtract'])
        print transferHandler
        time.sleep(6)
        status = public_storage_service.check_public_transfer_status(transferHandler)
        count = 0
        while not status.startswith('ftp') and count<20:
            time.sleep(6)
            count+=1
            status = public_storage_service.check_public_transfer_status(transferHandler)
        #print 'Url: ', status
        #print urllib2.urlopen(status).read()
        return status if status.startswith('ftp') else 'could not access url'    
    
    def getSubTrackName(self, userName, liste):
        print liste
        result = []
        datasetList = []
        if len(liste) == 1:
            publicDatasets = self.ListPublicDataSets()
            
            for dataset in publicDatasets:
                datasetList.append(dataset.name+',, ('+dataset.id+')')    
            
        elif len(liste) ==2:
            dataset_id = liste[1].split('(')[-1].split(')')[0].strip()
            dataset = [dSet for dSet in self.ListPublicDataSets() if dSet.id == dataset_id][0]
            
            #token = token_service.get_token('kaitre', 'katrno')
            #print data
            #dataset = storage_service.get_dataset(token,dataset_id)
            #print dataset
            print 'dataset.subTypeList: ', dataset.subTypeList
            datasetList =  dataset.subTypeList #[v+' (%s)' % dataset.name for v in dataset.subTypeList]#[dataset.type+' (%s)' % dataset.name]
            #dataset = self.GetPublicDataSet()
            #datasetList = [resource.type+' (%s)' % resource.name for resource in dataset if resource.state == 'COMPLETE'] #.Resource
        
        else:
            resType = liste[2]#.split('(')[0].strip()
            if len(liste)==3:
                requestStr = '' #if len(liste)==3
            else:
                requestStr = '/'.join(liste[3:][:]).replace(',FOLDER','')
                if requestStr.find(',FILE')>0:
                    return []
                
            
            dataSetId = liste[1].split('(')[1].split(')')[0].strip()
            resName = liste[2].split('(')[-1].split(')')[0].strip()
            
            print dataSetId, resType, requestStr, 
            folderContent = public_storage_service.get_folder_content(dataSetId, resType, requestStr)
            #storage_service.get_folder_content(token, dataSetId, resType, requestStr)
            print folderContent
            #ResourceElem = self.GetPublicResource(dataSetId, 0, requestStr, resourceName=resName)
            #if hasattr(ResourceElem, 'SubEntries'):
            datasetList = [item for item in folderContent if item.find(',FOLDER')>0]
            if len(datasetList)==0:
                datasetList = folderContent
            
                    
        for i in datasetList:
            result.append((str(i),str(i),False))
        return result

  
class WsStoreBioInfo(ParseXml):
    WS_XML_TEMPLATE = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xenc="http://www.w3.org/2001/04/xmlenc#"><soapenv:Header xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"><wsse:Security soapenv:mustUnderstand="1"> %s %s </wsse:Security></soapenv:Header><soapenv:Body xmlns:user="http://storebioinfo.norstore.no/service/UserManagement" xmlns:user1="http://storebioinfo.norstore.no/schema/usermanagement" xmlns:user2="http://esysbio.org/common/schema" xmlns:dat="http://storebioinfo.norstore.no/service/datastorage" xmlns:dat1="http://storebioinfo.norstore.no/schema/datastorage"> %s </soapenv:Body></soapenv:Envelope>'
    def __init__(self, userName, password):
        start = time.time()
        self.client = Client('https://storebioinfo.norstore.no/wsdl/wsdl-sts/WS-Trust_Suds_SSL.xml', cache=None)#'http://www.bccs.uni.no/~hakont/files/WS-Trust_SudsOsl.wsdl'
        #https://storebioinfo.norstore.no/wsdl/wsdl-sts/WS-Trust_SudsOslSSL.xml
        #print 'after self.client = Client("https://storeb...:   ' , time.time()-start
        self.userName = userName
        self.userPwd = password
        self.wsToken = token_service.get_token(self.userName, self.userPwd)
        
    
    def doAuthentication(self, userName, password):
        self.userName = userName
        self.userPwd = password
        if True:
            self.wsToken = token_service.get_token(self.userName, self.userPwd)
        #req_type = self.client.factory.create('ns0:RequestTypeEnum')
        ##print 'after self.client.factory.create("ns0:RequestTypeEnum"):   ' , time.time()-start
        #tok_type = 'http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.1#SAMLV1.1'
        #key_type = self.client.factory.create('ns0:KeyTypeEnum')
        #key_size = 256
        #key_alg = 'http://schemas.xmlsoap.org/ws/2005/02/trust/CK/PSHA1'
        #
        #security = Security()
        #utoken = UsernameToken(userName, password)
        #utoken.setnonce()
        #utoken.setcreated()
        ##print 'after utoken.setcreated():   ' , time.time()-start
        #timeStamp = Timestamp()
        #security.tokens.append(timeStamp)
        #security.tokens.append(utoken)
        #self.client.set_options(wsse=security)
        #self.client.set_options(retxml=True) 
        ##print 'before wsResponse = self.client.service.IssueToken(req_type[:   ' , time.time()-start
        #wsResponse = self.client.service.IssueToken(req_type["http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue"],tok_type,key_type["http://docs.oasis-open.org/ws-sx/ws-trust/200512/SymmetricKey"],key_size,key_alg)
        ##print 'after wsResponse = self.client.service.IssueToken(req_type[:   ' , time.time()-start
        #self.wsToken = wsResponse[wsResponse.find('<Assertion'):wsResponse.find('</Assertion')]+'</Assertion>'
        #self.timeStampValue = wsResponse[wsResponse.find('<wsu:Timestamp '):wsResponse.find('</wsse:Security>')]
        
    #fixme
    def handleAuthUpdate(self, userName, password, UserAuthentication): 
        if False:#UserAuthentication.get(userName):
            self.wsToken, self.timeStampValue = UserAuthentication[userName]
            print 'runObject.timeStampValue', self.timeStampValue
            self.doAuthentication(userName, password)
        
        else:
            self.doAuthentication(userName, password)
            UserAuthentication[userName] = [(self.wsToken, self.timeStampValue), time.time()]
            
        return UserAuthentication
        
    def ExtractXml(self, wsResponseString):
        if wsResponseString[:5]=='<?xml':
            return wsResponseString
        return wsResponseString[wsResponseString.find('<?xml'):wsResponseString.rfind('--MIMEBoundary')]
        
class WsDataStorageService(WsStoreBioInfo):
    #https://storebioinfo.norstore.no/wsdl/wsdl-ds/DataStorageServiceSSL.xml
    #https://storebioinfo.norstore.no/wsdl/wsdl-ds/DataStorageService_test.wsdl
    #file:///Users/trengere/wsdlTing/DataStorageService_test.wsdl
    #https://storebioinfo.norstore.no/wsdl/wsdl-ds/DataStorageServiceSSL_2.xml
    WSDL_DATA_STORAGE_SERVICE = config.DATA_STORAGE_WSDL # 'https://storebioinfo.norstore.no/wsdl/wsdl-ds/DataStorageService_test.xml'#'https://storebioinfo.norstore.no/wsdl/wsdl-ds/DataStorageService_test.wsdl'#'https://storebioinfo.norstore.no/wsdl/wsdl-ds/DataStorageServiceSSL_2.xml'
    
    def __init__(self, userName, password):
        super(WsDataStorageService, self).__init__(userName, password)
        self.dataStorageClient = Client(config.DATA_STORAGE_WSDL, cache=None)
        self.dataStorageClient.set_options(retxml=True)
    
    
    def _fetchWsResponse(self, bodyXml, webService, operation):
        
        xmlMessage = WsStoreBioInfo.WS_XML_TEMPLATE % (self.wsToken.timeStampXml, self.wsToken, bodyXml)
        if operation in ['AddDataSet','GetResourceByIdOrName', 'AddMetaDataToDataSet']:
            print xmlMessage, '\n\n'
        
        try:
            wsResponse =  getattr(self.dataStorageClient.service[webService], operation)(__inject={'msg':xmlMessage})
        except: 
            print 'operasjonen feilet: ', self.dataStorageClient.last_received()
            raise Exception
        
        print 'operasjon gikk bra: ',operation
        xmlString = self.ExtractXml(wsResponse)
        return unicode(xmlString, encoding='utf-8')#, errors='ignore', 
    
    #########
    def createDataset(self, name, description, quotaId, Type, ProjectAccessControlList):
        CREATE_DATA_SET_MAL = '<dat:CreateDataset> <Name>%s</Name> <Description>%s</Description> <QuotaId>%s</QuotaId> <Type>%s</Type> %s </dat:CreateDataset>'
        PROJECT_ACCESS_MAL ='<dat1:ProjectId>%s</dat1:ProjectId><dat1:UseDefaultPolicy>%s</dat1:UseDefaultPolicy>'
        ProjectAccessControlList_MAL = '<ProjectAccessControlList>%s</ProjectAccessControlList>'
        projAccString = ''
        if ProjectAccessControlList:
            projaccList = []
            for projAccTuple in ProjectAccessControlList:
                projaccList.append(PROJECT_ACCESS_MAL % projAccTuple)
            projAccString = ProjectAccessControlList_MAL % ('\n'.join(projaccList))
        
        bodyXml = CREATE_DATA_SET_MAL % (name, description, quotaId, Type, projAccString)
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'CreateDataset')
    
    def openDataset(self, datasetId):
        OPEN_DATASET_MAL = '<dat:OpenDataset><DatasetId>%s</DatasetId> </dat:OpenDataset>'
        bodyXml = OPEN_DATASET_MAL % (datasetId)
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'OpenDataset')
    
    def closeEDataset(self, datasetId):
        CLOSE_DATASET_MAL = '<dat:CloseDataset><DatasetId>%s</DatasetId> </dat:CloseDataset>'
        bodyXml = OPEN_DATASET_MAL % (datasetId)
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'CloseDataset')
        
    def addRemoteContent(self, datasetId, URLTypeMaps, userName, password):
        ADD_REMOTE_CONTENT_MAL = """<dat:AddRemoteContent><DatasetId>%s</DatasetId>
        <ResourceList> <URLTypeMap>%s</URLTypeMap>%s</ResourceList> </dat:AddRemoteContent>"""
        
        URLTypeMapString = '\n'.join(['<Url>%s</Url> <SubType>%s</SubType>' % i for i in URLTypeMaps])
        authString=''
        if userName:
            authString = '\n<Username>%s</Username>' % userName# if userName else ''
        if password:
            authString+= '\n<Password>%s</Password>' % password# if password else ''
        bodyXml = ADD_REMOTE_CONTENT_MAL % (datasetId, URLTypeMapString, authString)
        
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'AddRemoteContent')
    
    def getMetaKeys(self, datasetId):
        GET_META_KEYS_MAL = '<dat:GetMetaKeys><DatasetId>%s</DatasetId> </dat:GetMetaKeys>'
        bodyXml = GET_META_KEYS_MAL % (datasetId)
        
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'GetMetaKeys')
    
    def GetMetaData(self, datasetId, metaKeys):
        GET_META_DATA_MAL = '<dat:GetMetaData><DatasetId>%s</DatasetId> <MetaKeys>%s</MetaKeys></dat:GetMetaData>'
        
        metaKeysString = '\n'.join(['<Key>%s</Key>' % k for k in metaKeys])
        bodyXml = GET_META_DATA_MAL % (datasetId, metaKeysString)
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'GetMetaData')
        
   
    def GetFolderContent(self, datasetId, SubType, ParentPath=None):
        GET_FOLDER_CONTENT_MAL = '<dat:GetFolderContent><DatasetId>%s</DatasetId><SubType>%s</SubType>%s</dat:GetFolderContent>'
        if ParentPath is None:
            ParentPathStr = '<ParentPath>%s</ParentPath>' % SubType# if ParentPath is None
        else:
            ParentPathStr = '<ParentPath>%s</ParentPath>' % ParentPath
        bodyXml = GET_FOLDER_CONTENT_MAL % (datasetId, SubType, ParentPathStr)
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'GetFolderContent')
    

    
    def StartDatasetTransfer(self, datasetId, subTypes, notifyByEmail, LocalFtpServer=None, remoteUrl=None ):
        dataset_xml = '<DatasetId>%s</DatasetId>'%dataset_id
        sub_type_xml ='<Subtype>%s</Subtype>'%sub_type
        file_to_extract_xml =' <FileToExtract>%s</FileToExtract>'%file_to_extract
        
        sub_type_file_pair_xml ='<dat:SubTypeFilePair>%s%s</dat:SubTypeFilePair>'%(sub_type_xml,file_to_extract_xml)
        
        body_xml = '<dat:StartFileTransfer>%s%s<NotifyByEmail>false</NotifyByEmail></dat:StartFileTransfer>'%(dataset_xml,sub_type_file_pair_xml)
        
        response_xml = invoke_webservice_method(ws_client, 'DataStorageService', 'StartFileTransfer', body_xml, token)
        transfer_handler = response_xml.getElementsByTagName("TransferHandler")[0].childNodes[0].nodeValue.encode('latin-1')       
        
        #START_DATASET_TRANSFER_MAL = """<dat:StartDatasetTransfer>
        #<DatasetId>%s</DatasetId> <!--1 or more repetitions:-->  <Subtype>%s</Subtype>
        #<!--You have a CHOICE of the next 2 items at this level--> <!--Optional:-->
        #<LocalFtpServer>true</LocalFtpServer>
        #<RemoteUrl><Schema>%s</Schema><Hostname>%s</Hostname> <Folder>%s</Folder><!--Optional:--> <Username>%s</Username>
        #<!--Optional:--> <Password>%s</Password></RemoteUrl>
        #<NotifyByEmail>%s</NotifyByEmail>
        #</dat:StartDatasetTransfer>"""
        #
        #subTypesStr = '\n'.join([ '<Subtype>%s</Subtype>' % sub for sub in subTypes])
        return transfer_handler   
    #########
    
    
    #done??    
    def ListDataSetsForUser(self):
        
        return storage_service.get_data_set_list(self.wsToken, False, False, self.dataStorageClient)
        
    
    #done??    
    def ListTypesOfDataSet(self):
        typesOfDataSetL = storage_service.list_types_of_dataset(self.wsToken, self.dataStorageClient)
        return repr(typesOfDataSetL)
    
    
    def getDatasetsByProject(self, projId, includeMetaData, includeSubTypes):
        return storage_service.get_datasets_by_project(self.wsToken,projId,includeMetaData, includeSubTypes, self.dataStorageClient)
        
    
    #def AddResource(self, name,  quotaId, ResourceTypeEnum, description=None, UseDefaultProjectPolicy='false', InUserContext='false',localResource=None, dataSetId=None,  tagList=None, attachment=None,  projectAccessControlList=None):
    #    ADD_RESOURCE_MAL = '<dat:AddResource><Name>%s</Name>%s<UseDefaultProjectPolicy>%s</UseDefaultProjectPolicy><InUserContext>%s</InUserContext><QuotaId>%s</QuotaId>%s %s <dat1:ResourceTypeEnum>%s</dat1:ResourceTypeEnum>%s %s %s</dat:AddResource>'
    #    descriptionStr=''
    #    if description:
    #        descriptionStr+= '<Description>%s</Description>' % description
    #     
    #    localResourceStr = ''
    #    if localResource:
    #       localResourceStr+= '<LocalResource>%s</LocalResource>' % localResource
    #    
    #    dataSetIdStr=''
    #    if dataSetId:
    #        dataSetIdStr+= '<DataSetId>?</DataSetId>' % dataSetId
    #    
    #    tagListStr=''
    #    if tagList:
    #        tagListStr+= '<dat1:TagList>'
    #        for tagValue in tagList:
    #            tagListStr+= '<dat1:TagValue>%s</dat1:TagValue>' % tagValue
    #        tagListStr+= '</dat1:TagList>'
    #    attachmentStr = ''
    #    if attachment:
    #        attachmentStr += '<dat1:Attachment>'
    #        if 'RemoteFile' in attachment:
    #            attachmentStr += '<dat1:RemoteFile><dat1:Url>%s</dat1:Url>' % attachment['Url']
    #            if 'Username' in attachment['RemoteFile']: 
    #                attachmentStr += '<dat1:Username>%s</dat1:Username>' % attachment['RemoteFile']['Username']
    #            if 'Password' in attachment['RemoteFile']: 
    #                attachmentStr += '' '<dat1:Password>%s</dat1:Password>' % attachment['RemoteFile']['Password']
    #            attachmentStr += '<dat1:RemoteFile>'
    #            
    #        else:
    #            attachmentStr += '<dat1:FileInfo>'
    #            if  'FileName' in attachment['FileInfo']: 
    #                attachmentStr += '<dat1:FileName>%s</dat1:FileName>' % attachment['FileInfo']['FileName']
    #            attachmentStr +='<dat1:BinaryData xm:contentType="application/?">%s</dat1:BinaryData></dat1:FileInfo>' % attachment['FileInfo']['BinaryData']
    #        attachmentStr += '</dat1:Attachment>'
    #  
    #    projectAccessControlListStr=''
    #    if projectAccessControlList:
    #        projectAccessControlListStr+='<ProjectAccessControlList><dat1:ProjectId>%s</dat1:ProjectId><dat1:UseDefaultPolicy>%s</dat1:UseDefaultPolicy>' % (projectAccessControlList['ProjectId'], projectAccessControlList['UseDefaultPolicy'])
    #        if 'RolePermissions' in projectAccessControlList:
    #            for RolePermission in projectAccessControlList['RolePermissions']:
    #                projectAccessControlListStr += '<dat1:RolePermission><dat1:Role>%s</dat1:Role><dat1:Permission>%s</dat1:Permission></dat1:RolePermission>' % (RolePermission['Role'], RolePermission['Permission'])    
    #        projectAccessControlListStr+= '</ProjectAccessControlList>'
    #    
    #    bodyXml = ADD_RESOURCE_MAL % (name, descriptionStr, UseDefaultProjectPolicy, InUserContext, quotaId, localResourceStr, dataSetIdStr, ResourceTypeEnum, tagListStr, attachmentStr,  projectAccessControlListStr)
    #    return self._fetchWsResponse(bodyXml, 'DataStorageService', 'AddResource') 
    #


    #done
    def ApproveDataset(self, DataSetId):
        storage_service.approve_dataset(self.wsToken, DataSetId, self.dataStorageClient)
        #APPROVE_DATASET_MAL = '<dat:ApproveDataset><DataSetId>%s</DataSetId></dat:ApproveDataset>'
        #bodyXml = APPROVE_DATASET_MAL % (DataSetId)
        #return self._fetchWsResponse(bodyXml, 'DataStorageService', 'ApproveDataSet')
    
    def CreateDataSet(self, name, quotaId, dataset_type, description=None, projectAccessControlList=None):
        try:
            a = storage_service.create_dataset(self.wsToken, name, description, quotaId, dataset_type, projectAccessControlList[0] , self.dataStorageClient)
            return 'ok'
        except:
            return 'something went wrong...'
    
    
    def AddDataSetWithFTP(self, name, quotaId, type, localRootDir, description=None, projectAccessControlList=None):
        subType = 'Track'
        ADD_DATASET_MAL = """<dat:AddDataset><Name>%s</Name>%s<QuotaId>%s</QuotaId><Type>%s</Type>%s
                        <SubTypeToAddList><SubType>%s</SubType></SubTypeToAddList></dat:AddDataset>"""
        if description:    
            description = '<Description>%s</Description>' % description# if description
        else:
            description = ''
        
        if  projectAccessControlList:
            projAccMal = '<ProjectAccessControlList><dat1:ProjectId>%s</dat1:ProjectId><dat1:UseDefaultPolicy>%s</dat1:UseDefaultPolicy>%s</ProjectAccessControlList>'
            roleStr = ''
            if len(projectAccessControlList)>2:
                roleMal = '<dat1:RolePermission><dat1:Role>%s</dat1:Role><dat1:Permission>%s</dat1:Permission>'
                for row in projectAccessControlList[2]:
                    roleStr += roleMal % (row[0], row[1])
                
            projAccStr = projAccMal % (projectAccessControlList[0], projectAccessControlList[1], roleStr)    
        else:
            projAccStr = ''
        
        bodyXml = ADD_DATASET_MAL % (name, description, quotaId, type, projAccStr, subType)
        responseXml =  self._fetchWsResponse(bodyXml, 'DataStorageService', 'AddDataSet')
        print 'finished with WS AddDataSet'
        ftpLocalResourceUrl = responseXml.split('LocalResourceURL>')[1].split('<')[0].strip()
        datasetId = responseXml.split('<Id>')[1].split('<')[0].strip()
        
        urlParsed = urlparse(ftpLocalResourceUrl)
        
        print 'finished with URL parse'
        
        filePathList = upload_all(urlParsed.hostname,
                urlParsed.port,
                urlParsed.username, 
                urlParsed.password,
                localRootDir, 
                base_remote_dir=subType, 
                walk=True)
        response = self.ApproveDataset(datasetId)
        
        tiList = self.getTrackInfoForFiles(filePathList)
        if tiList!= None:
            self.AddMetaDataToDataSet(datasetId, tiList)
        print response
        return 'Finished adding data with FTP'
        
    
    def getTrackInfoForFiles(self, filepathList):
        from gold.description.TrackInfo import TrackInfo
        try:
            trackNames = [['StoreBioInfo']+ v.split('standardizedTracks/')[1].split('/')[:-1] for v in filepathList]
            results = []
            for tName in trackNames:
                ti = TrackInfo(tName[1], tName[2:])
                ti.trackName = ['StoreBioInfo']+ti.trackName
            
                results.append(ti.getStrReprOfAttrDict())
        
            return zip(['/'.join(['StoreBioInfo'] + v[1:]) for v in trackNames],results)
        except:
            return None
        
        
    
    def AddDataSet(self, name, quotaId, type, url ,resourceType, userName, password, description=None, projectAccessControlList=None):
        ADD_DATASET_MAL = """<dat:AddDataset><Name>%s</Name>%s<QuotaId>%s</QuotaId><Type>%s</Type>%s
            <ResourceList><URLTypeMap><Url>%s</Url><ResourceType>%s</ResourceType></URLTypeMap>
            <Username>%s</Username><Password>%s</Password></ResourceList></dat:AddDataset>"""
        if description:
            description = '<Description>%s</Description>' % description
        else:
            description = ''
        
        if  projectAccessControlList:
            projAccMal = '<ProjectAccessControlList><dat1:ProjectId>%s</dat1:ProjectId><dat1:UseDefaultPolicy>%s</dat1:UseDefaultPolicy>%s</ProjectAccessControlList>'
            roleStr = ''
            if len(projectAccessControlList)>2:
                roleMal = '<dat1:RolePermission><dat1:Role>%s</dat1:Role><dat1:Permission>%s</dat1:Permission>'
                for row in projectAccessControlList[2]:
                    roleStr += roleMal % (row[0], row[1])
                
            projAccStr = projAccMal % (projectAccessControlList[0], projectAccessControlList[1], roleStr)    
        else:
            projAccStr = ''
        
        bodyXml = ADD_DATASET_MAL % (name, description, quotaId, type, projAccStr, url, resourceType, userName, password)
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'AddDataSet')
    
    
    
    def AddFileToDataSet(self, dataSetId, subType, pathInSubtype, localDir, userName, password):
        
        FtpAddress = storage_service.open_dataset(self.wsToken,dataSetId, self.dataStorageClient)
        urlParsed = urlparse(FtpAddress)
        
        filePathList = upload_all(urlParsed.hostname,
                urlParsed.port,
                urlParsed.username, 
                urlParsed.password,
                localDir, 
                base_remote_dir=subType, 
                walk=True)

        storage_service.close_dataset(dataSetId, self.dataStorageClient)
        
        tiList = self.getTrackInfoForFiles(filePathList)
        if tiList!= None:
            self.AddMetaDataToDataSet(datasetId, tiList)
        
        return 'Finished adding data with FTP'
        
        
        
    
    def AddMetaDataToDataSet(self, dataSetId, metaDataMap):
        
        operationFlag = storage_service.add_meta_data(self.wsToken, dataSetId, metaDataMap, self.dataStorageClient)
        if operationFlag:
            return 'Metadata added to dataset'
        else:
            return 'something went wrong'
        
    def RemoveDataSet(self, dataSetIds):
        REMOVE_DATA_SET_MAL = '<dat:RemoveDataSet>%s</dat:RemoveDataSet>'
        dataSetIdStr = ''
        for dataSetId in dataSetIds:
            dataSetIdStr += '<DataSetId>%s</DataSetId>' % dataSetId
        
        bodyXml = REMOVE_DATA_SET_MAL % dataSetIdStr
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'RemoveDataSet')
    
    def RemoveMetaDataFromDataSet(self, DataSetId, metaKeys):
        REMOVE_METADATA_FROM_DATASET_MAL = '<dat:RemoveMetaDataFromDataSet><DataSetId>?</DataSetId> %s </MetaKeys>'
        metaKeyStr = ''
        for metaKey in metaKeys:
            metaKeyStr += '<Key>%s</Key>' % metaKey
        
        bodyXml = REMOVE_METADATA_FROM_DATASET_MAL % metaKeyStr
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'RemoveMetaDataFromDataSet')
    
    def GetDataFromStorage(self, FileHandler):
        bodyXml = '<dat:GetDataFromNorstore><FileHandler>%s</FileHandler></dat:GetDataFromNorstore>' % FileHandler
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'GetDataFromStorage')
    
    def GetDataSet(self, dataSetId):
        GET_DATA_SET_MAL ='<dat:GetDataSet><DataSetId>%s</DataSetId></dat:GetDataSet>'
        
        bodyXml = GET_DATA_SET_MAL % (dataSetId)
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'GetDataSet')
        
    
    def GetFileFromDataSet(self, fileHandler, fileEncoding=None):
        GET_FILE_FROM_DATASET_MAL = '<dat:GetFileFromDataSet><FileHandler>%s</FileHandler><dat1:ReturnFilter>%s</dat1:ReturnFilter></dat:GetFileFromDataSet>'
        fileEncodingStr = ''
        if fileEncoding:
            fileEncodingStr = '<dat1:SubEntryLevel>0</dat1:SubEntryLevel><dat1:FileEncoding><dat1:TransferMode>%s</dat1:TransferMode><dat1:ArchiveMethod>%s</dat1:ArchiveMethod></dat1:FileEncoding>' % (fileEncoding['TransferMode'], fileEncoding['ArchiveMethod'])
    
        bodyXml = GET_FILE_FROM_DATASET_MAL % (fileHandler, fileEncodingStr)
        
        return self._fetchWsResponse(bodyXml, 'DataStorageService', 'GetFileFromDataSet')
    
    
    def GetFilePreview(self, datasetId, SubTypeFilePair):
        return storage_service.get_file_preview(self.wsToken, datasetId, SubTypeFilePair[0], '/'.join(SubTypeFilePair[1:]), self.dataStorageClient)
        #print datasetId, subTypeFilePair
        #
        #GET_FILE_PREVIEW_MAL = """<dat:GetFilePreview><DatasetId>%s</DatasetId><dat:SubTypeFilePair><Subtype>%s</Subtype><FileToExtract>%s</FileToExtract></dat:SubTypeFilePair></dat:GetFilePreview>"""
        #
        #bodyXml = GET_FILE_PREVIEW_MAL % (tuple([datasetId] + SubTypeFilePair))
        #tmpResult =  self._fetchWsResponse(bodyXml, 'DataStorageService', 'GetFilePreview')
        #if tmpResult.find('<PreviewStaus>IN_PROGRESS</PreviewStaus>')<0:
        #    return tmpResult
        #count = 0
        #while tmpResult.find('<PreviewStaus>IN_PROGRESS</PreviewStaus>')>0 and count<20:
        #    time.sleep(5)
        #    tmpResult =  self._fetchWsResponse(bodyXml, 'DataStorageService', 'GetFilePreview')
        #    count+=1
        #
        #if count == 20:
        #    return'Not able to fetch FilePreview'
        #
        #return tmpResult
            
        
     
        
   
    #done    
    def ExtractFileFromDataSet(self, datasetId, subTypeFilePairs):
        transferHandlers = []
        for subTypeFilePair in subTypeFilePairs:
            transferHandlers.append(storage_service.start_file_transfer(self.wsToken, datasetId, subTypeFilePair['Subtype'], subTypeFilePair['FileToExtract'], self.dataStorageClient))
        return transferHandlers
        
        
        #EXTRACT_FILE_FROM_DATASET_MAL = '<dat:ExtractFileFromDataSet><DatasetId>%s</DatasetId>%s</dat:ExtractFileFromDataSet>'
        #subTypeFilePairStr = ''
        #for subTypeFilePair in subTypeFilePairs:
        #    subTypeFilePairStr+= '<dat:SubTypeFilePair><Subtype>%s</Subtype><FileToExtract>%s</FileToExtract></dat:SubTypeFilePair>' % (subTypeFilePair['Subtype'], subTypeFilePair['FileToExtract'])
        #
        #bodyXml = EXTRACT_FILE_FROM_DATASET_MAL % (datasetId, subTypeFilePairStr)
        #
        #return self._fetchWsResponse(bodyXml, 'DataStorageService', 'ExtractFileFromDataSet')
        
    #done    
    def GetFileUrlsFromDataSet2(self, datasetId, subTypeFilePairs, fileEncoding={'TransferMode':'FTP_URL', 'ArchiveMethod':'PLAIN_TEXT'}):
        
        transferHandler = storage_service.start_file_transfer(self.wsToken, datasetId, subTypeFilePairs[0]['Subtype'], subTypeFilePairs[0]['FileToExtract'], self.dataStorageClient)
        print transferHandler
        time.sleep(6)
        
        status = storage_service.check_transfer_status(self.wsToken, transferHandler, self.dataStorageClient)
        
        
        count = 0
        while not status.startswith('ftp') and count<20:
            time.sleep(6)
            count+=1
            status = storage_service.check_transfer_status(self.wsToken, transferHandler, self.dataStorageClient)
        print 'Url: ', status
        print urllib2.urlopen(status).read()
        return status if status.startswith('ftp') else 'could not access url'
            
            
        #subTypeFilePairs[0]['Subtype'] = subTypeFilePairs[0]['Subtype'].split('(')[0].strip()
        #print 'datasetId, subTypeFilePairs: ', datasetId, subTypeFilePairs
        #for subTypeFilePair in subTypeFilePairs:
        #    transferHandlers.append(storage_service.start_file_transfer(self.wsToken, datasetId, subTypeFilePair['Subtype'], subTypeFilePair['FileToExtract'], self.dataStorageClient))
        #return transferHandlers
        #fileTransferHandlers = self.ExtractFileFromDataSet(datasetId, subTypeFilePairs) #.encode('utf-8')
        #resultPaths = fileTransferHandlers #[]
        #return resultPaths[0]
        
        #fileTransferHandlers = minidom.parseString(self.ExtractFileFromDataSet(datasetId, subTypeFilePairs))#.encode('utf-8')
        #fileNames = [x['FileToExtract'] for x in subTypeFilePairs]
        #print 'fileNames: ', fileNames
        #for index, fileId in enumerate(fileTransferHandlers):
        #    time.sleep(1)
        #    
        #    print 'running GetFileFromDataSet with id =', fileId
        #    xml2 = minidom.parseString(self.GetFileFromDataSet(fileId, fileEncoding).encode('ascii', 'ignore'))
        #    #print xml2.toxml().endcode('latin-1')
        #    count=0
        #    while xml2.getElementsByTagName('Finished')[0].childNodes[0].nodeValue != 'true'and count < 20:
        #        time.sleep(1)
        #        xml2 = minidom.parseString(self.GetFileFromDataSet(fileId, fileEncoding).encode('utf-8'))
        #        count+=1
        #    if not fileNames[index].find('/')>=0: 
        #        filename = fileNames[index]
        #    else:
        #        filename = fileNames[index].split('/')[-1]
        #    filePath = xml2.getElementsByTagName('FileAsURL')[0].childNodes[0].nodeValue+filename
        #    print filePath
        #    resultPaths.append(filePath)
        #return resultPaths[0]
    
    
    #done    
    def getSubTrackName(self, userName, liste):
        print 'getSubTrackName: ', liste
        
        result = []
        datasetList = []
        if len(liste) == 1:
            dsList = self.ListDataSetsForUser()
            for ds in dsList:
                datasetList.append(ds.name.decode('ascii', errors='ignore')+' ('+ds.id+')')   
            
        elif len(liste) ==2:
            dataSetId = liste[1].split('(')[-1].split(')')[0].strip()
            dataset = storage_service.get_dataset(self.wsToken,dataSetId, self.dataStorageClient)
            datasetList = dataset.subTypeList
            print 'dataset.subTypeList', dataset.subTypeList
            #datasetList = [dataset.type+' (%s)' % dataset.name]
            
        else:
            resType = liste[2].split('(')[0].strip()
            requestStr = resType+('' if len(liste)==3 else '/'+ '/'.join(liste[3:][:]).replace(',FOLDER',''))
            
            dataSetId = liste[1].split('(')[1].split(')')[0].strip()
            resName = liste[2].split('(')[-1].split(')')[0].strip()
            print dataSetId, resType, requestStr,
            folderContent = storage_service.get_folder_content(self.wsToken, dataSetId, resType, requestStr, self.dataStorageClient)
            datasetList = [item for item in folderContent ] #if item.find(',FOLDER')>0
            
        
        
        for i in datasetList:
            result.append((i,i,False))
        return result

    
class WsUserMgntService(WsStoreBioInfo):
    #https://storebioinfo.norstore.no/wsdl/wsdl-usermgnt/UserMgntServiceOslSSL.xml
    WSDL_USER_MGNT_SERVICE = 'https://storebioinfo.norstore.no/wsdl/wsdl-usermgnt/UserMgntServiceOslSSL_2.xml'#'https://storebioinfo.norstore.no/wsdl/wsdl-usermgnt/UserMgntServiceOslSSL_2.xml'
    
    def __init__(self, userName, password):
        super(WsUserMgntService, self).__init__(userName, password)
        self.userMgntClient = Client(WsUserMgntService.WSDL_USER_MGNT_SERVICE, cache=None)
        self.userMgntClient.set_options(retxml=True)
        
    def _fetchWsResponse(self, bodyXml, webService, operation):
        xmlMessage = WsStoreBioInfo.WS_XML_TEMPLATE % (self.wsToken.timeStampXml, self.wsToken, bodyXml)
        #print xmlMessage, '\n\n'
        
        wsResponse =  getattr(self.userMgntClient.service[webService], operation)(__inject={'msg':xmlMessage})
        xmlString = self.ExtractXml(wsResponse)
        return unicode(xmlString, encoding='utf-8')
        
    
    def ListUsers(self):
        bodyXml = ' <user:ListUsers/> '
        return  self._fetchWsResponse(bodyXml, 'UserManagementService', 'ListUsers')
        
    def GetVersion(self):
        bodyXml = ' <user:GetVersion/> '
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'GetVersion')
        
    def GetUser(self, userId=None, UserName=None, returnUserFilter=None):
        GET_USER_MAL = '<user:GetUser> %s <user1:ReturnUserFilter><user1:ReturnMsgBoard>%s</user1:ReturnMsgBoard> <user1:ReturnProjects>%s</user1:ReturnProjects> <user1:ReturnGroups>%s</user1:ReturnGroups></user1:ReturnUserFilter></user:GetUser>'
        if not returnUserFilter:
            returnUserFilter = ['false', 'false', 'false']
        if userId:
            userIdentification = '<user:userId>'+userId+'</user:userId>'
        else:
            userIdentification = '<user:Username>'+UserName+'</user:Username>'
        
        bodyXml = GET_USER_MAL % (tuple([userIdentification]+returnUserFilter))
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'GetUser')
        
    def GetProject(self, ProjectId=None, ProjectName=None, returnFilter=None):
        GET_PROJECT_MAL = '<user:GetProject><user:ProjectKey>%s</user:ProjectKey><user1:ReturnFilter><user1:ReturnMsgBoard>%s</user1:ReturnMsgBoard> <user1:ReturnMembers>%s</user1:ReturnMembers></user1:ReturnFilter></user:GetProject>'
        if not returnFilter:
            returnFilter = ['false','false']#  else returnFilter
        if ProjectId:
            if type(ProjectId) == type([]):
                bodyXml = GET_PROJECT_MAL % tuple([(''.join(['<user:ProjectId>'+v+'</user:ProjectId>' for v in ProjectId]))]+returnFilter)
            else:
                bodyXml = GET_PROJECT_MAL % tuple(['<user:ProjectId>'+ProjectId+'</user:ProjectId>']+returnFilter)
        else:
            if type(ProjectName) == type([]):
                bodyXml = GET_PROJECT_MAL % tuple([(''.join(['<user:ProjectName>'+v+'</user:ProjectName>' for v in ProjectName]))] +returnFilter)
            else:
                bodyXml =  GET_PROJECT_MAL % tuple(['<user:ProjectName>'+ProjectName+'</user:ProjectName>']+returnFilter)
        #print bodyXml
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'GetProject')
        
    def ListProjects(self,returnFilter=None):
        
        projects =  user_management_service.list_projects(self.wsToken, None, self.userMgntClient)
        for i in projects:
            print 'project: ', i.name, i.quota.name, i.quota.id
        return projects
        
        #htmlMal = '<html><body>%s</body></html>'
        #tableList = []
        #for project in ProjectsList:
        #    tablestr = '<table>'
        #    keys = ['Name','Description','Creater','Created','Quota','DiskUsage']
        #    for key in keys:
        #        if key in project:
        #            if key == 'Quota':
        #                tablestr+= '<tr><td>%s: </td><td> </td><td>%s</td></tr>' % (key, project[key][key])
        #            else:
        #                tablestr+= '<tr><td>%s: </td><td> </td><td>%s</td></tr>' % (key, project[key])
        #    tablestr += '</table>'
        #    if 'ProjectMembers' in project:
        #        tablestr+= '<table><tr><td>ProjectMembers: </td><td> </td><td>Username </td><td>Roles </td><td> </td></tr>'
        #        for member in project['ProjectMembers']:
        #            tablestr+= '<tr><td> </td><td> </td><td>'+member['Username']+'</td><td>'+member['Roles']+'</td><td> </td></tr>'
        #        tablestr += '</table>'
        #    tablestr += '<br/><br/>'
        #    tableList.append(tablestr)
        #
        #return htmlMal % ('\n'.join(tableList))
            
    #def AddPublicationToProject(self,ProjectId, Publication):
    #    #<AddPublicationToProject>, <ProjectId>, <Publication>
    #    _ADD_PUBLICATION_TO_PROJECT_MAL = '<AddPublicationToProject></AddPublicationToProject>'
    #    bodyXml = _ADD_PUBLICATION_TO_PROJECT_MAL % tuple(ProjectId, Publication)
    #    
    #    self.xmlDoc = self._fetchWsResponse(bodyXml, 'UserManagementService', 'AddPublicationToProject')
    
        
         
         
    
        
    def AddUsersToProject(self,ProjectId, ProjectMembers):
        #<AddUsersToProject>, <ProjectId>, <ProjectMembers>
        _ADD_USERS_TO_PROJECT_MAL = '<user:AddUsersToProject><user:ProjectId>%s</user:ProjectId><user1:ProjectMembers>%s</user1:ProjectMembers></user:AddUsersToProject>'
        memberString=''
        for member in ProjectMembers.keys():
            memberString += '<user1:ProjectMember>'
            temp = ProjectMembers[member]
            if temp.has_key('Id'): 
                memberString+='<user1:Id>'+temp['Id']+'</user1:Id>'
            if temp.has_key('Username'):
                memberString+='<user1:Username>'+temp['Username']+'</user1:Username>' 
            if temp.has_key('Email'):
                memberString+='<user1:Email>'+temp['Email']+'</user1:Email>' 
            if temp.has_key('Roles'):
                for role in temp['Roles']:
                    memberString+='<user1:Roles>'+role+'</user1:Roles>'
            memberString += '</user1:ProjectMember>'
        
        bodyXml = _ADD_USERS_TO_PROJECT_MAL % tuple(ProjectId, memberString)
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'AddUsersToProject')
        
    def ConfirmInvitation(self,InvitationCode=None, NewFirstname=None, NewSurname=None, NewUsername=None, NewPassword=None):
        #<ConfirmInvitation>, <InvitationCode>, <NewFirstname>, <NewSurname>, <NewUsername>, <NewPassword>
        _CONFIRM_INVITATION_MAL = '<user:ConfirmInvitation>%s%s%s%s%s</user:ConfirmInvitation>'
        if InvitationCode:
            InvitationCode = '<user:InvitationCode>'+InvitationCode+'</user:InvitationCode>'
        else:
            InvitationCode = ''
        if NewFirstname:
            NewFirstname = '<user:NewFirstname>'+NewFirstname+'</user:NewFirstname>'
        else:
            NewFirstname = ''
        if NewSurname:
            NewSurname = '<user:NewSurname>'+NewSurname+'</user:NewSurname>'
        else:
            NewSurname = ''
        if NewUsername:
            NewUsername = '<user:NewUsername>'+NewUsername+'</user:NewUsername>'
        else:
            NewUsername = ''
        if NewPassword:
            NewPassword = '<user:NewPassword>'+NewPassword+'</user:NewPassword>'
        else:
            NewPassword = ''
        
        bodyXml = _CONFIRM_INVITATION_MAL % tuple(InvitationCode, NewFirstname, NewSurname, NewUsername, NewPassword)
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'ConfirmInvitation')
        
    def ConfirmMembership(self,ConfirmationCode):
        #<user:[A-Z]onfirmMembership>, <ConfirmationCode>
        _CONFIRM_MEMBERSHIP_MAL = '<user:ConfirmMembership>%s</user:ConfirmMembership>'
        bodyXml = _CONFIRM_MEMBERSHIP_MAL % tuple('<user:ConfirmationCode>'+ConfirmationCode+'</user:ConfirmationCode>')
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'ConfirmMembership')
        
    def ConfirmUser(self,ConfirmationCode):
        #<ConfirmUser>, <ConfirmationCode>
        _CONFIRM_USER_MAL = '<user:ConfirmUser>%s</user:ConfirmUser>'
        bodyXml = _CONFIRM_USER_MAL % tuple('<user:ConfirmationCode>'+ConfirmationCode+'</user:ConfirmationCode>')
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'ConfirmUser')
        
    def CreateProject(self,Projectname, Description, QuotaId, ProjectMembers=None):
        #<CreateProject>, <Projectname>, <Description>, <QuotaId>, <ProjectMembers>
        _CREATE_PROJECT_MAL = '<user:CreateProject>%s%s%s%s</user:CreateProject>'
        Projectname = '<user:Projectname>'+Projectname+'</user:Projectname>' 
        Description = '<user:Description>'+Description+'</user:Description>'
        if QuotaId:
            QuotaId = '<user:QuotaId>'+QuotaId+'</user:QuotaId>'
        else:
            QuotaId = ''
        if ProjectMembers:
            memberString='<user1:ProjectMembers>'
            for member in ProjectMembers.keys():
                memberString += '<user1:ProjectMember>'
                temp = ProjectMembers[member]
                if temp.has_key('Id'):
                    memberString+='<user1:Id>'+temp['Id']+'</user1:Id>'
                if temp.has_key('Username'):
                    memberString+='<user1:Username>'+temp['Username']+'</user1:Username>' 
                if temp.has_key('Email'):
                    memberString+='<user1:Email>'+temp['Email']+'</user1:Email>' 
                if temp.has_key('Roles'):
                    for role in temp['Roles']:
                        memberString+='<user1:Roles>'+role+'</user1:Roles>'
                memberString += '</user1:ProjectMember>'
            memberString+='</user1:ProjectMembers>'
        bodyXml = _CREATE_PROJECT_MAL % tuple(Projectname, Description, QuotaId, memberString)
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'CreateProject')
        
    def CreateUser(self,Firstname, Surname, Email, Username, Password):
        #<CreateUser>, <Firstname>, <Surname>, <Email>, <Username>, <Password>
        _CREATE_USER_MAL = '<user:CreateUser>%s%s%s%s%s</user:CreateUser>'
        Firstname = '<user:Firstname>'+Firstname+'</user:Firstname>' 
        Surname = '<user:Surname>'+Surname+'</user:Surname>'       
        Email = '<sch:Email>'+Email+'</sch:Email>' 
        Username = '<user:Username>'+Username+'</user:Username>' 
        Password = '<user:Password>'+Password+'</user:Password>' 
        bodyXml = _CREATE_USER_MAL % tuple(Firstname, Surname, Email, Username, Password)
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'CreateUser')
        
    def InviteUser(self,EmailAddress, ProjectOrGroupInvitation=None, InvitationMessage=None):
        #<InviteUser>, <ProjectOrGroupInvitation>, <EmailAddress>, <InvitationMessage>
        _INVITE_USER_MAL = '<user:InviteUser>%s%s%s</user:InviteUser>'
        EmailAddress = '<user:EmailAddress>'+EmailAddress+'</user:EmailAddress>'
        if InvitationMessage:
            InvitationMessage = '<user:InvitationMessage>'+InvitationMessage+'</user:InvitationMessage>'
        else:
            InvitationMessage = ''
        
        if ProjectOrGroupInvitation:
            if ProjectOrGroupInvitation.has_key('ProjectId'):
                ProjectOrGroupInvitationStr = '<user:ProjectOrGroupInvitation><user:ProjectId>'+ProjectId+'</user:ProjectId></user:ProjectOrGroupInvitation>'
            else:
                ProjectOrGroupInvitationStr = '<user:ProjectOrGroupInvitation><user:GroupId>'+GroupId+'</user:GroupId></user:ProjectOrGroupInvitation>'

        bodyXml = _INVITE_USER_MAL % tuple(ProjectOrGroupInvitationStr, EmailAddress, InvitationMessage)
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'InviteUser')
        
    def ModifyProject(self, projectIdentifier, RestrictedProfile, NewProjectname=None, NewDescription=None):
        #<ModifyProject>, <NewProjectname>, <RestrictedProfile>, <NewDescription>
        _MODIFY_PROJECT_MAL = '<user:ModifyProject>%s%s%s%s</user:ModifyProject>'
        if projectIdentifier.has_key('ProjectId'):
            if ProjectId:
                ProjectId = '<user:ProjectId>'+ProjectId+'</user:ProjectId>'
            else:
                ProjectId = ''
        else:
            if ProjectName:
                ProjectId = '<user:ProjectName>'+ProjectName+'</user:ProjectName>'
            else:
                ProjectName = ''
        if NewProjectname:
            NewProjectname = '<user:NewProjectname>'+NewProjectname+'</user:NewProjectname>'
        else:
            NewProjectname = ''
        RestrictedProfile = '<user:RestrictedProfile>'+RestrictedProfile+'</user:RestrictedProfile>'
        if NewDescription:
            NewDescription = '<user:NewDescription>'+NewDescription+'</user:NewDescription>'
        else:
            NewDescription = ''

        bodyXml = _MODIFY_PROJECT_MAL % tuple(ProjectId, NewProjectname, RestrictedProfile, NewDescription)
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'ModifyProject')
        
    def ModifyUser(self,userIdentity, NewEmailAdress=None, RestrictedProfile=None, NewFirstname=None, NewLastname=None, PasswordChange=None):
        #<ModifyUser>, <NewEmailAdress>, <RestrictedProfile>, <NewFirstname>, <NewLastname>, <PasswordChange>
        _MODIFY_USER_MAL = '<user:ModifyUser>%s%s%s%s%s%s</user:ModifyUser>'
        if userIdentity.has_key('Userid'):
            userId = '<user:Userid>'+Userid+'</Userid>'
        else:
            userId = '<user:Username>'+Username+'</user:Username>'
        if NewEmailAdress:
            NewEmailAdress = '<user:NewEmailAdress>'+NewEmailAdress+'</user:NewEmailAdress>'
        else:
            NewEmailAdress = ''
        if RestrictedProfile:
            RestrictedProfile = '<user:RestrictedProfile>'+RestrictedProfile+'</user:RestrictedProfile>'
        else:
            RestrictedProfile = ''
        if NewFirstname:
            NewFirstname = '<user:NewFirstname>'+NewFirstname+'</user:NewFirstname>'
        else:
            NewFirstname = ''
        if NewLastname:
            NewLastname = '<user:NewLastname>'+NewLastname+'</user:NewLastname>'
        else:
            NewLastname = ''

        if PasswordChange:
            passord = '<user:PasswordChange><user:OldPassword>'+PasswordChange['OldPassword']+'</user:OldPassword>'
            passord+= '<user:NewPassword>'+NewPassword+'</user:NewPassword></user:PasswordChange>'

        bodyXml = _MODIFY_USER_MAL % tuple(userId, NewEmailAdress, RestrictedProfile, NewFirstname, NewLastname, PasswordChange)
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'ModifyUser')
        
    def RemoveUserFromProject(self, ProjectIdentity, MemberKey):
        #<RemoveUserFromProject>, <MemberKey>
        _REMOVE_USER_FROM_PROJECT_MAL = '<user:RemoveUserFromProject>%s%s</user:RemoveUserFromProject>'
        
        memberStr = ''
        for member in MemberKey.keys():
            if MemberKey[member].has_key('Id'):
                memberStr+= '<user:MemberKey><user:Id>'+MemberKey[member]['Id']+'</user:Id></user:MemberKey>'
            else:
                memberStr += '<user:MemberKey><user:Name>'+MemberKey[member]['Name']+'</user:Name></user:MemberKey>'    
        if ProjectIdentity.has_key('ProjectId'):
            ProjectIdentity = '<user:ProjectId>'+ProjectIdentity['ProjectId']+'</user:ProjectId>'
        else:
            ProjectIdentity = '<user:ProjectName>'+ProjectIdentity['ProjectName']+'</user:ProjectName>'
        
        bodyXml = _REMOVE_USER_FROM_PROJECT_MAL % tuple(ProjectIdentity, memberStr)
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'RemoveUserFromProject')
        
    def ResetPassword(self,UserIdentity):
        #<ResetPassword>, <>
        _RESET_PASSWORD_MAL = '<user:ResetPassword>%s</user:ResetPassword>'
        if UserIdentity.has_key('Username'):
            User = '<user:Username>'+UserIdentity['Username']+'</user:Username>'
        else:
            User = '<user:EmailAdress>'+UserIdentity['EmailAdress']+'</user:EmailAdress>'
        bodyXml = _RESET_PASSWORD_MAL % tuple(User)
        return self._fetchWsResponse(bodyXml, 'UserManagementService', 'ResetPassword')
        
    def AssignUserToSystemRole(self,UserIds, Roles):
        #<AssignUserToSystemRole>, <UserId>, <Roles>
        _ASSIGN_USER_TO_SYSTEM_ROLE_MAL = '<user:AssignUserToSystemRole></user:AssignUserToSystemRole>'
        userIdentities=''

        for UserId in UserIds:
            userIdentities += '<user:UserId>'+UserId+'</user:UserId>' 
        rolesStr = '<sch:Roles>'

        for Role in Roles:
            rolesStr += '<sch:Role>'+Role+'</sch:Role>'
        rolesStr += '</sch:Roles>'
        
        bodyXml = _ASSIGN_USER_TO_SYSTEM_ROLE_MAL % tuple(userIdentities, rolesStr)
        return self._fetchWsResponse(bodyXml, 'UserManagementAdminService', 'AssignUserToSystemRole')
        
    def CreateQuota(self,DiskQuota, Name=None, Description=None):
        #<CreateQuota>, <DiskQuota>, <Name>, <Description>
        _CREATE_QUOTA_MAL = '<user:CreateQuota>%s%s%s</user:CreateQuota>'
        DiskQuota = '<user:DiskQuota>'+DiskQuota+'</user:DiskQuota>'
        if Name:
            Name = '<user:Name>'+Name+'</user:Name>'
        else:
            Name = ''
        if Description:
            Description = '<user:Description>'+Description+'</user:Description>'
        else:
            Description = ''
        bodyXml = _CREATE_QUOTA_MAL % tuple(DiskQuota, Name, Description)
        return self._fetchWsResponse(bodyXml, 'UserManagementAdminService', 'CreateQuota')
        
    def ListAllProjects(self, ReturnFilter=None):
        #<ListAllProjects>, <ReturnFilter>
        _LIST_ALL_PROJECTS_MAL = '<user:ListAllProjects> <user1:ReturnFilter><user1:ReturnMsgBoard>%s</user1:ReturnMsgBoard><user1:ReturnMembers>%s</user1:ReturnMembers></user1:ReturnFilter> </user:ListAllProjects>'
        if not ReturnFilter:
            ReturnFilter = ['false','false']
        bodyXml = _LIST_ALL_PROJECTS_MAL % tuple(ReturnFilter)
        return self._fetchWsResponse(bodyXml, 'UserManagementAdminService', 'ListAllProjects')
        
    def ListQuota(self):
        #<ListQuota>, <>
        bodyXml = '<user:ListQuota/>'
        return self._fetchWsResponse(bodyXml, 'UserManagementAdminService', 'ListQuota')
        
    def RemoveEntity(self,ProjectKey=None, UserKey=None):
        #<RemoveEntity>, <ProjectKey>, <UserKey>
        _REMOVE_ENTITY_MAL = '<user:RemoveEntity>%s</user:RemoveEntity>'
        bodyStr=''
        if ProjectKey:
            for project in ProjectKey.keys():
                if project.has_key('ProjectId'):
                    bodyStr += '<user:ProjectKey>'+  '<user:ProjectId>'+project['ProjectId']+'</user:ProjectId>' +'</user:ProjectKey>'
                else:
                    bodyStr += '<user:ProjectKey>'+  '<user:ProjectName>'+project['ProjectName']+'</user:ProjectName>' + '</user:ProjectKey>'
        
        if UserKey:
            for user in UserKey.keys():
                if user.has_key('UserId'):
                    bodyStr += '<user:UserKey>'+ '<user:UserId>'+user['UserId']+'</user:UserId>' +'</user:UserKey>'
                else:
                    bodyStr += '<user:UserKey>'+ '<user:UserName>'+user['UserName']+'</user:UserName>'+'</user:UserKey>'
        
        bodyXml = _REMOVE_ENTITY_MAL % tuple(bodyStr)
        return self._fetchWsResponse(bodyXml, 'UserManagementAdminService', 'RemoveEntity')
        
    def RemoveUserFromSystemRole(self,UserIds, Roles):
        #<RemoveUserFromSystemRole>, <UserId>, <Roles>
        _REMOVE_USER_FROM_SYSTEM_ROLE_MAL = '<user:RemoveUserFromSystemRole>%s<sch:Roles>%s</sch:Roles></user:RemoveUserFromSystemRole>'
        userIdStr,rolestr = '',''

        for userId in UserIds:
            userIdStr+='<user:UserId>'+userId+'</user:UserId>'        
        for role in Roles:
             rolestr += '<sch:Role>'+role+'</sch:Role>'

        bodyXml = _REMOVE_USER_FROM_SYSTEM_ROLE_MAL % tuple(userIdStr,rolestr)
        return self._fetchWsResponse(bodyXml, 'UserManagementAdminService', 'RemoveUserFromSystemRole')
        
    def SetDiskQuotaForProject(self,ProjectId, QuotaId, DiskQuota):
        #<SetDiskQuotaForProject>, <ProjectId>, <QuotaId>, <DiskQuota>
        _SET_DISK_QUOTA_FOR_PROJECT_MAL = '<user:SetDiskQuotaForProject>%s%s%s</user:SetDiskQuotaForProject>'
        ProjectId = '<user:ProjectId>'+ProjectId+'</user:ProjectId>' 
        QuotaId = '<user:QuotaId>'+QuotaId+'</user:QuotaId>' 
        DiskQuota = '<user:DiskQuota>'+DiskQuota+'</user:DiskQuota>'
        
        bodyXml = _SET_DISK_QUOTA_FOR_PROJECT_MAL % tuple(ProjectId, QuotaId, DiskQuota)
        return self._fetchWsResponse(bodyXml, 'UserManagementAdminService', 'SetDiskQuotaForProject')
        
    def UpdateProjectQuota(self,ProjectId, Quota):
        #<UpdateProjectQuota>, <ProjectId>, <Quota>
        _UPDATE_PROJECT_QUOTA_MAL = '<user:UpdateProjectQuota>%s%s</user:UpdateProjectQuota>'
        ProjectId = '<user:ProjectId>'+ProjectId+'</user:ProjectId>' 
        Quota = '<user:Quota>'+Quota+'</user:Quota>' 
        
        bodyXml = _UPDATE_PROJECT_QUOTA_MAL % tuple(ProjectId, Quota)
        return self._fetchWsResponse(bodyXml, 'UserManagementAdminService', 'UpdateProjectQuota')
        
    def GetMessages(self,Since):
        #<GetMessages>, <Since> Since er Dato sikkert
        _GET_MESSAGES_MAL = '<user:GetMessages>%s</user:GetMessages>'
        ince = '<user:Since>'+Since+'</user:Since>' 
        bodyXml = _GET_MESSAGES_MAL % tuple(Since)
        return self._fetchWsResponse(bodyXml, 'MessageService', 'GetMessages')
        
    def MarkAsRead(self,MessageIds):
        #<MarkAsRead>, <MessageId>
        _MARK_AS_READ_MAL = '<user:MarkAsRead>%s</user:MarkAsRead>'
        messageIdStr=''
        for MessageId in MessageIds:
            messageIdStr += '<user:MessageId>'+MessageId+'</user:MessageId>'         
        bodyXml = _MARK_AS_READ_MAL % tuple(messageIdStr)
        return self._fetchWsResponse(bodyXml, 'MessageService', 'MarkAsRead')
        
    def RemoveMessage(self,MessageId):
        #<RemoveMessage>, <MessageId>
        _REMOVE_MESSAGE_MAL = '<user:RemoveMessage>%s</user:RemoveMessage>'
        messageIdStr=''
        for MessageId in MessageIds:
            messageIdStr += '<user:MessageId>'+MessageId+'</user:MessageId>'   
        bodyXml = _REMOVE_MESSAGE_MAL % tuple(messageIdStr)
        return self._fetchWsResponse(bodyXml, 'MessageService', 'RemoveMessage')
        
    def SendMessage(self,EntityKey, From, To, Subject, Message, SendEmail):
        #<SendMessage>, <EntityKey>, <From>, <To>, <Subject>, <Message>, <SendEmail>
        _SEND_MESSAGE_MAL = '<user:SendMessage>%s%s%s%s%s%s</user:SendMessage>'
        if EntityKey.has_key('ProjectName'):
            EntityKey = '<user:EntityKey>'+ '<user:ProjectName>'+EntityKey['ProjectName']+'</user:ProjectName>'+'</user:EntityKey>'
        else:
            EntityKey = '<user:EntityKey>'+ '<user:GroupName>'+EntityKey['GroupName']+'</GroupName>'+'</user:EntityKey>'
        From = '<user:From>'+From+'</user:From>' 
        To = '<user:To>'+To+'</user:To>' 
        Subject = '<user:Subject>'+Subject+'</user:Subject>' 
        Message = '<user:Message>'+Message+'</user:Message>'
        if SendEmail:
            SendEmail = '<user:SendEmail>'+SendEmail+'</user:SendEmail>'
        else:
            SendEmail = ''
        bodyXml = _SEND_MESSAGE_MAL % tuple(EntityKey, From, To, Subject, Message, SendEmail)
        return self._fetchWsResponse(bodyXml, 'MessageService', 'SendMessage')
    
    def getNodeValue(self, domTree, element, typeOfElement):
        childVal = len(domTree.getElementsByTagName(element)[0].childNodes)>0
        value = ''
        if typeOfElement == 'str':
            if childVal:
                value = domTree.getElementsByTagName(element)[0].childNodes[0].nodeValue# if childVal else ''
        elif typeOfElement == 'int':
            value = None
            if childVal:
                value = int(domTree.getElementsByTagName(element)[0].childNodes[0].nodeValue)# if childVal else None
        elif typeOfElement == 'date':
            if childVal:
                value = domTree.getElementsByTagName(element)[0].childNodes[0].nodeValue[:-10]# if childVal else ''
        elif typeOfElement == 'boolean':
            value = None
            if childVal:
                value = bool(domTree.getElementsByTagName(element)[0].childNodes[0].nodeValue)# if childVal else None
        else:
            pass        
        return value
    
    def nodeExists(self, domTree, element):
        return len(domTree.getElementsByTagName(element))>0
    
class UserMapping(object):
    
    def __init__(self):
        self.userMappingDict = dict()
    
    def getSBLoginData(self, messageDict):
        if messageDict.has_key('username') and messageDict.has_key('password'):
            return messageDict['username'], messageDict['password']
        elif messageDict.has_key('galaxyUser'):
            return self.userMappingDict[messageDict['galaxyUser']]
        else:
            return None, None
            
    
        
if __name__ == '__main__':
    
    #dataStorageService = WsDataStorageService('hs', 'ssh')
    ##htmResult = dataStorageService.GetFileUrlsFromDataSet('e0bf8182-fd87-4cc3-864f-d411b884a639',  [{'Subtype': 'Analysis', 'FileToExtract': 're.txt'}])
    #htmResult = dataStorageService.ListDataSetsForUser('hs')
    
    import zmq
    ##dat="http://storebioinfo.norstore.no/service/datastorage" dat1="http://storebioinfo.norstore.no/schema/datastorage"     
    if True:
        from config.Config import STOREBIOINFO_USER, STOREBIOINFO_PASSWD
        #try:
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5559")
        
        dataStorageServicePub = WsPublicDatastorageService()
        userMngtService = WsUserMgntService(STOREBIOINFO_USER, STOREBIOINFO_PASSWD)
        dataStorageService = WsDataStorageService(STOREBIOINFO_USER, STOREBIOINFO_PASSWD)
        UserAuthentication = dict()
        userMapper = UserMapping()
        
        while True:
            if True:
                #Now: message must have userName, Passwd at Storebio as first params, and WsStorebioInfo-Object as last param
                
                message = socket.recv()
                messageDict = dict([ tuple(x.split(':='))for x in message.split('##')])
                if messageDict.get('params'):
                    params = messageDict['params'].split('<#>')
                    print params
                userName, password = userMapper.getSBLoginData(messageDict)
                
                print 'Starting new Request:  ', message
                start = time.time()
                runObject = globals()[messageDict['class']]
                print userName, password
                if userName:
                    if not (UserAuthentication.has_key(userName) and (time.time()-UserAuthentication[userName][-1]<200)):
                        try:
                            UserAuthentication = runObject.handleAuthUpdate(userName, password, UserAuthentication)
                        except:
                            pass
                            
                if messageDict.has_key('operation'):
                    #try:
                    
                    operationToExec = messageDict['operation']
                    if operationToExec == 'List Projects':
                        htmResult = pickle.dumps(runObject.ListProjects())
                        
                    elif operationToExec == 'List Datasets':
                        htmResult = pickle.dumps(runObject.ListDataSetsForUser())
                        
                    elif operationToExec == 'Download file from Dataset':
                        htmResult = pickle.dumps(runObject.ListDataSetsForUser())
                        
                    elif operationToExec == 'GetFileUrlsFromDataSet':
                        param1, param2 = ast.literal_eval(params[0]), ast.literal_eval(params[1])
                        print 'running GetFileUrlsFromDataSet..'
                        print runObject
                        htmResult = runObject.GetFileUrlsFromDataSet2(param1, param2 )
                    
                        
                    elif operationToExec == 'getSubTrackName':
                        parentTrack = ast.literal_eval(params[0])
                        htmResult = repr(runObject.getSubTrackName(userName, parentTrack))
                        
                    elif operationToExec == 'List DataSetType':
                        htmResult = runObject.ListTypesOfDataSet()
                    
                    elif operationToExec == 'GetFilePreview':
                        htmResult = runObject.GetFilePreview( params[0], ast.literal_eval(params[1]) )
                        
                    elif operationToExec == 'Add DataSet':
                        #[userName, password, 'Add DataSet', name, quotaId, type, url, resourceType, description, projectAccessControlList, 'dataStorageService']
                        name, quotaId, type, url ,resourceType, galaxyUser, galaxyPassword, = params[0], params[1], params[2], params[3], params[4], 'ehovig', 'voo5lagC'
                        description, projectAccessControlList  = params[5], ast.literal_eval(params[6])
                        htmResult = runObject.AddDataSet(name, quotaId, type, url ,resourceType, galaxyUser, galaxyPassword, description, projectAccessControlList)
                    
                    elif operationToExec == 'AddDataSetWithFTP':
                        #def AddDataSetWithFTP(self, name, quotaId, type, localRootDir, description=None, projectAccessControlList=None)
                        name, quotaId, type, url = params[0], params[1], params[2], params[3]
                        description, projectAccessControlList  = params[4], ast.literal_eval(params[5])
                        htmResult = runObject.AddDataSetWithFTP(name, quotaId, type, url, description, projectAccessControlList)
                    
                    elif operationToExec == 'CreateDataSet':
                        #def AddDataSetWithFTP(self, name, quotaId, type, localRootDir, description=None, projectAccessControlList=None)
                        name, quotaId, type = params[0], params[1], params[2]
                        description, projectAccessControlList  = params[3], ast.literal_eval(params[4])
                        htmResult = runObject.CreateDataSet(name, quotaId, type, description, projectAccessControlList)
                    
                    
                    
                    elif operationToExec == 'AddFileToDataSet':
                        dataSetId, subtype, pathInSubtype, url = params[0], params[1], params[2], params[3]
                        htmResult = runObject.AddFileToDataSet(dataSetId, subtype, pathInSubtype, url, 'ehovig', 'voo5lagC')    
                        
                    elif operationToExec == 'AddMetaDataToDataSet':
                        htmResult = runObject.AddMetaDataToDataSet( params[0], ast.literal_eval(params[1]) )
                    
                    elif operationToExec == 'GetFilePreviewFromPublicDataset':
                        htmResult = runObject.GetFilePreviewFromPublicDataset( params[0], ast.literal_eval(params[1])).Preview
                    
                    elif operationToExec == 'getDatasetsByProject':
                        projId, includeMetaData, includeSubTypes = params[0], ast.literal_eval(params[1]), ast.literal_eval(params[2])
                        htmResult = pickle.dumps(runObject.getDatasetsByProject(projId, includeMetaData, includeSubTypes))
                    
                    else:
                        htmResult = ''
                        socket.send(htmResult)
                    
                    socket.send_unicode(htmResult if htmResult is not None else '')
                    
                else:
                    #except BaseException as e:
                    #print 'something went wrong...', repr(e.args)
                    #UserAuthentication = runObject.handleAuthUpdate(userName, password, UserAuthentication)
                    #runObject.doAuthentication(message[0], message[1])
                    #UserAuthentication[message[0]] = (runObject.wsToken, runObject.timeStampValue)
                    socket.send('something went wrong...')
                print "after Received request(%s):   " % message[2], time.time()-start
            
            else:# BaseException as e:
                print 'something went wrong...'#, repr(e.args)
                socket.send_unicode('')
    else:
        #except Exception, e:
        raise e
        print 'this did not work....'
    
    
    
    #dataStorageService = WsDataStorageService(STOREBIOINFO_USER, STOREBIOINFO_PASSWD)
    #dataStorageService.AddMetaDataToDataSet('785b974c-8f1d-4403-a42c-efdd57d2d9d4', tiList)
    #fPathList = ['/usit/invitro/data/galaxy/galaxy_developer/hyperbrowser/tracks/standardizedTracks/hg18/DNA variation/SNPs/Validated/validated.snps.dbSNP.build129.point.bed',
    #'/usit/invitro/data/galaxy/galaxy_developer/hyperbrowser/tracks/standardizedTracks/hg18/DNA variation/SNPs/HapMap/hapmap.snps.dbSNP.build129.point.bed']
    #dataStorageService.AddMetaDataToDataSet('785b974c-8f1d-4403-a42c-efdd57d2d9d4', dataStorageService.getTrackInfoForFiles(fPathList))
    
    #dataStorageService.AddFileToDataSet('497d7406-5af7-4f95-af1f-6bfd0b2c4d59', 'reads', ' ', 'scp://invitro.titan.uio.no:/usit/invitro/work/hyperbrowser/nosync/nobackup/storeBioInfo_transfer/trengere@gmail.com2012_1_27_15_40_4224/64_-_missingScfpMap.txt.bed', 'ehovig', 'voo5lagC')
    
    """
    datasetList = []
    dataStorageService = WsDataStorageService('hs', 'ssh')
    param1 = 'e0bf8182-fd87-4cc3-864f-d411b884a639'
    param2 = [{'Subtype': 'Analysis', 'FileToExtract': 're.txt'}]
    #datasetId, subTypeFilePairs:  e0bf8182-fd87-4cc3-864f-d411b884a639 [{'Subtype': 'Analysis', 'FileToExtract': 're.txt'}]
    dataStorageService = WsDataStorageService('hs', 'ssh')
    #htmResult = dataStorageService.GetFileUrlsFromDataSet('e0bf8182-fd87-4cc3-864f-d411b884a639',  [{'Subtype': 'Analysis', 'FileToExtract': 're.txt'}])
    #htmResult = dataStorageService.ListDataSetsForUser('hs')
    #htmResult = dataStorageService.GetFileFromDataSet('58d2d1b9-5562-4575-a884-5dbd63ea3e1f', {'TransferMode':'FTP_URL', 'ArchiveMethod':'PLAIN_TEXT'})
    htmResult = dataStorageService.AddDataSet('KaiTest', 'b0cbabe1-ceed-4bfe-8d5b-86fda67819b9', 'SEQ_DATA', 'scp://invitro.titan.uio.no:/usit/invitro/work/hyperbrowser/nosync/nobackup/storeBioInfo_transfer/trengere@gmail.com2011_11_22_15_15_2349', 'Analysis', 'ehovig', 'voo5lagC', 'bla bla', ['3b65c249-c943-4bb6-9280-3079bf68f248', 'true'])
    
    
    xml2 =  dataStorageService.GetResourceByIdOrName( 0, 'Analysis/f1/f3/f5', resourceId='7f36830a-a861-4a58-a1db-fb64fc845da6')
    xmlDoc2 = minidom.parseString(xml2)
    
    for filePath in  xmlDoc2.getElementsByTagName('SubEntries'):
        print filePath.childNodes[0].nodeValue
        datasetList.append(filePath.childNodes[0].nodeValue)#.encode('latin-1').split(',')[0]
        #parentElem.childNodes[0].nodeValue
    print  datasetList  
    """    
    #To run a WS-operation, you have to make an WsUserMgntService object that takes username and password as arguments.
    # you then use this object to call WS-methods.
    # here follows some examples of how to call a WS-method,  and the last section contains the method signature for every WS-method that is currently implemented
    #userMngtService = WsUserMgntService('hs', 'ssh') # this line gets the security token that is used for every WS-operation mandatory to run this line before any WS-method
    #userMngtService.ListUsers() # OK
    #userMngtService.ListProjects() # = OK
    #userMngtService.ParseXmlResponse('ListProjects', userMngtService.xmlDoc)
    
    
    #mDataStorageService.ListDataSetTypes()
    #xmlDoc = mDataStorageService.ListDataSetsForUser('hs')
    #print 'after dataStorageService.ListDataSetsForUser(choices[0]):  ', time.time()-start
    
    #dataStorageService = WsDataStorageService('hs', 'ssh')
    #dataStorageService.ListDataSetTypes()
    #print dataStorageService.ListDataSetsForUser('hs').toxml().encode('latin-1')
    #dataStorageService.GetDataSet('721b3cca-c30e-4ea8-b626-2c10bac56d30')
    #print dataStorageService.GetFileUrlsFromDataSet('721b3cca-c30e-4ea8-b626-2c10bac56d30',  [{'Subtype':'Raw', 'FileToExtract':'fasta.txt'}])
    #225547d4-3843-460d-8342-6e581113d179
    #print dataStorageService.GetFileUrlsFromDataSet('23016dbc-67b0-40d3-8085-f41cdb6f403b', [{'Subtype':'Raw', 'FileToExtract':'2003-05-04_Human15k_750_0600-cltech-AHktr-1vask_W2.jpg'}])
    #fileId = xml.getElementsByTagName('FileHandler')[0].childNodes[0].nodeValue
    #print fileId
    #time.sleep(5)
    #fileEncoding = dict()
    #fileEncoding['TransferMode'] = 'FTP_URL'
    #fileEncoding['ArchiveMethod'] = 'PLAIN_TEXT'
    #xml2 = dataStorageService.GetFileFromDataSet(fileId, fileEncoding)
    #filePath = xml2.getElementsByTagName('FileAsURL')[0].childNodes[0].nodeValue
    #print urllib2.urlopen(filePath+'fasta.txt').read()
    
    
    #userMngtService.ListUsers() # OK
    #time.sleep(3)
    #userMngtService.ListUsers() # OK
    #userMngtService.GetVersion()# Failed
    #userMngtService.GetUser(UserName='hs')# = OK
    #userMngtService.GetProject(ProjectName='invite-test') #= OK
    #userMngtService.ListProjects() # = OK
    #userMngtService.ListAllProjects() # = Failed (AUTHORIZATION_ERROR</ns1:FaultEnum><FaultMessage>Non privileged user<)
    #userMngtService.AddUsersToProject -- Not tested yet
    #userMngtService.GetMessages # Ready for testing

    ######   TEMPLATES   ######

    #userMngtService.ListUsers()
    #userMngtService.GetVersion()
    #userMngtService.GetUser( userId=None, UserName=None, returnUserFilter=None)
    #userMngtService.GetProject( ProjectId=None, ProjectName=None, returnFilter=None)ject')   
    #print userMngtService.ListProjects(returnFilter=None)
    #userMngtService.AddUsersToProject(ProjectId, ProjectMembers)     
    #userMngtService.ConfirmInvitation(InvitationCode=None, NewFirstname=None, NewSurname=None, NewUsername=None, NewPassword=None)
    #userMngtService.ConfirmMembership(ConfirmationCode)
    #userMngtService.ConfirmUser(ConfirmationCode)
    #userMngtService.CreateProject(Projectname, Description, QuotaId, ProjectMembers=None)       
    #userMngtService.CreateUser(Firstname, Surname, Email, Username, Password)
    #userMngtService.InviteUser(EmailAddress, ProjectOrGroupInvitation=None, InvitationMessage=None)
    #userMngtService.ModifyProject( projectIdentifier, RestrictedProfile, NewProjectname=None, NewDescription=None)
