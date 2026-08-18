import json
import sys
from datetime import datetime,timezone


def log_event(message:str,*,severity:str="info",**fields)->None:
    event={"timestamp":datetime.now(timezone.utc).isoformat(),"severity":severity,"message":message,**{key:value for key,value in fields.items() if value is not None}}
    print(json.dumps(event,sort_keys=True),file=sys.stderr)
