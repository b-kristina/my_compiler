grammar Sql;

selectStatement
    : SELECT selectList FROM tableName (WHERE condition)? (GROUP BY groupByColumn)? (ORDER BY orderByColumn)? ';'
    ;

selectList
    : '*'
    | selectItem (',' selectItem)*
    ;

selectItem
    : column
    | aggregateFunction
    ;

column
    : IDENTIFIER
    ;

aggregateFunction
    : COUNT '(' '*' ')'                 # countAll
    | COUNT '(' column ')'              # countColumn
    | SUM '(' column ')'                # sumFunction
    | AVG '(' column ')'                # avgFunction
    | MIN '(' column ')'                # minFunction
    | MAX '(' column ')'                # maxFunction
    ;

tableName
    : IDENTIFIER
    ;

groupByColumn
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
GROUP  : 'GROUP';
AND    : 'AND';
OR     : 'OR';

COUNT : 'COUNT';
SUM   : 'SUM';
AVG   : 'AVG';
MIN   : 'MIN';
MAX   : 'MAX';

IDENTIFIER : [a-zA-Z_][a-zA-Z0-9_]*;
NUMBER     : [0-9]+;
STRING     : '\'' .*? '\'';

WS : [ \t\r\n]+ -> skip;