
import mhrc.automation
pscad_version = 'PSCAD 4.6.2 (x64)'
fortran_version = 'GFortran 4.6.2'
fortran_ext = '.gf46'

pscad = mhrc.automation.launch_pscad(certificate = False, silence = True)
print('PSCAD opened')



pscad.workspace().create_project("1","new_project",r"D:")
project_name='new_project'

pscad.load("")#这里需要加载一个已经保存过的project，博主用的是官方给的项目。

main=pscad.project(project_name).user_canvas('Main')
main.add_component('Master', 'capacitor',x=500,y=500)
main.add_wire((500,500), (700,500))

pscad.project(project_name).build()
pscad.project(project_name).run()
pscad.project(project_name).save()