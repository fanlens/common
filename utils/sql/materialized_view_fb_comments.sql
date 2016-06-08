create materialized view facebook_comments as
select key as comment_id, value::jsonb->'from'->>'id' as from_id, id as post_id, page, value as comment from (
    select id, page, (jsonb_each(facebook.data::jsonb->'comments')).* as comment from facebook
    where facebook.data::jsonb->'comments'->'__crawled_ts' is not null
) as comments
where key not in ('paging', '__crawled_ts', 'data')