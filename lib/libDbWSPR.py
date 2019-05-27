from libDb import *


class DatabaseWSPR(Database):
    databaseName = "/run/shm/wspr.db"

    def __init__(self):
        Database.__init__(self, self.databaseName)
        
        self.tableDownload = \
            Table(self,
                  "DOWNLOAD",
                  self.GetSchemaDownload(),
                  self.GetFieldListFromSchema(self.GetSchemaDownload()),
                  [["CALLSIGN"]])
        
        self.tableNameValue = \
            Table(self,
                  "NAME_VALUE",
                  self.GetSchemaNameValue(),
                  ["NAME"])
        
        
    def GetTableDownload(self):
        return self.tableDownload
        
        
    def GetSchemaDownload(self):
        return [
            ('DATE',      'text'),
            ('CALLSIGN',  'text'),
            ('FREQUENCY', 'text'),
            ('SNR',       'text'),
            ('DRIFT',     'text'),
            ('GRID',      'text'),
            ('DBM',       'text'),
            ('WATTS',     'text'),
            ('REPORTER',  'text'),
            ('RGRID',     'text'),
            ('KM',        'text'),
            ('MI',        'text')
        ]

    def GetTableNameValue(self):
        return self.tableNameValue
        
    def GetSchemaNameValue(self):
        return [
            ('NAME',  'text'),
            ('VALUE', 'text')
        ]



        