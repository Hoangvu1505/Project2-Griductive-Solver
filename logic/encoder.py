"""
CNF Encoder for Griductive clues.
Converts structured clues into Conjunctive Normal Form (CNF) clauses
using direct combinatorial encoding.
"""

from typing import List, Dict, Any, Optional
import itertools
from engine.clue import Clue
from engine.region import Region
from logic.var_map import VariableMap


def validate_clue(clue: Clue, n: int, name_to_coord: Optional[Dict[str, str]] = None) -> None:
    """
    Validates clue parameters and referenced regions.
    Raises ValueError or KeyError if invalid.
    """
    ctype = clue.clue_type.upper()

    if ctype == 'FACT':
        target = clue.params.get("target") or clue.params.get("cell")
        if not target:
            raise ValueError(f"Clue {clue.id}: FACT missing target")
        status = clue.params.get("status", "").upper()
        if status not in ('CRIMINAL', 'INNOCENT'):
            raise ValueError(f"Clue {clue.id}: Invalid status '{status}'")

    elif ctype in ('SAME', 'DIFFERENT'):
        t1 = clue.params.get("target1") or clue.params.get("cell1")
        t2 = clue.params.get("target2") or clue.params.get("cell2")
        if not t1 or not t2:
            raise ValueError(f"Clue {clue.id}: {ctype} requires target1 and target2")

    elif ctype in ('EXACTLY', 'AT_LEAST', 'AT_MOST'):
        if "k" not in clue.params:
            raise ValueError(f"Clue {clue.id}: Missing parameter 'k'")
        k = int(clue.params["k"])
        region: Region = clue.params.get("region")
        if not region:
            raise ValueError(f"Clue {clue.id}: Missing region")
        cells = region.resolve(n, name_to_coord)
        m = len(cells)
        if k < 0 or k > m:
            raise ValueError(f"Clue {clue.id}: k={k} out of range [0, {m}] for region")

    elif ctype == 'PARITY':
        parity = clue.params.get("parity", "").upper()
        if parity not in ('EVEN', 'ODD'):
            raise ValueError(f"Clue {clue.id}: Parity must be 'EVEN' or 'ODD'")
        region = clue.params.get("region")
        if not region:
            raise ValueError(f"Clue {clue.id}: Missing region for PARITY")

    elif ctype == 'COMPARE':
        op = clue.params.get("op", "")
        if op not in ('>', '<', '=', '==', '>=', '<='):
            raise ValueError(f"Clue {clue.id}: Invalid comparison operator '{op}'")
        if not clue.params.get("region1") or not clue.params.get("region2"):
            raise ValueError(f"Clue {clue.id}: COMPARE requires region1 and region2")

    else:
        raise ValueError(f"Unknown clue type '{ctype}'")


class CNFEncoder:
    """
    Translates Griductive clues into CNF clauses.
    Clause format: list of integers, e.g. [-1, 2] represents (not x1 or x2).
    """

    def __init__(self, var_map: VariableMap, n: int):
        self.var_map = var_map
        self.n = n

    def encode_fact(self, target: str, status: str) -> List[List[int]]:
        v = self.var_map.coord_to_var(target)
        if status.upper() == 'CRIMINAL':
            return [[v]]
        elif status.upper() == 'INNOCENT':
            return [[-v]]
        else:
            raise ValueError(f"Unknown status: {status}")

    def encode_same(self, t1: str, t2: str) -> List[List[int]]:
        v1 = self.var_map.coord_to_var(t1)
        v2 = self.var_map.coord_to_var(t2)
        # v1 <=> v2  =>  (-v1 \/ v2) /\ (v1 \/ -v2)
        return [[-v1, v2], [v1, -v2]]

    def encode_different(self, t1: str, t2: str) -> List[List[int]]:
        v1 = self.var_map.coord_to_var(t1)
        v2 = self.var_map.coord_to_var(t2)
        # v1 XOR v2  =>  (v1 \/ v2) /\ (-v1 \/ -v2)
        return [[v1, v2], [-v1, -v2]]

    def encode_at_most(self, k: int, vars_list: List[int]) -> List[List[int]]:
        """
        Direct combinatorial encoding for sum(vars) <= k.
        For every subset of size k + 1, at least one must be False.
        """
        m = len(vars_list)
        if k < 0:
            return [[]]  # UNSAT: empty clause
        if k >= m:
            return []    # Trivially True

        clauses = []
        for comb in itertools.combinations(vars_list, k + 1):
            clauses.append([-v for v in comb])
        return clauses

    def encode_at_least(self, k: int, vars_list: List[int]) -> List[List[int]]:
        """
        Direct combinatorial encoding for sum(vars) >= k.
        For every subset of size m - k + 1, at least one must be True.
        """
        m = len(vars_list)
        if k <= 0:
            return []    # Trivially True
        if k > m:
            return [[]]  # UNSAT: empty clause

        clauses = []
        subset_size = m - k + 1
        for comb in itertools.combinations(vars_list, subset_size):
            clauses.append([v for v in comb])
        return clauses

    def encode_exactly(self, k: int, vars_list: List[int]) -> List[List[int]]:
        """
        sum(vars) == k:
        Conjunction of encode_at_least(k) and encode_at_most(k).
        Special edge cases: k=0 (all False), k=m (all True).
        """
        m = len(vars_list)
        if k < 0 or k > m:
            return [[]]
        if k == 0:
            return [[-v] for v in vars_list]
        if k == m:
            return [[v] for v in vars_list]

        return self.encode_at_least(k, vars_list) + self.encode_at_most(k, vars_list)

    def encode_parity(self, parity: str, vars_list: List[int]) -> List[List[int]]:
        """
        Encodes that the number of true variables in vars_list has given parity (EVEN or ODD).
        For each forbidden assignment, generate a clause blocking it.
        """
        clauses = []
        target_mod = 0 if parity.upper() == 'EVEN' else 1
        m = len(vars_list)
        for bits in itertools.product([0, 1], repeat=m):
            if sum(bits) % 2 != target_mod:
                clause = []
                for b, v in zip(bits, vars_list):
                    clause.append(-v if b == 1 else v)
                clauses.append(clause)
        return clauses

    def encode_compare(self, r1_vars: List[int], r2_vars: List[int], op: str) -> List[List[int]]:
        """
        Encodes comparison between counts in region 1 and region 2:
        count(r1) op count(r2).
        For all assignments over union of vars, forbids assignments violating op.
        """
        union_vars = sorted(list(set(r1_vars + r2_vars)))
        m = len(union_vars)
        idx_r1 = [union_vars.index(v) for v in r1_vars]
        idx_r2 = [union_vars.index(v) for v in r2_vars]

        def condition_satisfied(c1: int, c2: int) -> bool:
            if op in ('=', '=='):
                return c1 == c2
            elif op == '>':
                return c1 > c2
            elif op == '<':
                return c1 < c2
            elif op == '>=':
                return c1 >= c2
            elif op == '<=':
                return c1 <= c2
            return False

        clauses = []
        for bits in itertools.product([0, 1], repeat=m):
            c1 = sum(bits[i] for i in idx_r1)
            c2 = sum(bits[i] for i in idx_r2)
            if not condition_satisfied(c1, c2):
                clause = []
                for b, v in zip(bits, union_vars):
                    clause.append(-v if b == 1 else v)
                clauses.append(clause)
        return clauses

    def encode_clue(self, clue: Clue) -> List[List[int]]:
        """Converts a single Clue instance to CNF clauses."""
        validate_clue(clue, self.n, self.var_map.get_name_to_coord_map())
        ctype = clue.clue_type.upper()
        name_map = self.var_map.get_name_to_coord_map()

        if ctype == 'FACT':
            t = clue.params.get("target") or clue.params.get("cell")
            st = clue.params.get("status")
            return self.encode_fact(t, st)

        elif ctype == 'SAME':
            t1 = clue.params.get("target1") or clue.params.get("cell1")
            t2 = clue.params.get("target2") or clue.params.get("cell2")
            return self.encode_same(t1, t2)

        elif ctype == 'DIFFERENT':
            t1 = clue.params.get("target1") or clue.params.get("cell1")
            t2 = clue.params.get("target2") or clue.params.get("cell2")
            return self.encode_different(t1, t2)

        elif ctype in ('EXACTLY', 'AT_LEAST', 'AT_MOST'):
            k = int(clue.params.get("k", 0))
            reg: Region = clue.params["region"]
            cells = reg.resolve(self.n, name_map)
            vars_list = [self.var_map.coord_to_var(c) for c in cells]

            if ctype == 'EXACTLY':
                return self.encode_exactly(k, vars_list)
            elif ctype == 'AT_LEAST':
                return self.encode_at_least(k, vars_list)
            elif ctype == 'AT_MOST':
                return self.encode_at_most(k, vars_list)

        elif ctype == 'PARITY':
            parity = clue.params.get("parity", "EVEN")
            reg: Region = clue.params["region"]
            cells = reg.resolve(self.n, name_map)
            vars_list = [self.var_map.coord_to_var(c) for c in cells]
            return self.encode_parity(parity, vars_list)

        elif ctype == 'COMPARE':
            op = clue.params.get("op", "=")
            r1: Region = clue.params["region1"]
            r2: Region = clue.params["region2"]
            cells1 = r1.resolve(self.n, name_map)
            cells2 = r2.resolve(self.n, name_map)
            v1 = [self.var_map.coord_to_var(c) for c in cells1]
            v2 = [self.var_map.coord_to_var(c) for c in cells2]
            return self.encode_compare(v1, v2, op)

        raise ValueError(f"Cannot encode unknown clue type: {ctype}")

