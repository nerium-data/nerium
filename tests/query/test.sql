select cast(1.25 as float) as foo  -- float check
        -- timestamp check
        , strftime('%Y-%m-%d', '2017-09-09') as bar
        , 'Hello' as quux  -- ascii string check
        , 'Björk Guðmundsdóttir' as quuux  -- unicode check
    union
    select 42
        , strftime('%Y-%m-%d','2031-05-25')
        , 'yo'
        , 'ƺƺƺƺ';