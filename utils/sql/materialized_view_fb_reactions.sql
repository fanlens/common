create materialized view facebook_reactions as
select id as post_id, page, key as from_id, value::jsonb->>'type' as type from (
    select id, page, (jsonb_each(facebook.data::jsonb->'reactions')).* as reaction from facebook
    where facebook.data::jsonb->'reactions'->'__crawled_ts' is not null) as unpacked
where key not in ('paging', '__crawled_ts', 'data')
