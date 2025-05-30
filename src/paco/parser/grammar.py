"""
Defining the grammar for SESE diagrams
"""

sese_diagram_grammar = r"""
?start: xor

?xor: parallel
    | xor "/" "[" NAME "]" parallel -> choice
    | xor "^" "[" NAME "]" parallel -> natural

?parallel: sequential
    | parallel "||" sequential  -> parallel

?sequential: region
    | sequential "," region -> sequential    

?region: 
    | NAME   -> task
    | "<" xor ">" -> loop
    | "<" "[" NAME "]"  xor ">" -> loop_probability
    | "(" xor ")"

%import common.CNAME -> NAME
%import common.NUMBER
%import common.WS_INLINE

%ignore WS_INLINE
"""
ALL_SYNTAX = ['^', '/', '||', '<', '>', '[', ']', ',', '', '(', ')'] # all syntax characters available

