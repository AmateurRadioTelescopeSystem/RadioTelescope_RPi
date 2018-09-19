# Strings of the default file settings are included here

log_config_str = """[loggers]
keys=root

[handlers]
keys=radioTelescopeThread,console,debugFile

[formatters]
keys=mainFile,debugging,brief

[logger_root]
level=INFO
handlers=radioTelescopeThread,console,debugFile


[handler_radioTelescopeThread]
class=CLogFileHandler.CustomLogHandler
level=INFO
formatter=mainFile
args=('logs/RadioTeleRPi_Logger.log', 'midnight', 'utf-8', True,)

[handler_console]
class=StreamHandler
level=DEBUG
formatter=brief
args=(sys.stderr,)

[handler_radioTelescope]
class=handlers.TimedRotatingFileHandler
level=WARNING
formatter=mainFile
args=('logs/RadioTelescope_Logger.log', 'midnight', 1, 0, 'utf-8', False, True,)

[handler_debugFile]
class=FileHandler
level=DEBUG
formatter=debugging
args=('logs/debugging_info.log',)


[formatter_mainFile]
format=%(asctime)s  [%(name)30s.%(funcName)-18s]  %(levelname)-8s -  %(message)s

[formatter_debugging]
format=%(asctime)s  [%(thread)12d] %(levelname)-8s - %(name)30s.%(funcName)-20s - %(message)s

[formatter_brief]
format=%(levelname)-8s [%(thread)d] - %(name)30s.%(funcName)-20s - %(message)s
"""

settings_xml_str = """<settings>
    <TCPServer>
        <host>remote</host>
        <port>10001</port>
    </TCPServer>
    <TCPClient>
        <host>10.42.0.1</host>
        <port>10003</port>
    </TCPClient>
    <Steps home_calib="0">
        <RA>0</RA>
        <DEC>0</DEC>
    </Steps>
</settings>
"""