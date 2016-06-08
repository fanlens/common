select agg.post_id, agg.type, agg.r, agg.c, string_agg(comments.comment::jsonb->>'message', E'\n') as text from (
  select post_id, type, dense_rank() over (partition by post_id order by count(type) desc) as r, count(*) as c
  from facebook_reactions
  where page = 'redbull' and type != 'LIKE'
  group by post_id, type
  ) as agg, facebook_comments as comments
where agg.post_id = comments.post_id and agg.r <= 2 and agg.c >= 10 and char_length(comments.comment::jsonb->>'message') > 140
group by agg.post_id, agg.type, agg.r, agg.c
order by agg.post_id, agg.r