"""Executor for running Blender Python scripts."""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import json


class BlenderExecutor:
    """Executes Python scripts in Blender's context."""

    def __init__(self, blender_path: str = r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"):
        """Initialize executor with Blender path."""
        self.blender_path = blender_path
        if not Path(blender_path).exists():
            raise FileNotFoundError(f"Blender not found at: {blender_path}")

    def execute_script(
        self,
        script_path: str,
        blend_file: Optional[str] = None,
        background: bool = True,
        python_exit: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a Python script in Blender.

        Args:
            script_path: Path to the Python script to execute
            blend_file: Optional .blend file to open
            background: Run Blender in background mode
            python_exit: Exit Blender after script execution

        Returns:
            Dict with execution results including stdout, stderr, and return code
        """
        cmd = [self.blender_path]

        if background:
            cmd.append("--background")

        if blend_file:
            cmd.append(blend_file)

        cmd.extend(["--python", script_path])

        if python_exit:
            cmd.append("--python-exit-code")
            cmd.append("1")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Execution timed out after 300 seconds",
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(cmd)
            }

    def execute_inline(
        self,
        python_code: str,
        blend_file: Optional[str] = None,
        background: bool = True
    ) -> Dict[str, Any]:
        """
        Execute inline Python code in Blender.

        Args:
            python_code: Python code to execute
            blend_file: Optional .blend file to open
            background: Run Blender in background mode

        Returns:
            Dict with execution results
        """
        # Create a temporary script file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_script = f.name

        try:
            result = self.execute_script(
                script_path=temp_script,
                blend_file=blend_file,
                background=background
            )
            return result
        finally:
            # Clean up temp file
            if os.path.exists(temp_script):
                os.remove(temp_script)

    def render_scene(
        self,
        blend_file: str,
        output_path: str,
        frame: Optional[int] = None,
        engine: str = "CYCLES"
    ) -> Dict[str, Any]:
        """
        Render a scene from a .blend file.

        Args:
            blend_file: Path to .blend file
            output_path: Output path for rendered image
            frame: Optional specific frame to render
            engine: Render engine (CYCLES or EEVEE)

        Returns:
            Dict with render results
        """
        render_script = f"""
import bpy

# Set render engine
bpy.context.scene.render.engine = '{engine}'

# Set output path
bpy.context.scene.render.filepath = r'{output_path}'

# Render
"""
        if frame is not None:
            render_script += f"bpy.context.scene.frame_set({frame})\n"

        render_script += "bpy.ops.render.render(write_still=True)\n"

        return self.execute_inline(
            python_code=render_script,
            blend_file=blend_file,
            background=True
        )
