# injection transfer 05

A balanced injection/withdrawal transfer is slack-independent: verify incremental branch currents satisfy nodal KCL and sum to the specified transfer.

Inputs and expected values: [fixture](../../references/injection_transfer_05.json). Variant 5 exercises a distinct operating point or bound within this family. The regression uses 1e-7 relative and absolute tolerance unless checking solver residual explicitly. This is an analytical example, not a certified field study.
