"""Registry of system capabilities - what can we do?"""

import json
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime


class CapabilityRegistry:
    """
    Tracks what the system can do.

    Capabilities are discovered by:
    - Scanning meta_framework/tools/
    - Reading capability definitions
    - Learning from successful operations
    """

    def __init__(self, meta_framework_path: str = None):
        """Initialize capability registry."""
        if meta_framework_path is None:
            meta_framework_path = Path(__file__).parent.parent

        self.meta_framework_path = Path(meta_framework_path)
        self.registry_file = self.meta_framework_path / "data" / "capabilities.json"

        # Load or create registry
        self.capabilities = self._load_or_scan()

    def _load_or_scan(self) -> Dict[str, Any]:
        """Load existing registry or scan for capabilities."""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)

        return self._scan_capabilities()

    def _scan_capabilities(self) -> Dict[str, Any]:
        """Scan meta_framework for available capabilities."""
        capabilities = {
            "last_scanned": datetime.now().isoformat(),
            "categories": {}
        }

        # Scan tools directory
        tools_dir = self.meta_framework_path / "tools"
        if tools_dir.exists():
            capabilities["categories"]["tools"] = self._scan_tools(tools_dir)

        return capabilities

    def _scan_tools(self, tools_dir: Path) -> Dict[str, List[str]]:
        """Scan tools directory for Python modules."""
        tools = {}

        for category_dir in tools_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('_'):
                category = category_dir.name
                tools[category] = []

                for py_file in category_dir.glob("*.py"):
                    if not py_file.name.startswith('_'):
                        tools[category].append(py_file.stem)

        return tools

    def save(self):
        """Save registry to file."""
        self.capabilities["last_scanned"] = datetime.now().isoformat()

        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.capabilities, f, indent=2)

    def add_capability(
        self,
        name: str,
        category: str,
        description: str,
        operations: List[str]
    ):
        """Register a new capability."""
        if category not in self.capabilities["categories"]:
            self.capabilities["categories"][category] = {}

        self.capabilities["categories"][category][name] = {
            "description": description,
            "operations": operations,
            "added_at": datetime.now().isoformat(),
            "used_count": 0,
            "success_rate": 1.0
        }

        self.save()

    def get_capability(self, name: str) -> Dict[str, Any]:
        """Get capability details."""
        for category in self.capabilities["categories"].values():
            if isinstance(category, dict) and name in category:
                return category[name]
        return None

    def has_capability(self, name: str) -> bool:
        """Check if capability exists."""
        return self.get_capability(name) is not None

    def list_capabilities(self, category: str = None) -> Dict[str, Any]:
        """List all capabilities or by category."""
        if category:
            return self.capabilities["categories"].get(category, {})
        return self.capabilities["categories"]

    def record_usage(self, name: str, success: bool):
        """Record capability usage."""
        capability = self.get_capability(name)
        if capability:
            capability["used_count"] += 1

            # Update success rate (exponential moving average)
            alpha = 0.2  # Weight for new observation
            current_rate = capability.get("success_rate", 1.0)
            new_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * current_rate
            capability["success_rate"] = new_rate

            self.save()

    def get_operations(self, category: str) -> List[str]:
        """Get available operations for a category."""
        operations = set()

        category_data = self.capabilities["categories"].get(category, {})
        if isinstance(category_data, dict):
            for cap_name, cap_data in category_data.items():
                if isinstance(cap_data, dict) and "operations" in cap_data:
                    operations.update(cap_data["operations"])

        return sorted(list(operations))

    def check_required_capabilities(
        self,
        required: List[str]
    ) -> Dict[str, bool]:
        """Check which required capabilities are available."""
        return {
            cap: self.has_capability(cap)
            for cap in required
        }

    def get_missing_capabilities(
        self,
        required: List[str]
    ) -> List[str]:
        """Get list of missing capabilities."""
        return [
            cap for cap in required
            if not self.has_capability(cap)
        ]

    def export_summary(self) -> Dict[str, Any]:
        """Export capability summary."""
        summary = {
            "total_capabilities": 0,
            "by_category": {},
            "most_used": [],
            "highest_success": []
        }

        all_caps = []

        for category, caps in self.capabilities["categories"].items():
            if isinstance(caps, dict):
                summary["by_category"][category] = len(caps)
                summary["total_capabilities"] += len(caps)

                for name, data in caps.items():
                    if isinstance(data, dict):
                        all_caps.append({
                            "name": name,
                            "category": category,
                            "used_count": data.get("used_count", 0),
                            "success_rate": data.get("success_rate", 1.0)
                        })

        # Sort by usage
        all_caps.sort(key=lambda x: x["used_count"], reverse=True)
        summary["most_used"] = all_caps[:5]

        # Sort by success rate (with min usage threshold)
        reliable = [c for c in all_caps if c["used_count"] >= 3]
        reliable.sort(key=lambda x: x["success_rate"], reverse=True)
        summary["highest_success"] = reliable[:5]

        return summary
