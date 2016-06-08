update facebook.meta
set data=sub.data
from (
select id, jsonb_set(data, '{tags}', (CAST(data::jsonb->'tags' as JSONB) - 'aaa' - 'bbb' - 'AAA')) as data
from facebook.meta where data::jsonb->'tags' ?| array['aaa', 'bbb', 'AAA']
) as sub
where facebook.meta.id = sub.id;