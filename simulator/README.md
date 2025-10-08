# Embedded simulator placeholder

The original PACO repository depends on a separate git submodule that hosts
an HTTP simulator.  The execution environment used for these exercises does
not have outbound network access, therefore the submodule cannot be cloned.

To keep the repository functional we vendor the small portion of code that
is required during development: the transformation from PACO parse trees to
the simulator's ``RegionModule`` structure.  The files live under
``simulator/src/paco/parser`` and can be edited directly without relying on
the external submodule.

If you have access to the original simulator repository you can replace this
folder with the upstream code.
