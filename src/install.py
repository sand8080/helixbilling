import os
import sys
from helixcore.install.install import PatchProcessor
from helixbilling.conf.db import get_connection
from helixbilling.conf.settings import patch_table_name

def update(patch_processor):
    patch_processor.apply(patch_processor.get_last_applied())

def reinit(patch_processor):
    patch_processor.revert_all()
    patch_processor.apply_all()
    
def revert(patch_processor):
    patch_processor.revert_all()

COMMANDS = {
    'update': update,
    'reinit': reinit,
    'revert': revert,
}

def execute(cmd_name):
    patches_path = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), 
        'patches'
    )
    patch_processor = PatchProcessor(get_connection, patch_table_name, patches_path)
    COMMANDS[cmd_name](patch_processor)
    
    print 'executed command: %s' % cmd_name

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print 'usage: %s %s' % (sys.argv[0], '|'.join(COMMANDS))
        sys.exit(1)
    execute(sys.argv[1])
    
if __name__ == '__main__':        
    main()
