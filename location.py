from dataclasses import dataclass

@dataclass
class Location:
    row: int
    column: int
    
@dataclass
class Span:
    start: Location
    end: Location