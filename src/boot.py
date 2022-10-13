#import esp
#esp.osdebug(None)

import gc
import uos

# disable REPL on UART(0)
# uos.dupterm(None, 1)

gc.collect()
