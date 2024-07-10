#--- coding=utf-8
#--- @author: yongsheng.guo@ansys.com
#--- @Time: 20240220

import sys
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import MessageBox
print("This is a test progrom.")

def main():
    MessageBox.Show(str(sys.argv))

# release()
if __name__ == '__main__':
#     test1()
    main()