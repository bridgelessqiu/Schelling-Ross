
""" 
This module contains dataclasses for all the *global* parameters.
"""

from dataclasses import dataclass
import utils as ut
from omegaconf import OmegaConf

# --------------------------
# -   Disease parameters   -
# --------------------------
@dataclass(frozen=True, slots=True)
class DiseaseParams:
    """
    Global disease parameters

    Attributes:
        alpha (float): The effectiveness of the receiver's intervention
        beta (float): The effectiveness of the spreader's intervention
        p_SI (float): The baseline transmission probability
        p_IH: (float): The probability of hospitalization
        p_IR: (float): The probability of recovery from infection 
        p_HR: (float): The probability of recovery from hospitalization
        p_RS: (float): The probability of being susceptible from recovery
    """
    
    # Intervention effectiveness 
    alpha: float
    beta: float

    # Disease dynamics probs. 
    p_SI: float
    p_IH: float
    p_IR: float
    p_HR: float
    p_RS: float

    def validate(self) -> None:
        for name in ("p_SI", "p_IH", "p_IR", "p_HR", "p_RS", "alpha", "beta"):
            ut.check_prob(name, getattr(self, name))


# -------------------------
# -   Social parameters   -
# -------------------------
@dataclass(frozen=True, slots=True)
class SocialParams:
    """
    Global social-contagion parameters.
    Attributes:
        p_stubborn (float): The probability of a versatile agents behaving stubborn.
    """
    
    p_stubborn: float

    def validate(self) -> None:
        ut.check_prob("p_stubborn", self.p_stubborn)


# ------------------------------
# -    Parameters master class -
# ------------------------------
@dataclass(frozen=True, slots=True)
class SimParams:
    """
    Top-level parameter bundle.
    """
    disease: DiseaseParams
    social: SocialParams

    def validate(self) -> None:
        self.disease.validate()
        self.social.validate()

    @classmethod
    def load_default(cls, path: str = "configs/global.yaml") -> "SimParams":
        """
        Load default parameters from a YAML config.
        """
        cfg = OmegaConf.load(path)

        params = cls(
            disease=DiseaseParams(**cfg.disease),
            social=SocialParams(**cfg.social),
        )

        params.validate()
        return params

if __name__ == "__main__":
    params = SimParams.load_default()
    print(params)