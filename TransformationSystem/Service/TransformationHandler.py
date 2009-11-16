""" DISET request handler base class for the TransformationDB.
"""
from types import *
from DIRAC.Core.DISET.RequestHandler import RequestHandler
from DIRAC import gLogger, gConfig, S_OK, S_ERROR
from DIRAC.Core.Transformation.TransformationDB import TransformationDB

class TransformationHandler(RequestHandler):

  def setDatabase(self,oDatabase):
    self.database = oDatabase

  types_getName = []
  def export_getName(self):
    res = self.database.getName()
    return res

  types_publishTransformation = [ StringType, StringType, StringType, StringType, IntType, BooleanType, DictType, StringType, StringType, StringType ]
  def export_publishTransformation( self,transName,description,longDescription,fileMask='',groupsize=0,update=False,bkQuery = {},plugin='',transGroup='',transType=''):
    """ Publish new transformation in the TransformationDB
    """
    authorDN = self._clientTransport.peerCredentials['DN']
    authorGroup = self._clientTransport.peerCredentials['group']
    res = self.database.addTransformation(transName,description,longDescription,authorDN,authorGroup,transType,plugin,'TransformationAgent',fileMask,bkQuery,transGroup)
    if res['OK']:
      message = 'Transformation created'
      res = self.database.updateTransformationLogging(transName,message,authorDN)
    return res

  types_removeTransformation = [[LongType, IntType, StringType]]
  def export_removeTransformation(self,transNameOrID):
    return self.database.deleteTransformation(transNameOrID)

  types_setTransformationStatus = [[LongType, IntType, StringType],StringType]
  def export_setTransformationStatus(self,transNameOrID,status):
    result = self.database.setTransformationStatus(transNameOrID,status)
    if result['OK']:
      authorDN = self._clientTransport.peerCredentials['DN']
      message = "Status changed to %s" % status
      result = self.database.updateTransformationLogging(transNameOrID,message,authorDN)
    return result
    
  types_setTransformationQuery = [[LongType, IntType, StringType],[LongType, IntType]]
  def export_setTransformationQuery(self,transNameOrID,queryID):
    result = self.database.setTransformationQuery(transNameOrID,queryID)
    if result['OK']:
      authorDN = self._clientTransport.peerCredentials['DN']
      message = "Bookkeeping Query changed to %d" % queryID
      result = self.database.updateTransformationLogging(transNameOrID,message,authorDN)
    return result  

  types_setTransformationAgentType = [ [LongType, IntType, StringType], StringType ]
  def export_setTransformationAgentType( self, transNameOrID, status ):
    result = self.database.setTransformationAgentType(transNameOrID, status)
    if not result['OK']:
      gLogger.error(result['Message'])
    else:
      authorDN = self._clientTransport.peerCredentials['DN']
      message = "Transformation AgentType changed to %s" % status
      result = self.database.updateTransformationLogging(transNameOrID,message,authorDN)
    return result

  types_setTransformationType = [ [LongType, IntType, StringType], StringType ]
  def export_setTransformationType( self, transNameOrID, status ):
    result = self.database.setTransformationType(transNameOrID, status)
    if not result['OK']:
      gLogger.error(result['Message'])
    else:
      authorDN = self._clientTransport.peerCredentials['DN']
      message = "Transformation Type changed to %s" % status
      result = self.database.updateTransformationLogging(transNameOrID,message,authorDN)
    return result

  types_setTransformationPlugin = [ [LongType, IntType, StringType], StringType ]
  def export_setTransformationPlugin( self, transNameOrID, status ):
    result = self.database.setTransformationPlugin(transNameOrID, status)
    if not result['OK']:
      gLogger.error(result['Message'])
    else:
      authorDN = self._clientTransport.peerCredentials['DN']
      message = "Transformation Plugin changed to %s" % status
      result = self.database.updateTransformationLogging(transNameOrID,message,authorDN)
    return result

  types_setTransformationMask = [[LongType, IntType, StringType],StringType]
  def export_setTransformationMask(self,transNameOrID,fileMask):
    res = self.database.setTransformationMask(transNameOrID,fileMask)
    if res['OK']:
      authorDN = self._clientTransport.peerCredentials['DN']
      message = "Mask changed to %s" % fileMask
      res = self.database.updateTransformationLogging(transNameOrID,message,authorDN)
    return res

  types_changeTransformationName = [[LongType, IntType, StringType],StringType]
  def export_changeTransformationName(self,transformationName,newName):
    res = self.database.changeTransformationName(transformationName,newName)
    authorDN = self._clientTransport.peerCredentials['DN']
    if res['OK']:
      message = "Transformation name changed to %s" % newName
      res = self.database.updateTransformationLogging(newName,message,authorDN)
    return res

  types_addTransformationParameter = [[LongType, IntType, StringType],StringType,StringType]
  def export_addTransformationParameter(self,transformationName,paramname,paramvalue):
    res = self.database.addTransformationParameter(transformationName,paramname,paramvalue)
    authorDN = self._clientTransport.peerCredentials['DN']
    if res['OK']:
      message = "Transformation parameter %s set to %s" % (paramname,paramvalue)
      res = self.database.updateTransformationLogging(transformationName,message,authorDN)
    return res

  types_addTransformationParameters = []
  def export_addTransformationParameters(self,transNameOrID,parameterDict):
    authorDN = self._clientTransport.peerCredentials['DN']
    failed = []
    for paramName,paramValue in parameterDict.items():
      result = self.database.addTransformationParameter(transNameOrID,paramName,paramValue)
      if result['OK']:
        message = 'Added parameter %s' % paramName
        result = self.database.updateTransformationLogging(transNameOrID,message,authorDN)
      else:
        failed.append(paramName)
    if failed:
      return S_ERROR("Failed to add parameters %s" % str(failed))
    return S_OK()

  types_getTransformationLFNs = [[LongType, IntType, StringType]]
  def export_getTransformationLFNs(self,transName,status='Unused'):
    return self.database.getTransformationLFNs(transName,status)

  types_getTransformationWithStatus = [StringType]
  def export_getTransformationWithStatus(self,status):
    return self.database.getTransformationWithStatus(status)

  types_getTransformationLastUpdate = [[LongType,IntType]]
  def export_getTransformationLastUpdate(self,transID):
    return self.database.getTransformationLastUpdate(transID)

  ############################################################################

  types_getTransformationStats = [[LongType, IntType, StringType]]
  def export_getTransformationStats(self,transformationName):
    res = self.database.getTransformationStats(transformationName)
    return res

  types_getTransformation = [[LongType, IntType, StringType]]
  def export_getTransformation(self,transformationName):
    res = self.database.getTransformation(transformationName)
    return res

  types_getAllTransformations = []
  def export_getAllTransformations(self):
    res = self.database.getAllTransformations()
    return res
    
  types_getDistinctAttributeValues = [StringTypes, DictType]
  def export_getDistinctAttributeValues(self,attribute,selectDict):
    """ Get distinct values of the given Transformation attribute
    """
    
    resultDict = {}
    last_update = None
    if selectDict.has_key('CreationDate'):
      last_update = selectDict['CreationDate']
      del selectDict['CreationDate']
    
    result = self.database.getDistinctAttributeValues("Transformations",attribute,
                                                      selectDict,
                                                      newer=last_update,
                                                      timeStamp='CreationDate')
    return result  

  types_getTransformationLogging = [[LongType, IntType, StringType]]
  def export_getTransformationLogging(self,transID):
    res = self.database.getTransformationLogging(transID)
    return res

  types_getFilesForTransformation = [[LongType, IntType, StringType]]
  def export_getFilesForTransformation(self,transformationName,orderByJobs=False):
    res = self.database.getFilesForTransformation(transformationName,orderByJobs)
    return res

  types_getFileSummary = [ListType,[LongType, IntType, StringType]]
  def export_getFileSummary(self,lfns,transformationName):
    res = self.database.getFileSummary(lfns,transformationName)
    return res

  types_getInputData = [[LongType, IntType, StringType],StringType]
  def export_getInputData(self,transformationName,status):
    res = self.database.getInputData(transformationName,status)
    return res
    
  types_addLFNsToTransformation = [ListType,[LongType, IntType, StringType]]
  def export_addLFNsToTransformation(self,lfns,transformationName):
    res = self.database.addLFNsToTransformation(lfns,transformationName)
    return res  

  types_setFileSEForTransformation = [[LongType, IntType, StringType],StringType,ListType]
  def export_setFileSEForTransformation(self,transformationName,storageElement,lfns):
    res = self.database.setFileSEForTransformation(transformationName,storageElement,lfns)
    return res

  types_setFileStatusForTransformation = [[LongType, IntType, StringType],StringTypes,ListType]
  def export_setFileStatusForTransformation(self,transformationName,status,lfns):
    res = self.database.setFileStatusForTransformation(transformationName,status,lfns)
    return res

  types_resetFileStatusForTransformation = [[LongType, IntType, StringType],ListType]
  def export_resetFileStatusForTransformation(self,transformationName,lfns):
    res = self.database.resetFileStatusForTransformation(transformationName,lfns)
    return res

  types_setFileJobID = [[LongType, IntType, StringType],IntType,ListType]
  def export_setFileJobID(self,transformationName,jobID,lfns):
    res = self.database.setFileJobID(transformationName,jobID,lfns)
    return res

  types_updateTransformation = [ [LongType, IntType, StringType]]
  def export_updateTransformation( self, id_ ):
    result = self.database.updateTransformation(id_)
    if not result['OK']:
      gLogger.error(result['Message'])
    return result  

  types_addBookkeepingQuery = [ DictType ]
  def export_addBookkeepingQuery( self, queryDict ):
    result = self.database.addBookkeepingQuery(queryDict)
    if not result['OK']:
      gLogger.error(result['Message'])
    return result  

  types_getBookkeepingQueryForTransformation = [ [LongType, IntType, StringType]]
  def export_getBookkeepingQueryForTransformation( self, id_ ):
    result = self.database.getBookkeepingQueryForTransformation(id_)
    if not result['OK']:
      gLogger.error(result['Message'])
    return result 
    
  types_getBookkeepingQuery = [ [LongType, IntType]]
  def export_getBookkeepingQuery( self, id_ ):
    result = self.database.getBookkeepingQuery(id_)
    if not result['OK']:
      gLogger.error(result['Message'])
    return result   
  
  types_deleteBookkeepingQuery = [ [LongType, IntType]]
  def export_deleteBookkeepingQuery( self, id_ ):
    result = self.database.deleteBookkeepingQuery(id_)
    if not result['OK']:
      gLogger.error(result['Message'])
    return result  
  
  types_getTransformationStatusCounters = []
  def export_getTransformationStatusCounters( self ):
    result = self.database.getCounters('Transformations',['Status'],{})
    if not result['OK']:
      gLogger.error(result['Message'])
      
    resultDict = {}
    for attrDict,count in result['Value']:
      status = attrDict['Status']
      resultDict[status] = count
        
    return S_OK(resultDict)

  ####################################################################
  #
  # These are the methods to file manipulation
  #

  types_addDirectory = [StringType]
  def export_addDirectory(self,path): #,force):
    res = self.database.addDirectory(path) #,force)
    return res

  types_exists = [ListType]
  def export_exists(self,lfns):
    res = self.database.exists(lfns)
    return res

  types_addFile = [ListType]
  def export_addFile(self,fileTuples,force):
    res = self.database.addFile(fileTuples,force)
    return res

  types_removeFile = [ListType]
  def export_removeFile(self,lfns):
    res = self.database.removeFile(lfns)
    return res

  types_addReplica = [ListType]
  def export_addReplica(self,replicaTuples,force):
    res = self.database.addReplica(replicaTuples,force)
    return res

  types_removeReplica = [ListType]
  def export_removeReplica(self,replicaTuples):
    res = self.database.removeReplica(replicaTuples)
    return res

  types_getReplicas = [ListType]
  def export_getReplicas(self,lfns):
    res = self.database.getReplicas(lfns)
    return res

  types_getReplicaStatus = [ListType]
  def export_getReplicaStatus(self,replicaTuples):
    res = self.database.getReplicaStatus(replicaTuples)
    return res

  types_setReplicaStatus = [ListType]
  def export_setReplicaStatus(self,replicaTuples):
    res = self.database.setReplicaStatus(replicaTuples)
    return res

  types_setReplicaHost = [ListType]
  def export_setReplicaHost(self,replicaTuples):
    res = self.database.setReplicaHost(replicaTuples)
    return res

