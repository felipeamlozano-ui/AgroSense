from dataclasses import dataclass
from typing import List


@dataclass
class DadosSoloDTO:
    umidade: float
    ph: float
    temperatura: float


@dataclass
class ResultadoDiagnosticoDTO:
    diagnosticos: List[str]
    score: int
    classificacao: str
    risco: str