grammar Sql;

selectStatement
    : SELECT selectList FROM tableName (WHERE condition)? (ORDER BY orderByColumn)? ';'
    ;

selectList
    : '*'
    | column (',' column)*
    ;

column
    : IDENTIFIER
    ;

tableName
    : IDENTIFIER
    ;

orderByColumn
    : IDENTIFIER
    ;

condition
    : '(' condition ')'                      # parenCondition
    | condition AND condition                # andCondition
    | condition OR condition                 # orCondition
    | column comparisonOperator value        # binCondition
    ;

comparisonOperator
    : '=' | '>' | '<' | '>=' | '<=' | '!='
    ;

value
    : IDENTIFIER
    | NUMBER
    | STRING
    ;


SELECT : 'SELECT';
FROM   : 'FROM';
WHERE  : 'WHERE';
ORDER  : 'ORDER';
BY     : 'BY';
AND    : 'AND';
OR     : 'OR';

IDENTIFIER : [a-zA-Z_][a-zA-Z0-9_]*;
NUMBER     : [0-9]+;
STRING     : '\'' .*? '\'';

WS : [ \t\r\n]+ -> skip;