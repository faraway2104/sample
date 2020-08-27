import subprocess
import unreal
import sys

BAT_PATH='***/Python/Template/convert.bat'

def main():
    result = subprocess.call(BAT_PATH)
    # When Success
    if result == 0:
        print('Success.')
    else:
        print('Failed.')
        sys.exit(1)

if __name__ == '__main__':
    main()
