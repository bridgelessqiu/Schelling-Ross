
"""
This module contains dataclasses for all the *global* parameters.

The following dataclasses are defined:

1. `DiseaseParams`: Global disease parameters (e.g., alpha/beta, state-transition probabilities.)

2. `SocialParams`: Global social contagion parameters (e.g., p_s)

3. `PopulationParams`: Parameters for the agents (e.g., tau, gamma)

4. `InitStateParams`: Parameters for the initial conditions (e.g., initial fraction of infections.)


- Author: Zirou Qiu        
- Last modified: 12/27/2025 

███████╗ ██████╗
     ██╔╝██╔═══██╗
   ██╔╝  ██║   ██║
 ██╔╝    ██║▄▄ ██║
███████╗ ╚██████╔╝
╚══════╝  ╚══▀▀═╝
"""

from dataclasses import dataclass
import utils as ut
from omegaconf import OmegaConf
from typing import Any, Dict, Optional

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
        
        if self.p_IH + self.p_IR > 1.0:
            raise ValueError(
                f"Invalid DiseaseParams: p_IH + p_IR must be <= 1, "
                f"got {self.p_IH} + {self.p_IR} = {self.p_IH + self.p_IR}."
            )


# -------------------------
# -   Social parameters   -
# -------------------------
@dataclass(frozen=True, slots=True)
class SocialParams:
    """
    Global social-contagion parameters.
    Attributes:
        p_s (float): The probability of a versatile agents behaving stubborn
            and does network rewiring.
    """
    
    p_s: float

    def validate(self) -> None:
        ut.check_prob("p_s", self.p_s)


# -----------------------------------
# -   Distribution spec for agents  -
# -----------------------------------
@dataclass(frozen=True, slots=True)
class DistSpec:
    """
    A distribution specification for sampling per-agent parameters.

    Supported distributions:
      - "const": always returns `value`
      - "uniform": samples uniformly from [low, high]
    """

    name: str
    value: Optional[float] = None
    low: Optional[float] = None
    high: Optional[float] = None
    args: Optional[Dict[str, Any]] = None  # for future extensions

    def validate(self, *, field_name: str) -> None:
        """A validation function for a agent-parameter prob. distribution.

        Args:
            field_name (str): The name of an agent parameter
                Note: This is different from self.name. In particular, 
                `field_name` is the name of a parameter (e.g., tau, gamma),
                where self.name is the name of the underlying distribution
                (e.g., uniform) for this parameter. 

        Raises:
            ValueErrors.
        """
        # Distribution name 
        dist_nm = (self.name or "").lower().strip()

        # Constant distribution
        if dist_nm == "const":
            if self.value is None:
                raise ValueError(f"DistSpec[{field_name}]: 'const' requires `value`.")
            ut.check_prob(f"{field_name}.value", self.value)
            return

        # Uniform distribution
        if dist_nm == "uniform":
            if self.low is None or self.high is None:
                raise ValueError(f"DistSpec[{field_name}]: 'uniform' requires `low` and `high`.")
            ut.check_prob(f"{field_name}.low", self.low)
            ut.check_prob(f"{field_name}.high", self.high)

            if self.low > self.high:
                raise ValueError(
                    f"DistSpec[{field_name}]: requires low <= high, got low={self.low}, high={self.high}."
                )
            return

        raise ValueError(
            f"DistSpec[{field_name}]: unsupported name={self.name!r}. "
            f"Supported: 'const', 'uniform'."
        )


# -----------------------------
# -   Population parameters   -
# -----------------------------
@dataclass(frozen=True, slots=True)
class PopulationParams:
    """
    Parameters for the agents

    Attributes:
        frac_stubborn (float): Fraction of stubborn agents.
        frac_prosocial (float): Fraction of pro-social agents.
        tau (DistSpec): Distribution spec for peer-pressure threshold tau_u.
        gamma (DistSpec): Distribution spec for local-fear threshold gamma_u.
        lam (DistSpec): Distribution spec for global-fear threshold lambda_u.
    """

    frac_stubborn: float
    frac_prosocial: float

    tau: DistSpec
    gamma: DistSpec
    lam: DistSpec

    def validate(self) -> None:
        ut.check_prob("frac_stubborn", self.frac_stubborn)
        ut.check_prob("frac_prosocial", self.frac_prosocial)

        self.tau.validate(field_name="tau")
        self.gamma.validate(field_name="gamma")
        self.lam.validate(field_name="lam")

# ------------------------------
# -   Initial state parameters  -
# ------------------------------
@dataclass(frozen=True, slots=True)
class InitStateParams:
    """
    Initial condition specification.

    Attributes:
        init_infected_frac (float): Fraction of agents initially infected (I)
        init_adopted_frac (float): Fraction of agents initially adopted intervention (A=1)
        init_recovered_frac (float, default=0): Fraction of initially recovered agents (R). 
        init_hospitalized_frac (float, default=0): Fraction of initially hospitalized agents (H).
    """

    init_infected_frac: float
    init_adopted_frac: float
    init_recovered_frac: float = 0.0
    init_hospitalized_frac: float = 0.0

    def validate(self) -> None:
        ut.check_prob("init_infected_frac", self.init_infected_frac)
        ut.check_prob("init_adopted_frac", self.init_adopted_frac)
        ut.check_prob("init_recovered_frac", self.init_recovered_frac)
        ut.check_prob("init_hospitalized_frac", self.init_hospitalized_frac)

        # Disease-state fractions checks
        total_disease = self.init_infected_frac + self.init_recovered_frac + self.init_hospitalized_frac

        if total_disease > 1.0:
            raise ValueError(
                "Invalid InitStateParams: init_infected_frac + init_recovered_frac + "
                f"init_hospitalized_frac must be <= 1, got {total_disease}."
            )

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
    population: PopulationParams
    init: InitStateParams

    def validate(self) -> None:
        self.disease.validate()
        self.social.validate()
        self.population.validate()
        self.init.validate()

    @classmethod
    def load_default(cls, path: str = "configs/global.yaml") -> "SimParams":
        """
        Load default parameters from a YAML config.
        """
        cfg = OmegaConf.load(path)

        params = cls(
            disease=DiseaseParams(**cfg.disease),
            social=SocialParams(**cfg.social),
            population=PopulationParams(
                frac_stubborn=cfg.population.frac_stubborn,
                frac_prosocial=cfg.population.frac_prosocial,

                # TODO: DistSpec(**OmegaConf.to_container(cfg.population.tau, resolve=True)) if it fails
                tau=DistSpec(**cfg.population.tau),
                gamma=DistSpec(**cfg.population.gamma),
                lam=DistSpec(**cfg.population.lam)
            ),
            init=InitStateParams(**cfg.init),
        )

        params.validate()
        return params

# For testing purposes only
if __name__ == "__main__":
    import pprint
    params = SimParams.load_default()
    pprint.pprint(params.disease)