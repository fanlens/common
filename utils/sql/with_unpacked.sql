with unpacked as (
    select id, (jsonb_each(facebook.data::jsonb->'reactions')).value as reaction from facebook
    where facebook.data::jsonb->'reactions' is not null
)
select id, reaction::jsonb->>'type' as r, count(*) from unpacked
where reaction::jsonb->>'type' is not null
group by id, r

