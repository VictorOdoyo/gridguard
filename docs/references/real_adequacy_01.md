# real adequacy 01

Required generator MW above an explicit bus aggregate Pmax must fail adequacy even when load flow converges.

Inputs and expected values: [fixture](../../references/real_adequacy_01.json). Variant 1 exercises a distinct operating point or bound within this family. The regression uses 1e-7 relative and absolute tolerance unless checking solver residual explicitly. This is an analytical example, not a certified field study.
