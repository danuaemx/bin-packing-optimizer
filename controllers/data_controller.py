"""
Controller for data management operations.
"""

from typing import Dict, Any, List, Optional
import json
import csv
from io import StringIO
from .base_controller import BaseController
from models.data_structures import Package, Container, PackingProblem
from models.validation import ValidationService

class DataController(BaseController):
    """Handles data import, export, and management operations."""
    
    def __init__(self):
        super().__init__()
        self.validation_service = ValidationService()
        
    def import_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import package and container data from various formats.
        
        Args:
            request_data: Contains data and format information
            
        Returns:
            Imported and validated data
        """
        self._start_timing()
        
        try:
            data_format = request_data.get('format', 'json')
            raw_data = request_data.get('data')
            
            if not raw_data:
                return self._format_response(False, error="No data provided")
            
            # Parse data based on format
            if data_format.lower() == 'json':
                parsed_data = self._parse_json_data(raw_data)
            elif data_format.lower() == 'csv':
                parsed_data = self._parse_csv_data(raw_data)
            else:
                return self._format_response(False, error=f"Unsupported format: {data_format}")
            
            if not parsed_data:
                return self._format_response(False, error="Failed to parse data")
            
            # Validate parsed data
            validation_results = self._validate_imported_data(parsed_data)
            
            execution_time = self._end_timing()
            
            return self._format_response(
                True,
                data={
                    "parsed_data": parsed_data,
                    "validation": validation_results,
                    "summary": self._generate_import_summary(parsed_data)
                },
                message="Data imported successfully",
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Data import failed: {str(e)}")
            return self._format_response(
                False,
                error=f"Import failed: {str(e)}",
                execution_time=self._end_timing()
            )
    
    def export_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export optimization results or problem data.
        
        Args:
            request_data: Contains data to export and format preferences
            
        Returns:
            Exported data in requested format
        """
        try:
            data = request_data.get('data')
            export_format = request_data.get('format', 'json')
            data_type = request_data.get('type', 'result')  # 'result' or 'problem'
            
            if not data:
                return self._format_response(False, error="No data to export")
            
            if export_format.lower() == 'json':
                exported_data = json.dumps(data, indent=2)
                content_type = 'application/json'
            elif export_format.lower() == 'csv':
                exported_data = self._convert_to_csv(data, data_type)
                content_type = 'text/csv'
            else:
                return self._format_response(False, error=f"Unsupported export format: {export_format}")
            
            return self._format_response(
                True,
                data={
                    "content": exported_data,
                    "content_type": content_type,
                    "filename": f"bin_packing_{data_type}.{export_format.lower()}"
                },
                message="Data exported successfully"
            )
            
        except Exception as e:
            return self._format_response(False, error=f"Export failed: {str(e)}")
    
    def validate_data_format(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data format without importing."""
        try:
            data_format = request_data.get('format', 'json')
            raw_data = request_data.get('data')
            
            validation_result = {
                "is_valid": False,
                "errors": [],
                "warnings": [],
                "structure_info": {}
            }
            
            if data_format.lower() == 'json':
                validation_result = self._validate_json_format(raw_data)
            elif data_format.lower() == 'csv':
                validation_result = self._validate_csv_format(raw_data)
            
            return self._format_response(
                validation_result["is_valid"],
                data=validation_result,
                message="Format validation completed"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))
    
    def get_data_templates(self) -> Dict[str, Any]:
        """Get data format templates for import."""
        try:
            templates = {
                "json": {
                    "packages": [
                        {
                            "name": "package_1",
                            "dimensions": [10, 10, 10],
                            "min_quantity": 1,
                            "max_quantity": 5,
                            "package_type": "regular",
                            "weight": 1.0,
                            "value": 10.0
                        }
                    ],
                    "containers": [
                        {
                            "id": "container_1",
                            "dimensions": [50, 50, 50],
                            "is_optional": false,
                            "container_type": "standard",
                            "max_weight": 100.0,
                            "cost": 50.0
                        }
                    ]
                },
                "csv_packages": "name,width,height,depth,min_quantity,max_quantity,package_type,weight,value\npackage_1,10,10,10,1,5,regular,1.0,10.0",
                "csv_containers": "id,width,height,depth,is_optional,container_type,max_weight,cost\ncontainer_1,50,50,50,false,standard,100.0,50.0"
            }
            
            return self._format_response(
                True,
                data=templates,
                message="Data templates retrieved"
            )
            
        except Exception as e:
            return self._format_response(False, error=str(e))
    
    def _parse_json_data(self, raw_data: str) -> Optional[Dict[str, Any]]:
        """Parse JSON format data."""
        try:
            if isinstance(raw_data, str):
                return json.loads(raw_data)
            return raw_data
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            return None
    
    def _parse_csv_data(self, raw_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Parse CSV format data."""
        try:
            result = {"packages": [], "containers": []}
            
            # Parse packages CSV
            if 'packages' in raw_data:
                packages_reader = csv.DictReader(StringIO(raw_data['packages']))
                for row in packages_reader:
                    package = {
                        "name": row['name'],
                        "dimensions": [int(row['width']), int(row['height']), int(row['depth'])],
                        "min_quantity": int(row.get('min_quantity', 1)),
                        "max_quantity": int(row.get('max_quantity', 1)),
                        "package_type": row.get('package_type', 'regular'),
                        "weight": float(row['weight']) if row.get('weight') else None,
                        "value": float(row['value']) if row.get('value') else None
                    }
                    result["packages"].append(package)
            
            # Parse containers CSV
            if 'containers' in raw_data:
                containers_reader = csv.DictReader(StringIO(raw_data['containers']))
                for row in containers_reader:
                    container = {
                        "id": row['id'],
                        "dimensions": [int(row['width']), int(row['height']), int(row['depth'])],
                        "is_optional": row.get('is_optional', 'false').lower() == 'true',
                        "container_type": row.get('container_type', 'standard'),
                        "max_weight": float(row['max_weight']) if row.get('max_weight') else None,
                        "cost": float(row['cost']) if row.get('cost') else None
                    }
                    result["containers"].append(container)
            
            return result
            
        except Exception as e:
            self.logger.error(f"CSV parsing error: {str(e)}")
            return None
    
    def _validate_imported_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate imported data structure."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate packages
        if 'packages' not in data or not data['packages']:
            validation_result["errors"].append("No packages found in data")
            validation_result["is_valid"] = False
        
        # Validate containers
        if 'containers' not in data or not data['containers']:
            validation_result["errors"].append("No containers found in data")
            validation_result["is_valid"] = False
        
        return validation_result
    
    def _generate_import_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of imported data."""
        return {
            "packages_count": len(data.get('packages', [])),
            "containers_count": len(data.get('containers', [])),
            "total_package_volume": sum(
                p.get('dimensions', [1])[0] * p.get('dimensions', [1, 1])[1] * p.get('dimensions', [1, 1, 1])[2]
                for p in data.get('packages', [])
            ),
            "total_container_volume": sum(
                c.get('dimensions', [1])[0] * c.get('dimensions', [1, 1])[1] * c.get('dimensions', [1, 1, 1])[2]
                for c in data.get('containers', [])
            )
        }
    
    def _convert_to_csv(self, data: Dict[str, Any], data_type: str) -> str:
        """Convert data to CSV format."""
        output = StringIO()
        
        if data_type == 'result' and 'container_assignments' in data:
            # Export packing results
            writer = csv.writer(output)
            writer.writerow(['Container', 'Package', 'Position_X', 'Position_Y', 'Position_Z', 'Width', 'Height', 'Depth'])
            
            for container_id, assignment in data['container_assignments'].items():
                for placed_package in assignment.get('placed_packages', []):
                    writer.writerow([
                        container_id,
                        placed_package['package_name'],
                        placed_package['position'][0] if placed_package['position'] else '',
                        placed_package['position'][1] if len(placed_package['position']) > 1 else '',
                        placed_package['position'][2] if len(placed_package['position']) > 2 else '',
                        placed_package['dimensions'][0],
                        placed_package['dimensions'][1] if len(placed_package['dimensions']) > 1 else '',
                        placed_package['dimensions'][2] if len(placed_package['dimensions']) > 2 else ''
                    ])
        
        return output.getvalue()
    
    def _validate_json_format(self, raw_data: str) -> Dict[str, Any]:
        """Validate JSON format."""
        try:
            data = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
            return {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "structure_info": {
                    "has_packages": 'packages' in data,
                    "has_containers": 'containers' in data,
                    "packages_count": len(data.get('packages', [])),
                    "containers_count": len(data.get('containers', []))
                }
            }
        except json.JSONDecodeError as e:
            return {
                "is_valid": False,
                "errors": [f"Invalid JSON: {str(e)}"],
                "warnings": [],
                "structure_info": {}
            }
    
    def _validate_csv_format(self, raw_data: Dict[str, str]) -> Dict[str, Any]:
        """Validate CSV format."""
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "structure_info": {}
        }
        
        try:
            for data_type, csv_data in raw_data.items():
                reader = csv.DictReader(StringIO(csv_data))
                rows = list(reader)
                result["structure_info"][f"{data_type}_count"] = len(rows)
                
                if not rows:
                    result["warnings"].append(f"No data rows found in {data_type} CSV")
                    
        except Exception as e:
            result["is_valid"] = False
            result["errors"].append(f"CSV validation error: {str(e)}")
        
        return result