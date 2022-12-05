# MBD02

## Input limitation in OCC protocol

- Only can handle data with one char value, e.g: R1(X) R22(Y) is accepted, and not R1(AB), R23(BD)
- Only can handle schedule with sequencial transaction ids from 1, e.g: T1, T2; or T1, T2, T3; or T1, T2, T3; etc, and not T2, T3; or T1, T3; etc
