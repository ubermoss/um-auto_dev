
import bpy

# Delete default cube if it exists
if "Cube" in bpy.data.objects and "RedCube" != "Cube":
    bpy.data.objects["Cube"].select_set(True)
    bpy.ops.object.delete()

# Create new cube
bpy.ops.mesh.primitive_cube_add(
    location=(0, 0, 0),
    scale=(2, 2, 2),
    rotation=(0, 0, 0)
)

# Rename the cube
bpy.context.active_object.name = "RedCube"

print("Cube 'RedCube' created successfully")



import bpy

# Get the object
obj = bpy.data.objects.get("RedCube")
if obj is None:
    print("Error: Object 'RedCube' not found")
else:
    # Create material
    mat = bpy.data.materials.new(name="RedMaterial")
    mat.use_nodes = True

    # Get the principled BSDF node
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1.0)

    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    print("Material 'RedMaterial' assigned to 'RedCube'")



import bpy
import math

# Get or create camera
if "MainCamera" in bpy.data.objects:
    camera = bpy.data.objects["MainCamera"]
else:
    camera_data = bpy.data.cameras.new(name="MainCamera")
    camera = bpy.data.objects.new("MainCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera)

# Set camera location and rotation
camera.location = (7, -7, 5)
camera.rotation_euler = (1.1, 0, 0.785)

# Set as active camera
bpy.context.scene.camera = camera

print("Camera 'MainCamera' configured")



import bpy

# Create light
light_data = bpy.data.lights.new(name="SunLight", type="SUN")
light_data.energy = 2.0

light_object = bpy.data.objects.new(name="SunLight", object_data=light_data)
bpy.context.scene.collection.objects.link(light_object)

# Set location
light_object.location = (5, 5, 10)

print("Light 'SunLight' created")



import bpy

# Set render engine
bpy.context.scene.render.engine = "CYCLES"

# Set samples for Cycles
if "CYCLES" == "CYCLES":
    bpy.context.scene.cycles.samples = 128

# Set resolution
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

print("Render settings configured")



import bpy

# Save the file
bpy.ops.wm.save_as_mainfile(filepath=r"G:\\projects\\um-auto_dev\\test_scenarios\\simple_cube\\output\\red_cube_scene.blend")
print("File saved to: G:\\projects\\um-auto_dev\\test_scenarios\\simple_cube\\output\\red_cube_scene.blend")



import bpy

print("=== Scene Information ===")
print(f"Scene name: {bpy.context.scene.name}")
print(f"Objects in scene: {len(bpy.context.scene.objects)}")
print("\nObjects:")
for obj in bpy.context.scene.objects:
    print(f"  - {obj.name} ({obj.type})")
print("=" * 40)
