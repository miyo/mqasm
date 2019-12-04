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
    gop = uop | "barrier" + idlist + ";"
    goplist = pp.OneOrMore(gop)
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
print(syntax.parseString('''
OPENQASM 1.0;
qreg hoge[10];
'''))

print(syntax.parseString('''
OPENQASM 2.0;
qreg q[3];
qreg a[2];
creg c[3];
creg syn[2];
x q[0];
barrier q;
syndrome q[0],q[1],q[2],a[0],a[1];
measure a -> syn;
if(syn==1) x q[0];
if(syn==2) x q[2];
if(syn==3) x q[1];
measure q -> c;
'''
))

print(syntax.parseString('''
OPENQASM 2.0;
qreg q[3];
qreg a[2];
creg c[3];
creg syn[2];
gate syndrome d1,d2,d3,a1,a2
{
  cx d1,a1; cx d2,a1;
  cx d2,a2; cx d3,a2;
}
x q[0];
barrier q;
syndrome q[0],q[1],q[2],a[0],a[1];
measure a -> syn;
if(syn==1) x q[0];
if(syn==2) x q[2];
if(syn==3) x q[1];
measure q -> c;
'''
))

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
