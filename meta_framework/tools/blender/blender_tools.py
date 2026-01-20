"""Blender-specific tools and script generation."""

from typing import Dict, Any, Optional, List
from pathlib import Path


class BlenderTools:
    """Tools for generating Blender Python scripts."""

    @staticmethod
    def generate_cube_script(
        location: tuple = (0, 0, 0),
        scale: tuple = (1, 1, 1),
        rotation: tuple = (0, 0, 0),
        name: str = "Cube"
    ) -> str:
        """Generate script to create a cube."""
        return f"""
import bpy

# Delete default cube if it exists
if "Cube" in bpy.data.objects and "{name}" != "Cube":
    bpy.data.objects["Cube"].select_set(True)
    bpy.ops.object.delete()

# Create new cube
bpy.ops.mesh.primitive_cube_add(
    location={location},
    scale={scale},
    rotation={rotation}
)

# Rename the cube
bpy.context.active_object.name = "{name}"

print("Cube '{name}' created successfully")
"""

    @staticmethod
    def generate_sphere_script(
        location: tuple = (0, 0, 0),
        radius: float = 1.0,
        name: str = "Sphere"
    ) -> str:
        """Generate script to create a sphere."""
        return f"""
import bpy

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius={radius},
    location={location}
)

# Rename the sphere
bpy.context.active_object.name = "{name}"

print("Sphere '{name}' created successfully")
"""

    @staticmethod
    def generate_material_script(
        object_name: str,
        color: tuple = (0.8, 0.1, 0.1, 1.0),
        material_name: str = "Material"
    ) -> str:
        """Generate script to create and assign a material."""
        return f"""
import bpy

# Get the object
obj = bpy.data.objects.get("{object_name}")
if obj is None:
    print("Error: Object '{object_name}' not found")
else:
    # Create material
    mat = bpy.data.materials.new(name="{material_name}")
    mat.use_nodes = True

    # Get the principled BSDF node
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = {color}

    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    print("Material '{material_name}' assigned to '{object_name}'")
"""

    @staticmethod
    def generate_camera_script(
        location: tuple = (7, -7, 5),
        rotation: tuple = (1.1, 0, 0.785),
        name: str = "Camera"
    ) -> str:
        """Generate script to set up a camera."""
        return f"""
import bpy
import math

# Get or create camera
if "{name}" in bpy.data.objects:
    camera = bpy.data.objects["{name}"]
else:
    camera_data = bpy.data.cameras.new(name="{name}")
    camera = bpy.data.objects.new("{name}", camera_data)
    bpy.context.scene.collection.objects.link(camera)

# Set camera location and rotation
camera.location = {location}
camera.rotation_euler = {rotation}

# Set as active camera
bpy.context.scene.camera = camera

print("Camera '{name}' configured")
"""

    @staticmethod
    def generate_light_script(
        light_type: str = "SUN",
        location: tuple = (5, 5, 5),
        energy: float = 1.0,
        name: str = "Light"
    ) -> str:
        """Generate script to create a light."""
        return f"""
import bpy

# Create light
light_data = bpy.data.lights.new(name="{name}", type="{light_type}")
light_data.energy = {energy}

light_object = bpy.data.objects.new(name="{name}", object_data=light_data)
bpy.context.scene.collection.objects.link(light_object)

# Set location
light_object.location = {location}

print("Light '{name}' created")
"""

    @staticmethod
    def generate_save_script(output_path: str) -> str:
        """Generate script to save the .blend file."""
        # Normalize path for Windows
        output_path = output_path.replace("\\", "\\\\")
        return f"""
import bpy

# Save the file
bpy.ops.wm.save_as_mainfile(filepath=r"{output_path}")
print("File saved to: {output_path}")
"""

    @staticmethod
    def generate_render_settings_script(
        engine: str = "CYCLES",
        samples: int = 128,
        resolution_x: int = 1920,
        resolution_y: int = 1080
    ) -> str:
        """Generate script to configure render settings."""
        return f"""
import bpy

# Set render engine
bpy.context.scene.render.engine = "{engine}"

# Set samples for Cycles
if "{engine}" == "CYCLES":
    bpy.context.scene.cycles.samples = {samples}

# Set resolution
bpy.context.scene.render.resolution_x = {resolution_x}
bpy.context.scene.render.resolution_y = {resolution_y}

print("Render settings configured")
"""

    @staticmethod
    def combine_scripts(scripts: List[str]) -> str:
        """Combine multiple script snippets into one."""
        return "\n\n".join(scripts)

    @staticmethod
    def generate_scene_info_script() -> str:
        """Generate script to print scene information."""
        return """
import bpy

print("=== Scene Information ===")
print(f"Scene name: {bpy.context.scene.name}")
print(f"Objects in scene: {len(bpy.context.scene.objects)}")
print("\\nObjects:")
for obj in bpy.context.scene.objects:
    print(f"  - {obj.name} ({obj.type})")
print("=" * 40)
"""
