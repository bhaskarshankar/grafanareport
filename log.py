import logging

logging.basicConfig ( level=logging.INFO , format='%(asctime)s- %(message)s' )
logger = logging.getLogger ( )
logger.addHandler ( logging.FileHandler ( 'grafanarport.log' , 'a' ) )
print = logger.info
