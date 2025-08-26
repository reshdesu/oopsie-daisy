import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import tempfile


class FileRecoveryEngine:
    """
    Cross-platform file recovery engine for finding and restoring deleted files.
    This is a simplified implementation focused on user-friendly recovery.
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.common_locations = self._get_common_locations()
        
    def _get_common_locations(self) -> List[Path]:
        """Get common locations where deleted files might be found."""
        locations = []
        home = Path.home()
        
        if self.system == "linux":
            locations.extend([
                home / ".local/share/Trash/files",
                home / ".Trash",
                Path("/tmp"),
                Path("/var/tmp"),
            ])
        elif self.system == "windows":
            # Windows Recycle Bin locations
            for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
                recycle_path = Path(f"{drive}:/$Recycle.Bin")
                if recycle_path.exists():
                    locations.append(recycle_path)
        elif self.system == "darwin":  # macOS
            locations.extend([
                home / ".Trash",
                Path("/.Trashes"),
            ])
            
        # Add common temp directories
        locations.extend([
            Path(tempfile.gettempdir()),
            home / "Downloads",  # Sometimes files get stuck here
        ])
        
        return [loc for loc in locations if loc.exists()]
    
    def scan_for_deleted_files(self) -> List[Dict]:
        """
        Scan for potentially recoverable deleted files.
        Returns a list of file information dictionaries.
        """
        found_files = []
        
        for location in self.common_locations:
            try:
                found_files.extend(self._scan_location(location))
            except (PermissionError, OSError) as e:
                # Skip locations we can't access
                continue
                
        return found_files
    
    def _scan_location(self, location: Path) -> List[Dict]:
        """Scan a specific location for deleted files."""
        files = []
        
        try:
            if location.name in [".local", "Trash", "files", "$Recycle.Bin"]:
                # These are trash/recycle bin locations
                files.extend(self._scan_trash_location(location))
            else:
                # Regular directory scan for temporary files
                files.extend(self._scan_temp_location(location))
                
        except Exception:
            pass
            
        return files
    
    def _scan_trash_location(self, location: Path) -> List[Dict]:
        """Scan trash/recycle bin locations."""
        files = []
        
        try:
            for item in location.iterdir():
                if item.is_file():
                    file_info = {
                        'name': item.name,
                        'path': str(item),
                        'size': item.stat().st_size,
                        'location': str(location),
                        'type': 'trash'
                    }
                    
                    try:
                        # Try to get modification time as deletion approximation
                        mtime = item.stat().st_mtime
                        import datetime
                        file_info['date_deleted'] = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        file_info['date_deleted'] = 'Unknown'
                        
                    files.append(file_info)
                    
        except (PermissionError, OSError):
            pass
            
        return files
    
    def _scan_temp_location(self, location: Path) -> List[Dict]:
        """Scan temporary locations for recently deleted files."""
        files = []
        
        try:
            # Look for files that might be temporary copies of deleted files
            for item in location.iterdir():
                if item.is_file():
                    # Skip system files and very new files
                    if (item.name.startswith('.') or 
                        item.name.startswith('tmp') or
                        item.stat().st_size == 0):
                        continue
                        
                    # Look for files that seem like they might be recovered
                    if any(pattern in item.name.lower() for pattern in [
                        'backup', 'copy', 'temp', 'recovery', 'restore'
                    ]):
                        file_info = {
                            'name': item.name,
                            'path': str(item),
                            'size': item.stat().st_size,
                            'location': str(location),
                            'type': 'temp'
                        }
                        
                        try:
                            import datetime
                            mtime = item.stat().st_mtime
                            file_info['date_deleted'] = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            file_info['date_deleted'] = 'Unknown'
                            
                        files.append(file_info)
                        
        except (PermissionError, OSError):
            pass
            
        return files
    
    def restore_file(self, file_info: Dict, destination_dir: str) -> bool:
        """
        Restore a file to the specified destination directory.
        
        Args:
            file_info: Dictionary containing file information
            destination_dir: Directory to restore the file to
            
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            source_path = Path(file_info['path'])
            dest_dir = Path(destination_dir)
            
            if not source_path.exists():
                return False
                
            if not dest_dir.exists():
                dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Create destination path
            dest_path = dest_dir / file_info['name']
            
            # Handle name conflicts
            counter = 1
            original_dest = dest_path
            while dest_path.exists():
                stem = original_dest.stem
                suffix = original_dest.suffix
                dest_path = dest_dir / f"{stem}_recovered_{counter}{suffix}"
                counter += 1
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            
            # Verify the copy was successful
            if dest_path.exists() and dest_path.stat().st_size > 0:
                return True
                
        except Exception as e:
            raise Exception(f"Failed to restore file: {str(e)}")
            
        return False
    
    def get_system_info(self) -> Dict:
        """Get system information for debugging."""
        return {
            'system': self.system,
            'locations_found': len(self.common_locations),
            'accessible_locations': [str(loc) for loc in self.common_locations],
            'temp_dir': tempfile.gettempdir(),
        }