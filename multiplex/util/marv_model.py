"""Marv Model for outputting to Marv compatible schema - https://github.com/SecretSheppy/marv/blob/main/api/marv-mutations-schema.json"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Status(str, Enum):
    KILLED = "KILLED"
    SURVIVED = "SURVIVED"
    CRASHED = "CRASHED"
    TIMEOUT = "TIMEOUT"
    NO_COVERAGE = "NO_COVERAGE"
    PENDING = "PENDING"
    IGNORED = "IGNORED"


@dataclass
class Pos:
    """A position within a source code file"""

    Line: int  # indexed from 0
    Char: int  # character number indexed from 0


@dataclass
class Mutation:
    """A mutation with data required for Marv to display it inline with the original source code file"""

    ID: str  # UUID
    Description: str
    Operation: str  # mutation operator used
    Start: Pos
    End: Pos
    Status: Status
    Replacement: str  # the source code mutation
    FrameworkMutantID: Optional[str] = None  # optional id assigned by the framework


@dataclass
class MutantRegion:
    """A mutant region (known in Marv as a conflict region) bounded by start and end lines"""

    ID: str  # UUID
    StartLine: int  # inclusive, indexed from 0
    EndLine: int  # non-inclusive, indexed from 0
    Mutations: List[Mutation] = field(default_factory=list)


@dataclass
class MarvOutput:
    """Map of source file paths to array of mutant regions"""

    files: Dict[str, List[MutantRegion]] = field(default_factory=dict)
