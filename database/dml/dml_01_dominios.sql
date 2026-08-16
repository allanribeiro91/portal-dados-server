/* CONFIGURAÇÃO DO SCHEMA */
SET SEARCH_PATH TO SCPORTALDADOS;

/* CONFIGURAÇÃO DE DATA */
SET DATESTYLE = DMY;

INSERT INTO TB_DOMINIO (
    CO_SEQ_DOMINIO,
    CO_DOMINIO,
    NO_DOMINIO,
    DS_DOMINIO,
    DS_OBSERVACOES
)
VALUES
    /* TIPO DE USUÁRIO */
    (
        1,
        NULL,
        'Tipo de Usuário',
        'Classificação dos níveis de acesso dos usuários.',
        'Domínio agrupador.'
    ),
    (
        2,
        1,
        'Usuário Comum',
        'Usuário com acesso às funcionalidades gerais do Portal de Dados.',
        'Sem observações.'
    ),
    (
        3,
        1,
        'Administrador',
        'Usuário responsável pela administração de usuários e conteúdos.',
        'Sem observações.'
    ),
    (
        4,
        1,
        'Master',
        'Superadministrador com acesso integral às funcionalidades da aplicação.',
        'Sem observações.'
    ),

    /* STATUS DO USUÁRIO */
    (
        5,
        NULL,
        'Status do Usuário',
        'Classificação dos status de acesso dos usuários.',
        'Domínio agrupador.'
    ),
    (
        6,
        5,
        'Ativo',
        'Usuário autorizado a acessar a aplicação.',
        'Sem observações.'
    ),
    (
        7,
        5,
        'Inativo',
        'Usuário desativado administrativamente e sem acesso à aplicação.',
        'Sem observações.'
    ),
    (
        8,
        5,
        'Bloqueado',
        'Usuário com acesso temporariamente bloqueado.',
        'Sem observações.'
    );

SELECT SETVAL(
    PG_GET_SERIAL_SEQUENCE(
        'scportaldados.tb_dominio',
        'co_seq_dominio'
    ),
    (SELECT MAX(CO_SEQ_DOMINIO) FROM TB_DOMINIO),
    TRUE
);