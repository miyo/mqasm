import pyparsing as pp

def Syntax():
    keywords_str = "SIN, COS, TAN, EXP, LN, SQRT, PI, U, CX, MEASURE, RESET, BARRIER, GATE, QREG, CREG, OPAQUE, IF, OPENQASM"
    keyword = pp.MatchFirst(map(pp.CaselessKeyword, keywords_str.replace(",","").split()))

    real = pp.Regex(r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?") #.setParseAction(lambda t: float(t[0]))
    ident = ~keyword + pp.Regex(r"[a-z][A-Za-z0-9_]*")
    nninteger = pp.Regex(r"[1-9]+\d*|0")
    pi = pp.Keyword('pi')
    unaryop = pp.oneOf('sin cos tan exp ln sqrt')
    
    atom = real | nninteger | pi | ident
    term = pp.Forward()
    factor = pp.Forward()
    exp = term + pp.ZeroOrMore(pp.oneOf("+ - ^") + term)
    term << (factor + pp.ZeroOrMore(pp.oneOf("* /") + factor))
    factor << (atom | "-" + exp | unaryop + "(" + exp + ")" | "(" + exp + ")")
    explist = exp + pp.ZeroOrMore("," + exp)

    argument = ident + "[" + nninteger + "]" | ident
    idlist = ident + pp.ZeroOrMore("," + ident)
    mixedlist = argument + pp.ZeroOrMore("," + argument)
    anylist = mixedlist | idlist
    
    uop = (
        "U" + "(" + explist + ")" + argument + ";"
        | "CX" + argument + "," + argument + ";"
        | ident + anylist + ";"
        | ident + "(" + ")" + anylist + ";"
        | ident + "(" + explist + ")" + anylist + ";"
    )
    
    qop = (uop
           | "measure" + argument + "-" + ">" + argument + ";"
           | "reset" + argument + ";"
    )
    goplist = pp.Forward()
    goplist << (uop
                | "barrier" + idlist + ";"
                | goplist + uop
                | goplist + "barrier" + idlist + ";"
    )
    gatedecl = ("gate" + ident + idlist + "{"
                | "gate" + ident + "(" + ")" + idlist + "{"
                | "gate" + ident + "(" + idlist + ")" + idlist + "{"
    )
    decl = "qreg" + ident + "[" + nninteger + "]" + ";" | "creg" + ident + "[" + nninteger + "]" + ";"

    statement = (decl
                 | gatedecl + goplist + "}"
                 | gatedecl + "}"
                 | "opaque" + ident + idlist + ";"
                 | "opaque" + ident + "(" + ")" + idlist + ";"
                 | "opaque" + ident + "(" + idlist + ")" + idlist + ";"
                 | qop
                 | "if" + "(" + ident + "==" + nninteger + ")" + qop
                 | "barrier" + anylist + ";"
    )
    
    program = statement + pp.ZeroOrMore(statement)
    mainprogram = "OPENQASM" + real + ";" + program
    
    return mainprogram

syntax = Syntax()

print(syntax.parseString("OPENQASM 1.0; qreg hoge[10];"))

# print(syntax.parseString("pi"))
# print(syntax.parseString("1.0"))
# print(syntax.parseString("1"))
# print(syntax.parseString("-1.0"))
# print(syntax.parseString("psi"))
# print(syntax.parseString("sin(10)"))
# print(syntax.parseString("10,10"))
# print(anylist.parseString("hoge"))
# print(anylist.parseString("hoge[10]"))
# print(anylist.parseString("hoge,fe"))
# print(anylist.parseString("hoge,fe[10]"))
# print(anylist.parseString("hoge[10],fe"))
# print(anylist.parseString("hoge[10],fe[10]"))
# print(uop.parseString("U(2,2)hoge[10];"))
# print(uop.parseString("CX hoge[10], fefe[20];"))
# print(uop.parseString("fefe hoge,nore;"))
