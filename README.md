# Welcome to Ansys Toolbox

## 工具说明
Ansys Toolbox提供了一种便捷的方式，让用户在AEDT中迅速运行脚本或外部程序。它通过悬浮图标和自定义菜单的组合，实现高效操作。用户可以借助XML文件快速定制菜单内容，一旦更新，这些变化将实时反映在右键菜单中，确保用户始终拥有个性化的操作体验。


当对应菜单被点击时，Toolbox会将脚本发送至最近一次打开的AEDT窗口并执行其内容。由于Toolbox不区分AEDT的版本，因此可以兼容不同版本的AEDT，使得同一个脚本可以在不同版本的AEDT中执行。

Toolbox支持外部程序和脚本的执行，包括Exe、Python和Ironpython三种类型。目前Toolbox仅支持Windows系统。
## 工具启动
通过目录下的"AnsysToolbox.exe"启动Toolbox，启动后Toolbox以悬浮窗口的形式显示，默认显示在所有窗体的最前面。


可以通过两种方式弹出右键菜单： 
1. 通过在悬浮窗口点击右键  
2. 通过通知图标点击右键。  

## Python环境配置
python和Ironpython的目录必须配置到系统的Path变量里，以确保工具的正确运行。如下图：
对于python脚本的执行，pyaedt必须安装，可以通过在命令窗口中输入：`pip install pyaedt`

## 用户子定义菜单和脚本
用户可以根据自身的需要添加菜单和脚本，定制符合本公司需求的Toolbox工具集合。可以参照下面的方法对菜单和脚本内容继续增加和删除。

## 菜单的设定更新
用户菜单可以通过目录下的menu.xml进行更新和设定。Toolbox发布时已经附带了一些功能和菜单项，用户可以根据需要进行删减和添加自己的菜单内容。

菜单格式如下：
``` xml
<Menu>
	<SubMenu Name="test">
		<SubMenu Type="MenuItem" Name="showProjectName_python" ExecuteType="Python" Path="$UserLib/Template/showProjectName.py" Arguments ="" PythonPath=""></SubMenu>
		<SubMenu Type="MenuItem" Name="showProjectName_Ironpython" ExecuteType="IronPython" Path="$UserLib/Template/showProjectName.py" Arguments ="" EntryFunc="main" PythonPath=""></SubMenu>
	</SubMenu>
</Menu>
```
### 参数说明
- <SubMenu> </SubMenu> 时对菜单项的声明，允许进行嵌套，嵌套将以子菜单的形式呈现。子菜单的深度未作限定，但是不建议嵌套的过深，影响用户体验。
- Type：取值可以为 "MenuItem"（菜单项）,"Separator"(分隔符), 省略时默认为"MenuItem"
- Name：菜单显示的名称
- ExecuteType：可执行程序的类型，可选值：Python，IronPython，EXE。 Command类型为内部保留类型，用户无法进行定义。
- Path: 可执行程序，脚本的路径。可以使用绝对路径值。如果使用相对路径，可以使用"$+目录"的形式引入当面目录下的文件夹。
- Arguments: 允许传递参数给可执行脚本，多个参数以空格隔开。
- PythonPath： 可以指定Python的执行路径，特别是存在多个版本时可以按照路径区分版本。省略时会从Path变量中查找Python执行文件。
- EntryFunc： 针对Python，IronPython指定运行脚本的入口函数，默认为"main"函数（可以省略），如果为其它函数则需要指定函数名称。

### 注意事项
- 设计到文件路径的位置，空格和中文字符可能会导致执行错误，请尽量避免使用。  
- XML里面的文件路径注意使用\\或者使用/。
- XML的语法可以自行搜寻，修改后的温度不能存在语法错误。
- 已知XML注释会导致菜单加载错误，请不用在XML文档中使用注释。
- XML文件编辑保持后，Toolbox会自动重新加载。

## Exe文件的添加

``` xml
<SubMenu Type="MenuItem" Name="Notepad" ExecuteType="EXE" Path="Notepad.exe" Arguments =""/>
```
属性定义如下：  

- Name：菜单显示的名称
- ExecuteType： "EXE"
- Path：可执行文件路径。如果这里指定文档，且系统有默认执行程序，也可以顺利打开，比如Path指定xxx.docx文档。
- Arguments: 传递参数，多个参数以空格隔开。

## Python脚本的添加

``` xml
<SubMenu Type="MenuItem" Name="QuitAedt" ExecuteType="Python" Path="$UserLib/Desktop/Close.py" EntryFunc="ForceQuitAedt" Arguments ="" PythonPath=""></SubMenu>
```
属性定义如下：  

- Name：菜单显示的名称
- ExecuteType：Python
- Path: 脚本的路径。可以使用绝对路径值。如果使用相对路径，可以使用"$+目录"的形式引入当面目录下的文件夹。
- Arguments: 可选，允许传递参数给可执行脚本，多个参数以空格隔开。
- PythonPath： 可选，可以指定Python的执行路径，特别是存在多个版本时可以按照路径区分版本。省略时会从Path变量中查找Python执行文件。
- EntryFunc： 可选，针对Python，IronPython指定运行脚本的入口函数，默认为"main"函数（可以省略），如果为其它函数则需要指定函数名称。

## IronPython脚本的添加

``` xml
<SubMenu Type="MenuItem" Name="QuitAedt" ExecuteType="Python" Path="$UserLib/Desktop/Close.py" EntryFunc="ForceQuitAedt" Arguments ="" PythonPath=""></SubMenu>
```
属性定义如下：  

- Name：菜单显示的名称
- ExecuteType：Python
- Path: 脚本的路径。可以使用绝对路径值。如果使用相对路径，可以使用"$+目录"的形式引入当面目录下的文件夹。
- Arguments: 可选，允许传递参数给可执行脚本，多个参数以空格隔开。
- PythonPath： 可选，可以指定Python的执行路径，特别是存在多个版本时可以按照路径区分版本。省略时会从Path变量中查找Python执行文件。
- EntryFunc： 可选，针对Python，IronPython指定运行脚本的入口函数，默认为"main"函数（可以省略），如果为其它函数则需要指定函数名称。

## python脚本的编写
python脚本可以按照正常的模式进行开发，将需要运行到功能包装成一个函数，最终在菜单的xml里面指定未入口函数即可。  
默认的入口函数未mian()函数，建议使用main()函数作为入口。

下面的案例中，python文件定义了多个函数，可以在xml里面分别指定不同的函数作为入口函数，完成不同的功能。  
另外也可以通过传递不同的Arguments来完成类似的功能。

```python

import sys,os

Module = sys.modules['__main__']
if hasattr(Module, "oDesktop"):
    oDesktop = getattr(Module, "oDesktop")
else:
    raise Exception("oDesktop intial error.")


def closeAndSave():
    oProject = oDesktop.GetActiveProject()
    oProject.Save()
    oProject.Close() 
    
def closeNotSave():
    oProject = oDesktop.GetActiveProject()
    # oProject.Save()
    oProject.Close() #Unsaved changes will be lost.

def closeAllProjectWithSave():
    projects = oDesktop.GetProjects()
    for oProject in projects:
        oProject.Save()
        oProject.Close()
        
def closeAllProjectWithoutSave():
    projects = oDesktop.GetProjects()
    for oProject in projects:
        # oProject.Save()
        oProject.Close() #Unsaved changes will be lost.

def ForceQuitAedt():
    oDesktop.QuitApplication()

def Reload():
    oProject = oDesktop.GetActiveProject()
    aedtPath = os.path.join(oProject.GetPath(),oProject.GetName()+".aedt")
    oProject.Close()
    print("Reload aedt:%s"%aedtPath)
    oDesktop.OpenProject(aedtPath)

```
XML菜单配置

```xml
	<SubMenu Name="Close">
		<SubMenu Type="MenuItem" Name="QuitAedt" ExecuteType="Python" Path="$UserLib/Desktop/Close.py" EntryFunc="ForceQuitAedt"></SubMenu>
		<SubMenu Type="MenuItem" Name="CloseProjectAndSave" ExecuteType="Python" Path="$UserLib/Desktop/Close.py" EntryFunc="closeAndSave"></SubMenu>
		<SubMenu Type="MenuItem" Name="CloseProjectNotSave" ExecuteType="Python" Path="$UserLib/Desktop/Close.py" EntryFunc="closeNotSave"></SubMenu>
		<SubMenu Type="MenuItem" Name="CloseAllProjectWithSave" ExecuteType="Python" Path="$UserLib/Desktop/Close.py" EntryFunc="closeAllProjectWithSave"></SubMenu>
		<SubMenu Type="MenuItem" Name="CloseAllProjectWithoutSave" ExecuteType="Python" Path="$UserLib/Desktop/Close.py" EntryFunc="closeAllProjectWithoutSave"></SubMenu>
		<SubMenu Type="MenuItem" Name="ReloadProject" ExecuteType="IronPython" Path="$UserLib/Desktop/Close.py" EntryFunc="Reload"></SubMenu>
	</SubMenu>
```
