-- Create the function to get user activity metrics
CREATE OR REPLACE FUNCTION get_user_activity_metrics()
RETURNS TABLE (
    user_id UUID,
    emails_generated BIGINT,
    slack_sessions BIGINT,
    last_email_at TIMESTAMPTZ,
    last_session_at TIMESTAMPTZ,
    emails_per_session NUMERIC
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id                              AS user_id,
        COUNT(DISTINCT e.id)              AS emails_generated,
        COUNT(DISTINCT ss.thread_id)      AS slack_sessions,
        MAX(e.created_at)                 AS last_email_at,
        MAX(ss.created_at)                AS last_session_at,
        CASE
            WHEN COUNT(DISTINCT ss.thread_id) > 0
            THEN ROUND(
                COUNT(DISTINCT e.id)::numeric /
                COUNT(DISTINCT ss.thread_id), 2)
            ELSE NULL
        END                               AS emails_per_session
    FROM public.users u
    LEFT JOIN public.emails e
           ON u.id = e.user_id
          AND e.deleted_at IS NULL
    LEFT JOIN public.slack_sessions ss
           ON u.id = ss.user_id
    GROUP BY
        u.id
    ORDER BY
        emails_generated DESC,
        last_email_at   DESC;
END;
$$; 