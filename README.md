# pscad_automation_python
 pscad的自动化库学习
<!-- TOC -->

- [pscad_automation_python](#pscad_automation_python)
- [完成路线](#完成路线)
  - [配置](#配置)
  - [前期准备](#前期准备)
  - [打开pscad](#打开pscad)
- [遇到的问题](#遇到的问题)
  - [workspace](#workspace)
  - [component](#component)

<!-- /TOC -->
# 完成路线
## 配置
pycharm

python 3.7

pscad V4.6.2

## 前期准备

* 配置pscad的自动化库`mhrc.automation`，附上官方的[下载地址](https://www.pscad.com/knowledge-base/article/369)
  
  * 因为博主是用anaconda管理环境的，所以我在anaconda建了虚拟环境，把下载的自动化库`.whl`文件放到所在环境地址的`\anacoda\envs\虚拟环境名字\Scripts\`下。
  
   * 在anaconda prompt里进入上述Scripts的文件夹下，并安装.whl文件

    ```python
     pip install mhrc_automation-1.2.4-py3-none-any.whl
    ```
## 打开pscad
```python
import mhrc.automation

pscad_version = 'PSCAD 4.6.2 (x64)'
fortran_version = 'GFortran 4.6.2'
fortran_ext = '.gf46'
pscad = mhrc.automation.launch_pscad(certificate = False, silence = True)
pscad.settings(fortran_version=fortran_version)
print('PSCAD opened')
```

# 遇到的问题
20201102
## workspace

```python
pscad.workspace().create_project("selection", "name", "path")
```

注意：create出来project必须要`build()`、`run()`之后才会在你设置的`path`路径下出现。（博主因为这个问题，create之后一直在路径下没找到文件。）

第二个问题是，必须同时在工作空间`pscad.load()`一个已经保存好的project，才会不报错，不知道为什么[1]。
## component
* 添加组件之前要获取画布控件
```python
    main =pscad.project(project_name).user_canvas('Main')
```

* 添加组件这里出现一个问题是，设定添加电容的位置为(500,500)，是该器件的中心位置。添加线也是(500,500),无法准确找到器件的左/右接线点，还需要再研究[2]。
```python
    main.add_component('Master', 'capacitor',x=500,y=500)
    main.add_wire((500,500), (700,500))
```
待解决[1][2]处，欢迎大家一起学习探讨~
***

