select 0 as grouping,
       'hello' as label,
       100 as part
union
select 0 as grouping,
       'hello' as label,
       50 as part
union
select 0 as grouping,
       'word' as label,
       20 as part
union 
select 1 as grouping,
       'hello' as label,
       150 as part
union
select 1 as grouping,
       'word' as label,
       20 as part
union
select 3 as grouping,
       NULL as label,
       170 as part