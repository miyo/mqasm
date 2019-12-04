import pyparsing as pp

def syntax():
    
    (SIN, COS, TAN, EXP, LN, SQRT, PI,
     U, CX,
     MEASURE, RESET, BARRIER, GATE, QREG, CREG, OPAQUE, IF,
     INCLUDE,
     OPENQASM) = keyword_list = map(pp.CaselessKeyword,
                                    '''
                                    SIN, COS, TAN, EXP, LN, SQRT, PI,
                                    U, CX,
                                    MEASURE, RESET, BARRIER, GATE, QREG, CREG, OPAQUE, IF,
                                    INCLUDE,
                                    OPENQASM
                                    '''.replace(",","").split())
    keyword = pp.MatchFirst(keyword_list)
    
    real = pp.Regex(r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?").setParseAction(lambda t: {"real" : float(t[0])})
    ident = ~keyword + pp.Regex(r"[a-z][A-Za-z0-9_]*").setParseAction(lambda t: {"ident" : str(t[0])})
    nninteger = pp.Regex(r"[1-9]+\d*|0").setParseAction(lambda t: {"nninteger" : int(t[0])})
    unaryop = (SIN | COS | TAN | EXP | LN | SQRT).setParseAction(lambda t: { "unary" : t[0]})
    quoted_string = pp.QuotedString('"')

    atom = (real | nninteger | PI | ident)
    term = pp.Forward()
    factor = pp.Forward()
    exp = (term + pp.ZeroOrMore(pp.oneOf("+ - ^") + term))
    term << (factor + pp.ZeroOrMore(pp.oneOf("* /") + factor))
    factor << ("-" + exp | unaryop + "(" + exp + ")" | "(" + exp + ")" | atom)
    explist = (exp + pp.ZeroOrMore("," + exp)).setParseAction()

    argument = ident + "[" + nninteger + "]" | ident
    idlist = ident + pp.ZeroOrMore("," + ident)
    mixedlist = argument + pp.ZeroOrMore("," + argument)
    anylist = mixedlist | idlist
    
    uop = (
        U + "(" + explist + ")" + argument + ";"
        | CX + argument + "," + argument + ";"
        | ident + anylist + ";"
        | ident + "(" + ")" + anylist + ";"
        | ident + "(" + explist + ")" + anylist + ";"
    )
    
    qop = (uop
           | MEASURE + argument + "-" + ">" + argument + ";"
           | RESET + argument + ";"
    )
    gop = uop | BARRIER + idlist + ";"
    goplist = pp.OneOrMore(gop)
    gatedecl = (GATE + ident + idlist + "{"
                | GATE + ident + "(" + ")" + idlist + "{"
                | GATE + ident + "(" + idlist + ")" + idlist + "{"
    )
    decl = QREG + ident + "[" + nninteger + "]" + ";" | CREG + ident + "[" + nninteger + "]" + ";"

    statement = (decl
                 | gatedecl + goplist + "}"
                 | gatedecl + "}"
                 | OPAQUE + ident + idlist + ";"
                 | OPAQUE + ident + "(" + ")" + idlist + ";"
                 | OPAQUE + ident + "(" + idlist + ")" + idlist + ";"
                 | qop
                 | IF + "(" + ident + "==" + nninteger + ")" + qop
                 | BARRIER + anylist + ";"
                 | (INCLUDE + quoted_string + ";").setParseAction(lambda t: {"include" : t[1]})
    ).setParseAction(lambda t: { "statement" : t })
    
    program = statement + pp.ZeroOrMore(statement)
    mainprogram = ("OPENQASM" + real + ";" + program + pp.StringEnd()).setParseAction(
        lambda t: {"version": t[1], "program": t[3:]})
    
    mainprogram.ignore(pp.cppStyleComment)
 
    return mainprogram

syntax = syntax()

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

print(syntax.parseString('''
OPENQASM 2.0;
include "qelib1.inc";
'''))
print(syntax.parseString('''
OPENQASM 2.0;
// c++-style comment
include "qel ib1.inc"; // a space in quoted string
'''))

# print(exp.parseString("pi"))
# print(exp.parseString("1.0"))
# print(exp.parseString("1"))
# print(exp.parseString("-1.0"))
# print(exp.parseString("psi"))
# print(exp.parseString("sin(10)"))
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
