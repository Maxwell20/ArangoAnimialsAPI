
# Logging config to the point. There are three main section formatters, handlers, and loggers.

#  formatters: It a map or dict struct of key and format key:value pair. How do you want the output to look. it will look like format:'balbalbal'
formatters:
  default: # just a variable name 
    "()": uvicorn.logging.DefaultFormatter
    datefmt: "%Y-%m-%dT%H:%M:%S" 
    format: '[%(asctime)s.%(msecs)03dZ] Mode Name %(name)s %(levelname)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s' # The format

# handlers: It a map or dict struct of key and output param key:value pair. What output source does the logs goto. Output can be console, file, a file with a date, a file and rotate after size. Main thing to look at here is class:'bla.bla.bla'. OH, you also ref the format output by formatter : "this is what you defined in formatters above"
handlers:
 default: # just a variable name 
    formatter: default #refer from above
    class: logging.StreamHandler
    stream: ext://sys.stderr  

# loggers: It a map or dict struct of key and param key:value pairs of what and how to log. 
loggers:
   uvicorn.error: # the class path struct that matches will 
    level: DEBUG     # log message of x and higher
                     # FATAL, ERROR, WARN, INFO, DEBUG
                     # DEBUG will log all, Fatal will only log 
                     # FATAL
    handlers: # Defined above 
      - uvicorn_log_file    # now delcare the ones to use.
    propagate: yes  # pass alone log or logger only to this.
   '':    # Default matches all path structs.
    level: DEBUG
    handlers:
      - app_log_file
      - default


