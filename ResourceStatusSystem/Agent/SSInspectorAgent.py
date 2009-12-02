########################################################################
# $Id: FailoverRequest.py 18161 2009-11-11 12:07:09Z acasajus $
########################################################################

import threading
from DIRAC import gLogger, S_OK, S_ERROR
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.Core.Utilities.ThreadPool import ThreadPool,ThreadedJob
from DIRAC.ResourceStatusSystem.Utilities.Exceptions import *
from DIRAC.ResourceStatusSystem.Utilities.Utils import *
from DIRAC.ResourceStatusSystem.PolicySystem.PEP import PEP
from DIRAC.ResourceStatusSystem.DB.ResourceStatusDB import *
from DIRAC.ResourceStatusSystem.Policy import Configurations

__RCSID__ = "$Id: ZuziaAgent.py 18894 2009-12-02 17:23:55Z atsareg $"

AGENT_NAME = 'ResourceStatus/SSInspectorAgent'

class SSInspectorAgent(AgentModule):
  """ Class SSInspectorAgent is in charge of going through Sites
      table, and pass Site and Status to the PEP
  """

  def initialize(self):
    """ Standard constructor
    """
    
    try:
      try:
        self.rsDB = ResourceStatusDB()
      except RSSDBException, x:
        gLogger.error(whoRaised(x))
      except RSSException, x:
        gLogger.error(whoRaised(x))
      
      self.am_setOption( "PollingTime", 60 )
      self.SitesToBeChecked = []
      self.SiteNamesInCheck = []
      #self.maxNumberOfThreads = gConfig.getValue(self.section+'/NumberOfThreads',1)
      #self.threadPoolDepth = gConfig.getValue(self.section+'/ThreadPoolDepth',1)
      
      self.maxNumberOfThreads = self.am_getOption( 'maxThreadsInPool', 1 )
      #self.threadPool = ThreadPool(1,self.maxNumberOfThreads)
  
      #vedi taskQueueDirector
      self.threadPool = ThreadPool( self.am_getOption('minThreadsInPool'),
                         self.am_getOption('maxThreadsInPool'),
                         self.am_getOption('totalThreadsInPool') )
      if not self.threadPool:
        self.log.error('Can not create Thread Pool:')
        return
      
      self.lockObj = threading.RLock()
      
      return S_OK()
    
    except Exception, x:
      errorStr = where(self, self.execute)
      gLogger.exception(errorStr,lException=x)
      return S_ERROR(errorStr)


  def execute(self):
    """ The main SSInspectorAgent execution method
    """
    
    try:
      sitesGetter = ThreadedJob(self._getSitesToCheck)
      self.threadPool.queueJob(sitesGetter)
      
      #for i in range(self.threadPoolDepth - 2):
      for i in range(self.maxNumberOfThreads - 1):
        checkExecutor = ThreadedJob(self._executeCheck)
        self.threadPool.queueJob(checkExecutor)
    
      self.threadPool.processResults()
      return S_OK()

    except Exception, x:
      errorStr = where(self, self.execute)
      gLogger.exception(errorStr,lException=x)
      return S_ERROR(errorStr)
      
  def _getSitesToCheck(self):
    """ 
    Call :meth:`DIRAC.ResourceStatusSystem.DB.ResourceStatusDB.getSitesToCheck` and put result in list
    """
    
    try:
      res = self.rsDB.getSitesToCheck(Configurations.ACTIVE_CHECK_FREQUENCY, Configurations.PROBING_CHECK_FREQUENCY, Configurations.BANNED_CHECK_FREQUENCY)
    except RSSDBException, x:
      gLogger.error(whoRaised(x))
    except RSSException, x:
      gLogger.error(whoRaised(x))

    for siteTuple in res:
      if siteTuple[0] in self.SiteNamesInCheck:
        break
      siteL = ['Site']
      for x in siteTuple:
        siteL.append(x)
      self.lockObj.acquire()
      try:
        self.SiteNamesInCheck.insert(0, siteL[1])
        self.SitesToBeChecked.insert(0, siteL)
      finally:
        self.lockObj.release()


  def _executeCheck(self):
    """ 
    Create istance of a PEP, instantiated popping a site from lists.
    """
    
    if len(self.SitesToBeChecked) > 0:
        
      self.lockObj.acquire()
      try:
        toBeChecked = self.SitesToBeChecked.pop()
      finally:
        self.lockObj.release()
      
      granularity = toBeChecked[0]
      siteName = toBeChecked[1]
      status = toBeChecked[2]
      formerStatus = toBeChecked[3]
      reason = toBeChecked[4]
      
      newPEP = PEP(granularity = granularity, name = siteName, status = status, formerStatus = formerStatus, reason = reason)
      newPEP.enforce()

      self.lockObj.acquire()
      try:
        self.SiteNamesInCheck.remove(siteName)
      finally:
        self.lockObj.release()
