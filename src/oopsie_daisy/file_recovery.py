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
            
        # Add common temp directories and recovery locations
        locations.extend([
            Path(tempfile.gettempdir()),
            home / "Downloads",  # Sometimes files get stuck here
            home / "AppData/Local/Temp" if self.system == "windows" else None,
            home / ".cache" if self.system == "linux" else None,
            home / "Library/Caches" if self.system == "darwin" else None,
        ])
        
        # Add browser cache/download locations for deeper recovery
        if self.system == "windows":
            browser_locations = [
                home / "AppData/Local/Google/Chrome/User Data/Default/Downloads",
                home / "AppData/Local/Microsoft/Edge/User Data/Default/Downloads",
                home / "AppData/Roaming/Mozilla/Firefox/Profiles"
            ]
        elif self.system == "linux":
            browser_locations = [
                home / ".config/google-chrome/Default/Downloads",
                home / ".mozilla/firefox",
                home / "snap/firefox/common/.mozilla/firefox"
            ]
        else:  # macOS
            browser_locations = [
                home / "Library/Application Support/Google/Chrome/Default/Downloads",
                home / "Library/Application Support/Firefox/Profiles"
            ]
        
        locations.extend(browser_locations)
        
        return [loc for loc in locations if loc and loc.exists()]
    
    def scan_for_deleted_files(self, deep_scan: bool = False) -> List[Dict]:
        """
        Scan for potentially recoverable deleted files.
        Args:
            deep_scan: If True, attempts more thorough recovery methods
        Returns a list of file information dictionaries.
        """
        found_files = []
        
        for location in self.common_locations:
            try:
                found_files.extend(self._scan_location(location))
            except (PermissionError, OSError) as e:
                # Skip locations we can't access
                continue
        
        # Deep scan for permanently deleted files (if requested)
        if deep_scan:
            found_files.extend(self._deep_scan_recovery())
                
        return found_files
    
    def _deep_scan_recovery(self) -> List[Dict]:
        """
        Attempt to find permanently deleted files using system tools.
        This requires elevated permissions and may take longer.
        """
        found_files = []
        
        try:
            if self.system == "linux":
                found_files.extend(self._linux_deep_scan())
            elif self.system == "windows":
                found_files.extend(self._windows_deep_scan())
            elif self.system == "darwin":
                found_files.extend(self._macos_deep_scan())
                
        except Exception as e:
            # Deep scan failed, return empty list
            pass
            
        return found_files
    
    def _linux_deep_scan(self) -> List[Dict]:
        """Linux-specific deep recovery using system tools."""
        found_files = []
        home = Path.home()
        
        # Check for .*.swp files (vim temporary files)
        for pattern in ["**/.*.swp", "**/*~", "**/*.tmp"]:
            try:
                for file_path in home.glob(pattern):
                    if file_path.is_file():
                        found_files.append({
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': file_path.stat().st_size,
                            'type': 'temporary_file'
                        })
            except:
                continue
        
        # Check recent file operations in bash history
        bash_history = home / ".bash_history"
        if bash_history.exists():
            try:
                with open(bash_history, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f.readlines()[-100:]:  # Last 100 commands
                        if 'rm ' in line and not line.strip().startswith('#'):
                            # Extract potential deleted file paths
                            parts = line.strip().split()
                            for part in parts[1:]:  # Skip 'rm' command
                                if '/' in part and not part.startswith('-'):
                                    potential_path = Path(part).resolve()
                                    if not potential_path.exists():
                                        found_files.append({
                                            'name': potential_path.name,
                                            'path': str(potential_path),
                                            'size': 0,
                                            'type': 'recently_deleted',
                                            'note': 'Found in bash history'
                                        })
            except:
                pass
                
        return found_files
    
    def _windows_deep_scan(self) -> List[Dict]:
        """Windows-specific deep recovery methods."""
        found_files = []
        
        try:
            # Check Windows Recent Items
            recent_folder = Path.home() / "AppData/Roaming/Microsoft/Windows/Recent"
            if recent_folder.exists():
                for lnk_file in recent_folder.glob("*.lnk"):
                    # Parse .lnk files to find original file paths
                    try:
                        # Simple approach - just get the name from .lnk filename
                        original_name = lnk_file.stem
                        found_files.append({
                            'name': original_name,
                            'path': f"Recent: {original_name}",
                            'size': 0,
                            'type': 'recent_item',
                            'note': 'Found in Recent Items'
                        })
                    except:
                        continue
            
            # Check for temp files in Windows temp directories
            temp_dirs = [
                Path.home() / "AppData/Local/Temp",
                Path("C:/Windows/Temp") if Path("C:/Windows/Temp").exists() else None
            ]
            
            for temp_dir in filter(None, temp_dirs):
                try:
                    for pattern in ["*.tmp", "*.temp", "~*"]:
                        for temp_file in temp_dir.glob(pattern):
                            if temp_file.is_file():
                                found_files.append({
                                    'name': temp_file.name,
                                    'path': str(temp_file),
                                    'size': temp_file.stat().st_size,
                                    'type': 'temp_file'
                                })
                except:
                    continue
                    
        except Exception:
            pass
            
        return found_files
    
    def _macos_deep_scan(self) -> List[Dict]:
        """macOS-specific deep recovery methods."""
        found_files = []
        
        try:
            # Check macOS Recent Items
            recent_folders = [
                Path.home() / "Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.RecentDocuments.sfl2",
                Path.home() / "Library/Preferences/com.apple.recentitems.plist"
            ]
            
            for folder in recent_folders:
                if folder.exists():
                    # This would require plist parsing - simplified approach
                    found_files.append({
                        'name': 'Recent Documents',
                        'path': str(folder),
                        'size': folder.stat().st_size,
                        'type': 'recent_items',
                        'note': 'macOS recent items database'
                    })
                    
        except Exception:
            pass
            
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