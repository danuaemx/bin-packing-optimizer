"""
Core data structures for bin packing optimization.
"""

from dataclasses import dataclass
from typing import Tuple, List, Optional, Union
from enum import Enum


class PackageType(Enum):
    """Enumeration of package types."""
    REGULAR = "regular"
    FRAGILE = "fragile"
    HEAVY = "heavy"
    LIQUID = "liquid"


class ContainerType(Enum):
    """Enumeration of container types."""
    STANDARD = "standard"
    REFRIGERATED = "refrigerated"
    SPECIAL = "special"


@dataclass
class Package:
    """
    Represents a package to be packed.
    
    Attributes:
        name: Unique package identifier
        dimensions: Package dimensions (width, height, depth)
        min_quantity: Minimum number of packages required
        max_quantity: Maximum number of packages allowed
        package_type: Type of package (regular, fragile, etc.)
        weight: Package weight (optional)
        value: Package value (optional)
    """
    name: str
    dimensions: Union[Tuple[int], Tuple[int, int], Tuple[int, int, int]]
    min_quantity: int
    max_quantity: int
    package_type: PackageType = PackageType.REGULAR
    weight: Optional[float] = None
    value: Optional[float] = None
    
    def __post_init__(self):
        """Validate package data after initialization."""
        if self.min_quantity < 0:
            raise ValueError("Minimum quantity cannot be negative")
        if self.max_quantity < self.min_quantity:
            raise ValueError("Maximum quantity cannot be less than minimum quantity")
        if len(self.dimensions) not in [1, 2, 3]:
            raise ValueError("Dimensions must be 1D, 2D, or 3D")
        if any(d <= 0 for d in self.dimensions):
            raise ValueError("All dimensions must be positive")
    
    @property
    def volume(self) -> float:
        """Calculate package volume."""
        volume = 1.0
        for dim in self.dimensions:
            volume *= dim
        return volume
    
    @property
    def dimensions_count(self) -> int:
        """Get number of dimensions."""
        return len(self.dimensions)


@dataclass
class Container:
    """
    Represents a container for packing.
    
    Attributes:
        id: Unique container identifier
        dimensions: Container dimensions (width, height, depth)
        is_optional: Whether this container usage is optional
        container_type: Type of container
        max_weight: Maximum weight capacity (optional)
        cost: Container cost (optional)
    """
    id: str
    dimensions: Union[Tuple[int], Tuple[int, int], Tuple[int, int, int]]
    is_optional: bool = False
    container_type: ContainerType = ContainerType.STANDARD
    max_weight: Optional[float] = None
    cost: Optional[float] = None
    
    def __post_init__(self):
        """Validate container data after initialization."""
        if len(self.dimensions) not in [1, 2, 3]:
            raise ValueError("Dimensions must be 1D, 2D, or 3D")
        if any(d <= 0 for d in self.dimensions):
            raise ValueError("All dimensions must be positive")
    
    @property
    def volume(self) -> float:
        """Calculate container volume."""
        volume = 1.0
        for dim in self.dimensions:
            volume *= dim
        return volume
    
    @property
    def dimensions_count(self) -> int:
        """Get number of dimensions."""
        return len(self.dimensions)


@dataclass
class PlacedPackage:
    """
    Represents a package placed in a container.
    
    Attributes:
        package_name: Name of the package
        position: Position in container (x, y, z)
        dimensions: Actual dimensions after rotation
        rotation: Applied rotation identifier
    """
    package_name: str
    position: Union[Tuple[int], Tuple[int, int], Tuple[int, int, int]]
    dimensions: Union[Tuple[int], Tuple[int, int], Tuple[int, int, int]]
    rotation: Optional[str] = None


@dataclass
class PackingProblem:
    """
    Complete bin packing problem definition.
    
    Attributes:
        packages: List of packages to pack
        containers: List of available containers
        allowed_rotations: Rotation permissions per package
        objective: Optimization objective (minimize_containers, maximize_efficiency, etc.)
    """
    packages: List[Package]
    containers: List[Container]
    allowed_rotations: Optional[List[Tuple[bool, ...]]] = None
    objective: str = "minimize_containers"
    
    def __post_init__(self):
        """Validate problem definition."""
        if not self.packages:
            raise ValueError("At least one package must be provided")
        if not self.containers:
            raise ValueError("At least one container must be provided")
        
        # Check dimension consistency
        package_dims = set(len(p.dimensions) for p in self.packages)
        container_dims = set(len(c.dimensions) for c in self.containers)
        
        if len(package_dims) > 1 or len(container_dims) > 1:
            raise ValueError("All packages and containers must have the same number of dimensions")
        
        if package_dims != container_dims:
            raise ValueError("Packages and containers must have the same number of dimensions")
    
    @property
    def dimensions_count(self) -> int:
        """Get number of dimensions for this problem."""
        return len(self.packages[0].dimensions) if self.packages else 0