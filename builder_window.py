#-------------------------------------------------
#   File builder_window_builder.py
#-------------------------------------------------

import bpy

#-------------------------------------------------
#   Create class Window
#-------------------------------------------------

class create_window(bpy.types.Operator):
    
    bl_idname = 'mesh.builder_window_builder'
    bl_label = 'Add Window'
    bl_description = 'Add a window object to current scene'
    bl_options = {'REGISTER', 'UNDO'}
    bl_category = 'Builder'
    
    def draw(self, context):
        
        self.layout.label('Look in the properties panel for more configuration options', icon = 'INFO')
        
    def execute(self, context):
        
        create_object(self, context)
        self.report({'INFO'}, 'Exceution succesful')
        return {'FINISHED'}

def create_object(self, context):
    
    # Deselect all objects before adding window object
    
    objects = context.scene.objects
    
    for ob in objects:
        ob.select = False
    
    # Add the window object
    
    # 1. Create the main object
    
    mesh = bpy.data.meshes.new('WindowMesh')
    mesh_object = bpy.data.objects.new('Window', mesh)
    context.scene.objects.link(mesh_object)
    mesh_object.location = context.scene.cursor_location
    
    mesh_object.window_property.add()
    
    #2. Generate window data based on window type
    
    window_type = mesh_object.window_property[0].window_type
    window_data = None
    
    window_data = generate_window_data(window_type, mesh_object.window_property)
    
    # 3. Generate the objects from window data
        
    generate_object_from_data(mesh_object, window_data, context)
    
    # generate_components(self, context)
    

def update_object(self, context):
    
    # Update the old mesh with the updated window attributes
    
    ob = context.object
    
    # Deselect all objects
    
    objects = context.scene.objects
    
    for o in objects:
        o.select = False
    
    window_type = ob.window_property[0].window_type
    window_data = None
    
    window_data = generate_window_data(window_type, ob.window_property)
    
    generate_object_from_data(ob, window_data, context, True)

def update_window_type(self, context):
    
    window_type = context.object.window_property[0].window_type
    # print(window_type)
    
    window_data = None
    if window_type == '1':
        window_data = window_type_1()
    elif window_type == '2':
        window_data = window_type_2()
    
window_type_items = (
    ('1', 'Picture Window', ''),
    ('2', 'Awning Window', ''),
    )
    
class WindowProperty(bpy.types.PropertyGroup):
    
    window_frame_width = bpy.props.FloatProperty(name = 'Window Width', default = 6.0, min = 1.0, max = 100.0, update = update_object, description = 'Width of the window')
    window_frame_height = bpy.props.FloatProperty(name = 'Window Height', default = 2.0, min = 1.0, max = 100.0, update = update_object, description = 'Height of the window')
    window_frame_thickness = bpy.props.FloatProperty(name = 'Window Thickness', default = 0.2, min = 0.1, update = update_object, description = 'Thickness of the window')
    window_frame_depth = bpy.props.FloatProperty(name = 'Window Depth', default = 0.4, min = 0.1, max = 100.0, update = update_object, description = 'Depth of the window')
    glass_pane_thickness = bpy.props.FloatProperty(name = 'Glass Pane Thickness', default = 0.01, min = 0.01, update = update_object, description = 'Thickness of the glass pane')
    
    window_type = bpy.props.EnumProperty(name = 'Window Type', items = window_type_items, update = update_object, description = 'Window Type')
    
#-------------------------------------------------
#   Register the property class
#-------------------------------------------------

bpy.utils.register_class(WindowProperty)
bpy.types.Object.window_property = bpy.props.CollectionProperty(type = WindowProperty)

class VIEW3D_PT_window_builder_config(bpy.types.Panel):
    
    bl_idname = 'VIEW3D_PT_window_builder_config'
    bl_label = 'Window Properties'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_description = 'Configure window object'
    bl_category = 'Builder'
    
    @classmethod
    def poll(cls, context):
        ob = context.object
        
        if ob is None:
            return False
        if 'window_property' not in ob:
            return False
        else:
            return True
    
    def draw(self, context):
        
        ob = context.object
        
        try:
            if 'window_property' not in ob:
                return
        except:
            return
        
        layout = self.layout
        window_properties = ob.window_property[0]
        layout.prop(window_properties, 'window_type')
        
        if window_properties.window_type == '1':
            layout_window_type_1(layout, window_properties)
        elif window_properties.window_type == '2':
            layout_window_type_2(layout, window_properties)
        

def generate_object_from_data(mesh_object, window_data, context, update = False):
    
    if not update:
        # 1. Generate window frame

        mesh = mesh_object.data
        mesh.from_pydata(window_data[0][0], window_data[0][1], window_data[0][2])
        mesh.update()
        mesh_object.select = True
        context.scene.objects.active = mesh_object

        # 2. Generate bounding box

        mesh_2 = bpy.data.meshes.new('WindowBoundingBoxMesh')
        mesh_object_2 = bpy.data.objects.new('WindowBoundingBox', mesh_2)
        context.scene.objects.link(mesh_object_2)
        mesh_object_2.location = context.scene.cursor_location
        mesh_2.from_pydata(window_data[-1][0], window_data[-1][1], window_data[-1][2])
        mesh_2.update()

        # 3. Generate child objects and parent them to main object

        length = len(window_data) - 2
        for i in range(0, length):

            mesh_1 = bpy.data.meshes.new('WindowPanelMesh' + str(i))
            mesh_object_1 = bpy.data.objects.new('WindowPanel' + str(i) , mesh_1)
            context.scene.objects.link(mesh_object_1)
            mesh_object_1.location = context.scene.cursor_location
            mesh_1.from_pydata(window_data[i+1][0], window_data[i+1][1], window_data[i+1][2])
            mesh_1.update()

            mesh_object_1.select = True
            bpy.ops.object.parent_set(type='OBJECT', keep_transform = True)
            mesh_object_1.select = False

        mesh_object_2.select = True
        bpy.ops.object.parent_set(type='OBJECT', keep_transform = True)
        mesh_object_2.select = False
        
    else:
        # 1. Update window frame
        
        oldmesh = mesh_object.data
        mesh = bpy.data.meshes.new(oldmesh.name + 'temp')
        mesh.from_pydata(window_data[0][0], window_data[0][1], window_data[0][2])
        mesh.update()
        mesh_object.select = True
        context.scene.objects.active = mesh_object
        
        children = mesh_object.children
        
        # 2. Update bounding box
        
        oldmesh_2 = children[0]
        mesh_2 = bpy.data.meshes.new(oldmesh_2.name + 'temp')
        mesh_2.from_pydata(window_data[-1][0], window_data[-1][1], window_data[-1][2])
        mesh_2.update()
        
        # 3. Update child objects
        
        length = len(children) - 1
        
        for i in range(0, length):
            oldmesh_1 = children[i+1].data
            mesh_1 = bpy.data.meshes.new(oldmesh_1.name + 'temp')
            mesh_1.from_pydata(window_data[i+1][0], window_data[i+1][1], window_data[i+1][2])
            mesh_1.update()
            
            children[i+1].data = mesh_1
            mesh_1.name = oldmesh_1.name
            bpy.data.meshes.remove(oldmesh_1)
            
        #  4. Remove the old mesh for window frame and bounding box
        
        mesh_object.data = mesh
        mesh.name = oldmesh.name
        bpy.data.meshes.remove(oldmesh)
        
        children[0].data = mesh_2
        mesh_2.name = oldmesh_2.name
        bpy.data.meshes.remove(oldmesh_2)

def generate_window_data(window_type, window_property):
    
    if window_type == '1':
        return window_type_1(window_property)
    elif window_type == '2':
        return window_type_2(window_property)

def window_type_1(window_property):
    window_data = []
    
    w = window_property[0].window_frame_width / 2
    h = window_property[0].window_frame_height / 2
    d = window_property[0].window_frame_depth / 2
    t = window_property[0].window_frame_thickness
    gt = window_property[0].glass_pane_thickness / 2
    
    # 1. Data for main object
    
    vertices = [
                (-w, -d, h),
                (w, -d, h),
                (w, -d, -h),
                (-w, -d, -h),
                (-w+t, -d, h-t),
                (w-t, -d, h-t),
                (w-t, -d, -h+t),
                (-w+t, -d, -h+t),
                (-w, d, h),
                (w, d, h),
                (w, d, -h),
                (-w, d, -h),
                (-w+t, d, h-t),
                (w-t, d, h-t),
                (w-t, d, -h+t),
                (-w+t, d, -h+t)
    ]
    
    faces = [
            (0, 4, 5, 1),
            (1, 5, 6, 2),
            (2, 6, 7, 3),
            (3, 7, 4, 0),
            (8, 9, 13, 12),
            (9, 10, 14, 13),
            (10, 11, 15, 14),
            (11, 8, 12, 15),
            (0, 1, 9, 8),
            (1, 2, 10, 9),
            (2, 3, 11, 10),
            (3, 0, 8, 11),
            (4, 12, 13, 5),
            (5, 13, 14, 6),
            (7, 6, 14, 15),
            (4, 7, 15, 12)
    ]
    
    window_data.append((vertices, [], faces))
    
    # 2. Data for child objects
    
    vertices = [
                (-w+t, -gt, h-t),
                (w-t, -gt, h-t),
                (w-t, -gt, -h+t),
                (-w+t, -gt, -h+t),
                (-w+t, gt, h-t),
                (w-t, gt, h-t),
                (w-t, gt, -h+t),
                (-w+t, gt, -h+t)
    ]
    
    faces = [
            (0, 3, 2, 1),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7)
    ]
    
    window_data.append((vertices, [], faces))
    
    # 3. Data for bounding box
    
    vertices = [
                (-w, -d, h),
                (w, -d, h),
                (w, -d, -h),
                (-w, -d, -h),
                (-w, d, h),
                (w, d, h),
                (w, d, -h),
                (-w, d, -h)
    ]
    
    edges = [
            (0, 1),
            (0, 3),
            (0, 4),
            (1, 5),
            (1, 2),
            (2, 6),
            (2, 3),
            (3, 7),
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4)
    ]
    
    window_data.append((vertices, edges, []))
    print(window_data[0][0])
    return window_data
    
def window_type_2():
    return 2
    
def layout_window_type_1(layout, window_properties):
    layout.prop(window_properties, 'window_frame_width')
    layout.prop(window_properties, 'window_frame_height')
    layout.prop(window_properties, 'window_frame_depth')
    layout.prop(window_properties, 'window_frame_thickness')
    layout.prop(window_properties, 'glass_pane_thickness')
    
def layout_window_type_2(layout, window_properties):
    layout.prop(window_properties, 'window_frame_width')
    layout.prop(window_properties, 'window_frame_height')
